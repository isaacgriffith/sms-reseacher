"""Unit tests for backend.services.slr_phase_gate (feature 007, 012).

Tests cover:
- Phase 1 always unlocked.
- Phase 2 locked until ReviewProtocol is validated.
- Phase 3 locked until a completed SearchExecution exists.
- Phase 4 requires accepted papers from phase 3 (012 — not its own QA scores).
- Phase 5 requires QA scores from phase 4 (012 — not its own synthesis result).
"""

from __future__ import annotations

import db.models  # noqa: F401
import db.models.candidate  # noqa: F401
import db.models.search  # noqa: F401
import db.models.search_exec  # noqa: F401
import db.models.slr  # noqa: F401
import db.models.study  # noqa: F401
import db.models.users  # noqa: F401
import pytest
import pytest_asyncio
from db.base import Base
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


@pytest_asyncio.fixture
async def db_session():
    """Provide a per-test in-memory SQLite session with all tables."""
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
    """Insert a minimal Study and ResearchGroup, returning the study id."""
    from db.models import Study, StudyStatus, StudyType
    from db.models.users import ResearchGroup

    group = ResearchGroup(name="Phase Gate Group")
    db.add(group)
    await db.flush()

    study = Study(
        name="SLR Phase Gate Test",
        research_group_id=group.id,
        study_type=StudyType.SLR,
        status=StudyStatus.ACTIVE,
    )
    db.add(study)
    await db.commit()
    await db.refresh(study)
    return study.id


async def _validate_protocol(db: AsyncSession, study_id: int) -> None:
    """Insert a validated ReviewProtocol so phase 2 (and thus later phases) can unlock."""
    from db.models.slr import ReviewProtocol, ReviewProtocolStatus

    db.add(ReviewProtocol(study_id=study_id, status=ReviewProtocolStatus.VALIDATED))
    await db.commit()


async def _complete_search(db: AsyncSession, study_id: int) -> None:
    """Insert a completed SearchExecution so phase 3 can unlock."""
    from db.models.search import SearchString
    from db.models.search_exec import SearchExecution, SearchExecutionStatus

    ss = SearchString(study_id=study_id, version=1, string_text="test", is_active=True)
    db.add(ss)
    await db.flush()

    db.add(
        SearchExecution(
            study_id=study_id,
            search_string_id=ss.id,
            status=SearchExecutionStatus.COMPLETED,
        )
    )
    await db.commit()


async def _insert_candidate_paper(db: AsyncSession, study_id: int, status) -> int:
    """Insert a CandidatePaper with the given ``current_status``, returning its id.

    Reuses an existing completed ``SearchExecution`` for the study rather than
    creating a second one — ``slr_phase_gate`` uses ``scalar_one_or_none()``
    on that query, which raises ``MultipleResultsFound`` given two rows.
    """
    from db.models import Paper
    from db.models.candidate import CandidatePaper
    from db.models.search import SearchString
    from db.models.search_exec import SearchExecution, SearchExecutionStatus

    existing_se_result = await db.execute(
        select(SearchExecution).where(
            SearchExecution.study_id == study_id,
            SearchExecution.status == SearchExecutionStatus.COMPLETED,
        )
    )
    existing_se = existing_se_result.scalars().first()
    if existing_se is None:
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
        se_id = se.id
    else:
        se_id = existing_se.id

    paper = Paper(title="Test Paper", doi=f"10.0000/test.{study_id}.{se_id}")
    db.add(paper)
    await db.flush()

    cp = CandidatePaper(
        study_id=study_id,
        paper_id=paper.id,
        search_execution_id=se_id,
        phase_tag="phase2",
        current_status=status,
    )
    db.add(cp)
    await db.commit()
    await db.refresh(cp)
    return cp.id


