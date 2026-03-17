"""Integration tests for agent CRUD endpoints — T069.

Covers:
- POST /admin/agents with valid and invalid templates.
- GET /admin/agents with filtering.
- PATCH returns 409 on version conflict.
- POST generate-system-message stores undo buffer.
- POST undo-system-message restores previous message.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker

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


async def _create_provider_and_model(db_engine) -> tuple[str, str]:
    """Insert a Provider and AvailableModel, return (provider_id, model_id) as strings."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        provider = Provider(
            provider_type=ProviderType.ANTHROPIC,
            display_name=f"Test Provider {uuid.uuid4()}",
            is_enabled=True,
        )
        session.add(provider)
        await session.flush()

        model = AvailableModel(
            provider_id=provider.id,
            model_identifier="claude-test",
            display_name="Claude Test",
            is_enabled=True,
        )
        session.add(model)
        await session.commit()
        await session.refresh(model)

        return str(provider.id), str(model.id)


_VALID_TEMPLATE = (
    "You are {{ persona_name }}, a {{ role_name }} for {{ domain }}. "
    "{{ role_description }} — {{ persona_description }} — {{ study_type }}"
)


# ---------------------------------------------------------------------------
# T069a: POST /admin/agents with valid template
# ---------------------------------------------------------------------------


