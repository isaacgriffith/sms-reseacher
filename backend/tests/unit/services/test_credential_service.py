"""Unit tests for CredentialService (T050).

Covers:
- Encrypt/decrypt round-trip for api_key.
- upsert creates new record.
- upsert updates existing record.
- get_credential returns None when missing.
- get_effective_key returns DB key when stored.
- get_effective_key falls back to env var when no DB record.
- Passing null api_key clears stored key.
- Version conflict detection.
- configured_via returns correct source string.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import db.models  # noqa: F401
import db.models.search_integrations  # noqa: F401
import db.models.users  # noqa: F401
import pytest
import pytest_asyncio
from db.base import Base
from db.models.search_integrations import IntegrationType, SearchIntegrationCredential
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from backend.services.credential_service import CredentialService, VersionConflictError
from backend.utils.encryption import decrypt_secret, encrypt_secret

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide an in-memory SQLite session with all relevant tables."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
def service() -> CredentialService:
    """Return a fresh CredentialService."""
    return CredentialService()


SECRET = "test-secret-key"

# ---------------------------------------------------------------------------
# Encrypt / decrypt round-trip
# ---------------------------------------------------------------------------


class TestEncryptionRoundTrip:
    """Verifies the encryption utility used by CredentialService."""

    def test_round_trip(self) -> None:
        """Encrypted bytes decrypt back to the original plaintext."""
        plaintext = "sk-ieee-test-key"
        ciphertext = encrypt_secret(plaintext, SECRET)
        assert decrypt_secret(ciphertext, SECRET) == plaintext

    def test_different_secrets_produce_different_ciphertexts(self) -> None:
        """Different secrets produce different ciphertexts."""
        c1 = encrypt_secret("key", "secret-a")
        c2 = encrypt_secret("key", "secret-b")
        assert c1 != c2


# ---------------------------------------------------------------------------
# get_credential
# ---------------------------------------------------------------------------


class TestGetCredential:
    """Tests for CredentialService.get_credential."""

    @pytest.mark.asyncio
    async def test_returns_none_when_missing(self, service, db_session) -> None:
        """Returns None when no record exists for the integration type."""
        result = await service.get_credential(IntegrationType.IEEE_XPLORE, db_session)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_existing_record(self, service, db_session) -> None:
        """Returns the stored row after upsert."""
        with patch("backend.services.credential_service.get_settings") as mock_settings:
            mock_settings.return_value.secret_key = SECRET
            await service.upsert_credential(
                IntegrationType.IEEE_XPLORE, "my-key", None, None, None, db_session
            )

        cred = await service.get_credential(IntegrationType.IEEE_XPLORE, db_session)
        assert cred is not None
        assert cred.integration_type == IntegrationType.IEEE_XPLORE


# ---------------------------------------------------------------------------
# upsert_credential
# ---------------------------------------------------------------------------


class TestUpsertCredential:
    """Tests for CredentialService.upsert_credential."""

    @pytest.mark.asyncio
    async def test_creates_new_record(self, service, db_session) -> None:
        """Creates a new credential record when none exists."""
        with patch("backend.services.credential_service.get_settings") as mock_settings:
            mock_settings.return_value.secret_key = SECRET
            cred = await service.upsert_credential(
                IntegrationType.IEEE_XPLORE, "ieee-key-123", None, None, None, db_session
            )
        assert cred.id is not None
        assert cred.integration_type == IntegrationType.IEEE_XPLORE
        assert cred.api_key_encrypted is not None

    @pytest.mark.asyncio
    async def test_updates_existing_record(self, service, db_session) -> None:
        """Updates the credential when the record already exists."""
        with patch("backend.services.credential_service.get_settings") as mock_settings:
            mock_settings.return_value.secret_key = SECRET
            await service.upsert_credential(
                IntegrationType.IEEE_XPLORE, "old-key", None, None, None, db_session
            )
            cred = await service.upsert_credential(
                IntegrationType.IEEE_XPLORE, "new-key", None, None, 1, db_session
            )

        assert cred.version_id == 2
        decrypted = decrypt_secret(cred.api_key_encrypted, SECRET)
        assert decrypted == "new-key"

    @pytest.mark.asyncio
    async def test_null_api_key_clears_stored_key(self, service, db_session) -> None:
        """Passing api_key=None clears the encrypted key."""
        with patch("backend.services.credential_service.get_settings") as mock_settings:
            mock_settings.return_value.secret_key = SECRET
            await service.upsert_credential(
                IntegrationType.IEEE_XPLORE, "some-key", None, None, None, db_session
            )
            cred = await service.upsert_credential(
                IntegrationType.IEEE_XPLORE, None, None, None, 1, db_session
            )
        assert cred.api_key_encrypted is None

    @pytest.mark.asyncio
    async def test_version_conflict_raises(self, service, db_session) -> None:
        """VersionConflictError raised when version_id does not match stored version."""
        with patch("backend.services.credential_service.get_settings") as mock_settings:
            mock_settings.return_value.secret_key = SECRET
            await service.upsert_credential(
                IntegrationType.IEEE_XPLORE, "key", None, None, None, db_session
            )
            with pytest.raises(VersionConflictError):
                await service.upsert_credential(
                    IntegrationType.IEEE_XPLORE, "new-key", None, None, 99, db_session
                )


# ---------------------------------------------------------------------------
# get_effective_key
# ---------------------------------------------------------------------------


class TestGetEffectiveKey:
    """Tests for CredentialService.get_effective_key."""

    def test_returns_db_key_when_stored(self, service) -> None:
        """Returns the decrypted DB key when api_key_encrypted is present."""
        from unittest.mock import MagicMock
        cred = MagicMock(spec=SearchIntegrationCredential)
        cred.api_key_encrypted = encrypt_secret("db-key", SECRET)
        result = service.get_effective_key(IntegrationType.IEEE_XPLORE, cred, SECRET)
        assert result == "db-key"

    def test_falls_back_to_env_var(self, service, monkeypatch) -> None:
        """Returns the env var value when no DB credential stored."""
        monkeypatch.setenv("IEEE_XPLORE_API_KEY", "env-key-value")
        result = service.get_effective_key(IntegrationType.IEEE_XPLORE, None, SECRET)
        assert result == "env-key-value"

    def test_returns_none_when_no_key_anywhere(self, service, monkeypatch) -> None:
        """Returns None when neither DB nor env var has a key."""
        monkeypatch.delenv("IEEE_XPLORE_API_KEY", raising=False)
        result = service.get_effective_key(IntegrationType.IEEE_XPLORE, None, SECRET)
        assert result is None

    def test_falls_back_to_env_var_when_decrypt_fails(self, service, monkeypatch) -> None:
        """Falls back to env var when decrypt raises an exception."""
        from unittest.mock import MagicMock
        monkeypatch.setenv("IEEE_XPLORE_API_KEY", "fallback-env-key")
        cred = MagicMock(spec=SearchIntegrationCredential)
        cred.api_key_encrypted = b"corrupted-data"  # invalid Fernet token
        result = service.get_effective_key(IntegrationType.IEEE_XPLORE, cred, SECRET)
        assert result == "fallback-env-key"

    def test_db_key_takes_precedence_over_env(self, service, monkeypatch) -> None:
        """DB key is used even when env var is also set."""
        from unittest.mock import MagicMock
        monkeypatch.setenv("IEEE_XPLORE_API_KEY", "env-key")
        cred = MagicMock(spec=SearchIntegrationCredential)
        cred.api_key_encrypted = encrypt_secret("db-key", SECRET)
        result = service.get_effective_key(IntegrationType.IEEE_XPLORE, cred, SECRET)
        assert result == "db-key"


# ---------------------------------------------------------------------------
# configured_via
# ---------------------------------------------------------------------------


class TestConfiguredVia:
    """Tests for CredentialService.configured_via."""

    def test_returns_database_when_db_key_present(self, service) -> None:
        """Returns "database" when api_key_encrypted is set."""
        from unittest.mock import MagicMock
        cred = MagicMock(spec=SearchIntegrationCredential)
        cred.api_key_encrypted = b"some-bytes"
        assert service.configured_via(IntegrationType.IEEE_XPLORE, cred) == "database"

    def test_returns_environment_when_env_var_set(self, service, monkeypatch) -> None:
        """Returns "environment" when env var is set but no DB record."""
        monkeypatch.setenv("IEEE_XPLORE_API_KEY", "env-key")
        assert service.configured_via(IntegrationType.IEEE_XPLORE, None) == "environment"

    def test_returns_not_configured_when_nothing_set(self, service, monkeypatch) -> None:
        """Returns "not_configured" when neither source has a key."""
        monkeypatch.delenv("IEEE_XPLORE_API_KEY", raising=False)
        assert service.configured_via(IntegrationType.IEEE_XPLORE, None) == "not_configured"


# ---------------------------------------------------------------------------
# run_connectivity_test
# ---------------------------------------------------------------------------


class TestRunConnectivityTest:
    """Tests for CredentialService.run_connectivity_test."""

    @pytest.mark.asyncio
    async def test_returns_auth_failed_when_no_key(self, service, db_session) -> None:
        """Returns AUTH_FAILED when no API key is configured."""
        from unittest.mock import patch

        with patch("backend.services.credential_service.get_settings") as mock_settings:
            mock_settings.return_value.secret_key = SECRET
            result = await service.run_connectivity_test(
                IntegrationType.SPRINGER_NATURE, None, db_session
            )
        assert result["status"] == "auth_failed"
        assert "No API key" in result["message"]
        assert "tested_at" in result

    @pytest.mark.asyncio
    async def test_returns_success_for_non_ieee_with_key(self, service, db_session) -> None:
        """Returns SUCCESS for non-IEEE integration with a configured key."""
        from unittest.mock import MagicMock, patch

        cred = MagicMock(spec=SearchIntegrationCredential)
        cred.api_key_encrypted = encrypt_secret("test-api-key", SECRET)
        cred.version_id = 1

        with patch("backend.services.credential_service.get_settings") as mock_settings:
            mock_settings.return_value.secret_key = SECRET
            result = await service.run_connectivity_test(
                IntegrationType.SPRINGER_NATURE, cred, db_session
            )
        assert result["status"] == "success"
        assert "configured" in result["message"]

    @pytest.mark.asyncio
    async def test_creates_new_cred_record_when_cred_is_none(self, service, db_session) -> None:
        """Creates a credential record when cred is None but key configured via env."""
        from unittest.mock import patch

        with patch.dict(os.environ, {"SPRINGER_API_KEY": "env-springer-key"}):  # noqa: SIM117
            with patch("backend.services.credential_service.get_settings") as mock_settings:
                mock_settings.return_value.secret_key = SECRET
                result = await service.run_connectivity_test(
                    IntegrationType.SPRINGER_NATURE, None, db_session
                )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_ieee_probe_called_for_ieee_type(self, service, db_session) -> None:
        """Calls _probe_ieee for IEEE_XPLORE integration type."""
        from unittest.mock import AsyncMock, MagicMock, patch

        cred = MagicMock(spec=SearchIntegrationCredential)
        cred.api_key_encrypted = encrypt_secret("ieee-key", SECRET)
        cred.version_id = 0

        with patch("backend.services.credential_service.get_settings") as mock_settings:
            mock_settings.return_value.secret_key = SECRET
            from db.models.search_integrations import TestStatus
            with patch.object(
                service, "_probe_ieee", new=AsyncMock(return_value=(TestStatus.SUCCESS, "OK"))
            ) as mock_probe:
                await service.run_connectivity_test(
                    IntegrationType.IEEE_XPLORE, cred, db_session
                )
        mock_probe.assert_called_once_with("ieee-key")


# ---------------------------------------------------------------------------
# _probe_ieee
# ---------------------------------------------------------------------------


class TestProbeIeee:
    """Tests for CredentialService._probe_ieee."""

    @pytest.mark.asyncio
    async def test_returns_success_on_200(self) -> None:
        """Returns SUCCESS when IEEE API responds with 200."""
        from unittest.mock import AsyncMock, MagicMock, patch

        import httpx

        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            status, msg = await CredentialService._probe_ieee("test-key")

        from db.models.search_integrations import TestStatus
        assert status == TestStatus.SUCCESS
        assert "reachable" in msg

    @pytest.mark.asyncio
    async def test_returns_auth_failed_on_401(self) -> None:
        """Returns AUTH_FAILED when IEEE API responds with 401."""
        from unittest.mock import AsyncMock, MagicMock, patch

        import httpx

        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 401

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            status, msg = await CredentialService._probe_ieee("bad-key")

        from db.models.search_integrations import TestStatus
        assert status == TestStatus.AUTH_FAILED

    @pytest.mark.asyncio
    async def test_returns_rate_limited_on_429(self) -> None:
        """Returns RATE_LIMITED when IEEE API responds with 429."""
        from unittest.mock import AsyncMock, MagicMock, patch

        import httpx

        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 429

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            status, msg = await CredentialService._probe_ieee("rate-key")

        from db.models.search_integrations import TestStatus
        assert status == TestStatus.RATE_LIMITED

    @pytest.mark.asyncio
    async def test_returns_unreachable_on_transport_error(self) -> None:
        """Returns UNREACHABLE when network error occurs."""
        from unittest.mock import AsyncMock, patch

        import httpx

        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.TransportError("Connection refused")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            status, msg = await CredentialService._probe_ieee("test-key")

        from db.models.search_integrations import TestStatus
        assert status == TestStatus.UNREACHABLE
        assert "Network error" in msg

    @pytest.mark.asyncio
    async def test_returns_unreachable_on_unexpected_status(self) -> None:
        """Returns UNREACHABLE for unexpected HTTP status codes."""
        from unittest.mock import AsyncMock, MagicMock, patch

        import httpx

        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 500

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("httpx.AsyncClient", return_value=mock_client):
            status, msg = await CredentialService._probe_ieee("test-key")

        from db.models.search_integrations import TestStatus
        assert status == TestStatus.UNREACHABLE
        assert "500" in msg
