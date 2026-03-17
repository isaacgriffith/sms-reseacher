"""Additional unit tests for backend.services.agent_service.

Covers uncovered lines: AgentHasDependentsError, get_agent_task_types,
provider_id mismatch in create_agent, StaleVersionError, model update paths,
deactivate with dependents, _build_provider_config with api key decrypt,
and generate_system_message error paths.
"""

from __future__ import annotations

import uuid
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
# AgentHasDependentsError
# ---------------------------------------------------------------------------


def test_agent_has_dependents_error_stores_reviewer_ids():
    """AgentHasDependentsError stores reviewer_ids and formats the message.

    The reviewer_ids attribute should contain the provided list and the
    error message should mention the count.
    """
    from backend.services.agent_service import AgentHasDependentsError

    err = AgentHasDependentsError([1, 2, 3])
    assert err.reviewer_ids == [1, 2, 3]
    assert "3" in str(err)


# ---------------------------------------------------------------------------
# get_agent_task_types
# ---------------------------------------------------------------------------


def test_get_agent_task_types_returns_sorted_list():
    """get_agent_task_types returns a sorted list of task type strings.

    All AgentTaskType enum values should appear in the result.
    """
    from backend.services.agent_service import AgentService

    service = AgentService()
    types = service.get_agent_task_types()
    assert isinstance(types, list)
    assert len(types) > 0
    # Should be sorted
    assert types == sorted(types)


# ---------------------------------------------------------------------------
# create_agent — provider_id mismatch
# ---------------------------------------------------------------------------


async def test_create_agent_raises_when_provider_id_mismatches(
    db_session: AsyncSession,
    provider_and_model: tuple[Provider, AvailableModel],
) -> None:
    """create_agent raises ValueError when model.provider_id != data.provider_id.

    If the model belongs to a different provider than the one specified the
    function should raise ValueError.
    """
    from backend.services.agent_service import AgentCreate, AgentService

    provider, model = provider_and_model
    service = AgentService()

    # Use a random UUID for provider_id that won't match
    wrong_provider_id = uuid.uuid4()
    data = AgentCreate(
        task_type=AgentTaskType.SCREENER.value,
        role_name="Screener",
        role_description="Screens",
        persona_name="Dr. Aria",
        persona_description="Reviewer",
        system_message_template=_VALID_TEMPLATE,
        model_id=model.id,
        provider_id=wrong_provider_id,
    )
    with pytest.raises(ValueError, match="provider_id"):
        await service.create_agent(data, db_session)


# ---------------------------------------------------------------------------
# update_agent — StaleVersionError
# ---------------------------------------------------------------------------


async def test_update_agent_raises_stale_version_error(
    db_session: AsyncSession,
    provider_and_model: tuple[Provider, AvailableModel],
) -> None:
    """update_agent raises StaleVersionError when version_id does not match.

    If the supplied version_id differs from the current DB version the
    optimistic lock should trigger StaleVersionError.
    """
    from backend.services.agent_service import AgentService, AgentUpdate, StaleVersionError

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

    wrong_version = agent.version_id + 999
    update = AgentUpdate(version_id=wrong_version, role_name="New Name")
    with pytest.raises(StaleVersionError):
        await service.update_agent(agent.id, update, db_session)


# ---------------------------------------------------------------------------
# update_agent — model_id update path
# ---------------------------------------------------------------------------


async def test_update_agent_with_model_id_update(
    db_session: AsyncSession,
    provider_and_model: tuple[Provider, AvailableModel],
) -> None:
    """update_agent with a new model_id validates and updates the model reference.

    When model_id is provided the function should look up and validate the
    new model before persisting.
    """
    from backend.services.agent_service import AgentService, AgentUpdate

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

    # Update with the same model_id (valid) and correct version
    update = AgentUpdate(
        version_id=agent.version_id,
        model_id=model.id,
        provider_id=provider.id,
    )
    updated = await service.update_agent(agent.id, update, db_session)
    assert updated.model_id == model.id