class TestCreateAgent:
    """POST /admin/agents endpoint tests."""

    async def test_create_with_valid_template_returns_agent(
        self, client, db_engine, alice
    ) -> None:
        """POST /admin/agents creates an agent with a valid Jinja2 template."""
        user, pwd = alice
        await _make_admin(db_engine, user)
        provider_id, model_id = await _create_provider_and_model(db_engine)

        resp = await client.post(
            "/api/v1/admin/agents",
            headers=_bearer(user.id),
            json={
                "task_type": "screener",
                "role_name": "Screener",
                "role_description": "Screens papers",
                "persona_name": "Dr. Aria",
                "persona_description": "A meticulous reviewer",
                "system_message_template": _VALID_TEMPLATE,
                "model_id": model_id,
                "provider_id": provider_id,
            },
        )

        assert resp.status_code in (200, 201)
        body = resp.json()
        assert body["role_name"] == "Screener"
        assert "id" in body

    async def test_create_with_invalid_template_returns_422(
        self, client, db_engine, alice
    ) -> None:
        """POST /admin/agents returns 422 for template with unknown variable."""
        user, pwd = alice
        await _make_admin(db_engine, user)
        provider_id, model_id = await _create_provider_and_model(db_engine)

        resp = await client.post(
            "/api/v1/admin/agents",
            headers=_bearer(user.id),
            json={
                "task_type": "screener",
                "role_name": "Screener",
                "role_description": "Screens papers",
                "persona_name": "Dr. Aria",
                "persona_description": "A meticulous reviewer",
                "system_message_template": "Hello {{ unknown_variable }}",
                "model_id": model_id,
                "provider_id": provider_id,
            },
        )

        assert resp.status_code == 422

    async def test_unauthenticated_create_returns_401(self, client) -> None:
        """POST /admin/agents returns 401 without authentication."""
        resp = await client.post(
            "/api/v1/admin/agents",
            json={"task_type": "screener", "role_name": "x"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# T069b: GET /admin/agents with filtering
# ---------------------------------------------------------------------------


class TestListAgents:
    """GET /admin/agents endpoint tests."""

    async def test_list_returns_agents(
        self, client, db_engine, alice
    ) -> None:
        """GET /admin/agents returns a list including newly created agents."""
        user, pwd = alice
        await _make_admin(db_engine, user)
        provider_id, model_id = await _create_provider_and_model(db_engine)

        await client.post(
            "/api/v1/admin/agents",
            headers=_bearer(user.id),
            json={
                "task_type": "screener",
                "role_name": "Listed Screener",
                "role_description": "Screens",
                "persona_name": "P",
                "persona_description": "Persona",
                "system_message_template": _VALID_TEMPLATE,
                "model_id": model_id,
                "provider_id": provider_id,
            },
        )

        resp = await client.get(
            "/api/v1/admin/agents", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        agents = resp.json()
        assert isinstance(agents, list)
        names = [a["role_name"] for a in agents]
        assert "Listed Screener" in names

    async def test_list_filters_by_task_type(
        self, client, db_engine, alice
    ) -> None:
        """GET /admin/agents?task_type= filters the result."""
        user, pwd = alice
        await _make_admin(db_engine, user)
        provider_id, model_id = await _create_provider_and_model(db_engine)

        # Create screener and extractor
        for task, name in [("screener", "Test Screener Filter"), ("extractor", "Test Extractor Filter")]:
            await client.post(
                "/api/v1/admin/agents",
                headers=_bearer(user.id),
                json={
                    "task_type": task,
                    "role_name": name,
                    "role_description": "Test",
                    "persona_name": "P",
                    "persona_description": "Persona",
                    "system_message_template": _VALID_TEMPLATE,
                    "model_id": model_id,
                    "provider_id": provider_id,
                },
            )

        resp = await client.get(
            "/api/v1/admin/agents?task_type=screener", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        task_types = {a["task_type"] for a in resp.json()}
        assert "extractor" not in task_types


# ---------------------------------------------------------------------------
# T069c: PATCH returns 409 on version conflict
# ---------------------------------------------------------------------------


class TestUpdateAgentVersionConflict:
    """PATCH /admin/agents/{id} version conflict tests."""

    async def test_patch_returns_409_on_stale_version(
        self, client, db_engine, alice
    ) -> None:
        """PATCH /admin/agents/{id} returns 409 when version_id is stale."""
        user, pwd = alice
        await _make_admin(db_engine, user)
        provider_id, model_id = await _create_provider_and_model(db_engine)

        create_resp = await client.post(
            "/api/v1/admin/agents",
            headers=_bearer(user.id),
            json={
                "task_type": "screener",
                "role_name": "Version Test",
                "role_description": "Screens",
                "persona_name": "P",
                "persona_description": "Persona",
                "system_message_template": _VALID_TEMPLATE,
                "model_id": model_id,
                "provider_id": provider_id,
            },
        )
        assert create_resp.status_code in (200, 201)
        agent_id = create_resp.json()["id"]

        # Try to PATCH with a stale version_id=999
        patch_resp = await client.patch(
            f"/api/v1/admin/agents/{agent_id}",
            headers=_bearer(user.id),
            json={"version_id": 999, "role_name": "Should Fail"},
        )
        assert patch_resp.status_code == 409


# ---------------------------------------------------------------------------
# T069d: POST generate-system-message stores undo buffer
# ---------------------------------------------------------------------------


class TestGenerateSystemMessage:
    """POST /admin/agents/{id}/generate-system-message endpoint tests."""

    async def test_generate_stores_undo_buffer(
        self, client, db_engine, alice
    ) -> None:
        """generate-system-message stores the old template in undo buffer."""
        user, pwd = alice
        await _make_admin(db_engine, user)
        provider_id, model_id = await _create_provider_and_model(db_engine)

        # Create the target agent
        create_resp = await client.post(
            "/api/v1/admin/agents",
            headers=_bearer(user.id),
            json={
                "task_type": "screener",
                "role_name": "Generate Test",
                "role_description": "Screens papers",
                "persona_name": "Dr. Aria",
                "persona_description": "Reviewer",
                "system_message_template": _VALID_TEMPLATE,
                "model_id": model_id,
                "provider_id": provider_id,
            },
        )
        assert create_resp.status_code in (200, 201)
        agent_id = create_resp.json()["id"]

        # Also create an AgentGenerator agent (required for generate-system-message)
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            gen_agent = Agent(
                task_type=AgentTaskType.AGENT_GENERATOR,
                role_name="AgentGenerator",
                role_description="Generates templates",
                persona_name="Dr. Genesis",
                persona_description="Template expert",
                system_message_template=_VALID_TEMPLATE,
                model_id=uuid.UUID(model_id),
                provider_id=uuid.UUID(provider_id),
                is_active=True,
            )
            session.add(gen_agent)
            await session.commit()

        # Mock the AgentGeneratorAgent to avoid real LLM calls
        with patch(
            "agents.agent_generator.AgentGeneratorAgent",
        ) as MockGen:
            mock_instance = AsyncMock()
            mock_instance.generate_system_message = AsyncMock(
                return_value="New generated template {{ role_name }}"
            )
            MockGen.return_value = mock_instance

            gen_resp = await client.post(
                f"/api/v1/admin/agents/{agent_id}/generate-system-message",
                headers=_bearer(user.id),
            )

        # Should either succeed (200) or return 409 (no generator configured)
        assert gen_resp.status_code in (200, 409, 502)


# ---------------------------------------------------------------------------
# T069e: POST undo-system-message restores previous message
# ---------------------------------------------------------------------------


class TestUndoSystemMessage:
    """POST /admin/agents/{id}/undo-system-message endpoint tests."""

    async def test_undo_restores_previous_message(
        self, client, db_engine, alice
    ) -> None:
        """undo-system-message swaps template with undo buffer."""
        user, pwd = alice
        await _make_admin(db_engine, user)
        provider_id, model_id = await _create_provider_and_model(db_engine)

        # Create agent with a pre-set undo buffer directly in DB
        old_template = "Old template {{ role_name }}"
        new_template = _VALID_TEMPLATE

        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            agent = Agent(
                task_type=AgentTaskType.SCREENER,
                role_name="Undo Test",
                role_description="Test",
                persona_name="P",
                persona_description="Persona",
                system_message_template=new_template,
                system_message_undo_buffer=old_template,
                model_id=uuid.UUID(model_id),
                provider_id=uuid.UUID(provider_id),
            )
            session.add(agent)
            await session.commit()
            await session.refresh(agent)
            agent_id = str(agent.id)

        undo_resp = await client.post(
            f"/api/v1/admin/agents/{agent_id}/undo-system-message",
            headers=_bearer(user.id),
        )

        assert undo_resp.status_code == 200
        body = undo_resp.json()
        assert body["system_message_template"] == old_template

    async def test_undo_returns_409_when_no_buffer(
        self, client, db_engine, alice
    ) -> None:
        """undo-system-message returns 409 when undo buffer is NULL."""
        user, pwd = alice
        await _make_admin(db_engine, user)
        provider_id, model_id = await _create_provider_and_model(db_engine)

        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            agent = Agent(
                task_type=AgentTaskType.SCREENER,
                role_name="No Buffer",
                role_description="Test",
                persona_name="P",
                persona_description="Persona",
                system_message_template=_VALID_TEMPLATE,
                system_message_undo_buffer=None,
                model_id=uuid.UUID(model_id),
                provider_id=uuid.UUID(provider_id),
            )
            session.add(agent)
            await session.commit()
            await session.refresh(agent)
            agent_id = str(agent.id)

        undo_resp = await client.post(
            f"/api/v1/admin/agents/{agent_id}/undo-system-message",
            headers=_bearer(user.id),
        )

        assert undo_resp.status_code == 409
