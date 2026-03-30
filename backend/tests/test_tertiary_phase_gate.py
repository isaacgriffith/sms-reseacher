"""Unit tests for backend.services.tertiary_phase_gate (feature 009, T041).

Tests cover:
- Phase 1 always unlocked.
- Phase 2 locked without a TertiaryStudyProtocol.
- Phase 2 locked when protocol exists but is draft.
- Phase 2 unlocked when protocol is validated.
- Phase 3 locked when no CandidatePaper records exist.
- Phase 3 unlocked when at least one CandidatePaper exists.
- Phases 4 and 5 locked when quality / extraction prerequisites are missing.
- Return value is always a list in ascending order.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db.base import Base
import db.models  # noqa: F401  — registers all ORM tables including tertiary
import db.models.users  # noqa: F401
import db.models.study  # noqa: F401
import db.models.slr  # noqa: F401
import db.models.candidate  # noqa: F401
import db.models.search  # noqa: F401
import db.models.search_exec  # noqa: F401
import db.models.tertiary  # noqa: F401


@pytest_asyncio.fixture
async def db_session():
    """Provide a per-test in-memory SQLite session with all tables.

    Yields:
        An :class:`~sqlalchemy.ext.asyncio.AsyncSession` backed by SQLite
        in-memory storage.
    """
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


async def _insert_study(db: AsyncSession) -> int:
    """Insert a minimal Study and ResearchGroup, returning the study id.

    Args:
        db: Active async database session.

    Returns:
        The integer study id.
    """
    from db.models.users import ResearchGroup
    from db.models import Study, StudyType, StudyStatus

    group = ResearchGroup(name="Tertiary Phase Gate Group")
    db.add(group)
    await db.flush()

    study = Study(
        name="Tertiary Phase Gate Test",
        research_group_id=group.id,
        study_type=StudyType.TERTIARY,
        status=StudyStatus.ACTIVE,
    )
    db.add(study)
    await db.commit()
    await db.refresh(study)
    return study.id


async def _insert_candidate_paper(db: AsyncSession, study_id: int) -> int:
    """Insert a minimal CandidatePaper, returning its id.

    Args:
        db: Active async database session.
        study_id: The study to attach the paper to.

    Returns:
        The integer candidate paper id.
    """
    from db.models.candidate import CandidatePaper, CandidatePaperStatus
    from db.models.search import SearchString
    from db.models.search_exec import SearchExecution, SearchExecutionStatus

    ss = SearchString(study_id=study_id, version=1, string_text="test", is_active=True)
    db.add(ss)
    await db.flush()

    se = SearchExecution(
        study_id=study_id,
        search_string_id=ss.id,
        status=SearchExecutionStatus.COMPLETED,
    )
    db.add(se)
    await db.flush()

    from db.models import Paper

    paper = Paper(title="Test Paper", doi="10.0000/test.001")
    db.add(paper)
    await db.flush()

    cp = CandidatePaper(
        study_id=study_id,
        paper_id=paper.id,
        search_execution_id=se.id,
        phase_tag="phase2",
        current_status=CandidatePaperStatus.ACCEPTED,
    )
    db.add(cp)
    await db.commit()
    await db.refresh(cp)
    return cp.id


# ---------------------------------------------------------------------------
# Phase 1 — always unlocked
# ---------------------------------------------------------------------------


class TestPhase1AlwaysUnlocked:
    """Phase 1 is always accessible."""

    @pytest.mark.asyncio
    async def test_phase_1_unlocked_no_data(self, db_session) -> None:
        """Phase 1 is unlocked even with no protocol row."""
        from backend.services.tertiary_phase_gate import get_tertiary_unlocked_phases

        study_id = await _insert_study(db_session)
        unlocked = await get_tertiary_unlocked_phases(study_id, db_session)
        assert 1 in unlocked

    @pytest.mark.asyncio
    async def test_returns_list(self, db_session) -> None:
        """Return type is always a list."""
        from backend.services.tertiary_phase_gate import get_tertiary_unlocked_phases

        study_id = await _insert_study(db_session)
        result = await get_tertiary_unlocked_phases(study_id, db_session)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Phase 2 — requires validated TertiaryStudyProtocol
# ---------------------------------------------------------------------------


class TestPhase2ProtocolValidation:
    """Phase 2 requires a validated TertiaryStudyProtocol."""

    @pytest.mark.asyncio
    async def test_phase_2_locked_without_protocol(self, db_session) -> None:
        """Phase 2 is not unlocked when no protocol row exists."""
        from backend.services.tertiary_phase_gate import get_tertiary_unlocked_phases

        study_id = await _insert_study(db_session)
        unlocked = await get_tertiary_unlocked_phases(study_id, db_session)
        assert 2 not in unlocked

    @pytest.mark.asyncio
    async def test_phase_2_locked_when_protocol_is_draft(self, db_session) -> None:
        """Phase 2 is locked when protocol exists but is in draft status."""
        from db.models.tertiary import TertiaryStudyProtocol, TertiaryProtocolStatus
        from backend.services.tertiary_phase_gate import get_tertiary_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = TertiaryStudyProtocol(
            study_id=study_id, status=TertiaryProtocolStatus.DRAFT
        )
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_tertiary_unlocked_phases(study_id, db_session)
        assert 2 not in unlocked

    @pytest.mark.asyncio
    async def test_phase_2_unlocked_when_protocol_validated(self, db_session) -> None:
        """Phase 2 is unlocked when TertiaryStudyProtocol status == validated."""
        from db.models.tertiary import TertiaryStudyProtocol, TertiaryProtocolStatus
        from backend.services.tertiary_phase_gate import get_tertiary_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = TertiaryStudyProtocol(
            study_id=study_id, status=TertiaryProtocolStatus.VALIDATED
        )
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_tertiary_unlocked_phases(study_id, db_session)
        assert 2 in unlocked

    @pytest.mark.asyncio
    async def test_phase_1_still_present_when_phase_2_unlocked(self, db_session) -> None:
        """Phase 1 is always included even when phase 2 is unlocked."""
        from db.models.tertiary import TertiaryStudyProtocol, TertiaryProtocolStatus
        from backend.services.tertiary_phase_gate import get_tertiary_unlocked_phases

        study_id = await _insert_study(db_session)
        db_session.add(
            TertiaryStudyProtocol(study_id=study_id, status=TertiaryProtocolStatus.VALIDATED)
        )
        await db_session.commit()

        unlocked = await get_tertiary_unlocked_phases(study_id, db_session)
        assert 1 in unlocked
        assert 2 in unlocked


# ---------------------------------------------------------------------------
# Phase 3 — requires at least one CandidatePaper
# ---------------------------------------------------------------------------


class TestPhase3CandidatePapers:
    """Phase 3 requires ≥1 CandidatePaper in the study."""

    @pytest.mark.asyncio
    async def test_phase_3_locked_without_candidate_papers(self, db_session) -> None:
        """Phase 3 is locked when no CandidatePaper records exist."""
        from db.models.tertiary import TertiaryStudyProtocol, TertiaryProtocolStatus
        from backend.services.tertiary_phase_gate import get_tertiary_unlocked_phases

        study_id = await _insert_study(db_session)
        db_session.add(
            TertiaryStudyProtocol(study_id=study_id, status=TertiaryProtocolStatus.VALIDATED)
        )
        await db_session.commit()

        unlocked = await get_tertiary_unlocked_phases(study_id, db_session)
        assert 3 not in unlocked

    @pytest.mark.asyncio
    async def test_phase_3_unlocked_with_one_candidate_paper(self, db_session) -> None:
        """Phase 3 is unlocked when at least one CandidatePaper exists."""
        from db.models.tertiary import TertiaryStudyProtocol, TertiaryProtocolStatus
        from backend.services.tertiary_phase_gate import get_tertiary_unlocked_phases

        study_id = await _insert_study(db_session)
        db_session.add(
            TertiaryStudyProtocol(study_id=study_id, status=TertiaryProtocolStatus.VALIDATED)
        )
        await db_session.commit()

        await _insert_candidate_paper(db_session, study_id)

        unlocked = await get_tertiary_unlocked_phases(study_id, db_session)
        assert 3 in unlocked


# ---------------------------------------------------------------------------
# Phase 4 — requires QA scores (approximated)
# ---------------------------------------------------------------------------


class TestPhase4QualityAssessment:
    """Phase 4 is locked when no QA scores exist."""

    @pytest.mark.asyncio
    async def test_phase_4_locked_without_qa_scores(self, db_session) -> None:
        """Phase 4 is locked when no QualityAssessmentScore exists."""
        from db.models.tertiary import TertiaryStudyProtocol, TertiaryProtocolStatus
        from backend.services.tertiary_phase_gate import get_tertiary_unlocked_phases

        study_id = await _insert_study(db_session)
        db_session.add(
            TertiaryStudyProtocol(study_id=study_id, status=TertiaryProtocolStatus.VALIDATED)
        )
        await db_session.commit()
        await _insert_candidate_paper(db_session, study_id)

        unlocked = await get_tertiary_unlocked_phases(study_id, db_session)
        assert 4 not in unlocked


# ---------------------------------------------------------------------------
# Return ordering
# ---------------------------------------------------------------------------


class TestReturnOrdering:
    """Unlocked phases list is always in ascending order."""

    @pytest.mark.asyncio
    async def test_phases_are_ordered_ascending(self, db_session) -> None:
        """Returned list is always sorted in ascending order."""
        from backend.services.tertiary_phase_gate import get_tertiary_unlocked_phases

        study_id = await _insert_study(db_session)
        result = await get_tertiary_unlocked_phases(study_id, db_session)
        assert result == sorted(result)

    @pytest.mark.asyncio
    async def test_nonexistent_study_returns_phase_1(self, db_session) -> None:
        """A study that does not exist still returns at least phase 1."""
        from backend.services.tertiary_phase_gate import get_tertiary_unlocked_phases

        unlocked = await get_tertiary_unlocked_phases(99999, db_session)
        assert unlocked == [1]