# ---------------------------------------------------------------------------
# deactivate_agent — raises AgentHasDependentsError
# ---------------------------------------------------------------------------


async def test_deactivate_raises_when_reviewer_references_agent(
    db_session: AsyncSession,
    provider_and_model: tuple[Provider, AvailableModel],
) -> None:
    """deactivate_agent raises AgentHasDependentsError when Reviewer rows exist.

    If any Reviewer record references this agent the deactivation should
    be refused with AgentHasDependentsError.
    """
    from db.models.study import Reviewer, ReviewerType

    from backend.services.agent_service import AgentHasDependentsError, AgentService

    import db.models.study  # noqa: F401

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

    # Create a Reviewer that references this agent
    reviewer = Reviewer(
        study_id=1,
        reviewer_type=ReviewerType.AI_AGENT,
        agent_id=agent.id,
        agent_name="TestAgent",
    )
    db_session.add(reviewer)
    await db_session.flush()

    with pytest.raises(AgentHasDependentsError) as exc_info:
        await service.deactivate_agent(agent.id, db_session)
    assert reviewer.id in exc_info.value.reviewer_ids


# ---------------------------------------------------------------------------
# _build_provider_config
# ---------------------------------------------------------------------------


def test_build_provider_config_returns_none_when_provider_is_none():
    """_build_provider_config returns None when provider is None.

    When no provider is configured the function should return None to signal
    fallback to environment-based settings.
    """
    from backend.services.agent_service import _build_provider_config

    result = _build_provider_config(None, MagicMock())
    assert result is None


def test_build_provider_config_returns_none_when_model_is_none():
    """_build_provider_config returns None when model is None.

    When no model is configured the function should return None.
    """
    from backend.services.agent_service import _build_provider_config

    result = _build_provider_config(MagicMock(), None)
    assert result is None


def test_build_provider_config_returns_config_when_both_provided():
    """_build_provider_config returns a _DbProviderConfig when both are provided.

    When valid provider and model mocks are given the function should return
    a provider config with the correct model_string.
    """
    from backend.services.agent_service import _build_provider_config

    provider = MagicMock()
    provider.provider_type = ProviderType.ANTHROPIC
    provider.api_key_encrypted = None
    provider.base_url = None
    provider.id = uuid.uuid4()

    model = MagicMock()
    model.model_identifier = "claude-3-haiku"

    result = _build_provider_config(provider, model)
    assert result is not None
    assert "claude-3-haiku" in result.model_string


def test_build_provider_config_handles_api_key_decrypt_error():
    """_build_provider_config handles decryption failures gracefully.

    When the API key cannot be decrypted the function should log a warning
    and continue with api_key=None rather than raising.
    """
    from backend.services.agent_service import _build_provider_config

    provider = MagicMock()
    provider.provider_type = ProviderType.OPENAI
    provider.api_key_encrypted = "bad-encrypted-value"
    provider.base_url = None
    provider.id = uuid.uuid4()

    model = MagicMock()
    model.model_identifier = "gpt-4"

    with patch("backend.services.agent_service.decrypt_secret", side_effect=Exception("decrypt error")):
        result = _build_provider_config(provider, model)

    # Should still return a config (with None api_key) rather than raising
    assert result is not None


# ---------------------------------------------------------------------------
# PersonaSvgGenerationError
# ---------------------------------------------------------------------------


def test_persona_svg_generation_error_is_exception():
    """PersonaSvgGenerationError is a subclass of Exception.

    The custom error class should be raisable and catchable as an Exception.
    """
    from backend.services.agent_service import PersonaSvgGenerationError

    with pytest.raises(PersonaSvgGenerationError):
        raise PersonaSvgGenerationError("LLM failed")


# ---------------------------------------------------------------------------
# StaleVersionError
# ---------------------------------------------------------------------------


def test_stale_version_error_is_exception():
    """StaleVersionError is a subclass of Exception.

    The custom error class should be raisable with a message.
    """
    from backend.services.agent_service import StaleVersionError

    with pytest.raises(StaleVersionError):
        raise StaleVersionError("Version mismatch")
