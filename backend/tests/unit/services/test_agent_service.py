"""Unit tests for AgentService — T065.

Covers:
- create/list/update/deactivate operations.
- Jinja2 template validation (accept valid, reject unknown variable).
- render_system_message: correct substitution and StrictUndefined error.
- undo buffer swap behaviour.
- TemplateRenderError and TemplateValidationError exceptions.
"""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

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

from backend.services.agent_service import (
    AgentCreate,
    AgentHasDependentsError,
    AgentNotFoundError,
    AgentService,
    AgentUpdate,
    NoUndoBufferError,
    StudyContext,
    TemplateRenderError,
    TemplateValidationError,
    build_study_context,
    render_system_message,
)


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
async def provider_and_model(db_session: AsyncSession) -> tuple[Provider, AvailableModel]:
    """Insert a Provider and AvailableModel, return both."""
    provider = Provider(
        provider_type=ProviderType.ANTHROPIC,
        display_name="Test Provider",
        is_enabled=True,
    )
    db_session.add(provider)
    await db_session.flush()

    model = AvailableModel(
        provider_id=provider.id,
        model_identifier="claude-haiku-test",
        display_name="Claude Haiku Test",
        is_enabled=True,
    )
    db_session.add(model)
    await db_session.flush()

    return provider, model


_VALID_TEMPLATE = (
    "You are {{ persona_name }}, a {{ role_name }} for {{ domain }} research. "
    "{{ role_description }} — {{ persona_description }} — {{ study_type }}"
)


# ---------------------------------------------------------------------------
# T065a: create_agent
# ---------------------------------------------------------------------------


class TestCreateAgent:
    """AgentService.create_agent tests."""

    async def test_creates_agent_with_valid_template(
        self,
        db_session: AsyncSession,
        provider_and_model: tuple[Provider, AvailableModel],
    ) -> None:
        """create_agent persists a valid agent and returns the ORM record."""
        provider, model = provider_and_model
        service = AgentService()

        data = AgentCreate(
            task_type=AgentTaskType.SCREENER.value,
            role_name="Screener",
            role_description="Screens papers",
            persona_name="Dr. Aria",
            persona_description="A meticulous reviewer",
            system_message_template=_VALID_TEMPLATE,
            model_id=model.id,
            provider_id=provider.id,
        )
        agent = await service.create_agent(data, db_session)

        assert agent.id is not None
        assert agent.role_name == "Screener"
        assert agent.task_type == AgentTaskType.SCREENER

    async def test_raises_on_unknown_template_variable(
        self,
        db_session: AsyncSession,
        provider_and_model: tuple[Provider, AvailableModel],
    ) -> None:
        """create_agent raises TemplateValidationError for unknown Jinja2 variable."""
        provider, model = provider_and_model
        service = AgentService()

        bad_template = "Hello {{ unknown_variable }}"
        data = AgentCreate(
            task_type=AgentTaskType.SCREENER.value,
            role_name="Screener",
            role_description="Screens",
            persona_name="Dr. Aria",
            persona_description="Reviewer",
            system_message_template=bad_template,
            model_id=model.id,
            provider_id=provider.id,
        )
        with pytest.raises(TemplateValidationError) as exc_info:
            await service.create_agent(data, db_session)
        assert exc_info.value.variable_name == "unknown_variable"

    async def test_raises_on_invalid_model(
        self,
        db_session: AsyncSession,
        provider_and_model: tuple[Provider, AvailableModel],
    ) -> None:
        """create_agent raises ValueError when model_id is not found."""
        provider, _ = provider_and_model
        service = AgentService()

        data = AgentCreate(
            task_type=AgentTaskType.SCREENER.value,
            role_name="Screener",
            role_description="Screens",
            persona_name="Dr. Aria",
            persona_description="Reviewer",
            system_message_template=_VALID_TEMPLATE,
            model_id=uuid.uuid4(),
            provider_id=provider.id,
        )
        with pytest.raises(ValueError, match="not found"):
            await service.create_agent(data, db_session)

    async def test_raises_on_disabled_model(
        self,
        db_session: AsyncSession,
        provider_and_model: tuple[Provider, AvailableModel],
    ) -> None:
        """create_agent raises ValueError when the model is disabled."""
        provider, model = provider_and_model
        model.is_enabled = False
        await db_session.flush()

        service = AgentService()
        data = AgentCreate(
            task_type=AgentTaskType.SCREENER.value,
            role_name="Screener",
            role_description="Screens",
            persona_name="Dr. Aria",
            persona_description="Reviewer",
            system_message_template=_VALID_TEMPLATE,
            model_id=model.id,
            provider_id=provider.id,
        )
        with pytest.raises(ValueError, match="disabled"):
            await service.create_agent(data, db_session)


