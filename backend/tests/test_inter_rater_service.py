"""Unit tests for backend.services.inter_rater_service (feature 007).

Tests cover:
- Kappa computed and stored correctly for perfect/partial agreement.
- threshold_met flag set correctly relative to slr_kappa_threshold.
- kappa_undefined_reason populated when Kappa is None (zero-variance).
- HTTP 422 when a reviewer has incomplete assessments.
- HTTP 422 when no papers exist for the round.
- get_records returns all records in creation order.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db.base import Base
import db.models  # noqa: F401
import db.models.users  # noqa: F401
import db.models.study  # noqa: F401
import db.models.slr  # noqa: F401
import db.models.candidate  # noqa: F401
import db.models.search  # noqa: F401
import db.models.search_exec  # noqa: F401
import db.models.pico  # noqa: F401
import db.models.seeds  # noqa: F401
import db.models.criteria  # noqa: F401


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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _insert_study(db: AsyncSession) -> int:
    """Insert a minimal Study and ResearchGroup, returning the study id."""
    from db.models.users import ResearchGroup
    from db.models import Study, StudyType, StudyStatus

    group = ResearchGroup(name="IRR Test Group")
    db.add(group)
    await db.flush()

    study = Study(
        name="IRR Test SLR",
        research_group_id=group.id,
        study_type=StudyType.SLR,
        status=StudyStatus.ACTIVE,
    )
    db.add(study)
    await db.commit()
    await db.refresh(study)
    return study.id


async def _insert_reviewer(db: AsyncSession, study_id: int) -> int:
    """Insert a minimal Reviewer row for a study, returning reviewer id."""
    from db.models.study import Reviewer, ReviewerType

    reviewer = Reviewer(study_id=study_id, reviewer_type=ReviewerType.HUMAN)
    db.add(reviewer)
    await db.commit()
    await db.refresh(reviewer)
    return reviewer.id


_paper_counter = 0


async def _insert_paper(db: AsyncSession) -> int:
    """Insert a minimal Paper row with a unique DOI, returning paper id."""
    global _paper_counter
    _paper_counter += 1
    from db.models import Paper

    paper = Paper(title=f"Test Paper {_paper_counter}", doi=f"10.0000/test.irr.{_paper_counter}")
    db.add(paper)
    await db.commit()
    await db.refresh(paper)
    return paper.id


async def _insert_search_exec(db: AsyncSession, study_id: int) -> int:
    """Insert a minimal SearchString + SearchExecution, returning execution id."""
    from db.models.search import SearchString
    from db.models.search_exec import SearchExecution, SearchExecutionStatus

    search_string = SearchString(
        study_id=study_id,
        version=1,
        string_text="test AND paper",
        is_active=True,
    )
    db.add(search_string)
    await db.flush()

    exec_row = SearchExecution(
        study_id=study_id,
        search_string_id=search_string.id,
        phase_tag="title_abstract",
        status=SearchExecutionStatus.COMPLETED,
    )
    db.add(exec_row)
    await db.commit()
    await db.refresh(exec_row)
    return exec_row.id


async def _insert_candidate_paper(
    db: AsyncSession,
    study_id: int,
    paper_id: int,
    search_execution_id: int,
    phase_tag: str = "title_abstract",
) -> int:
    """Insert a CandidatePaper, returning its id."""
    from db.models.candidate import CandidatePaper, CandidatePaperStatus

    cp = CandidatePaper(
        study_id=study_id,
        paper_id=paper_id,
        search_execution_id=search_execution_id,
        phase_tag=phase_tag,
        current_status=CandidatePaperStatus.PENDING,
    )
    db.add(cp)
    await db.commit()
    await db.refresh(cp)
    return cp.id


async def _insert_decision(
    db: AsyncSession,
    candidate_paper_id: int,
    reviewer_id: int,
    decision: str = "accepted",
) -> None:
    """Insert a PaperDecision row."""
    from db.models.candidate import PaperDecision, PaperDecisionType

    dec = PaperDecision(
        candidate_paper_id=candidate_paper_id,
        reviewer_id=reviewer_id,
        decision=PaperDecisionType(decision),
    )
    db.add(dec)
    await db.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestComputeAndStoreKappa:
    """compute_and_store_kappa produces correct records."""

    @pytest.mark.asyncio
    async def test_perfect_agreement_returns_kappa_one(self, db_session) -> None:
        """Perfect agreement with mixed decisions gives kappa=1.0."""
        from db.models.slr import AgreementRoundType
        from backend.services.inter_rater_service import compute_and_store_kappa

        study_id = await _insert_study(db_session)
        exec_id = await _insert_search_exec(db_session, study_id)
        rev_a = await _insert_reviewer(db_session, study_id)
        rev_b = await _insert_reviewer(db_session, study_id)

        # Mixed decisions: both accept 2, both reject 2 → kappa=1.0
        for decision in ("accepted", "accepted", "rejected", "rejected"):
            paper_id = await _insert_paper(db_session)
            cp_id = await _insert_candidate_paper(
                db_session, study_id, paper_id, exec_id, "title_abstract"
            )
            await _insert_decision(db_session, cp_id, rev_a, decision)
            await _insert_decision(db_session, cp_id, rev_b, decision)

        record = await compute_and_store_kappa(
            study_id, rev_a, rev_b,
            AgreementRoundType.TITLE_ABSTRACT, "pre_discussion", db_session,
        )
        assert record.kappa_value == 1.0
        assert record.n_papers == 4
        assert record.phase == "pre_discussion"

    @pytest.mark.asyncio
    async def test_threshold_met_flag_true_above_threshold(self, db_session) -> None:
        """threshold_met is True when kappa >= slr_kappa_threshold (0.6)."""
        from db.models.slr import AgreementRoundType
        from backend.services.inter_rater_service import compute_and_store_kappa

        study_id = await _insert_study(db_session)
        exec_id = await _insert_search_exec(db_session, study_id)
        rev_a = await _insert_reviewer(db_session, study_id)
        rev_b = await _insert_reviewer(db_session, study_id)

        # Perfect agreement with mixed labels → kappa=1.0 ≥ 0.6
        for decision in ("accepted", "accepted", "rejected", "rejected"):
            paper_id = await _insert_paper(db_session)
            cp_id = await _insert_candidate_paper(
                db_session, study_id, paper_id, exec_id, "title_abstract"
            )
            await _insert_decision(db_session, cp_id, rev_a, decision)
            await _insert_decision(db_session, cp_id, rev_b, decision)

        with patch("backend.services.inter_rater_service.get_settings") as mock_settings:
            mock_settings.return_value.slr_kappa_threshold = 0.6
            record = await compute_and_store_kappa(
                study_id, rev_a, rev_b,
                AgreementRoundType.TITLE_ABSTRACT, "pre_discussion", db_session,
            )
        assert record.threshold_met is True

    @pytest.mark.asyncio
    async def test_threshold_met_flag_false_below_threshold(self, db_session) -> None:
        """threshold_met is False when kappa < slr_kappa_threshold."""
        from db.models.slr import AgreementRoundType
        from backend.services.inter_rater_service import compute_and_store_kappa

        study_id = await _insert_study(db_session)
        exec_id = await _insert_search_exec(db_session, study_id)
        rev_a = await _insert_reviewer(db_session, study_id)
        rev_b = await _insert_reviewer(db_session, study_id)

        # Disagreement: rev_a always accepts, rev_b always rejects → kappa=-1.0
        for _ in range(4):
            paper_id = await _insert_paper(db_session)
            cp_id = await _insert_candidate_paper(
                db_session, study_id, paper_id, exec_id, "title_abstract"
            )
            await _insert_decision(db_session, cp_id, rev_a, "accepted")
            await _insert_decision(db_session, cp_id, rev_b, "rejected")

        with patch("backend.services.inter_rater_service.get_settings") as mock_settings:
            mock_settings.return_value.slr_kappa_threshold = 0.6
            record = await compute_and_store_kappa(
                study_id, rev_a, rev_b,
                AgreementRoundType.TITLE_ABSTRACT, "pre_discussion", db_session,
            )
        assert record.threshold_met is False

    @pytest.mark.asyncio
    async def test_kappa_undefined_reason_when_zero_variance(self, db_session) -> None:
        """kappa_undefined_reason is populated when kappa is None."""
        from db.models.slr import AgreementRoundType
        from backend.services.inter_rater_service import compute_and_store_kappa

        study_id = await _insert_study(db_session)
        exec_id = await _insert_search_exec(db_session, study_id)
        rev_a = await _insert_reviewer(db_session, study_id)
        rev_b = await _insert_reviewer(db_session, study_id)

        # Both reviewers always accept → zero-variance → kappa undefined
        for _ in range(2):
            paper_id = await _insert_paper(db_session)
            cp_id = await _insert_candidate_paper(
                db_session, study_id, paper_id, exec_id, "title_abstract"
            )
            await _insert_decision(db_session, cp_id, rev_a, "accepted")
            await _insert_decision(db_session, cp_id, rev_b, "accepted")

        # Patch safe_cohen_kappa to return None (simulating zero-variance)
        with patch("backend.services.inter_rater_service.safe_cohen_kappa", return_value=None):
            with patch("backend.services.inter_rater_service.get_settings") as mock_settings:
                mock_settings.return_value.slr_kappa_threshold = 0.6
                record = await compute_and_store_kappa(
                    study_id, rev_a, rev_b,
                    AgreementRoundType.TITLE_ABSTRACT, "pre_discussion", db_session,
                )
        assert record.kappa_value is None
        assert record.kappa_undefined_reason is not None
        assert record.threshold_met is False

    @pytest.mark.asyncio
    async def test_post_discussion_phase_stored(self, db_session) -> None:
        """phase='post_discussion' is stored correctly."""
        from db.models.slr import AgreementRoundType
        from backend.services.inter_rater_service import compute_and_store_kappa

        study_id = await _insert_study(db_session)
        exec_id = await _insert_search_exec(db_session, study_id)
        rev_a = await _insert_reviewer(db_session, study_id)
        rev_b = await _insert_reviewer(db_session, study_id)

        for _ in range(2):
            paper_id = await _insert_paper(db_session)
            cp_id = await _insert_candidate_paper(
                db_session, study_id, paper_id, exec_id, "title_abstract"
            )
            await _insert_decision(db_session, cp_id, rev_a, "accepted")
            await _insert_decision(db_session, cp_id, rev_b, "accepted")

        record = await compute_and_store_kappa(
            study_id, rev_a, rev_b,
            AgreementRoundType.TITLE_ABSTRACT, "post_discussion", db_session,
        )
        assert record.phase == "post_discussion"


class TestComputeKappaValidation:
    """compute_and_store_kappa raises HTTP errors for invalid inputs."""

    @pytest.mark.asyncio
    async def test_raises_422_when_no_papers_in_round(self, db_session) -> None:
        """422 is raised when no CandidatePapers exist for the round."""
        from fastapi import HTTPException
        from db.models.slr import AgreementRoundType
        from backend.services.inter_rater_service import compute_and_store_kappa

        study_id = await _insert_study(db_session)
        rev_a = await _insert_reviewer(db_session, study_id)
        rev_b = await _insert_reviewer(db_session, study_id)

        with pytest.raises(HTTPException) as exc_info:
            await compute_and_store_kappa(
                study_id, rev_a, rev_b,
                AgreementRoundType.TITLE_ABSTRACT, "pre_discussion", db_session,
            )
        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_raises_422_when_reviewer_missing_decisions(self, db_session) -> None:
        """422 is raised when a reviewer hasn't assessed all papers."""
        from fastapi import HTTPException
        from db.models.slr import AgreementRoundType
        from backend.services.inter_rater_service import compute_and_store_kappa

        study_id = await _insert_study(db_session)
        exec_id = await _insert_search_exec(db_session, study_id)
        rev_a = await _insert_reviewer(db_session, study_id)
        rev_b = await _insert_reviewer(db_session, study_id)

        # Add 2 papers; only rev_a has decisions for both, rev_b has none
        for _ in range(2):
            paper_id = await _insert_paper(db_session)
            cp_id = await _insert_candidate_paper(
                db_session, study_id, paper_id, exec_id, "title_abstract"
            )
            await _insert_decision(db_session, cp_id, rev_a, "accepted")

        with pytest.raises(HTTPException) as exc_info:
            await compute_and_store_kappa(
                study_id, rev_a, rev_b,
                AgreementRoundType.TITLE_ABSTRACT, "pre_discussion", db_session,
            )
        assert exc_info.value.status_code == 422