async def _insert_qa_score(db: AsyncSession, study_id: int, candidate_paper_id: int) -> None:
    """Insert a full QualityAssessmentScore chain (checklist, item, reviewer, score)."""
    from db.models.slr import (
        ChecklistScoringMethod,
        QualityAssessmentChecklist,
        QualityAssessmentScore,
        QualityChecklistItem,
    )
    from db.models.study import Reviewer, ReviewerType

    checklist = QualityAssessmentChecklist(study_id=study_id, name="Standard Checklist")
    db.add(checklist)
    await db.flush()

    item = QualityChecklistItem(
        checklist_id=checklist.id,
        order=1,
        question="Is the study empirical?",
        scoring_method=ChecklistScoringMethod.BINARY,
        weight=1.0,
    )
    db.add(item)
    await db.flush()

    reviewer = Reviewer(study_id=study_id, reviewer_type=ReviewerType.HUMAN)
    db.add(reviewer)
    await db.flush()

    db.add(
        QualityAssessmentScore(
            candidate_paper_id=candidate_paper_id,
            reviewer_id=reviewer.id,
            checklist_item_id=item.id,
            score_value=1.0,
        )
    )
    await db.commit()


async def _study_ready_for_phase_4(db: AsyncSession) -> int:
    """Bring a study through phases 1-3 (validated protocol, completed search)."""
    study_id = await _insert_study(db)
    await _validate_protocol(db, study_id)
    await _complete_search(db, study_id)
    return study_id


class TestPhase1AlwaysUnlocked:
    """Phase 1 is always accessible regardless of study state."""

    @pytest.mark.asyncio
    async def test_phase_1_unlocked_with_no_protocol(self, db_session) -> None:
        """Phase 1 is unlocked even when no protocol exists."""
        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 1 in unlocked


class TestPhase2ProtocolValidation:
    """Phase 2 requires a validated ReviewProtocol."""

    @pytest.mark.asyncio
    async def test_phase_2_locked_without_protocol(self, db_session) -> None:
        """Phase 2 is not in unlocked list when no protocol exists."""
        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 2 not in unlocked

    @pytest.mark.asyncio
    async def test_phase_2_locked_when_protocol_is_draft(self, db_session) -> None:
        """Phase 2 is locked when protocol exists but is still in draft."""
        from db.models.slr import ReviewProtocol, ReviewProtocolStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = ReviewProtocol(study_id=study_id, status=ReviewProtocolStatus.DRAFT)
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 2 not in unlocked

    @pytest.mark.asyncio
    async def test_phase_2_locked_when_protocol_under_review(self, db_session) -> None:
        """Phase 2 is locked when protocol is under_review."""
        from db.models.slr import ReviewProtocol, ReviewProtocolStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = ReviewProtocol(study_id=study_id, status=ReviewProtocolStatus.UNDER_REVIEW)
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 2 not in unlocked

    @pytest.mark.asyncio
    async def test_phase_2_unlocked_when_protocol_validated(self, db_session) -> None:
        """Phase 2 is unlocked when ReviewProtocol.status == validated."""
        from db.models.slr import ReviewProtocol, ReviewProtocolStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = ReviewProtocol(
            study_id=study_id,
            status=ReviewProtocolStatus.VALIDATED,
            review_report={"issues": [], "overall_assessment": "OK"},
        )
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 2 in unlocked

    @pytest.mark.asyncio
    async def test_phase_1_always_included(self, db_session) -> None:
        """Phase 1 is always in the result even when phase 2 unlocks."""
        from db.models.slr import ReviewProtocol, ReviewProtocolStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = ReviewProtocol(
            study_id=study_id,
            status=ReviewProtocolStatus.VALIDATED,
        )
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 1 in unlocked
        assert 2 in unlocked

    @pytest.mark.asyncio
    async def test_phase_3_not_included_without_search(self, db_session) -> None:
        """Phase 3 is not unlocked when no completed search execution exists."""
        from db.models.slr import ReviewProtocol, ReviewProtocolStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = ReviewProtocol(
            study_id=study_id,
            status=ReviewProtocolStatus.VALIDATED,
        )
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 3 not in unlocked

    @pytest.mark.asyncio
    async def test_unlocked_phases_ordered(self, db_session) -> None:
        """Unlocked phases list is in ascending order."""
        from db.models.slr import ReviewProtocol, ReviewProtocolStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = ReviewProtocol(
            study_id=study_id,
            status=ReviewProtocolStatus.VALIDATED,
        )
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert unlocked == sorted(unlocked)


