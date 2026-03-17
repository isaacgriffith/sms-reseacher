"""Unit tests for ProviderService — T064.

Covers:
- Model-list fetch for each provider type (mocked HTTP).
- Encrypt/decrypt round-trip via encryption utility.
- CRUD validation rules (create, list, get, update, delete).
- ProviderHasDependentsError when deleting a provider referenced by agents.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import db.models  # noqa: F401
import db.models.agents  # noqa: F401
import db.models.study  # noqa: F401
import db.models.users  # noqa: F401
from db.base import Base
from db.models.agents import Agent, AgentTaskType, AvailableModel, Provider, ProviderType

from backend.services.provider_service import (
    ModelRecord,
    ProviderCreate,
    ProviderFetchError,
    ProviderHasDependentsError,
    ProviderService,
    ProviderUpdate,
)
from backend.utils.encryption import decrypt_secret, encrypt_secret


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide an in-memory SQLite session with all agent tables created."""
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
async def service() -> ProviderService:
    """Return a fresh ProviderService."""
    return ProviderService()


# ---------------------------------------------------------------------------
# T064a: fetch_models_anthropic (mocked HTTP)
# ---------------------------------------------------------------------------


class TestFetchModelsAnthropic:
    """Anthropic model-list fetch tests."""

    async def test_returns_model_records_on_success(self, service: ProviderService) -> None:
        """fetch_models_anthropic returns ModelRecord list on 200 response."""
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {
            "data": [
                {"id": "claude-3-haiku-20240307"},
                {"id": "claude-3-sonnet-20240229"},
            ]
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client_class.return_value = mock_client

            records = await service.fetch_models_anthropic("sk-test")

        assert len(records) == 2
        assert records[0].model_identifier == "claude-3-haiku-20240307"

    async def test_raises_provider_fetch_error_on_http_failure(
        self, service: ProviderService
    ) -> None:
        """fetch_models_anthropic raises ProviderFetchError on non-2xx response."""
        mock_resp = MagicMock()
        mock_resp.is_success = False
        mock_resp.status_code = 401

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client_class.return_value = mock_client

            with pytest.raises(ProviderFetchError) as exc_info:
                await service.fetch_models_anthropic("sk-bad-key")

        assert exc_info.value.status_code == 401

    async def test_raises_provider_fetch_error_on_network_error(
        self, service: ProviderService
    ) -> None:
        """fetch_models_anthropic raises ProviderFetchError on network failure."""
        import httpx

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(side_effect=httpx.RequestError("timeout"))
            mock_client_class.return_value = mock_client

            with pytest.raises(ProviderFetchError):
                await service.fetch_models_anthropic("sk-test")


# ---------------------------------------------------------------------------
# T064b: fetch_models_openai (mocked HTTP)
# ---------------------------------------------------------------------------


class TestFetchModelsOpenAI:
    """OpenAI model-list fetch tests."""

    async def test_returns_model_records_on_success(self, service: ProviderService) -> None:
        """fetch_models_openai returns ModelRecord list on 200 response."""
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {
            "data": [
                {"id": "gpt-4"},
                {"id": "gpt-3.5-turbo"},
            ]
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client_class.return_value = mock_client

            records = await service.fetch_models_openai("sk-openai-test")

        assert len(records) == 2
        assert any(r.model_identifier == "gpt-4" for r in records)


# ---------------------------------------------------------------------------
# T064c: fetch_models_ollama (mocked HTTP)
# ---------------------------------------------------------------------------


class TestFetchModelsOllama:
    """Ollama model-list fetch tests."""

    async def test_returns_model_records_on_success(self, service: ProviderService) -> None:
        """fetch_models_ollama returns ModelRecord list on 200 response."""
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {
            "models": [
                {"name": "llama3.2:3b"},
                {"name": "mistral:7b"},
            ]
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client_class.return_value = mock_client

            records = await service.fetch_models_ollama("http://localhost:11434")

        assert len(records) == 2
        assert records[0].model_identifier == "llama3.2:3b"


# ---------------------------------------------------------------------------
# T064d: encrypt/decrypt round-trip
# ---------------------------------------------------------------------------


class TestEncryptDecryptRoundTrip:
    """Verify encryption utilities work correctly."""

    def test_roundtrip(self) -> None:
        """encrypt_secret then decrypt_secret returns the original string."""
        plaintext = "sk-anthropic-test-key-abc123"
        secret_key = "my-app-secret-key-for-testing"

        encrypted = encrypt_secret(plaintext, secret_key)
        decrypted = decrypt_secret(encrypted, secret_key)

        assert decrypted == plaintext

    def test_wrong_key_raises(self) -> None:
        """decrypt_secret with wrong key raises InvalidToken."""
        from cryptography.fernet import InvalidToken

        encrypted = encrypt_secret("secret", "correct-key")
        with pytest.raises(InvalidToken):
            decrypt_secret(encrypted, "wrong-key")


# ---------------------------------------------------------------------------
# T064e: CRUD — create, list, get, update, delete
# ---------------------------------------------------------------------------


class TestProviderCRUD:
    """CRUD operation tests for ProviderService."""

    async def test_create_provider_returns_record(
        self, service: ProviderService, db_session: AsyncSession
    ) -> None:
        """create_provider persists and returns the provider row."""
        data = ProviderCreate(
            provider_type=ProviderType.OLLAMA,
            display_name="Test Ollama",
            base_url="http://localhost:11434",
        )
        with patch(
            "backend.services.provider_service.get_settings",
            return_value=MagicMock(secret_key="test-secret"),
        ):
            provider = await service.create_provider(data, db_session)

        assert provider.id is not None
        assert provider.display_name == "Test Ollama"
        assert provider.provider_type == ProviderType.OLLAMA

    async def test_list_providers_returns_all(
        self, service: ProviderService, db_session: AsyncSession
    ) -> None:
        """list_providers returns all created providers."""
        for i in range(3):
            data = ProviderCreate(
                provider_type=ProviderType.OLLAMA,
                display_name=f"Ollama {i}",
                base_url=f"http://localhost:1143{i}",
            )
            with patch(
                "backend.services.provider_service.get_settings",
                return_value=MagicMock(secret_key="test-secret"),
            ):
                await service.create_provider(data, db_session)

        providers = await service.list_providers(db_session)
        assert len(providers) >= 3

    async def test_get_provider_returns_none_for_missing(
        self, service: ProviderService, db_session: AsyncSession
    ) -> None:
        """get_provider returns None for a non-existent UUID."""
        import uuid

        result = await service.get_provider(uuid.uuid4(), db_session)
        assert result is None

    async def test_update_provider_changes_display_name(
        self, service: ProviderService, db_session: AsyncSession
    ) -> None:
        """update_provider applies the new display_name."""
        data = ProviderCreate(
            provider_type=ProviderType.OLLAMA,
            display_name="Old Name",
            base_url="http://localhost:11434",
        )
        with patch(
            "backend.services.provider_service.get_settings",
            return_value=MagicMock(secret_key="test-secret"),
        ):
            provider = await service.create_provider(data, db_session)
            update = ProviderUpdate(display_name="New Name")
            updated = await service.update_provider(provider.id, update, db_session)

        assert updated.display_name == "New Name"

    async def test_delete_nonexistent_provider_raises_key_error(
        self, service: ProviderService, db_session: AsyncSession
    ) -> None:
        """delete_provider raises KeyError for a non-existent ID."""
        import uuid

        with pytest.raises(KeyError):
            await service.delete_provider(uuid.uuid4(), db_session)


# ---------------------------------------------------------------------------
# T064f: ProviderHasDependentsError on delete
# ---------------------------------------------------------------------------


class TestProviderHasDependentsError:
    """ProviderHasDependentsError is raised when deleting a provider with agents."""

    async def test_delete_raises_when_agents_exist(
        self, service: ProviderService, db_session: AsyncSession
    ) -> None:
        """delete_provider raises ProviderHasDependentsError when agents reference it."""
        import uuid

        from sqlalchemy import insert

        with patch(
            "backend.services.provider_service.get_settings",
            return_value=MagicMock(secret_key="test-secret"),
        ):
            provider = await service.create_provider(
                ProviderCreate(
                    provider_type=ProviderType.OLLAMA,
                    display_name="Dep Provider",
                    base_url="http://localhost:11434",
                ),
                db_session,
            )

        # Insert a model so the agent FK is satisfied
        model = AvailableModel(
            provider_id=provider.id,
            model_identifier="test-model",
            display_name="Test Model",
            is_enabled=True,
        )
        db_session.add(model)
        await db_session.flush()

        # Insert an agent referencing this provider
        agent = Agent(
            task_type=AgentTaskType.SCREENER,
            role_name="Test",
            role_description="Test role",
            persona_name="TestPerson",
            persona_description="Test persona",
            system_message_template="Hello {{ role_name }}",
            model_id=model.id,
            provider_id=provider.id,
        )
        db_session.add(agent)
        await db_session.commit()

        with pytest.raises(ProviderHasDependentsError):
            await service.delete_provider(provider.id, db_session)