# ---------------------------------------------------------------------------
# T065b: list_agents
# ---------------------------------------------------------------------------


class TestListAgents:
    """AgentService.list_agents tests."""

    async def test_list_returns_all_agents(
        self,
        db_session: AsyncSession,
        provider_and_model: tuple[Provider, AvailableModel],
    ) -> None:
        """list_agents returns all agents when no filters are applied."""
        provider, model = provider_and_model
        service = AgentService()

        for i in range(3):
            agent = Agent(
                task_type=AgentTaskType.SCREENER,
                role_name=f"Agent {i}",
                role_description="Test",
                persona_name=f"P{i}",
                persona_description="Test persona",
                system_message_template=_VALID_TEMPLATE,
                model_id=model.id,
                provider_id=provider.id,
            )
            db_session.add(agent)
        await db_session.flush()

        agents = await service.list_agents(db_session)
        assert len(agents) >= 3

    async def test_list_filters_by_task_type(
        self,
        db_session: AsyncSession,
        provider_and_model: tuple[Provider, AvailableModel],
    ) -> None:
        """list_agents with task_type filter returns only matching agents."""
        provider, model = provider_and_model
        service = AgentService()

        screener = Agent(
            task_type=AgentTaskType.SCREENER,
            role_name="Screener",
            role_description="Test",
            persona_name="P1",
            persona_description="Test persona",
            system_message_template=_VALID_TEMPLATE,
            model_id=model.id,
            provider_id=provider.id,
        )
        extractor = Agent(
            task_type=AgentTaskType.EXTRACTOR,
            role_name="Extractor",
            role_description="Test",
            persona_name="P2",
            persona_description="Test persona",
            system_message_template=_VALID_TEMPLATE,
            model_id=model.id,
            provider_id=provider.id,
        )
        db_session.add(screener)
        db_session.add(extractor)
        await db_session.flush()

        screeners = await service.list_agents(db_session, task_type="screener")
        task_types = {a.task_type for a in screeners}
        assert task_types == {AgentTaskType.SCREENER}


# ---------------------------------------------------------------------------
# T065c: update_agent
# ---------------------------------------------------------------------------


class TestUpdateAgent:
    """AgentService.update_agent tests."""

    async def test_update_role_name(
        self,
        db_session: AsyncSession,
        provider_and_model: tuple[Provider, AvailableModel],
    ) -> None:
        """update_agent changes the role_name field."""
        provider, model = provider_and_model
        service = AgentService()

        agent = Agent(
            task_type=AgentTaskType.SCREENER,
            role_name="Old Name",
            role_description="Test",
            persona_name="P",
            persona_description="Test persona",
            system_message_template=_VALID_TEMPLATE,
            model_id=model.id,
            provider_id=provider.id,
        )
        db_session.add(agent)
        await db_session.flush()

        # SQLAlchemy version_id_col starts at 1 on INSERT (not 0)
        update = AgentUpdate(version_id=agent.version_id, role_name="New Name")
        updated = await service.update_agent(agent.id, update, db_session)

        assert updated.role_name == "New Name"

    async def test_update_rejects_unknown_template_variable(
        self,
        db_session: AsyncSession,
        provider_and_model: tuple[Provider, AvailableModel],
    ) -> None:
        """update_agent raises TemplateValidationError for unknown Jinja2 variable."""
        provider, model = provider_and_model
        service = AgentService()

        agent = Agent(
            task_type=AgentTaskType.SCREENER,
            role_name="Screener",
            role_description="Test",
            persona_name="P",
            persona_description="Test persona",
            system_message_template=_VALID_TEMPLATE,
            model_id=model.id,
            provider_id=provider.id,
        )
        db_session.add(agent)
        await db_session.flush()

        # SQLAlchemy version_id_col starts at 1 on INSERT (not 0)
        update = AgentUpdate(version_id=agent.version_id, system_message_template="{{ bad_var }}")
        with pytest.raises(TemplateValidationError):
            await service.update_agent(agent.id, update, db_session)


