"""Unit tests for db.models.study — StudyMember, Reviewer, and their enums."""

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db.base import Base
from db.models import Study, StudyType
from db.models.study import Reviewer, ReviewerType, StudyMember, StudyMemberRole
from db.models.users import ResearchGroup, User


# ---------------------------------------------------------------------------
# Test database fixture
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def session():
    """Yield an in-memory SQLite session with all tables created.

    Imports Study and users models to ensure FK target tables exist before
    creating the study module's tables.
    """
    # Ensure all related models are registered on Base.metadata
    import db.models  # noqa: F401
    import db.models.users  # noqa: F401

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
    await engine.dispose()


# ---------------------------------------------------------------------------
# Enum tests
# ---------------------------------------------------------------------------


class TestStudyMemberRoleEnum:
    """StudyMemberRole enum values."""

    def test_lead_value(self) -> None:
        """StudyMemberRole.LEAD has value 'lead'."""
        assert StudyMemberRole.LEAD.value == "lead"

    def test_member_value(self) -> None:
        """StudyMemberRole.MEMBER has value 'member'."""
        assert StudyMemberRole.MEMBER.value == "member"

    @pytest.mark.parametrize("role", list(StudyMemberRole))
    def test_all_values_are_strings(self, role: StudyMemberRole) -> None:
        """All StudyMemberRole values are str subclasses."""
        assert isinstance(role, str)

    def test_invalid_value_raises(self) -> None:
        """Unknown value raises ValueError."""
        with pytest.raises(ValueError):
            StudyMemberRole("owner")


class TestReviewerTypeEnum:
    """ReviewerType enum values."""

    def test_human_value(self) -> None:
        """ReviewerType.HUMAN has value 'human'."""
        assert ReviewerType.HUMAN.value == "human"

    def test_ai_agent_value(self) -> None:
        """ReviewerType.AI_AGENT has value 'ai_agent'."""
        assert ReviewerType.AI_AGENT.value == "ai_agent"

    @pytest.mark.parametrize("rtype", list(ReviewerType))
    def test_all_values_are_strings(self, rtype: ReviewerType) -> None:
        """All ReviewerType values are str subclasses."""
        assert isinstance(rtype, str)


# ---------------------------------------------------------------------------
# StudyMember
# ---------------------------------------------------------------------------


class TestStudyMemberModel:
    """Attribute and persistence tests for StudyMember."""

    def test_instantiates_with_required_fields(self) -> None:
        """StudyMember can be constructed with study_id, user_id, and role."""
        sm = StudyMember(study_id=1, user_id=2, role=StudyMemberRole.LEAD)
        assert sm.study_id == 1
        assert sm.user_id == 2
        assert sm.role == StudyMemberRole.LEAD

    @pytest.mark.asyncio
    async def test_default_role_is_member_after_persist(self, session) -> None:
        """Default role is MEMBER after the row is flushed to the database."""
        user = User(email="drole@test.com", hashed_password="h", display_name="DR")
        study = Study(name="Default Role Study", study_type=StudyType.SMS)
        session.add_all([user, study])
        await session.flush()

        sm = StudyMember(study_id=study.id, user_id=user.id)
        session.add(sm)
        await session.flush()
        assert sm.role == StudyMemberRole.MEMBER

    def test_repr_contains_study_and_user(self) -> None:
        """__repr__ includes study_id and user_id."""
        sm = StudyMember(study_id=3, user_id=9, role=StudyMemberRole.LEAD)
        r = repr(sm)
        assert "3" in r
        assert "9" in r

    @pytest.mark.asyncio
    async def test_persists_with_fk_rows(self, session) -> None:
        """StudyMember persists when study and user rows exist."""
        user = User(email="sm@test.com", hashed_password="h", display_name="SM")
        study = Study(name="SM Study", study_type=StudyType.SMS)
        session.add_all([user, study])
        await session.flush()

        sm = StudyMember(study_id=study.id, user_id=user.id, role=StudyMemberRole.LEAD)
        session.add(sm)
        await session.commit()
        assert sm.study_id == study.id
        assert sm.user_id == user.id

    @pytest.mark.asyncio
    async def test_joined_at_is_set_on_persist(self, session) -> None:
        """joined_at timestamp is populated after commit."""
        user = User(email="jat@test.com", hashed_password="h", display_name="JAT")
        study = Study(name="JAT Study", study_type=StudyType.SMS)
        session.add_all([user, study])
        await session.flush()

        sm = StudyMember(study_id=study.id, user_id=user.id, role=StudyMemberRole.MEMBER)
        session.add(sm)
        await session.commit()
        await session.refresh(sm)
        assert sm.joined_at is not None

    @pytest.mark.asyncio
    async def test_unique_constraint_study_user_pair(self, session) -> None:
        """Two StudyMember rows for the same (study_id, user_id) raise IntegrityError."""
        user = User(email="uq@test.com", hashed_password="h", display_name="UQ")
        study = Study(name="UQ Study", study_type=StudyType.SMS)
        session.add_all([user, study])
        await session.flush()

        session.add(StudyMember(study_id=study.id, user_id=user.id, role=StudyMemberRole.LEAD))
        await session.flush()

        session.add(StudyMember(study_id=study.id, user_id=user.id, role=StudyMemberRole.MEMBER))
        with pytest.raises(IntegrityError):
            await session.commit()


