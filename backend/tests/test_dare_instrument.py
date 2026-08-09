"""Unit tests for backend.services.dare_instrument (TFIX7 part 3).

DARE is the quality instrument the corpus assigns to tertiary studies
(``07-quality-assessment.md:146``), with full anchors in
``04-tertiary.md:150-178``.  These tests pin the parts of the instrument that
a paraphrase loses:

- four questions, scored **Y = 1, P = 0.5, N = 0**, total out of 4;
- three anchor descriptions per question, stored beside the value they
  describe rather than folded into the question prose;
- a **mandatory justification per answer** — ``04-tertiary.md:202`` calls this
  out explicitly as "not optional metadata";
- an optional fifth *synthesis* question, which the SE community dropped from
  the original CRD set and which ``10-reporting-and-evaluation.md:175-178``
  says is "worth restoring as an optional fifth question".

The wording assertions are deliberate.  An instrument whose questions have
drifted from the source is no longer the instrument it claims to be, and
Principle XI makes that a correctness defect rather than a documentation one.
"""

from __future__ import annotations

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
from db.models.slr import ChecklistScoringMethod, QualityAssessmentChecklist
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload
from sqlalchemy.pool import StaticPool

from backend.services.dare_instrument import (
    DARE_CHECKLIST_NAME,
    DARE_QUESTIONS,
    DARE_SYNTHESIS_QUESTION,
    YES_PARTIAL_NO_SCORES,
    dare_item_payloads,
    dare_total,
    seed_dare_checklist,
    validate_yes_partial_no,
)


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
# Instrument shape
# ---------------------------------------------------------------------------


class TestDareQuestions:
    """The four core questions match 04-tertiary.md 2.3."""

    def test_has_exactly_four_questions(self) -> None:
        """Four, not five: the synthesis question is offered separately."""
        assert len(DARE_QUESTIONS) == 4

    def test_orders_are_one_through_four(self) -> None:
        assert [q.order for q in DARE_QUESTIONS] == [1, 2, 3, 4]

    def test_every_question_has_three_anchors(self) -> None:
        """One anchor per score value, keyed by the value it describes."""
        for question in DARE_QUESTIONS:
            assert set(question.anchors) == {"1.0", "0.5", "0.0"}, question.order

    def test_no_anchor_is_blank(self) -> None:
        for question in DARE_QUESTIONS:
            for value, text in question.anchors.items():
                assert text.strip(), f"Q{question.order} anchor {value} is blank"

    def test_q1_covers_inclusion_and_exclusion_criteria(self) -> None:
        assert "inclusion and exclusion criteria" in DARE_QUESTIONS[0].question.lower()

    def test_q2_yes_anchor_requires_four_or_more_libraries(self) -> None:
        """The count is the discriminating part of the anchor and must survive."""
        assert "four or more" in DARE_QUESTIONS[1].anchors["1.0"].lower()

    def test_q3_no_anchor_carries_the_2010_tightening(self) -> None:
        """Quality data extracted but not used scores N.

        This clause is the one that makes collecting scores and ignoring them
        *worse* than not collecting them (``07-quality-assessment.md:151``).
        Dropping it silently converts an N into an N-or-P judgement call.
        """
        assert "not used" in DARE_QUESTIONS[2].anchors["0.0"].lower()

    def test_q4_yes_anchor_is_a_traceability_check(self) -> None:
        assert "trace" in DARE_QUESTIONS[3].anchors["1.0"].lower()


class TestSynthesisQuestion:
    """The fifth criterion SE dropped, restorable as an opt-in."""

    def test_is_not_one_of_the_four(self) -> None:
        assert DARE_SYNTHESIS_QUESTION not in DARE_QUESTIONS

    def test_orders_after_the_core_four(self) -> None:
        assert DARE_SYNTHESIS_QUESTION.order == 5

    def test_has_three_anchors(self) -> None:
        assert set(DARE_SYNTHESIS_QUESTION.anchors) == {"1.0", "0.5", "0.0"}


# ---------------------------------------------------------------------------
# Checklist payloads
# ---------------------------------------------------------------------------


class TestDareItemPayloads:
    """Payloads are shaped for quality_assessment_service.upsert_checklist."""

    def test_default_excludes_the_synthesis_question(self) -> None:
        """SE's four-question DARE is the default; the fifth is opt-in."""
        assert len(dare_item_payloads()) == 4

    def test_include_synthesis_adds_the_fifth(self) -> None:
        assert len(dare_item_payloads(include_synthesis=True)) == 5

    def test_every_item_scores_yes_partial_no(self) -> None:
        for payload in dare_item_payloads(include_synthesis=True):
            assert payload["scoring_method"] == ChecklistScoringMethod.YES_PARTIAL_NO.value

    def test_every_item_is_equally_weighted(self) -> None:
        """DARE totals out of 4 — an unequal weight would silently rescale it."""
        for payload in dare_item_payloads():
            assert payload["weight"] == 1.0

    def test_payloads_carry_anchors(self) -> None:
        for payload in dare_item_payloads():
            assert set(payload["anchors"]) == {"1.0", "0.5", "0.0"}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


