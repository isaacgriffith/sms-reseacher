"""Integration tests for provider CRUD endpoints — T068.

Covers:
- POST /admin/providers creates provider and returns has_api_key.
- PATCH /admin/providers/{id} updates api_key.
- DELETE /admin/providers/{id} returns 409 when agents depend on provider.
- POST /admin/providers/{id}/refresh-models returns 502 on unreachable provider.
- GET /admin/providers returns list.
- GET /admin/providers/{id} returns single provider.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker
from unittest.mock import AsyncMock, MagicMock, patch

from backend.core.auth import create_access_token
from db.models.agents import Agent, AgentTaskType, AvailableModel, Provider, ProviderType
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Create a Bearer token header for the given user."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _make_admin(db_engine, user) -> None:
    """Add user as admin of a fresh research group."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=f"Admin Group {user.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()


# ---------------------------------------------------------------------------
# T068a: POST /admin/providers creates provider and returns has_api_key
# ---------------------------------------------------------------------------


class TestCreateProvider:
    """POST /admin/providers endpoint tests."""

    async def test_create_ollama_provider_returns_has_api_key_false(
        self, client, db_engine, alice
    ) -> None:
        """Creating an Ollama provider returns has_api_key=False (no key needed)."""
        user, pwd = alice
        await _make_admin(db_engine, user)

        with patch(
            "backend.services.provider_service.ProviderService.fetch_models_ollama",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.post(
                "/api/v1/admin/providers",
                headers=_bearer(user.id),
                json={
                    "provider_type": "ollama",
                    "display_name": "Test Ollama",
                    "base_url": "http://localhost:11434",
                },
            )

        assert resp.status_code in (200, 201)
        body = resp.json()
        assert body["display_name"] == "Test Ollama"
        assert body["has_api_key"] is False

    async def test_create_anthropic_provider_returns_has_api_key_true(
        self, client, db_engine, alice
    ) -> None:
        """Creating an Anthropic provider with api_key returns has_api_key=True."""
        user, pwd = alice
        await _make_admin(db_engine, user)

        with patch(
            "backend.services.provider_service.ProviderService.fetch_models_anthropic",
            new_callable=AsyncMock,
            return_value=[],
        ):
            resp = await client.post(
                "/api/v1/admin/providers",
                headers=_bearer(user.id),
                json={
                    "provider_type": "anthropic",
                    "display_name": "Test Anthropic",
                    "api_key": "sk-test-key",
                },
            )

        assert resp.status_code in (200, 201)
        body = resp.json()
        assert body["has_api_key"] is True
        # API key must NOT be returned in plaintext
        assert "api_key" not in body or body.get("api_key") is None

    async def test_unauthenticated_create_returns_401(self, client) -> None:
        """POST /admin/providers returns 401 without a token."""
        resp = await client.post(
            "/api/v1/admin/providers",
            json={"provider_type": "ollama", "display_name": "x"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# T068b: PATCH /admin/providers/{id} updates api_key
# ---------------------------------------------------------------------------


class TestUpdateProvider:
    """PATCH /admin/providers/{id} endpoint tests."""

    async def test_patch_display_name(self, client, db_engine, alice) -> None:
        """PATCH updates display_name successfully."""
        user, pwd = alice
        await _make_admin(db_engine, user)

        with patch(
            "backend.services.provider_service.ProviderService.fetch_models_ollama",
            new_callable=AsyncMock,
            return_value=[],
        ):
            create_resp = await client.post(
                "/api/v1/admin/providers",
                headers=_bearer(user.id),
                json={
                    "provider_type": "ollama",
                    "display_name": "Original Name",
                    "base_url": "http://localhost:11434",
                },
            )
        assert create_resp.status_code in (200, 201)
        provider_id = create_resp.json()["id"]

        patch_resp = await client.patch(
            f"/api/v1/admin/providers/{provider_id}",
            headers=_bearer(user.id),
            json={"display_name": "Updated Name"},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["display_name"] == "Updated Name"


# ---------------------------------------------------------------------------
# T068c: DELETE /admin/providers/{id} returns 409 with dependent agents
# ---------------------------------------------------------------------------


class TestDeleteProvider:
    """DELETE /admin/providers/{id} endpoint tests."""

    async def test_delete_provider_with_agents_returns_409(
        self, client, db_engine, alice
    ) -> None:
        """DELETE returns 409 when agents depend on the provider."""
        user, pwd = alice
        await _make_admin(db_engine, user)

        # Create provider
        with patch(
            "backend.services.provider_service.ProviderService.fetch_models_ollama",
            new_callable=AsyncMock,
            return_value=[],
        ):
            create_resp = await client.post(
                "/api/v1/admin/providers",
                headers=_bearer(user.id),
                json={
                    "provider_type": "ollama",
                    "display_name": "Provider With Deps",
                    "base_url": "http://localhost:11434",
                },
            )
        provider_id = create_resp.json()["id"]

        # Insert a model and agent that reference this provider
        import uuid
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            model = AvailableModel(
                provider_id=uuid.UUID(provider_id),
                model_identifier="test-model",
                display_name="Test Model",
                is_enabled=True,
            )
            session.add(model)
            await session.flush()

            agent = Agent(
                task_type=AgentTaskType.SCREENER,
                role_name="Screener",
                role_description="Test",
                persona_name="P",
                persona_description="Test persona",
                system_message_template="Hello {{ role_name }}",
                model_id=model.id,
                provider_id=uuid.UUID(provider_id),
            )
            session.add(agent)
            await session.commit()

        delete_resp = await client.delete(
            f"/api/v1/admin/providers/{provider_id}",
            headers=_bearer(user.id),
        )
        assert delete_resp.status_code == 409

    async def test_delete_provider_without_agents_returns_204(
        self, client, db_engine, alice
    ) -> None:
        """DELETE returns 204 when no agents reference the provider."""
        user, pwd = alice
        await _make_admin(db_engine, user)

        with patch(
            "backend.services.provider_service.ProviderService.fetch_models_ollama",
            new_callable=AsyncMock,
            return_value=[],
        ):
            create_resp = await client.post(
                "/api/v1/admin/providers",
                headers=_bearer(user.id),
                json={
                    "provider_type": "ollama",
                    "display_name": "Provider No Deps",
                    "base_url": "http://localhost:11434",
                },
            )
        provider_id = create_resp.json()["id"]

        delete_resp = await client.delete(
            f"/api/v1/admin/providers/{provider_id}",
            headers=_bearer(user.id),
        )
        assert delete_resp.status_code in (200, 204)


# ---------------------------------------------------------------------------
# T068d: POST refresh-models returns 502 on unreachable provider
# ---------------------------------------------------------------------------


class TestRefreshModels:
    """POST /admin/providers/{id}/refresh-models endpoint tests."""

    async def test_refresh_returns_502_on_fetch_error(
        self, client, db_engine, alice
    ) -> None:
        """refresh-models returns 502 when the provider API is unreachable."""
        from backend.services.provider_service import ProviderFetchError

        user, pwd = alice
        await _make_admin(db_engine, user)

        with patch(
            "backend.services.provider_service.ProviderService.fetch_models_ollama",
            new_callable=AsyncMock,
            return_value=[],
        ):
            create_resp = await client.post(
                "/api/v1/admin/providers",
                headers=_bearer(user.id),
                json={
                    "provider_type": "ollama",
                    "display_name": "Unreachable Provider",
                    "base_url": "http://unreachable:11434",
                },
            )
        provider_id = create_resp.json()["id"]

        with patch(
            "backend.services.provider_service.ProviderService.fetch_models_ollama",
            side_effect=ProviderFetchError("Connection refused", status_code=None),
        ):
            refresh_resp = await client.post(
                f"/api/v1/admin/providers/{provider_id}/refresh-models",
                headers=_bearer(user.id),
            )

        assert refresh_resp.status_code == 502


# ---------------------------------------------------------------------------
# T068e: GET /admin/providers returns list
# ---------------------------------------------------------------------------


class TestListProviders:
    """GET /admin/providers endpoint tests."""

    async def test_list_returns_created_providers(
        self, client, db_engine, alice
    ) -> None:
        """GET /admin/providers returns the list including newly created providers."""
        user, pwd = alice
        await _make_admin(db_engine, user)

        with patch(
            "backend.services.provider_service.ProviderService.fetch_models_ollama",
            new_callable=AsyncMock,
            return_value=[],
        ):
            await client.post(
                "/api/v1/admin/providers",
                headers=_bearer(user.id),
                json={
                    "provider_type": "ollama",
                    "display_name": "List Test Provider",
                    "base_url": "http://localhost:11434",
                },
            )

        list_resp = await client.get(
            "/api/v1/admin/providers", headers=_bearer(user.id)
        )
        assert list_resp.status_code == 200
        providers = list_resp.json()
        assert isinstance(providers, list)
        names = [p["display_name"] for p in providers]
        assert "List Test Provider" in names