# ---------------------------------------------------------------------------
# T065d: deactivate_agent
# ---------------------------------------------------------------------------


class TestDeactivateAgent:
    """AgentService.deactivate_agent tests."""

    async def test_deactivate_sets_is_active_false(
        self,
        db_session: AsyncSession,
        provider_and_model: tuple[Provider, AvailableModel],
    ) -> None:
        """deactivate_agent sets is_active=False when no dependents exist."""
        provider, model = provider_and_model
        service = AgentService()

        agent = Agent(
            task_type=AgentTaskType.SCREENER,
            role_name="Screener",
            role_description="Test",
            persona_name="P",
            persona_description="Test persona",
            system_message_template=_VALID_TEMPLATE,
            model_id=model.id,
            provider_id=provider.id,
        )
        db_session.add(agent)
        await db_session.flush()

        result = await service.deactivate_agent(agent.id, db_session)
        assert result.is_active is False

    async def test_deactivate_raises_agent_not_found(
        self, db_session: AsyncSession
    ) -> None:
        """deactivate_agent raises AgentNotFoundError for non-existent ID."""
        service = AgentService()
        with pytest.raises(AgentNotFoundError):
            await service.deactivate_agent(uuid.uuid4(), db_session)


# ---------------------------------------------------------------------------
# T065e: render_system_message
# ---------------------------------------------------------------------------


class TestRenderSystemMessage:
    """render_system_message function tests."""

    def _make_agent(self) -> MagicMock:
        """Create a stub Agent object for testing (uses MagicMock to avoid ORM init)."""
        agent = MagicMock(spec_set=["role_name", "role_description", "persona_name", "persona_description", "system_message_template"])
        agent.role_name = "Screener"
        agent.role_description = "Screens papers"
        agent.persona_name = "Dr. Aria"
        agent.persona_description = "A meticulous reviewer"
        agent.system_message_template = _VALID_TEMPLATE
        return agent

    def test_renders_all_six_variables(self) -> None:
        """render_system_message substitutes all six known template variables."""
        agent = self._make_agent()
        result = render_system_message(
            _VALID_TEMPLATE, agent, domain="Software Engineering", study_type="SMS"
        )
        assert "Screener" in result
        assert "Software Engineering" in result
        assert "SMS" in result
        assert "Dr. Aria" in result
        assert "Screens papers" in result
        assert "A meticulous reviewer" in result

    def test_raises_template_render_error_for_unknown_variable(self) -> None:
        """render_system_message raises TemplateRenderError for unknown variable."""
        agent = self._make_agent()
        bad_template = "Hello {{ unknown_thing }}"
        with pytest.raises(TemplateRenderError) as exc_info:
            render_system_message(bad_template, agent, domain="SE", study_type="SMS")
        assert exc_info.value.variable_name == "unknown_thing"

    def test_render_error_has_variable_name(self) -> None:
        """TemplateRenderError.variable_name is populated with the unknown variable."""
        agent = self._make_agent()
        bad_template = "{{ mystery_var }}"
        try:
            render_system_message(bad_template, agent, domain="SE", study_type="SMS")
        except TemplateRenderError as exc:
            assert exc.variable_name == "mystery_var"


