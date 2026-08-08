"""The search pipeline really screens the papers it discovers.

Driven against a live database rather than mocks, because the defect these
cover was invisible to mocks: both callers handed ``_run_screening_pass`` a
``CandidatePaper``, which carried no ``title`` or ``abstract``, so every call
raised ``AttributeError`` into a bare ``except`` and returned
``("rejected", [])``. The screener was never invoked for any paper in any
search, and every candidate was rejected by a crash rather than a judgement.

Only the two genuinely external edges are stubbed — researcher-mcp, and the
LLM behind the ScreenerAgent. Everything between them is the real code path:
real ORM, real session, real ``run_full_search``.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from agents.services.screener import CriterionRef, ScreeningResult
from db.models import Paper, Study, StudyType
from db.models.candidate import CandidatePaper, CandidatePaperStatus, PaperDecision
from db.models.criteria import InclusionCriterion
from db.models.jobs import BackgroundJob, JobStatus, JobType
from db.models.search import SearchString
from db.models.search_exec import SearchExecution, SearchExecutionStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

_PAPERS = [
    {
        "doi": "10.1/accept",
        "title": "An Empirical Study of Test Flakiness",
        "abstract": "We report an empirical study of flaky tests in CI.",
        "year": 2024,
    },
    {
        "doi": "10.1/reject",
        "title": "A Keynote on the Future of Everything",
        "abstract": "Opinion piece with no evidence gathered.",
        "year": 2023,
    },
]


class _RecordingScreener:
    """A ScreenerAgent stand-in that records what it was asked to judge."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def run(self, **kwargs) -> ScreeningResult:
        """Accept papers whose abstract reports an empirical study."""
        self.calls.append(kwargs)
        empirical = "empirical" in (kwargs["abstract"] or "").lower()
        return ScreeningResult(
            decision="accepted" if empirical else "rejected",
            reasons=[
                CriterionRef(
                    criterion_id=1,
                    criterion_type="inclusion",
                    text="empirical" if empirical else "not empirical",
                )
            ],
        )


class _FailingScreener:
    """A ScreenerAgent stand-in whose provider is down."""

    async def run(self, **kwargs) -> ScreeningResult:
        """Fail the way a provider outage does."""
        raise RuntimeError("provider timeout")


@pytest_asyncio.fixture
async def seeded(db_engine):
    """Seed a study ready to run a full search, and yield its session maker."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as db:
        study = Study(name="Flaky tests", study_type=StudyType.SMS, topic="flaky tests")
        db.add(study)
        await db.flush()

        db.add(
            InclusionCriterion(
                study_id=study.id, description="Empirical studies only", order_index=1
            )
        )
        search_string = SearchString(
            study_id=study.id, string_text="flaky AND test", is_active=True
        )
        db.add(search_string)
        await db.flush()

        execution = SearchExecution(
            study_id=study.id,
            search_string_id=search_string.id,
            status=SearchExecutionStatus.PENDING,
            phase_tag="initial",
            databases_queried=["acm"],
        )
        db.add(execution)
        db.add(
            BackgroundJob(
                id="job-full-search",
                study_id=study.id,
                job_type=JobType.FULL_SEARCH,
                status=JobStatus.QUEUED,
            )
        )
        await db.commit()
        yield maker, study.id, execution.id


async def _run(maker, screener, study_id: int, execution_id: int):
    """Run the real ``run_full_search`` against the test database."""
    from backend.jobs.search_job import run_full_search

    with (
        patch("backend.core.database._session_maker", maker),
        patch(
            "backend.jobs.search_job._fetch_database_results",
            new=AsyncMock(return_value=_PAPERS),
        ),
        patch(
            "backend.jobs.search_job._build_screener_with_context",
            new=AsyncMock(return_value=screener),
        ),
    ):
        return await run_full_search({}, study_id, execution_id)


async def test_search_pipeline_sends_each_paper_to_the_screener(seeded):
    """Every discovered paper reaches the screener with its bibliography.

    The regression: the screener was never called at all, because the
    candidate handed to it could not produce a title or an abstract.
    """
    maker, study_id, execution_id = seeded
    screener = _RecordingScreener()

    await _run(maker, screener, study_id, execution_id)

    judged = {call["title"] for call in screener.calls}
    assert judged == {p["title"] for p in _PAPERS}
    assert all(call["abstract"] for call in screener.calls)


async def test_search_pipeline_persists_the_screener_verdict(seeded):
    """The screener's decision is what gets written, not a blanket rejection.

    Before the fix both papers were rejected regardless of content, so an
    accepted paper is the assertion that matters here.
    """
    maker, study_id, execution_id = seeded

    summary = await _run(maker, _RecordingScreener(), study_id, execution_id)

    assert summary["accepted"] == 1
    assert summary["rejected"] == 1

    async with maker() as db:
        rows = (
            (
                await db.execute(
                    select(CandidatePaper, Paper).join(Paper, CandidatePaper.paper_id == Paper.id)
                )
            )
            .tuples()
            .all()
        )
        statuses = {paper.doi: candidate.current_status for candidate, paper in rows}

    assert statuses["10.1/accept"] is CandidatePaperStatus.ACCEPTED
    assert statuses["10.1/reject"] is CandidatePaperStatus.REJECTED


async def test_search_pipeline_records_the_reasons_the_screener_gave(seeded):
    """Decisions carry the screener's reasons, not an empty list.

    The swallow returned ``("rejected", [])``, so every decision arrived
    without evidence — indistinguishable from a judgement nobody justified.
    """
    maker, study_id, execution_id = seeded

    await _run(maker, _RecordingScreener(), study_id, execution_id)

    async with maker() as db:
        decisions = (await db.execute(select(PaperDecision))).scalars().all()

    assert len(decisions) == len(_PAPERS)
    assert all(d.reasons for d in decisions)


async def test_provider_outage_fails_the_job_instead_of_rejecting_the_papers(seeded):
    """A provider outage fails the run; it does not judge the papers.

    FR-024 requires "assessed and rejected" to stay distinct from "never
    assessed". Persisting a timeout as a rejection collapses the two, and a
    job left RUNNING for ever collapses them a second way — the UI cannot tell
    a crashed run from a slow one.
    """
    from backend.jobs.screening_pipeline import ScreeningUnavailableError

    maker, study_id, execution_id = seeded

    with pytest.raises(ScreeningUnavailableError) as excinfo:
        await _run(maker, _FailingScreener(), study_id, execution_id)

    assert str(excinfo.value.__cause__) == "provider timeout"

    async with maker() as db:
        decisions = (await db.execute(select(PaperDecision))).scalars().all()
        job = (await db.execute(select(BackgroundJob))).scalars().one()
        execution = (await db.execute(select(SearchExecution))).scalars().one()

    assert decisions == []
    assert job.status is JobStatus.FAILED
    assert job.error_message
    assert job.completed_at is not None
    assert execution.status is SearchExecutionStatus.FAILED


# ---------------------------------------------------------------------------
# run_snowball
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def seeded_snowball(db_engine):
    """Seed a study ready to snowball, with a queued snowball job."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as db:
        study = Study(name="Flaky tests", study_type=StudyType.SMS, topic="flaky tests")
        db.add(study)
        await db.flush()

        search_string = SearchString(study_id=study.id, string_text="flaky", is_active=True)
        db.add(search_string)
        await db.flush()

        execution = SearchExecution(
            study_id=study.id,
            search_string_id=search_string.id,
            status=SearchExecutionStatus.PENDING,
            phase_tag="backward-search-1",
        )
        db.add(execution)
        db.add(
            BackgroundJob(
                id="job-snowball",
                study_id=study.id,
                job_type=JobType.SNOWBALL_SEARCH,
                status=JobStatus.QUEUED,
            )
        )
        await db.commit()
        yield maker, study.id, execution.id