class TestGetRecords:
    """get_records returns records in creation order."""

    @pytest.mark.asyncio
    async def test_returns_all_records_for_study(self, db_session) -> None:
        """get_records returns all records for the given study."""
        from db.models.slr import AgreementRoundType, InterRaterAgreementRecord
        from backend.services.inter_rater_service import get_records

        study_id = await _insert_study(db_session)
        exec_id = await _insert_search_exec(db_session, study_id)
        rev_a = await _insert_reviewer(db_session, study_id)
        rev_b = await _insert_reviewer(db_session, study_id)

        # Insert a record directly
        record = InterRaterAgreementRecord(
            study_id=study_id,
            reviewer_a_id=rev_a,
            reviewer_b_id=rev_b,
            round_type=AgreementRoundType.TITLE_ABSTRACT,
            phase="pre_discussion",
            kappa_value=0.75,
            n_papers=10,
            threshold_met=True,
        )
        db_session.add(record)
        await db_session.commit()

        records = await get_records(study_id, db_session)
        assert len(records) == 1
        assert records[0].kappa_value == 0.75

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_records(self, db_session) -> None:
        """get_records returns an empty list when no records exist."""
        from backend.services.inter_rater_service import get_records

        study_id = await _insert_study(db_session)
        records = await get_records(study_id, db_session)
        assert records == []
