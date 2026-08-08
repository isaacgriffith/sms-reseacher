"""Characterisation tests for the shared screening pipeline.

These pin the behaviour of the helpers that both the search job and the
re-screen job compose, so the extraction out of ``search_job.py`` (TREF4,
plan.md C2) is provably behaviour-preserving rather than merely asserted to be.

They are deliberately written against ``backend.jobs.screening_pipeline``
before that module exists: the RED state is the module import failing, and the
GREEN state is the same assertions passing against the extracted module without
a single expectation being edited.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scalar_result(value: object) -> MagicMock:
    """Return a mock mimicking an ``AsyncSession.execute()`` result.

    Args:
        value: The value returned by ``scalar_one_or_none()``.

    Returns:
        A MagicMock with ``scalar_one_or_none`` and ``scalars()`` wired.

    """
    r = MagicMock()
    r.scalar_one_or_none.return_value = value
    r.scalars.return_value.all.return_value = [] if value is None else [value]
    r.scalars.return_value.first.return_value = value
    return r


def _criteria_result(*criteria: object) -> MagicMock:
    """Return a mock result whose ``scalars().all()`` yields the given criteria."""
    r = MagicMock()
    r.scalars.return_value.all.return_value = list(criteria)
    return r


def _criterion(criterion_id: int, description: str) -> MagicMock:
    """Return a mock criterion row carrying an id and a description."""
    c = MagicMock()
    c.id = criterion_id
    c.description = description
    return c


# ---------------------------------------------------------------------------
# _load_criteria
# ---------------------------------------------------------------------------


async def test_load_criteria_returns_empty_lists_when_study_has_none():
    """Both lists come back empty when the study defines no criteria.

    A study with no criteria must yield two empty lists rather than None, since
    the screener receives them positionally and would otherwise be handed a
    non-iterable.
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_criteria_result())

    from backend.jobs.screening_pipeline import _load_criteria

    inclusion, exclusion = await _load_criteria(db, study_id=1)

    assert inclusion == []
    assert exclusion == []


async def test_load_criteria_projects_rows_to_id_and_description_dicts():
    """Criteria are projected to ``{id, description}`` dicts, inclusion first.

    The screener agent consumes plain dicts, not ORM rows. Ordering matters:
    the first query is inclusion and the second is exclusion, so swapping them
    would silently invert every screening decision.
    """
    db = AsyncMock()
    db.execute = AsyncMock(
        side_effect=[
            _criteria_result(_criterion(1, "Primary studies only")),
            _criteria_result(_criterion(2, "Exclude non-English")),
        ]
    )

    from backend.jobs.screening_pipeline import _load_criteria

    inclusion, exclusion = await _load_criteria(db, study_id=1)

    assert inclusion == [{"id": 1, "description": "Primary studies only"}]
    assert exclusion == [{"id": 2, "description": "Exclude non-English"}]


async def test_load_criteria_preserves_query_order_for_multiple_criteria():
    """Multiple criteria keep the order the query returned them in.

    The queries order by ``order_index``, which is the order the reviewer
    authored. Re-sorting or de-duplicating here would detach the criterion
    numbering shown in the UI from the numbering the screener reasons about.
    """
    db = AsyncMock()
    db.execute = AsyncMock(
        side_effect=[
            _criteria_result(_criterion(1, "First"), _criterion(2, "Second")),
            _criteria_result(),
        ]
    )

    from backend.jobs.screening_pipeline import _load_criteria

    inclusion, _ = await _load_criteria(db, study_id=1)

    assert [c["description"] for c in inclusion] == ["First", "Second"]


# ---------------------------------------------------------------------------
# _process_single_candidate
# ---------------------------------------------------------------------------


def _dedup(*, is_duplicate: bool, candidate_id: int | None = None) -> MagicMock:
    """Return a mock dedup verdict."""
    d = MagicMock()
    d.is_duplicate = is_duplicate
    d.candidate_id = candidate_id
    return d