# ---------------------------------------------------------------------------
# Reviewer
# ---------------------------------------------------------------------------


class TestReviewerModel:
    """Attribute and persistence tests for Reviewer."""

    def test_instantiates_as_human(self) -> None:
        """Reviewer can be constructed as a human reviewer."""
        r = Reviewer(study_id=1, reviewer_type=ReviewerType.HUMAN, user_id=5)
        assert r.reviewer_type == ReviewerType.HUMAN
        assert r.user_id == 5
        assert r.agent_name is None

    def test_instantiates_as_ai_agent(self) -> None:
        """Reviewer can be constructed as an AI agent reviewer."""
        r = Reviewer(
            study_id=1,
            reviewer_type=ReviewerType.AI_AGENT,
            agent_name="ScreenerAgent",
            agent_config={"model": "claude-sonnet-4-6"},
        )
        assert r.reviewer_type == ReviewerType.AI_AGENT
        assert r.agent_name == "ScreenerAgent"
        assert r.agent_config == {"model": "claude-sonnet-4-6"}
        assert r.user_id is None

    def test_repr_contains_study_and_type(self) -> None:
        """__repr__ includes study_id and reviewer_type."""
        r = Reviewer(study_id=7, reviewer_type=ReviewerType.HUMAN, user_id=3)
        repr_str = repr(r)
        assert "7" in repr_str
        assert "human" in repr_str.lower()

    @pytest.mark.asyncio
    async def test_persists_human_reviewer(self, session) -> None:
        """Human Reviewer row is persisted; id is populated."""
        user = User(email="rev@test.com", hashed_password="h", display_name="Rev")
        study = Study(name="Rev Study", study_type=StudyType.SMS)
        session.add_all([user, study])
        await session.flush()

        reviewer = Reviewer(
            study_id=study.id, reviewer_type=ReviewerType.HUMAN, user_id=user.id
        )
        session.add(reviewer)
        await session.commit()
        assert reviewer.id is not None
        assert reviewer.id > 0

    @pytest.mark.asyncio
    async def test_persists_ai_reviewer(self, session) -> None:
        """AI agent Reviewer row is persisted with agent_name and agent_config."""
        study = Study(name="AI Study", study_type=StudyType.SMS)
        session.add(study)
        await session.flush()

        reviewer = Reviewer(
            study_id=study.id,
            reviewer_type=ReviewerType.AI_AGENT,
            agent_name="Screener",
            agent_config={"threshold": 0.8},
        )
        session.add(reviewer)
        await session.commit()
        await session.refresh(reviewer)
        assert reviewer.id is not None
        assert reviewer.agent_name == "Screener"

    @pytest.mark.asyncio
    async def test_created_at_is_set_on_persist(self, session) -> None:
        """created_at is populated after commit."""
        study = Study(name="TS Study", study_type=StudyType.SMS)
        session.add(study)
        await session.flush()

        reviewer = Reviewer(
            study_id=study.id,
            reviewer_type=ReviewerType.AI_AGENT,
            agent_name="TS Agent",
        )
        session.add(reviewer)
        await session.commit()
        await session.refresh(reviewer)
        assert reviewer.created_at is not None