class TestPhase4RequiresAcceptedPapers:
    """Phase 4 (Quality Assessment) gates on phase 3's output, not its own.

    A gate that requires its own phase's output can never open: Quality
    Assessment is the *only* UI that creates a ``QualityAssessmentScore``,
    so requiring one to unlock phase 4 made phase 4 permanently unreachable
    (012 — circular phase-gate defect). The correct prerequisite is what
    screening (phase 3) produces: at least one accepted candidate paper.
    """

    @pytest.mark.asyncio
    async def test_phase_4_unlocked_with_accepted_papers_and_no_qa_scores(self, db_session) -> None:
        """An SLR study past screening with accepted papers unlocks phase 4.

        Today (before the fix) this fails: the gate requires a
        QualityAssessmentScore, which can only be created from inside phase 4
        itself — the deadlock this test exists to catch.
        """
        from db.models.candidate import CandidatePaperStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _study_ready_for_phase_4(db_session)
        await _insert_candidate_paper(db_session, study_id, CandidatePaperStatus.ACCEPTED)

        unlocked = await get_slr_unlocked_phases(study_id, db_session)

        assert 4 in unlocked

    @pytest.mark.asyncio
    async def test_phase_4_locked_without_accepted_papers(self, db_session) -> None:
        """A study whose screening produced no accepted papers does not unlock phase 4.

        This is the test that stops the fix degenerating into "always
        unlock": the gate must still gate on something real.
        """
        from db.models.candidate import CandidatePaperStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _study_ready_for_phase_4(db_session)
        await _insert_candidate_paper(db_session, study_id, CandidatePaperStatus.REJECTED)

        unlocked = await get_slr_unlocked_phases(study_id, db_session)

        assert 4 not in unlocked


class TestPhase5RequiresQualityScores:
    """Phase 5 (Synthesis) gates on phase 4's output, not its own.

    Synthesis's ``useSynthesis`` hook is the only caller of
    ``startSynthesis``, so requiring a completed ``SynthesisResult`` to
    unlock phase 5 made phase 5 permanently unreachable (012 — circular
    phase-gate defect). The correct prerequisite is what Quality Assessment
    (phase 4) produces: at least one QualityAssessmentScore.
    """

    @pytest.mark.asyncio
    async def test_phase_5_unlocked_with_qa_scores_and_no_completed_synthesis(
        self, db_session
    ) -> None:
        """An SLR study with QA scores but no completed SynthesisResult unlocks phase 5.

        Today (before the fix) this fails: the gate requires a completed
        SynthesisResult, which can only be created from inside phase 5
        itself — the deadlock this test exists to catch.
        """
        from db.models.candidate import CandidatePaperStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _study_ready_for_phase_4(db_session)
        cp_id = await _insert_candidate_paper(db_session, study_id, CandidatePaperStatus.ACCEPTED)
        await _insert_qa_score(db_session, study_id, cp_id)

        unlocked = await get_slr_unlocked_phases(study_id, db_session)

        assert 5 in unlocked

    @pytest.mark.asyncio
    async def test_phase_5_locked_without_qa_scores(self, db_session) -> None:
        """Phase 5 stays locked when phase 4 has not produced any QA scores yet."""
        from db.models.candidate import CandidatePaperStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _study_ready_for_phase_4(db_session)
        await _insert_candidate_paper(db_session, study_id, CandidatePaperStatus.ACCEPTED)

        unlocked = await get_slr_unlocked_phases(study_id, db_session)

        assert 5 not in unlocked