async def _run_snowball(maker, screener, study_id: int, execution_id: int):
    """Run the real ``run_snowball`` against the test database."""
    from backend.jobs.snowball_job import run_snowball

    with (
        patch("backend.core.database._session_maker", maker),
        patch(
            "backend.jobs.snowball_job._fetch_snowball_papers",
            new=AsyncMock(return_value=_PAPERS),
        ),
        patch(
            "backend.jobs.snowball_job._build_screener_with_context",
            new=AsyncMock(return_value=screener),
        ),
    ):
        return await run_snowball(
            {}, study_id, "backward-search-1", ["10.1/seed"], "backward", execution_id
        )


async def test_snowball_completes_its_execution(seeded_snowball):
    """A finished snowball marks its execution completed.

    It previously left the execution at ``pending`` whatever happened, so
    "failed" would have been the only status the run ever set — a signal with
    nothing to contrast against.
    """
    maker, study_id, execution_id = seeded_snowball

    await _run_snowball(maker, _RecordingScreener(), study_id, execution_id)

    async with maker() as db:
        execution = (await db.execute(select(SearchExecution))).scalars().one()
        job = (await db.execute(select(BackgroundJob))).scalars().one()

    assert execution.status is SearchExecutionStatus.COMPLETED
    assert execution.completed_at is not None
    assert job.status is JobStatus.COMPLETED


async def test_snowball_screens_the_papers_it_discovers(seeded_snowball):
    """Snowballed papers are screened, not rejected by a crash.

    ``_process_snowball_batch`` shares the screening pass with the full search,
    so it shared the defect: it passed a CandidatePaper that could not produce
    a title.
    """
    maker, study_id, execution_id = seeded_snowball
    screener = _RecordingScreener()

    summary = await _run_snowball(maker, screener, study_id, execution_id)

    assert {call["title"] for call in screener.calls} == {p["title"] for p in _PAPERS}
    assert summary["accepted"] == 1
    assert summary["rejected"] == 1


async def test_snowball_provider_outage_fails_the_run(seeded_snowball):
    """A provider outage fails the snowball run rather than stranding it.

    Same contract as the full search: a job left RUNNING for ever is
    indistinguishable from a slow one, and a partial sweep committed as though
    it finished would misstate the PRISMA counts.
    """
    from backend.jobs.screening_pipeline import ScreeningUnavailableError

    maker, study_id, execution_id = seeded_snowball

    with pytest.raises(ScreeningUnavailableError):
        await _run_snowball(maker, _FailingScreener(), study_id, execution_id)

    async with maker() as db:
        decisions = (await db.execute(select(PaperDecision))).scalars().all()
        job = (await db.execute(select(BackgroundJob))).scalars().one()
        execution = (await db.execute(select(SearchExecution))).scalars().one()

    assert decisions == []
    assert job.status is JobStatus.FAILED
    assert job.error_message
    assert execution.status is SearchExecutionStatus.FAILED
