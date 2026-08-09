"""Unit tests for backend.services.quality_assessment_service (feature 007).

Tests cover:
- get_checklist returns None when no checklist exists.
- upsert_checklist creates a new checklist with items.
- upsert_checklist replaces items on second call.
- get_scores returns empty dict when no scores exist.
- submit_scores creates score rows and returns list.
- submit_scores updates existing scores on second call.
- compute_aggregate_score computes weighted average correctly.
- compute_aggregate_score returns 0.0 for empty inputs.
- Kappa is triggered when both reviewers complete all accepted papers.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import db.models  # noqa: F401
import db.models.candidate  # noqa: F401
import db.models.criteria  # noqa: F401
import db.models.pico  # noqa: F401
import db.models.search  # noqa: F401
import db.models.search_exec  # noqa: F401
import db.models.seeds  # noqa: F401
import db.models.slr  # noqa: F401
import db.models.study  # noqa: F401
import db.models.users  # noqa: F401
import pytest
import pytest_asyncio
from db.base import Base
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _insert_study(db: AsyncSession) -> int:
    """Insert a minimal Study and ResearchGroup, returning the study id."""
    from db.models import Study, StudyStatus, StudyType
    from db.models.users import ResearchGroup

    group = ResearchGroup(name="QA Test Group")
    db.add(group)
    await db.flush()

    study = Study(
        name="QA Test SLR",
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

    paper = Paper(title=f"QA Test Paper {_paper_counter}", doi=f"10.0000/qa.{_paper_counter}")
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
        string_text="quality AND assessment",
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
    status: str = "accepted",
) -> int:
    """Insert a CandidatePaper with the given status, returning its id."""
    from db.models.candidate import CandidatePaper, CandidatePaperStatus

    cp = CandidatePaper(
        study_id=study_id,
        paper_id=paper_id,
        search_execution_id=search_execution_id,
        phase_tag="title_abstract",
        current_status=CandidatePaperStatus(status),
    )
    db.add(cp)
    await db.commit()
    await db.refresh(cp)
    return cp.id


# ---------------------------------------------------------------------------
# Tests — get_checklist
# ---------------------------------------------------------------------------


class TestGetChecklist:
    """get_checklist returns None when no checklist exists."""

    @pytest.mark.asyncio
    async def test_get_checklist_none(self, db_session) -> None:
        """Returns None when no checklist has been created for the study."""
        from backend.services.quality_assessment_service import get_checklist

        study_id = await _insert_study(db_session)
        result = await get_checklist(study_id, db_session)
        assert result is None


# ---------------------------------------------------------------------------
# Tests — upsert_checklist
# ---------------------------------------------------------------------------


class TestUpsertChecklist:
    """upsert_checklist creates and replaces checklists."""

    @pytest.mark.asyncio
    async def test_upsert_checklist_creates(self, db_session) -> None:
        """Creates a new checklist with the given items."""
        from backend.services.quality_assessment_service import upsert_checklist

        study_id = await _insert_study(db_session)
        data = {
            "name": "My Checklist",
            "description": "A test checklist",
            "items": [
                {"order": 1, "question": "Q1?", "scoring_method": "binary", "weight": 1.0},
                {"order": 2, "question": "Q2?", "scoring_method": "scale_1_3", "weight": 2.0},
            ],
        }
        checklist = await upsert_checklist(study_id, data, db_session)
        assert checklist.study_id == study_id
        assert checklist.name == "My Checklist"
        assert len(checklist.items) == 2
        assert checklist.items[0].question == "Q1?"

    @pytest.mark.asyncio
    async def test_upsert_checklist_replaces_items(self, db_session) -> None:
        """Second upsert replaces all existing items."""
        from backend.services.quality_assessment_service import upsert_checklist

        study_id = await _insert_study(db_session)
        first_data = {
            "name": "First",
            "items": [
                {"order": 1, "question": "Old Q?", "scoring_method": "binary", "weight": 1.0},
            ],
        }
        await upsert_checklist(study_id, first_data, db_session)

        second_data = {
            "name": "Second",
            "items": [
                {"order": 1, "question": "New Q1?", "scoring_method": "scale_1_5", "weight": 3.0},
                {"order": 2, "question": "New Q2?", "scoring_method": "binary", "weight": 1.0},
            ],
        }
        checklist = await upsert_checklist(study_id, second_data, db_session)
        assert checklist.name == "Second"
        assert len(checklist.items) == 2
        questions = {item.question for item in checklist.items}
        assert "Old Q?" not in questions
        assert "New Q1?" in questions

    @pytest.mark.asyncio
    async def test_upsert_checklist_persists_anchors(self, db_session) -> None:
        """Anchors submitted with an item survive the write (TFIX7 part 3).

        ``upsert_checklist`` builds each ``QualityChecklistItem`` field by
        field, so a key it does not read is dropped in silence — the item is
        created, the request succeeds, and the anchors are simply gone.
        """
        from backend.services.quality_assessment_service import upsert_checklist

        study_id = await _insert_study(db_session)
        anchors = {"1.0": "Explicit", "0.5": "Implicit", "0.0": "Absent"}
        data = {
            "name": "DARE",
            "items": [
                {
                    "order": 1,
                    "question": "Criteria described?",
                    "scoring_method": "yes_partial_no",
                    "weight": 1.0,
                    "anchors": anchors,
                },
            ],
        }
        checklist = await upsert_checklist(study_id, data, db_session)
        assert checklist.items[0].anchors == anchors

    @pytest.mark.asyncio
    async def test_upsert_checklist_without_anchors_stores_none(self, db_session) -> None:
        """Items that carry no anchors are unaffected."""
        from backend.services.quality_assessment_service import upsert_checklist

        study_id = await _insert_study(db_session)
        data = {
            "name": "CL",
            "items": [
                {"order": 1, "question": "Q1?", "scoring_method": "binary", "weight": 1.0},
            ],
        }
        checklist = await upsert_checklist(study_id, data, db_session)
        assert checklist.items[0].anchors is None


# ---------------------------------------------------------------------------
# Tests — yes/partial/no validation (TFIX7 part 3)
# ---------------------------------------------------------------------------


class TestYesPartialNoValidation:
    """submit_scores enforces DARE's rules on yes_partial_no items.

    Validation belongs in the service rather than the request schema because
    the rule depends on the *item* being scored: only ``yes_partial_no`` items
    are constrained, and a Pydantic model validating ``ScoreItemInput`` alone
    cannot see which item an id refers to.
    """

    @staticmethod
    async def _dare_fixture(db_session) -> tuple[int, int, list[int]]:
        """Create a study with a two-item DARE checklist; return ids.

        Two items rather than one: the batch-atomicity test needs a valid
        answer and an invalid one in the same submission, and reusing a single
        item id twice would trip the ``(paper, reviewer, item)`` unique
        constraint before validation ever ran.
        """
        from backend.services.quality_assessment_service import upsert_checklist

        study_id = await _insert_study(db_session)
        reviewer_id = await _insert_reviewer(db_session, study_id)
        exec_id = await _insert_search_exec(db_session, study_id)
        paper_id = await _insert_paper(db_session)
        cp_id = await _insert_candidate_paper(db_session, study_id, paper_id, exec_id, "accepted")

        checklist = await upsert_checklist(
            study_id,
            {
                "name": "DARE",
                "items": [
                    {
                        "order": 1,
                        "question": "Criteria described?",
                        "scoring_method": "yes_partial_no",
                        "weight": 1.0,
                        "anchors": {"1.0": "Explicit", "0.5": "Implicit", "0.0": "Absent"},
                    },
                    {
                        "order": 2,
                        "question": "Search adequate?",
                        "scoring_method": "yes_partial_no",
                        "weight": 1.0,
                        "anchors": {"1.0": "Four or more", "0.5": "Three", "0.0": "Two"},
                    },
                ],
            },
            db_session,
        )
        item_ids = [item.id for item in sorted(checklist.items, key=lambda i: i.order)]
        return cp_id, reviewer_id, item_ids

    @pytest.mark.asyncio
    async def test_rejects_answer_without_justification(self, db_session) -> None:
        """A DARE answer with no justification is refused.

        ``04-tertiary.md`` requires reviewers to answer "providing a
        justification for each answer", and its implementation note calls this
        out as "not optional metadata". A stored score with no reasoning cannot
        be adjudicated against a second reviewer's, which is the whole reason
        scores are held per reviewer.
        """
        from backend.services.quality_assessment_service import submit_scores

        cp_id, reviewer_id, item_ids = await self._dare_fixture(db_session)

        with pytest.raises(ValueError, match="justification"):
            await submit_scores(
                cp_id,
                reviewer_id,
                [{"checklist_item_id": item_ids[0], "score_value": 1.0, "notes": None}],
                db_session,
            )

    @pytest.mark.asyncio
    async def test_rejects_off_scale_value(self, db_session) -> None:
        """0.75 is not a finer-grained DARE judgement; it is unreadable."""
        from backend.services.quality_assessment_service import submit_scores

        cp_id, reviewer_id, item_ids = await self._dare_fixture(db_session)

        with pytest.raises(ValueError, match="0.0, 0.5 or 1.0"):
            await submit_scores(
                cp_id,
                reviewer_id,
                [{"checklist_item_id": item_ids[0], "score_value": 0.75, "notes": "Mostly."}],
                db_session,
            )

    @pytest.mark.asyncio
    async def test_accepts_valid_answer(self, db_session) -> None:
        """A scored answer with a justification is stored."""
        from backend.services.quality_assessment_service import submit_scores

        cp_id, reviewer_id, item_ids = await self._dare_fixture(db_session)

        with patch(
            "backend.services.quality_assessment_service._maybe_trigger_kappa",
            new_callable=AsyncMock,
        ):
            result = await submit_scores(
                cp_id,
                reviewer_id,
                [
                    {
                        "checklist_item_id": item_ids[0],
                        "score_value": 0.5,
                        "notes": "Criteria are implied by the RQs but never stated.",
                    }
                ],
                db_session,
            )

        assert result[0].score_value == 0.5
        assert "implied" in result[0].notes

    @pytest.mark.asyncio
    async def test_nothing_is_written_when_one_answer_is_invalid(self, db_session) -> None:
        """A rejected batch stores none of its answers.

        Validation runs over the whole batch before any row is touched, so a
        reviewer never ends up with half a DARE assessment recorded.
        """
        from backend.services.quality_assessment_service import get_scores, submit_scores

        cp_id, reviewer_id, item_ids = await self._dare_fixture(db_session)

        with pytest.raises(ValueError):
            await submit_scores(
                cp_id,
                reviewer_id,
                [
                    {"checklist_item_id": item_ids[0], "score_value": 1.0, "notes": "Fine."},
                    {"checklist_item_id": item_ids[1], "score_value": 0.75, "notes": "Off."},
                ],
                db_session,
            )

        assert await get_scores(cp_id, db_session) == {}

    @pytest.mark.asyncio
    async def test_binary_items_still_accept_null_notes(self, db_session) -> None:
        """Existing instruments are untouched — notes stay optional for them.

        The mandate is DARE's, not the platform's. Applying it to every
        checklist would break every SLR study already scoring binary items
        without notes.
        """
        from backend.services.quality_assessment_service import submit_scores, upsert_checklist

        study_id = await _insert_study(db_session)
        reviewer_id = await _insert_reviewer(db_session, study_id)
        exec_id = await _insert_search_exec(db_session, study_id)
        paper_id = await _insert_paper(db_session)
        cp_id = await _insert_candidate_paper(db_session, study_id, paper_id, exec_id, "accepted")

        checklist = await upsert_checklist(
            study_id,
            {
                "name": "CL",
                "items": [
                    {"order": 1, "question": "Q?", "scoring_method": "binary", "weight": 1.0},
                ],
            },
            db_session,
        )

        with patch(
            "backend.services.quality_assessment_service._maybe_trigger_kappa",
            new_callable=AsyncMock,
        ):
            result = await submit_scores(
                cp_id,
                reviewer_id,
                [
                    {
                        "checklist_item_id": checklist.items[0].id,
                        "score_value": 1.0,
                        "notes": None,
                    }
                ],
                db_session,
            )

        assert result[0].notes is None


# ---------------------------------------------------------------------------
# Tests — get_scores
# ---------------------------------------------------------------------------


class TestGetScores:
    """get_scores returns an empty dict when no scores exist."""

    @pytest.mark.asyncio
    async def test_get_scores_empty(self, db_session) -> None:
        """Returns empty dict when no scores have been submitted for the paper."""
        from backend.services.quality_assessment_service import get_scores

        result = await get_scores(9999, db_session)
        assert result == {}


# ---------------------------------------------------------------------------
# Tests — submit_scores
# ---------------------------------------------------------------------------


class TestSubmitScores:
    """submit_scores creates and updates score rows."""

    @pytest.mark.asyncio
    async def test_submit_scores_creates(self, db_session) -> None:
        """Creates score rows when none exist; returns the list."""
        from backend.services.quality_assessment_service import (
            submit_scores,
            upsert_checklist,
        )

        study_id = await _insert_study(db_session)
        reviewer_id = await _insert_reviewer(db_session, study_id)
        exec_id = await _insert_search_exec(db_session, study_id)
        paper_id = await _insert_paper(db_session)
        cp_id = await _insert_candidate_paper(db_session, study_id, paper_id, exec_id, "accepted")

        checklist_data = {
            "name": "CL",
            "items": [
                {"order": 1, "question": "Q?", "scoring_method": "binary", "weight": 1.0},
            ],
        }
        checklist = await upsert_checklist(study_id, checklist_data, db_session)
        item_id = checklist.items[0].id

        scores_input = [{"checklist_item_id": item_id, "score_value": 1.0, "notes": None}]
        with patch(
            "backend.services.quality_assessment_service._maybe_trigger_kappa",
            new_callable=AsyncMock,
        ):
            result = await submit_scores(cp_id, reviewer_id, scores_input, db_session)

        assert len(result) == 1
        assert result[0].score_value == 1.0
        assert result[0].candidate_paper_id == cp_id
        assert result[0].reviewer_id == reviewer_id

    @pytest.mark.asyncio
    async def test_submit_scores_updates(self, db_session) -> None:
        """Second submit_scores call updates existing scores."""
        from backend.services.quality_assessment_service import (
            submit_scores,
            upsert_checklist,
        )

        study_id = await _insert_study(db_session)
        reviewer_id = await _insert_reviewer(db_session, study_id)
        exec_id = await _insert_search_exec(db_session, study_id)
        paper_id = await _insert_paper(db_session)
        cp_id = await _insert_candidate_paper(db_session, study_id, paper_id, exec_id, "accepted")

        checklist_data = {
            "name": "CL",
            "items": [
                {"order": 1, "question": "Q?", "scoring_method": "scale_1_3", "weight": 1.0},
            ],
        }
        checklist = await upsert_checklist(study_id, checklist_data, db_session)
        item_id = checklist.items[0].id

        with patch(
            "backend.services.quality_assessment_service._maybe_trigger_kappa",
            new_callable=AsyncMock,
        ):
            await submit_scores(
                cp_id, reviewer_id, [{"checklist_item_id": item_id, "score_value": 1.0}], db_session
            )
            result = await submit_scores(
                cp_id,
                reviewer_id,
                [{"checklist_item_id": item_id, "score_value": 3.0, "notes": "Updated"}],
                db_session,
            )

        assert result[0].score_value == 3.0
        assert result[0].notes == "Updated"


# ---------------------------------------------------------------------------
# Tests — compute_aggregate_score
# ---------------------------------------------------------------------------


class TestComputeAggregateScore:
    """compute_aggregate_score computes weighted averages correctly."""

    def test_compute_aggregate_score_weighted(self) -> None:
        """Computes weighted average: sum(score*weight)/sum(weight)."""
        from unittest.mock import MagicMock

        from backend.services.quality_assessment_service import compute_aggregate_score

        item1 = MagicMock()
        item1.id = 1
        item1.weight = 2.0

        item2 = MagicMock()
        item2.id = 2
        item2.weight = 3.0

        score1 = MagicMock()
        score1.checklist_item_id = 1
        score1.score_value = 4.0

        score2 = MagicMock()
        score2.checklist_item_id = 2
        score2.score_value = 2.0

        # (4.0*2.0 + 2.0*3.0) / (2.0+3.0) = (8+6)/5 = 2.8
        result = compute_aggregate_score([score1, score2], [item1, item2])
        assert abs(result - 2.8) < 1e-9

    def test_compute_aggregate_score_empty(self) -> None:
        """Returns 0.0 when no items match."""
        from backend.services.quality_assessment_service import compute_aggregate_score

        result = compute_aggregate_score([], [])
        assert result == 0.0


# ---------------------------------------------------------------------------
# Tests — kappa trigger
# ---------------------------------------------------------------------------


class TestKappaTrigger:
    """Kappa is triggered when both reviewers complete all accepted papers."""

    @pytest.mark.asyncio
    async def test_kappa_triggered_when_both_reviewers_complete(self, db_session) -> None:
        """inter_rater_service.compute_and_store_kappa is called when both reviewers done."""
        from backend.services.quality_assessment_service import (
            submit_scores,
            upsert_checklist,
        )

        study_id = await _insert_study(db_session)
        rev_a = await _insert_reviewer(db_session, study_id)
        rev_b = await _insert_reviewer(db_session, study_id)
        exec_id = await _insert_search_exec(db_session, study_id)
        paper_id = await _insert_paper(db_session)
        cp_id = await _insert_candidate_paper(db_session, study_id, paper_id, exec_id, "accepted")

        checklist_data = {
            "name": "CL",
            "items": [
                {"order": 1, "question": "Q?", "scoring_method": "binary", "weight": 1.0},
            ],
        }
        checklist = await upsert_checklist(study_id, checklist_data, db_session)
        item_id = checklist.items[0].id

        with patch(
            "backend.services.quality_assessment_service.inter_rater_service.compute_and_store_kappa",
            new_callable=AsyncMock,
        ) as mock_kappa:
            # Rev A scores
            await submit_scores(
                cp_id,
                rev_a,
                [{"checklist_item_id": item_id, "score_value": 1.0}],
                db_session,
            )
            # Kappa should NOT be triggered yet — rev_b hasn't scored
            assert mock_kappa.call_count == 0

            # Rev B scores
            await submit_scores(
                cp_id,
                rev_b,
                [{"checklist_item_id": item_id, "score_value": 0.0}],
                db_session,
            )
            # Now both are complete — kappa should be triggered
            assert mock_kappa.call_count == 1
