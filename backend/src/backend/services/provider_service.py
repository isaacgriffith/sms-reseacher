"""ProviderService — CRUD and model-list fetching for LLM providers (Feature 005).

Handles creation, retrieval, update, and deletion of Provider records,
as well as fetching and upserting AvailableModel records from each
provider's catalog API (Anthropic, OpenAI, Ollama).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import httpx
from db.models.agents import Agent, AvailableModel, Provider, ProviderType
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_logger, get_settings
from backend.utils.encryption import decrypt_secret, encrypt_secret

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class ProviderFetchError(Exception):
    """Raised when fetching model list from a provider API fails.

    Attributes:
        message: Human-readable description of the failure.
        status_code: HTTP status code if available.

    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialise with a message and optional HTTP status.

        Args:
            message: Description of the failure.
            status_code: HTTP status code returned by the upstream API.

        """
        super().__init__(message)
        self.status_code = status_code


class ProviderHasDependentsError(Exception):
    """Raised when deleting a Provider that still has Agent dependents.

    Attributes:
        agent_ids: List of dependent agent UUID strings.

    """

    def __init__(self, agent_ids: list[str]) -> None:
        """Initialise with the dependent agent identifiers.

        Args:
            agent_ids: List of agent UUID strings that reference the provider.

        """
        super().__init__(f"Provider is referenced by {len(agent_ids)} agent(s)")
        self.agent_ids = agent_ids


class ModelHasDependentsError(Exception):
    """Raised when disabling an AvailableModel that still has active Agent dependents.

    Attributes:
        agent_ids: List of dependent agent UUID strings.

    """

    def __init__(self, agent_ids: list[str]) -> None:
        """Initialise with the dependent agent identifiers.

        Args:
            agent_ids: List of agent UUID strings that reference the model.

        """
        super().__init__(f"Model is referenced by {len(agent_ids)} active agent(s)")
        self.agent_ids = agent_ids


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclass
class ModelRecord:
    """A discovered model returned from a provider's catalog API.

    Attributes:
        model_identifier: Provider-native model identifier string.
        display_name: Human-readable display label (defaults to model_identifier).

    """

    model_identifier: str
    display_name: str


@dataclass
class ModelRefreshResult:
    """Summary of a provider model-list refresh operation.

    Attributes:
        models_added: Number of newly inserted AvailableModel rows.
        models_removed: Number of model rows that no longer appear in the API response.
        models_total: Total number of AvailableModel rows after the refresh.

    """

    models_added: int
    models_removed: int
    models_total: int


# ---------------------------------------------------------------------------
# Pydantic schemas for create/update
# ---------------------------------------------------------------------------


class ProviderCreate(BaseModel):
    """Input schema for creating a new Provider.

    Attributes:
        provider_type: One of ``anthropic``, ``openai``, or ``ollama``.
        display_name: Unique human-readable name for the provider.
        api_key: Plaintext API key (Anthropic/OpenAI).  Stored encrypted.
        base_url: Base URL for self-hosted providers (Ollama).
        is_enabled: Whether the provider is active on creation.

    """

    provider_type: ProviderType
    display_name: str
    api_key: str | None = None
    base_url: str | None = None
    is_enabled: bool = True


class ProviderUpdate(BaseModel):
    """Input schema for a partial update of a Provider.

    All fields are optional; only supplied fields are modified.

    Attributes:
        display_name: New human-readable name.
        api_key: New plaintext API key (will be re-encrypted on update).
        base_url: New base URL.
        is_enabled: New enabled state.

    """

    display_name: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    is_enabled: bool | None = None


# ---------------------------------------------------------------------------
# ProviderService
# ---------------------------------------------------------------------------


class ProviderService:
    """Service layer for LLM Provider and AvailableModel management.

    All public methods are async and accept an :class:`AsyncSession` to
    allow the caller to control transaction boundaries.
    """

    # ------------------------------------------------------------------
    # Model-list fetchers (T016–T018)
    # ------------------------------------------------------------------

    async def fetch_models_anthropic(self, api_key: str) -> list[ModelRecord]:
        """Fetch available models from the Anthropic API.

        Calls ``GET https://api.anthropic.com/v1/models`` with the
        supplied API key and returns the full model list.

        Args:
            api_key: Anthropic API key (plaintext).

        Returns:
            List of :class:`ModelRecord` instances, one per model in the
            Anthropic catalog.

        Raises:
            ProviderFetchError: If the upstream HTTP request fails or
                returns a non-2xx response.

        """
        url = "https://api.anthropic.com/v1/models"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=headers)
        except httpx.RequestError as exc:
            raise ProviderFetchError(f"Network error contacting Anthropic API: {exc}") from exc

        if not resp.is_success:
            raise ProviderFetchError(
                f"Anthropic API returned HTTP {resp.status_code}",
                status_code=resp.status_code,
            )

        data = resp.json()
        records: list[ModelRecord] = []
        for item in data.get("data", []):
            mid = item.get("id", "")
            if mid:
                records.append(ModelRecord(model_identifier=mid, display_name=mid))
        return records

    async def fetch_models_openai(self, api_key: str) -> list[ModelRecord]:
        """Fetch available models from the OpenAI API.

        Calls ``GET https://api.openai.com/v1/models`` with a Bearer token
        and returns the full model list.

        Args:
            api_key: OpenAI API key (plaintext).

        Returns:
            List of :class:`ModelRecord` instances, one per model.

        Raises:
            ProviderFetchError: If the upstream HTTP request fails or
                returns a non-2xx response.

        """
        url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=headers)
        except httpx.RequestError as exc:
            raise ProviderFetchError(f"Network error contacting OpenAI API: {exc}") from exc

        if not resp.is_success:
            raise ProviderFetchError(
                f"OpenAI API returned HTTP {resp.status_code}",
                status_code=resp.status_code,
            )

        data = resp.json()
        records: list[ModelRecord] = []
        for item in data.get("data", []):
            mid = item.get("id", "")
            if mid:
                records.append(ModelRecord(model_identifier=mid, display_name=mid))
        return records

    async def fetch_models_ollama(self, base_url: str) -> list[ModelRecord]:
        """Fetch available models from a self-hosted Ollama server.

        Calls ``GET {base_url}/api/tags`` and parses the ``.models[].name``
        field.

        Args:
            base_url: Base URL of the Ollama server
                (e.g. ``http://localhost:11434``).

        Returns:
            List of :class:`ModelRecord` instances.

        Raises:
            ProviderFetchError: If the HTTP request fails or the server
                returns a non-2xx response.

        """
        url = base_url.rstrip("/") + "/api/tags"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url)
        except httpx.RequestError as exc:
            raise ProviderFetchError(
                f"Network error contacting Ollama at {base_url}: {exc}"
            ) from exc

        if not resp.is_success:
            raise ProviderFetchError(
                f"Ollama server returned HTTP {resp.status_code}",
                status_code=resp.status_code,
            )

        data = resp.json()
        records: list[ModelRecord] = []
        for item in data.get("models", []):
            name = item.get("name", "")
            if name:
                records.append(ModelRecord(model_identifier=name, display_name=name))
        return records

    # ------------------------------------------------------------------
    # CRUD (T019)
    # ------------------------------------------------------------------

    async def create_provider(
        self,
        data: ProviderCreate,
        session: AsyncSession,
    ) -> Provider:
        """Create and persist a new Provider record.

        The ``api_key`` is encrypted at rest using :func:`encrypt_secret`
        before the row is written.

        Args:
            data: Validated provider creation payload.
            session: Active async database session.

        Returns:
            The newly created :class:`Provider` ORM instance.

        """
        settings = get_settings()
        api_key_encrypted: bytes | None = None
        if data.api_key:
            api_key_encrypted = encrypt_secret(data.api_key, settings.secret_key)

        provider = Provider(
            provider_type=data.provider_type,
            display_name=data.display_name,
            api_key_encrypted=api_key_encrypted,
            base_url=data.base_url,
            is_enabled=data.is_enabled,
        )
        session.add(provider)
        await session.commit()
        await session.refresh(provider)
        logger.info("provider_created", provider_id=str(provider.id), type=data.provider_type)
        return provider

    async def list_providers(self, session: AsyncSession) -> list[Provider]:
        """Return all Provider records.

        Args:
            session: Active async database session.

        Returns:
            List of :class:`Provider` ORM instances ordered by display name.

        """
        result = await session.execute(
            select(Provider).order_by(Provider.display_name)
        )
        return list(result.scalars().all())

    async def get_provider(
        self,
        provider_id: uuid.UUID,
        session: AsyncSession,
    ) -> Provider | None:
        """Retrieve a single Provider by primary key.

        Args:
            provider_id: The UUID of the provider to look up.
            session: Active async database session.

        Returns:
            The :class:`Provider` ORM instance, or ``None`` if not found.

        """
        result = await session.execute(
            select(Provider).where(Provider.id == provider_id)
        )
        return result.scalar_one_or_none()

    async def update_provider(
        self,
        provider_id: uuid.UUID,
        data: ProviderUpdate,
        session: AsyncSession,
    ) -> Provider:
        """Apply a partial update to an existing Provider.

        Only fields explicitly set in *data* are modified.  If ``api_key``
        is supplied it is re-encrypted before storage.

        Args:
            provider_id: UUID of the provider to update.
            data: Partial update payload.
            session: Active async database session.

        Returns:
            The updated :class:`Provider` ORM instance.

        Raises:
            KeyError: If no provider with the given ID exists.

        """
        provider = await self.get_provider(provider_id, session)
        if provider is None:
            raise KeyError(f"Provider {provider_id} not found")

        settings = get_settings()
        if data.display_name is not None:
            provider.display_name = data.display_name
        if data.api_key is not None:
            provider.api_key_encrypted = encrypt_secret(data.api_key, settings.secret_key)
        if data.base_url is not None:
            provider.base_url = data.base_url
        if data.is_enabled is not None:
            provider.is_enabled = data.is_enabled

        await session.commit()
        await session.refresh(provider)
        logger.info("provider_updated", provider_id=str(provider_id))
        return provider

    async def delete_provider(
        self,
        provider_id: uuid.UUID,
        session: AsyncSession,
    ) -> None:
        """Delete a Provider by primary key.

        Raises :class:`ProviderHasDependentsError` if any Agent records
        reference this provider (RESTRICT FK constraint).

        Args:
            provider_id: UUID of the provider to delete.
            session: Active async database session.

        Raises:
            KeyError: If no provider with the given ID exists.
            ProviderHasDependentsError: If agents reference this provider.

        """
        provider = await self.get_provider(provider_id, session)
        if provider is None:
            raise KeyError(f"Provider {provider_id} not found")

        agents_result = await session.execute(
            select(Agent).where(Agent.provider_id == provider_id)
        )
        agents = agents_result.scalars().all()
        if agents:
            raise ProviderHasDependentsError([str(a.id) for a in agents])

        await session.delete(provider)
        await session.commit()
        logger.info("provider_deleted", provider_id=str(provider_id))

    # ------------------------------------------------------------------
    # refresh_models (T020)
    # ------------------------------------------------------------------

    async def refresh_models(
        self,
        provider_id: uuid.UUID,
        session: AsyncSession,
    ) -> ModelRefreshResult:
        """Re-fetch the model list from the provider API and upsert DB rows.

        Existing :class:`AvailableModel` rows are updated (display_name
        refreshed, ``is_enabled`` state preserved).  New models are
        inserted with ``is_enabled=True``.  Previously fetched models
        that no longer appear in the API response are counted as removed
        but are **not** deleted (to avoid breaking agent assignments).

        If the upstream API call raises :class:`ProviderFetchError` the
        database is **not** mutated and the error is re-raised.

        Args:
            provider_id: UUID of the Provider to refresh.
            session: Active async database session.

        Returns:
            :class:`ModelRefreshResult` with counts of added, removed, and
            total models.

        Raises:
            KeyError: If no provider with the given ID exists.
            ProviderFetchError: If the upstream API call fails.

        """
        provider = await self.get_provider(provider_id, session)
        if provider is None:
            raise KeyError(f"Provider {provider_id} not found")

        settings = get_settings()

        # Fetch fresh model list from upstream — may raise ProviderFetchError
        if provider.provider_type == ProviderType.ANTHROPIC:
            if not provider.api_key_encrypted:
                raise ProviderFetchError("No API key configured for Anthropic provider")
            api_key = decrypt_secret(provider.api_key_encrypted, settings.secret_key)
            fresh_records = await self.fetch_models_anthropic(api_key)
        elif provider.provider_type == ProviderType.OPENAI:
            if not provider.api_key_encrypted:
                raise ProviderFetchError("No API key configured for OpenAI provider")
            api_key = decrypt_secret(provider.api_key_encrypted, settings.secret_key)
            fresh_records = await self.fetch_models_openai(api_key)
        else:  # OLLAMA
            base_url = provider.base_url or "http://localhost:11434"
            fresh_records = await self.fetch_models_ollama(base_url)

        # Build lookup of existing DB rows
        existing_result = await session.execute(
            select(AvailableModel).where(AvailableModel.provider_id == provider_id)
        )
        existing: dict[str, AvailableModel] = {
            m.model_identifier: m for m in existing_result.scalars().all()
        }

        fresh_identifiers = {r.model_identifier for r in fresh_records}

        added = 0
        for record in fresh_records:
            if record.model_identifier in existing:
                # Update display_name; preserve is_enabled
                existing[record.model_identifier].display_name = record.display_name
            else:
                new_model = AvailableModel(
                    provider_id=provider_id,
                    model_identifier=record.model_identifier,
                    display_name=record.display_name,
                    is_enabled=True,
                )
                session.add(new_model)
                added += 1

        removed = len(existing) - len(fresh_identifiers & set(existing.keys()))

        await session.commit()

        total_result = await session.execute(
            select(AvailableModel).where(AvailableModel.provider_id == provider_id)
        )
        total = len(total_result.scalars().all())

        logger.info(
            "models_refreshed",
            provider_id=str(provider_id),
            added=added,
            removed=removed,
            total=total,
        )
        return ModelRefreshResult(models_added=added, models_removed=removed, models_total=total)