# ---------------------------------------------------------------------------
# T065f: build_study_context
# ---------------------------------------------------------------------------


class TestBuildStudyContext:
    """build_study_context function tests."""

    def _make_study(self, study_type_str: str, topic: str | None) -> MagicMock:
        """Create a stub Study object."""
        study = MagicMock()
        study.study_type = MagicMock()
        study.study_type.value = study_type_str
        study.topic = topic
        return study

    def test_sms_maps_to_correct_label(self) -> None:
        """StudyType.SMS maps to 'Systematic Mapping Study'."""
        study = self._make_study("SMS", "Software Testing")
        ctx = build_study_context(study)
        assert ctx.study_type == "Systematic Mapping Study"

    def test_slr_maps_to_correct_label(self) -> None:
        """StudyType.SLR maps to 'Systematic Literature Review'."""
        study = self._make_study("SLR", "Machine Learning")
        ctx = build_study_context(study)
        assert ctx.study_type == "Systematic Literature Review"

    def test_tertiary_maps_to_correct_label(self) -> None:
        """StudyType.TERTIARY maps to 'Tertiary Study'."""
        study = self._make_study("Tertiary", "AI Ethics")
        ctx = build_study_context(study)
        assert ctx.study_type == "Tertiary Study"

    def test_rapid_maps_to_correct_label(self) -> None:
        """StudyType.RAPID maps to 'Rapid Review'."""
        study = self._make_study("Rapid", None)
        ctx = build_study_context(study)
        assert ctx.study_type == "Rapid Review"

    def test_uses_topic_as_domain(self) -> None:
        """build_study_context uses study.topic as the domain."""
        study = self._make_study("SMS", "Software Engineering")
        ctx = build_study_context(study)
        assert ctx.domain == "Software Engineering"

    def test_defaults_domain_when_topic_none(self) -> None:
        """build_study_context defaults to SE/AI when topic is None."""
        study = self._make_study("SMS", None)
        ctx = build_study_context(study)
        assert "Software Engineering" in ctx.domain


# ---------------------------------------------------------------------------
# T065g: undo buffer swap
# ---------------------------------------------------------------------------


class TestUndoBuffer:
    """AgentService.restore_system_message undo buffer tests."""

    async def test_swap_restores_previous_message(
        self,
        db_session: AsyncSession,
        provider_and_model: tuple[Provider, AvailableModel],
    ) -> None:
        """restore_system_message swaps template with undo buffer."""
        provider, model = provider_and_model
        service = AgentService()

        agent = Agent(
            task_type=AgentTaskType.SCREENER,
            role_name="Screener",
            role_description="Test",
            persona_name="P",
            persona_description="Test persona",
            system_message_template="Current template {{ role_name }}",
            system_message_undo_buffer="Previous template {{ role_name }}",
            model_id=model.id,
            provider_id=provider.id,
        )
        db_session.add(agent)
        await db_session.flush()

        result = await service.restore_system_message(agent.id, db_session)

        assert result.system_message_template == "Previous template {{ role_name }}"
        assert result.system_message_undo_buffer == "Current template {{ role_name }}"

    async def test_raises_no_undo_buffer_error_when_buffer_null(
        self,
        db_session: AsyncSession,
        provider_and_model: tuple[Provider, AvailableModel],
    ) -> None:
        """restore_system_message raises NoUndoBufferError when buffer is NULL."""
        provider, model = provider_and_model
        service = AgentService()

        agent = Agent(
            task_type=AgentTaskType.SCREENER,
            role_name="Screener",
            role_description="Test",
            persona_name="P",
            persona_description="Test persona",
            system_message_template="Template {{ role_name }}",
            system_message_undo_buffer=None,
            model_id=model.id,
            provider_id=provider.id,
        )
        db_session.add(agent)
        await db_session.flush()

        with pytest.raises(NoUndoBufferError):
            await service.restore_system_message(agent.id, db_session)