async def test_process_single_candidate_reports_duplicate_when_already_a_candidate():
    """An already-seen paper returns ``(None, True)`` and creates nothing.

    The True flag is what makes the caller ``continue``. Were it False the loop
    would fall through and hand a None candidate to the screening pass — the
    exact pairing that let a cosmic-ray mutant reject papers silently
    (docs/feature-gaps.md).
    """
    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(MagicMock()))
    db.add = MagicMock()
    db.flush = AsyncMock()

    paper = MagicMock(id=7)

    with (
        patch(
            "backend.jobs.screening_pipeline._upsert_paper",
            new=AsyncMock(return_value=paper),
        ),
        patch(
            "backend.services.dedup.check_duplicate",
            new=AsyncMock(return_value=_dedup(is_duplicate=False)),
        ),
    ):
        from backend.jobs.screening_pipeline import _process_single_candidate

        candidate, is_duplicate = await _process_single_candidate(
            db, {"doi": "10.1/x", "title": "Title"}, 1, 1, "initial"
        )

    assert candidate is None
    assert is_duplicate is True
    db.add.assert_not_called()


async def test_process_single_candidate_creates_pending_candidate_for_novel_paper():
    """A novel paper yields a PENDING candidate with no duplicate link.

    PENDING is what makes the candidate eligible for screening; a candidate
    created in any other state would never be judged.
    """
    from db.models import Paper
    from db.models.candidate import CandidatePaperStatus

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.flush = AsyncMock()

    paper = Paper(title="Novel", abstract="An abstract", doi="10.1/new")

    with (
        patch(
            "backend.jobs.screening_pipeline._upsert_paper",
            new=AsyncMock(return_value=paper),
        ),
        patch(
            "backend.services.dedup.check_duplicate",
            new=AsyncMock(return_value=_dedup(is_duplicate=False)),
        ),
    ):
        from backend.jobs.screening_pipeline import _process_single_candidate

        candidate, is_duplicate = await _process_single_candidate(
            db, {"doi": "10.1/new", "title": "Novel"}, 3, 9, "initial"
        )

    assert is_duplicate is False
    assert candidate is not None
    added = db.add.call_args[0][0]
    assert added.current_status is CandidatePaperStatus.PENDING
    assert added.duplicate_of_id is None
    assert added.study_id == 3
    assert added.search_execution_id == 9
    assert added.phase_tag == "initial"


async def test_process_single_candidate_persists_the_citation_intent():
    """A snowballed reference's citation intent survives into the candidate row.

    Regression test for G55. Semantic Scholar returns why a paper cites another
    (methodology / background / result), the MCP snowball tool already requests
    and maps that field, and the pipeline then dropped it on the floor. Wohlin's
    backward-snowballing step 4 is to examine the reference's place in the citing
    text — "the step that distinguishes the method from mechanical
    reference-following" — so this is the one signal that makes snowball
    screening more than title matching. See docs/methodology/06-search-and-selection.md.
    """
    from db.models import Paper

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.flush = AsyncMock()

    paper = Paper(title="Cited work", abstract="An abstract", doi="10.1/cited")

    with (
        patch(
            "backend.jobs.screening_pipeline._upsert_paper",
            new=AsyncMock(return_value=paper),
        ),
        patch(
            "backend.services.dedup.check_duplicate",
            new=AsyncMock(return_value=_dedup(is_duplicate=False)),
        ),
    ):
        from backend.jobs.screening_pipeline import _process_single_candidate

        await _process_single_candidate(
            db,
            {"doi": "10.1/cited", "title": "Cited work", "intent": "methodology"},
            3,
            9,
            "snowball",
        )

    added = db.add.call_args[0][0]
    assert added.citation_intent == "methodology"


async def test_process_single_candidate_tolerates_absent_citation_intent():
    """Database-search results carry no intent, and must not be rejected for it.

    Only snowballed references have a citing context; a paper found by query has
    no citation to examine, so the column stays null rather than being faked.
    """
    from db.models import Paper

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.flush = AsyncMock()

    paper = Paper(title="From search", abstract="An abstract", doi="10.1/search")

    with (
        patch(
            "backend.jobs.screening_pipeline._upsert_paper",
            new=AsyncMock(return_value=paper),
        ),
        patch(
            "backend.services.dedup.check_duplicate",
            new=AsyncMock(return_value=_dedup(is_duplicate=False)),
        ),
    ):
        from backend.jobs.screening_pipeline import _process_single_candidate

        await _process_single_candidate(
            db, {"doi": "10.1/search", "title": "From search"}, 3, 9, "initial"
        )

    added = db.add.call_args[0][0]
    assert added.citation_intent is None