class TestYesPartialNoScores:
    """Only the three DARE values are admissible."""

    def test_allowed_values(self) -> None:
        assert YES_PARTIAL_NO_SCORES == (0.0, 0.5, 1.0)

    @pytest.mark.parametrize("value", [0.0, 0.5, 1.0])
    def test_valid_score_with_justification_passes(self, value: float) -> None:
        validate_yes_partial_no(value, "Searched five digital libraries plus snowballing.")

    @pytest.mark.parametrize("value", [0.25, 0.75, 1.5, -1.0, 2.0])
    def test_off_scale_value_is_rejected(self, value: float) -> None:
        with pytest.raises(ValueError, match="0.0, 0.5 or 1.0"):
            validate_yes_partial_no(value, "A justification.")

    def test_missing_justification_is_rejected(self) -> None:
        """04-tertiary.md:202 — justification per answer is mandatory."""
        with pytest.raises(ValueError, match="justification"):
            validate_yes_partial_no(1.0, None)

    def test_whitespace_only_justification_is_rejected(self) -> None:
        """Whitespace satisfies "not null" while carrying no reasoning."""
        with pytest.raises(ValueError, match="justification"):
            validate_yes_partial_no(1.0, "   \n\t ")


class TestDareTotal:
    """DARE reports a total out of N, not the weighted average stored upstream."""

    def test_converts_average_to_total(self) -> None:
        """compute_aggregate_score returns a 0-1 weighted mean; DARE wants 0-4."""
        assert dare_total(0.75, 4) == 3.0

    def test_full_marks(self) -> None:
        assert dare_total(1.0, 4) == 4.0

    def test_zero(self) -> None:
        assert dare_total(0.0, 4) == 0.0

    def test_five_item_variant_totals_out_of_five(self) -> None:
        assert dare_total(0.6, 5) == 3.0

    def test_zero_items_is_zero_not_a_division_error(self) -> None:
        assert dare_total(0.0, 0) == 0.0


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------


class TestSeedDareChecklist:
    """Seeding gives a tertiary study the instrument its type requires."""

    @pytest.mark.asyncio
    async def test_creates_checklist_named_dare(self, db_session) -> None:
        checklist = await seed_dare_checklist(1, db_session)
        assert checklist.name == DARE_CHECKLIST_NAME

    @pytest.mark.asyncio
    async def test_creates_four_items(self, db_session) -> None:
        checklist = await seed_dare_checklist(1, db_session)
        assert len(checklist.items) == 4

    @pytest.mark.asyncio
    async def test_persists_anchors(self, db_session) -> None:
        """Anchors must survive the round trip or the UI cannot show them."""
        await seed_dare_checklist(1, db_session)

        result = await db_session.execute(
            select(QualityAssessmentChecklist)
            .options(selectinload(QualityAssessmentChecklist.items))
            .where(QualityAssessmentChecklist.study_id == 1)
        )
        stored = result.scalar_one()
        first = sorted(stored.items, key=lambda i: i.order)[0]
        assert set(first.anchors) == {"1.0", "0.5", "0.0"}

    @pytest.mark.asyncio
    async def test_include_synthesis_seeds_five_items(self, db_session) -> None:
        checklist = await seed_dare_checklist(1, db_session, include_synthesis=True)
        assert len(checklist.items) == 5

    @pytest.mark.asyncio
    async def test_is_idempotent(self, db_session) -> None:
        """Re-seeding must not duplicate items or trip the unique study_id.

        ``quality_assessment_checklist.study_id`` is unique, so a second
        unguarded insert raises rather than no-opping.
        """
        await seed_dare_checklist(1, db_session)
        checklist = await seed_dare_checklist(1, db_session)
        assert len(checklist.items) == 4

    @pytest.mark.asyncio
    async def test_does_not_overwrite_an_existing_non_dare_checklist(self, db_session) -> None:
        """A study that already defined its own instrument keeps it.

        Silently replacing a reviewer's checklist would discard their work and,
        worse, invalidate scores already recorded against its items.
        """
        existing = QualityAssessmentChecklist(study_id=7, name="Dyba & Dingsoyr 11-item")
        db_session.add(existing)
        await db_session.commit()

        checklist = await seed_dare_checklist(7, db_session)
        assert checklist.name == "Dyba & Dingsoyr 11-item"
        assert checklist.items == []
