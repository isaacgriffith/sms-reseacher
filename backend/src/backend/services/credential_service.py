"""CredentialService — encrypted API key management for search integrations.

Handles creating, updating, and retrieving :class:`SearchIntegrationCredential`
records with Fernet-based encryption at rest. Also provides env-var fallback
resolution and lightweight connectivity tests.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

import httpx
from db.models.search_integrations import (
    IntegrationType,
    SearchIntegrationCredential,
    TestStatus,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_logger, get_settings
from backend.utils.encryption import decrypt_secret, encrypt_secret

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Env-var fallback map
# ---------------------------------------------------------------------------

_ENV_FALLBACKS: dict[IntegrationType, str] = {
    IntegrationType.IEEE_XPLORE: "IEEE_XPLORE_API_KEY",
    IntegrationType.ELSEVIER: "ELSEVIER_API_KEY",
    IntegrationType.WEB_OF_SCIENCE: "WOS_API_KEY",
    IntegrationType.SPRINGER_NATURE: "SPRINGER_API_KEY",
    IntegrationType.SEMANTIC_SCHOLAR: "SEMANTIC_SCHOLAR_API_KEY",
    IntegrationType.UNPAYWALL: "UNPAYWALL_EMAIL",
    IntegrationType.GOOGLE_SCHOLAR: "SCHOLARLY_PROXY_URL",
}

# ---------------------------------------------------------------------------
# Version conflict exception
# ---------------------------------------------------------------------------


class VersionConflictError(Exception):
    """Raised when an optimistic-lock version mismatch is detected.

    Attributes:
        integration_type: The integration type that caused the conflict.

    """

    def __init__(self, integration_type: IntegrationType) -> None:
        """Initialise with the conflicting integration type.

        Args:
            integration_type: The :class:`IntegrationType` whose version conflicted.

        """
        super().__init__(f"Version conflict for {integration_type}")
        self.integration_type = integration_type


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class CredentialService:
    """Manages encrypted API credentials for database search integrations.

    All write operations use Fernet symmetric encryption via the application
    ``SECRET_KEY``.  Keys are never returned in plaintext — callers must use
    :meth:`get_effective_key` to resolve a usable key.
    """

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    async def get_credential(
        self,
        integration_type: IntegrationType,
        db: AsyncSession,
    ) -> SearchIntegrationCredential | None:
        """Retrieve the stored credential record for an integration type.

        Args:
            integration_type: The :class:`IntegrationType` to look up.
            db: Active async database session.

        Returns:
            The :class:`SearchIntegrationCredential` ORM object, or ``None``
            if no record exists for the given type.

        """
        result = await db.execute(
            select(SearchIntegrationCredential).where(
                SearchIntegrationCredential.integration_type == integration_type
            )
        )
        return result.scalar_one_or_none()

    async def upsert_credential(
        self,
        integration_type: IntegrationType,
        api_key: str | None,
        auxiliary_token: str | None,
        config_json: dict[str, Any] | None,
        version_id: int | None,
        db: AsyncSession,
    ) -> SearchIntegrationCredential:
        """Create or update the credential record for an integration type.

        Passing ``api_key=None`` clears any previously stored key (the
        integration then falls back to the env-var).  Existing values for
        ``api_key_encrypted``, ``auxiliary_token_encrypted``, and
        ``config_json_encrypted`` are overwritten unconditionally.

        Optimistic locking: if a record already exists and ``version_id``
        does not match the stored version, :class:`VersionConflictError` is
        raised before any write is performed.

        Args:
            integration_type: The :class:`IntegrationType` to upsert.
            api_key: Plaintext API key to encrypt and store, or ``None`` to clear.
            auxiliary_token: Plaintext secondary token (e.g. Elsevier inst token),
                or ``None`` to clear.
            config_json: Additional config dict (e.g. ``{"proxy_url": "…"}``),
                or ``None`` to clear.
            version_id: Client-supplied version for optimistic locking.  Pass
                ``None`` when creating a new record.
            db: Active async database session.

        Returns:
            The updated or newly created :class:`SearchIntegrationCredential`.

        Raises:
            VersionConflictError: If ``version_id`` does not match the stored version.

        """
        import json

        settings = get_settings()
        secret_key = settings.secret_key

        existing = await self.get_credential(integration_type, db)

        if existing is not None:
            # Optimistic locking check
            if version_id is not None and existing.version_id != version_id:
                raise VersionConflictError(integration_type)

            existing.api_key_encrypted = (
                encrypt_secret(api_key, secret_key) if api_key is not None else None
            )
            existing.auxiliary_token_encrypted = (
                encrypt_secret(auxiliary_token, secret_key) if auxiliary_token is not None else None
            )
            existing.config_json_encrypted = (
                encrypt_secret(json.dumps(config_json), secret_key)
                if config_json is not None
                else None
            )
            existing.version_id = existing.version_id + 1
            await db.commit()
            await db.refresh(existing)
            return existing

        # Create new record
        cred = SearchIntegrationCredential(
            integration_type=integration_type,
            api_key_encrypted=(
                encrypt_secret(api_key, secret_key) if api_key is not None else None
            ),
            auxiliary_token_encrypted=(
                encrypt_secret(auxiliary_token, secret_key) if auxiliary_token is not None else None
            ),
            config_json_encrypted=(
                encrypt_secret(json.dumps(config_json), secret_key)
                if config_json is not None
                else None
            ),
            version_id=1,
            last_test_status=TestStatus.UNTESTED,
        )
        db.add(cred)
        await db.commit()
        await db.refresh(cred)
        return cred

    # ------------------------------------------------------------------
    # Key resolution
    # ------------------------------------------------------------------

    def get_effective_key(
        self,
        integration_type: IntegrationType,
        cred: SearchIntegrationCredential | None,
        secret_key: str,
    ) -> str | None:
        """Resolve the effective API key for an integration, DB-first then env-var.

        Args:
            integration_type: The :class:`IntegrationType` being queried.
            cred: The stored credential record, or ``None`` if not in DB.
            secret_key: Application secret for Fernet decryption.

        Returns:
            The plaintext API key string, or ``None`` if no key is configured
            anywhere.

        """
        if cred is not None and cred.api_key_encrypted:
            try:
                return decrypt_secret(cred.api_key_encrypted, secret_key)
            except Exception:  # noqa: BLE001
                logger.warning("credential_decrypt_failed", integration_type=integration_type)

        env_var = _ENV_FALLBACKS.get(integration_type, "")
        if env_var:
            value = os.environ.get(env_var, "").strip()
            if value:
                return value

        return None

    def configured_via(
        self,
        integration_type: IntegrationType,
        cred: SearchIntegrationCredential | None,
    ) -> str:
        """Return the source of the effective credential.

        Returns one of ``"database"``, ``"environment"``, or ``"not_configured"``.

        Args:
            integration_type: The :class:`IntegrationType` being queried.
            cred: The stored credential record, or ``None``.

        Returns:
            One of ``"database"``, ``"environment"``, or ``"not_configured"``.

        """
        if cred is not None and cred.api_key_encrypted:
            return "database"
        env_var = _ENV_FALLBACKS.get(integration_type, "")
        if env_var and os.environ.get(env_var, "").strip():
            return "environment"
        return "not_configured"

    # ------------------------------------------------------------------
    # Connectivity test
    # ------------------------------------------------------------------

    async def run_connectivity_test(
        self,
        integration_type: IntegrationType,
        cred: SearchIntegrationCredential | None,
        db: AsyncSession,
    ) -> dict[str, str]:
        """Run a lightweight connectivity probe for an integration type.

        For most types, simply verifies that a key is configured and returns
        ``success``.  For IEEE Xplore, attempts a real API call.  The result
        is persisted to ``last_tested_at`` and ``last_test_status``.

        Args:
            integration_type: The :class:`IntegrationType` to test.
            cred: Existing credential record (may be ``None``).
            db: Active async database session.

        Returns:
            Dict with ``status``, ``message``, and ``tested_at`` keys.

        """
        settings = get_settings()
        effective_key = self.get_effective_key(integration_type, cred, settings.secret_key)
        now = datetime.now(UTC)

        if effective_key is None:
            test_status = TestStatus.AUTH_FAILED
            message = "No API key configured"
        elif integration_type == IntegrationType.IEEE_XPLORE:
            test_status, message = await self._probe_ieee(effective_key)
        else:
            test_status = TestStatus.SUCCESS
            message = f"Key is configured for {integration_type.value}"

        # Persist result
        if cred is not None:
            cred.last_tested_at = now
            cred.last_test_status = test_status
            cred.version_id = cred.version_id + 1
            await db.commit()
        else:
            new_cred = SearchIntegrationCredential(
                integration_type=integration_type,
                last_tested_at=now,
                last_test_status=test_status,
                version_id=1,
            )
            db.add(new_cred)
            await db.commit()

        return {
            "status": test_status.value,
            "message": message,
            "tested_at": now.isoformat(),
        }

    @staticmethod
    async def _probe_ieee(api_key: str) -> tuple[TestStatus, str]:
        """Probe the IEEE Xplore API with a minimal search request.

        Args:
            api_key: IEEE Xplore API key to use for the probe.

        Returns:
            Tuple of (:class:`TestStatus`, human-readable message).

        """
        url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    url, params={"apikey": api_key, "querytext": "test", "max_records": "1"}
                )
            if resp.status_code == 200:
                return (TestStatus.SUCCESS, "IEEE Xplore API reachable and key accepted")
            if resp.status_code in (401, 403):
                return (
                    TestStatus.AUTH_FAILED,
                    f"IEEE Xplore rejected key (HTTP {resp.status_code})",
                )
            if resp.status_code == 429:
                return (TestStatus.RATE_LIMITED, "IEEE Xplore rate limit reached")
            return (TestStatus.UNREACHABLE, f"Unexpected HTTP {resp.status_code}")
        except httpx.TransportError as exc:
            return (TestStatus.UNREACHABLE, f"Network error: {exc}")