async def test_process_single_candidate_composes_the_paper_it_refers_to():
    """The new candidate carries the Paper itself, not just its id.

    The screening pass reads ``candidate.title`` and ``.abstract``, which
    delegate to the composed paper. Setting only ``paper_id`` would leave the
    relationship unloaded, and a lazy load on a freshly flushed row raises
    MissingGreenlet under an async session — which the screening pass used to
    swallow as a rejection.
    """
    from db.models import Paper

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.flush = AsyncMock()

    paper = Paper(title="Composed", abstract="Delegated abstract", doi="10.1/c")

    with (
        patch(
            "backend.jobs.screening_pipeline._upsert_paper",
            new=AsyncMock(return_value=paper),
        ),
        patch(
            "backend.services.dedup.check_duplicate",
            new=AsyncMock(return_value=_dedup(is_duplicate=False)),
        ),
    ):
        from backend.jobs.screening_pipeline import _process_single_candidate

        candidate, _ = await _process_single_candidate(
            db, {"doi": "10.1/c", "title": "Composed"}, 1, 1, "initial"
        )

    assert candidate.paper is paper
    assert candidate.title == "Composed"
    assert candidate.abstract == "Delegated abstract"


async def test_process_single_candidate_links_duplicate_to_its_original():
    """A dedup hit yields a DUPLICATE candidate carrying ``duplicate_of_id``.

    The link is the whole point of recording the duplicate rather than dropping
    it: the PRISMA funnel counts duplicates, and a reviewer must be able to
    reach the candidate this one duplicates.
    """
    from db.models import Paper
    from db.models.candidate import CandidatePaperStatus

    db = AsyncMock()
    db.execute = AsyncMock(return_value=_scalar_result(None))
    db.add = MagicMock()
    db.flush = AsyncMock()

    paper = Paper(title="Dup", doi="10.1/dup")

    with (
        patch(
            "backend.jobs.screening_pipeline._upsert_paper",
            new=AsyncMock(return_value=paper),
        ),
        patch(
            "backend.services.dedup.check_duplicate",
            new=AsyncMock(return_value=_dedup(is_duplicate=True, candidate_id=3)),
        ),
    ):
        from backend.jobs.screening_pipeline import _process_single_candidate

        candidate, is_duplicate = await _process_single_candidate(
            db, {"doi": "10.1/dup", "title": "Dup"}, 1, 1, "initial"
        )

    assert is_duplicate is True
    assert candidate is not None
    added = db.add.call_args[0][0]
    assert added.current_status is CandidatePaperStatus.DUPLICATE
    assert added.duplicate_of_id == 3


# ---------------------------------------------------------------------------
# _run_screening_pass
# ---------------------------------------------------------------------------


async def test_run_screening_pass_raises_when_the_provider_fails():
    """A provider fault raises instead of returning a rejection.

    This is the whole of C3. A timeout is not a judgement, and FR-024 requires
    a run to distinguish papers it assessed from papers it never reached — a
    distinction that cannot exist while a fault is written to the database as a
    legitimate reject.
    """
    from backend.jobs.screening_pipeline import ScreeningUnavailableError, _run_screening_pass

    screener = MagicMock()
    screener.run = AsyncMock(side_effect=RuntimeError("provider timeout"))

    paper = MagicMock(title="Title", abstract="Abstract")

    with pytest.raises(ScreeningUnavailableError):
        await _run_screening_pass(screener, paper, [], [])


async def test_run_screening_pass_chains_the_original_provider_error():
    """The raised error keeps the provider's own exception as its cause.

    Operators need the underlying fault — a rate limit reads very differently
    from a bad API key — and the wrapper exists to classify, not to discard.
    """
    from backend.jobs.screening_pipeline import ScreeningUnavailableError, _run_screening_pass

    original = RuntimeError("429 rate limited")
    screener = MagicMock()
    screener.run = AsyncMock(side_effect=original)

    paper = MagicMock(title="Title", abstract="Abstract")

    with pytest.raises(ScreeningUnavailableError) as excinfo:
        await _run_screening_pass(screener, paper, [], [])

    assert excinfo.value.__cause__ is original


async def test_run_screening_pass_screens_a_candidate_through_its_composed_paper():
    """A CandidatePaper is screenable because it delegates to its paper.

    The regression this pins is the reason C3 mattered so much: both callers
    pass a CandidatePaper, which carried no bibliography, so every call raised
    AttributeError and was swallowed into a rejection. The screener was never
    reached for any paper in any search.
    """
    from db.models import Paper
    from db.models.candidate import CandidatePaper, CandidatePaperStatus

    from backend.jobs.screening_pipeline import _run_screening_pass

    candidate = CandidatePaper(
        study_id=1,
        paper=Paper(title="Screenable", abstract="Real abstract"),
        search_execution_id=1,
        phase_tag="initial",
        current_status=CandidatePaperStatus.PENDING,
    )

    screener = MagicMock()
    screener.run = AsyncMock(return_value="accept this paper")

    decision, _ = await _run_screening_pass(screener, candidate, [], [])

    assert decision == "accepted"
    assert screener.run.await_args.kwargs["title"] == "Screenable"
    assert screener.run.await_args.kwargs["abstract"] == "Real abstract"


async def test_run_screening_pass_lets_a_missing_candidate_surface_as_itself():
    """A missing candidate stays an AttributeError, not an outage.

    ``None`` reaching here is a programming error, and relabelling it as a
    provider failure would repeat the mistake C3 fixes at one remove: a bug
    filed under the wrong cause is a bug nobody looks for.
    """
    from backend.jobs.screening_pipeline import ScreeningUnavailableError, _run_screening_pass

    screener = MagicMock()
    screener.run = AsyncMock()

    with pytest.raises(AttributeError) as excinfo:
        await _run_screening_pass(screener, None, [], [])

    assert not isinstance(excinfo.value, ScreeningUnavailableError)
    screener.run.assert_not_awaited()


# ---------------------------------------------------------------------------
# _record_paper_decision
# ---------------------------------------------------------------------------


async def test_record_paper_decision_writes_decision_and_advances_status():
    """The decision is persisted and the candidate's status follows it.

    Both halves matter: the PaperDecision row is the audit trail and the
    ``current_status`` is what the screening queue filters on. Writing one
    without the other leaves a judged paper sitting in the pending queue.
    """
    from db.models.candidate import CandidatePaperStatus, PaperDecisionType

    candidate = MagicMock(id=11)
    candidate.current_status = CandidatePaperStatus.PENDING

    db = AsyncMock()
    db.add = MagicMock()

    from backend.jobs.screening_pipeline import _record_paper_decision

    await _record_paper_decision(db, candidate, reviewer_id=5, decision="accepted", reasons=[])

    assert candidate.current_status is CandidatePaperStatus.ACCEPTED
    decision = db.add.call_args[0][0]
    assert decision.candidate_paper_id == 11
    assert decision.reviewer_id == 5
    assert decision.decision is PaperDecisionType.ACCEPTED


async def test_record_paper_decision_stores_reasons_verbatim():
    """Screening reasons are stored as given, not summarised or filtered.

    The reasons are the evidence for an automated judgement; a reviewer
    auditing the round needs exactly what the screener returned.
    """
    reasons = [{"criterion_id": 1, "criterion_type": "inclusion", "text": "Empirical study"}]

    candidate = MagicMock(id=11)
    db = AsyncMock()
    db.add = MagicMock()

    from backend.jobs.screening_pipeline import _record_paper_decision

    await _record_paper_decision(db, candidate, reviewer_id=5, decision="rejected", reasons=reasons)

    assert db.add.call_args[0][0].reasons == reasons


async def test_record_paper_decision_marks_automated_decisions_as_not_overrides():
    """A pipeline decision is never an override.

    ``is_override`` distinguishes a reviewer correcting themselves from two
    reviewers disagreeing (FR-022). An automated first pass is neither, so it
    must record False rather than leaving the column to a default.
    """
    candidate = MagicMock(id=11)
    db = AsyncMock()
    db.add = MagicMock()

    from backend.jobs.screening_pipeline import _record_paper_decision

    await _record_paper_decision(db, candidate, reviewer_id=5, decision="duplicate", reasons=[])

    assert db.add.call_args[0][0].is_override is False
