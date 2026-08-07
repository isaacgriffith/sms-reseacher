"""ARQ background jobs for test-search execution."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from backend.core.config import get_logger

# The screening pipeline lives in its own module (plan.md C2) because the
# re-screen job is its second consumer. Imported rather than copied so that a
# fix to how a paper is judged applies to every job that judges one.
from backend.jobs.screening_pipeline import (  # noqa: PLC2701 — same package
    _build_screener_with_context,
    _load_criteria,
    _process_single_candidate,
    _record_paper_decision,
    _run_screening_pass,
)

logger = get_logger(__name__)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

_HTTP_OK = 200
_HTTP_MULTIPLE_CHOICES = 300


class TestSearchUnavailableError(RuntimeError):
    """Raised when researcher-mcp cannot serve a test search.

    Distinguishes a search-service failure from a search that legitimately
    returned no results, so a pilot run is never recorded against fabricated
    counts.
    """


# ---------------------------------------------------------------------------
# run_test_search
# ---------------------------------------------------------------------------


async def run_test_search(
    ctx: dict[str, Any],
    study_id: int,
    search_string_id: int,
    databases: list[str],
) -> dict[str, Any]:
    """Run a test search and compute recall against the seed paper test set.

    Calls researcher-mcp ``search_papers`` with the search string against the
    requested databases, counts how many seed papers are in the result set,
    computes recall, and creates a :class:`SearchStringIteration` record.

    Args:
        ctx: ARQ context dict (contains Redis connection etc.).
        study_id: The study whose seeds are used as the test set.
        search_string_id: The search string to evaluate.
        databases: Database identifiers to query (e.g. ``["acm", "ieee"]``).

    Returns:
        A dict with ``{iteration_id, result_set_count, test_set_recall}``.

    """
    from db.models.jobs import BackgroundJob, JobStatus, JobType
    from db.models.search import SearchString, SearchStringIteration
    from db.models.seeds import SeedPaper
    from sqlalchemy import select

    from backend.core.database import _session_maker  # noqa: PLC2701 — internal

    arq_job_id: str = ctx.get("job_id", f"test-search-{search_string_id}")

    async with _session_maker() as db:
        # FR-027a: create BackgroundJob record at start with status=running
        bg_job = BackgroundJob(
            id=arq_job_id,
            study_id=study_id,
            job_type=JobType.TEST_SEARCH,
            status=JobStatus.RUNNING,
            started_at=datetime.now(UTC),
        )
        db.add(bg_job)
        await db.commit()

        try:
            ss_result = await db.execute(
                select(SearchString).where(SearchString.id == search_string_id)
            )
            ss = ss_result.scalar_one_or_none()
            if ss is None:
                logger.error(
                    "run_test_search: search_string not found", search_string_id=search_string_id
                )
                bg_job.status = JobStatus.FAILED
                bg_job.error_message = "search_string not found"
                bg_job.completed_at = datetime.now(UTC)
                await db.commit()
                return {"error": "search_string not found"}

            seeds_result = await db.execute(select(SeedPaper).where(SeedPaper.study_id == study_id))
            seed_papers = list(seeds_result.scalars().all())

            result_dois, result_count = await _fetch_test_search_results(ss.string_text, databases)
            seed_dois = await _collect_seed_dois(db, seed_papers)
            recall = len(seed_dois & result_dois) / len(seed_dois) if seed_dois else 0.0

            next_iter_num = await _next_iteration_number(db, search_string_id)
            iteration = SearchStringIteration(
                search_string_id=search_string_id,
                iteration_number=next_iter_num,
                result_set_count=result_count,
                test_set_recall=recall,
            )
            db.add(iteration)

            # Mark BackgroundJob as completed
            bg_job.status = JobStatus.COMPLETED
            bg_job.progress_pct = 100
            bg_job.completed_at = datetime.now(UTC)
            bg_job.progress_detail = {
                "result_set_count": result_count,
                "test_set_recall": recall,
            }
            await db.commit()

            logger.info(
                "run_test_search: completed",
                study_id=study_id,
                search_string_id=search_string_id,
                result_count=result_count,
                recall=recall,
                iteration_id=iteration.id,
            )
            return {
                "iteration_id": iteration.id,
                "result_set_count": result_count,
                "test_set_recall": recall,
            }

        except Exception as exc:
            logger.error("run_test_search: failed", error=str(exc))
            bg_job.status = JobStatus.FAILED
            bg_job.error_message = str(exc)
            bg_job.completed_at = datetime.now(UTC)
            await db.commit()
            raise


async def _fetch_test_search_results(query: str, databases: list[str]) -> tuple[set[str], int]:
    """Call researcher-mcp search_papers and return (doi_set, count).

    Raises:
        TestSearchUnavailableError: If researcher-mcp is unreachable or returns
            a non-2xx status. A service failure must not be reported as a result
            set — the caller cannot otherwise distinguish "the search service is
            down" from "this search string matches nothing".

    """
    import httpx

    from backend.core.config import get_settings

    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=61.0) as client:
            resp = await client.post(
                f"{settings.researcher_mcp_url.removesuffix('/sse').removesuffix('/')}/tools/search_papers",
                json={
                    "query": query,
                    "databases": databases or ["acm", "ieee", "scopus"],
                    "max_results": 100,
                },
            )
    except Exception as exc:
        logger.warning("_fetch_test_search_results: researcher-mcp unavailable", exc=str(exc))
        raise TestSearchUnavailableError("researcher-mcp is unreachable") from exc

    if not (_HTTP_OK <= resp.status_code < _HTTP_MULTIPLE_CHOICES):
        logger.warning(
            "_fetch_test_search_results: researcher-mcp error status",
            status_code=resp.status_code,
        )
        raise TestSearchUnavailableError(f"researcher-mcp returned status {resp.status_code}")

    papers = resp.json().get("papers", [])
    dois = {p.get("doi", "").lower().strip() for p in papers if p.get("doi")}
    return dois, len(papers)


async def _collect_seed_dois(db: AsyncSession, seed_papers: list) -> set[str]:
    """Collect lowercase DOIs for all seed papers that have a DOI."""
    from db.models import Paper
    from sqlalchemy import select

    dois: set[str] = set()
    for sp in seed_papers:
        result = await db.execute(select(Paper).where(Paper.id == sp.paper_id))
        paper = result.scalar_one_or_none()
        if paper and paper.doi:
            dois.add(paper.doi.lower().strip())
    return dois


async def _next_iteration_number(db: AsyncSession, search_string_id: int) -> int:
    """Return the next sequential iteration number for a search string."""
    from db.models.search import SearchStringIteration
    from sqlalchemy import select

    existing = await db.execute(
        select(SearchStringIteration)
        .where(SearchStringIteration.search_string_id == search_string_id)
        .order_by(SearchStringIteration.iteration_number.desc())
    )
    latest = existing.scalars().first()
    return (latest.iteration_number**1) if latest else 1


# ---------------------------------------------------------------------------
# run_full_search helpers (TREF2)
# ---------------------------------------------------------------------------


async def _fetch_database_results(mcp_base_url: str, db_name: str, query_text: str) -> list[dict]:
    """Query researcher-mcp for papers from a single database."""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{mcp_base_url}/tools/search_papers",
                json={"query": query_text, "databases": [db_name], "max_results": 200},
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("results", data.get("papers", []))
    except Exception as exc:
        logger.warning("_fetch_database_results: mcp error", db_name=db_name, exc=str(exc))
    return []


async def _fail_search_run(
    db: AsyncSession, search_execution_id: int, bg_job_id: str | None, exc: Exception
) -> None:
    """Roll back partial work and record the failure on the execution and job.

    Without this a fault escaping ``run_full_search`` leaves the
    ``BackgroundJob`` row at ``running`` for ever, so the UI cannot tell a
    crashed search from a slow one — the same conflation of *failed* and *in
    progress* that FR-024 forbids one layer down.

    The rollback comes first and is deliberate: everything since the last
    commit is a partial sweep of one database, and half a database's results
    recorded as though the sweep completed would misstate the PRISMA counts.
    A failed run is restarted, not resumed.

    Args:
        db: The session the run was using; left usable and committed.
        search_execution_id: The execution to mark failed.
        bg_job_id: The job to mark failed, if the run had one.
        exc: The fault to record against the job.

    """
    from db.models.jobs import BackgroundJob, JobStatus
    from db.models.search_exec import SearchExecution, SearchExecutionStatus
    from sqlalchemy import select

    await db.rollback()
    now = datetime.now(UTC)

    search_exec = (
        await db.execute(select(SearchExecution).where(SearchExecution.id == search_execution_id))
    ).scalar_one_or_none()
    if search_exec is not None:
        search_exec.status = SearchExecutionStatus.FAILED
        search_exec.completed_at = now

    if bg_job_id is not None:
        bg_job = (
            await db.execute(select(BackgroundJob).where(BackgroundJob.id == bg_job_id))
        ).scalar_one_or_none()
        if bg_job is not None:
            bg_job.status = JobStatus.FAILED
            bg_job.error_message = str(exc)
            bg_job.completed_at = now

    await db.commit()
    logger.error(
        "run_full_search: failed",
        search_execution_id=search_execution_id,
        job_id=bg_job_id,
        error=str(exc),
    )


async def _finalize_search_metrics(
    db: AsyncSession,
    metrics: Any,
    search_exec: Any,
    bg_job: Any,
    total: int,
    accepted: int,
    rejected: int,
    duplicates: int,
) -> None:
    """Write final counts to metrics, close execution, and update background job."""
    from db.models.jobs import JobStatus
    from db.models.search_exec import SearchExecutionStatus

    now = datetime.now(UTC)
    metrics.total_identified = total
    metrics.accepted = accepted
    metrics.rejected = rejected
    metrics.duplicates = duplicates
    metrics.computed_at = now
    search_exec.status = SearchExecutionStatus.COMPLETED
    search_exec.completed_at = now
    if bg_job:
        bg_job.status = JobStatus.COMPLETED
        bg_job.progress_pct = 100
        bg_job.completed_at = now
        bg_job.progress_detail = {
            "phase": "complete",
            "total_identified": total,
            "accepted": accepted,
            "rejected": rejected,
            "duplicates": duplicates,
        }
    await db.commit()


# ---------------------------------------------------------------------------
# run_full_search (TREF2: orchestrates helpers)
# ---------------------------------------------------------------------------


async def run_full_search(ctx: dict, study_id: int, search_execution_id: int) -> dict:
    """Execute the full search pipeline for a study.

    Steps:
    1. Query each database via researcher-mcp ``search_papers``.
    2. Deduplicate each result against existing CandidatePapers.
    3. Create CandidatePaper records.
    4. Call ScreenerAgent for each candidate.
    5. Create PaperDecision records.
    6. Update SearchMetrics.
    7. Write progress to BackgroundJob.

    Args:
        ctx: ARQ context.
        study_id: The study being searched.
        search_execution_id: The SearchExecution to run.

    Returns:
        Summary dict with candidate counts.

    """
    from db.models.jobs import BackgroundJob, JobStatus
    from db.models.search_exec import SearchExecution, SearchExecutionStatus
    from sqlalchemy import select

    from backend.core.database import _session_maker  # noqa: PLC2701

    async with _session_maker() as db:
        exec_result = await db.execute(
            select(SearchExecution).where(SearchExecution.id == search_execution_id)
        )
        search_exec = exec_result.scalar_one_or_none()
        if search_exec is None:
            logger.error(
                "run_full_search: SearchExecution not found",
                search_execution_id=search_execution_id,
            )
            return {"error": "search_execution not found"}

        search_exec.status = SearchExecutionStatus.RUNNING
        search_exec.started_at = datetime.now(UTC)

        job_result = await db.execute(
            select(BackgroundJob).where(
                BackgroundJob.study_id == study_id,
                BackgroundJob.status == JobStatus.QUEUED,
            )
        )
        bg_job = job_result.scalars().first()
        bg_job_id = bg_job.id if bg_job else None
        if bg_job:
            bg_job.status = JobStatus.RUNNING
            bg_job.started_at = datetime.now(UTC)
        await db.commit()

        try:
            return await _execute_search_sweep(
                db, study_id, search_execution_id, search_exec, bg_job
            )
        except Exception as exc:
            await _fail_search_run(db, search_execution_id, bg_job_id, exc)
            raise


async def _execute_search_sweep(
    db: AsyncSession,
    study_id: int,
    search_execution_id: int,
    search_exec: Any,
    bg_job: Any,
) -> dict:
    """Sweep every selected database, screening each paper it returns.

    Split out of :func:`run_full_search` so that the caller can own one
    ``try``: anything raised in here means the run did not complete, and the
    job and execution rows must say so rather than sitting at ``running``.

    Args:
        db: Active async session, already carrying the run's started state.
        study_id: The study being searched.
        search_execution_id: The execution being run.
        search_exec: The :class:`SearchExecution` row, already RUNNING.
        bg_job: The :class:`BackgroundJob` row, or None if the run has none.

    Returns:
        Summary dict with candidate counts.

    """
    from db.models import Study
    from db.models.search import SearchString
    from sqlalchemy import select

    from backend.core.config import get_settings

    ss_result = await db.execute(
        select(SearchString).where(SearchString.id == search_exec.search_string_id)
    )
    ss = ss_result.scalar_one_or_none()
    if ss is None:
        logger.error("run_full_search: SearchString not found")
        return {"error": "search_string not found"}

    inclusion_criteria, exclusion_criteria = await _load_criteria(db, study_id)
    ai_reviewer = await _get_or_create_ai_reviewer(db, study_id)
    metrics = await _get_or_create_metrics(db, search_execution_id)

    settings = get_settings()
    mcp_url = settings.researcher_mcp_url.removesuffix("/sse").removesuffix("/")
    databases = search_exec.databases_queried or ["acm", "ieee", "scopus"]
    phase_tag = search_exec.phase_tag

    # T061: resolve agent context for the AI reviewer
    screener = await _build_screener_with_context(db, ai_reviewer, study_id)
    total_identified = accepted_count = rejected_count = duplicate_count = 0

    for db_name in databases:
        _update_search_progress(bg_job, db_name, databases, total_identified)
        await db.commit()

        papers = await _fetch_database_results(mcp_url, db_name, ss.string_text)
        for paper_data in papers:
            total_identified += 1
            cp, is_dup = await _process_single_candidate(
                db, paper_data, study_id, search_execution_id, phase_tag
            )
            if is_dup:
                duplicate_count += 1
                continue
            decision, reasons = await _run_screening_pass(
                screener, cp, inclusion_criteria, exclusion_criteria
            )
            await _record_paper_decision(db, cp, ai_reviewer.id, decision, reasons)
            if decision == "accepted":
                accepted_count += 1
            else:
                rejected_count += 1
            await db.flush()

    await _finalize_search_metrics(
        db,
        metrics,
        search_exec,
        bg_job,
        total_identified,
        accepted_count,
        rejected_count,
        duplicate_count,
    )

    # T065b: advance study.current_phase after search completes (mirrors pico.py pattern)
    from backend.services.phase_gate import compute_current_phase

    new_phase = await compute_current_phase(study_id, db)
    study_result2 = await db.execute(select(Study).where(Study.id == study_id))
    study_obj = study_result2.scalar_one_or_none()
    if study_obj is not None:
        study_obj.current_phase = max(study_obj.current_phase, new_phase)
        await db.commit()

    logger.info(
        "run_full_search: completed",
        study_id=study_id,
        total=total_identified,
        accepted=accepted_count,
    )
    return {
        "search_execution_id": search_execution_id,
        "total_identified": total_identified,
        "accepted": accepted_count,
        "rejected": rejected_count,
        "duplicates": duplicate_count,
    }


async def _get_or_create_ai_reviewer(db: AsyncSession, study_id: int) -> Any:
    """Load or create the AI screener reviewer for a study."""
    from db.models.study import Reviewer
    from sqlalchemy import select

    result = await db.execute(
        select(Reviewer).where(
            Reviewer.study_id == study_id,
            Reviewer.reviewer_type == "ai_agent",
        )
    )
    reviewer = result.scalars().first()
    if reviewer is None:
        reviewer = Reviewer(
            study_id=study_id,
            reviewer_type="ai_agent",
            agent_config={"agent_name": "screener"},
        )
        db.add(reviewer)
        await db.flush()
    return reviewer


async def _get_or_create_metrics(db: AsyncSession, search_execution_id: int) -> Any:
    """Load or create a SearchMetrics record for the given execution."""
    from db.models.search_exec import SearchMetrics
    from sqlalchemy import select

    result = await db.execute(
        select(SearchMetrics).where(SearchMetrics.search_execution_id == search_execution_id)
    )
    metrics = result.scalar_one_or_none()
    if metrics is None:
        metrics = SearchMetrics(search_execution_id=search_execution_id)
        db.add(metrics)
        await db.flush()
    return metrics


def _update_search_progress(
    bg_job: Any, db_name: str, databases: list[str], papers_found: int
) -> None:
    """Update BackgroundJob progress percentage and detail for the current DB."""
    if bg_job is None:
        return
    pct = int((databases.index(db_name) / len(databases)) * 80)
    bg_job.progress_pct = pct
    bg_job.progress_detail = {
        "phase": "searching",
        "current_database": db_name,
        "papers_found": papers_found,
    }


# ---------------------------------------------------------------------------
# run_snowball helpers (TREF3)
# ---------------------------------------------------------------------------


async def _fetch_snowball_papers(mcp_base_url: str, doi: str, direction: str) -> list[dict]:
    """Fetch references (backward) or citations (forward) for a DOI via researcher-mcp."""
    import httpx

    tool = "get_references" if direction == "backward" else "get_citations"
    key = "references" if direction == "backward" else "citations"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{mcp_base_url}/tools/{tool}",
                json={"doi": doi, "max_results": 50},
            )
            if resp.status_code == 200:
                return resp.json().get(key, [])
    except Exception as exc:
        logger.warning("_fetch_snowball_papers: mcp error", doi=doi, exc=str(exc))
    return []


async def _process_snowball_batch(
    db: AsyncSession,
    papers_list: list[dict],
    study_id: int,
    search_execution_id: int,
    phase_tag: str,
    inclusion_criteria: list[dict],
    exclusion_criteria: list[dict],
    screener: Any,
    ai_reviewer_id: int,
) -> tuple[int, int, int, int]:
    """Upsert, dedup, screen papers. Returns (new_non_dup, accepted, rejected, duplicates)."""
    new_non_dup = accepted = rejected = duplicates = 0
    for paper_data in papers_list:
        cp, is_dup = await _process_single_candidate(
            db, paper_data, study_id, search_execution_id, phase_tag
        )
        if is_dup:
            duplicates += 1
            continue
        new_non_dup += 1
        decision, reasons = await _run_screening_pass(
            screener, cp, inclusion_criteria, exclusion_criteria
        )
        await _record_paper_decision(db, cp, ai_reviewer_id, decision, reasons)
        if decision == "accepted":
            accepted += 1
        else:
            rejected += 1
        await db.flush()
    return new_non_dup, accepted, rejected, duplicates


def _snowball_threshold_reached(new_non_duplicate_count: int, snowball_threshold: int) -> bool:
    """Return True when new papers discovered fall below the stopping threshold."""
    return new_non_duplicate_count < snowball_threshold


# ---------------------------------------------------------------------------
# run_snowball (TREF3: orchestrates helpers)
# ---------------------------------------------------------------------------


async def run_snowball(
    ctx: dict,
    study_id: int,
    phase_tag: str,
    paper_dois: list[str],
    direction: str,
    search_execution_id: int,
) -> dict:
    """Execute iterative snowball sampling from a set of papers.

    Calls ``get_references`` (backward) or ``get_citations`` (forward) via
    the researcher-mcp, deduplicates, screens new papers, updates
    SearchMetrics, and stops if new non-duplicate count < snowball_threshold.

    Args:
        ctx: ARQ context.
        study_id: The study to snowball for.
        phase_tag: Phase label (e.g. ``"backward-search-1"``).
        paper_dois: List of DOIs of seed papers for snowball.
        direction: ``"backward"`` (references) or ``"forward"`` (citations).
        search_execution_id: The SearchExecution to record results against.

    Returns:
        Summary dict with counts.

    """
    from db.models import Study
    from sqlalchemy import select

    from backend.core.config import get_settings
    from backend.core.database import _session_maker  # noqa: PLC2701

    async with _session_maker() as db:
        study_result = await db.execute(select(Study).where(Study.id == study_id))
        study = study_result.scalar_one_or_none()
        if study is None:
            return {"error": "study not found"}

        snowball_threshold = study.snowball_threshold or 5
        inclusion_criteria, exclusion_criteria = await _load_criteria(db, study_id)
        ai_reviewer = await _get_or_create_ai_reviewer(db, study_id)

        settings = get_settings()
        mcp_url = settings.researcher_mcp_url.removesuffix("/sse").removesuffix("/")

        screener = await _build_screener_with_context(db, ai_reviewer, study_id)
        total_new = total_accepted = total_rejected = total_duplicates = 0

        for doi in paper_dois:
            papers_list = await _fetch_snowball_papers(mcp_url, doi, direction)
            new, accepted, rejected, dups = await _process_snowball_batch(
                db,
                papers_list,
                study_id,
                search_execution_id,
                phase_tag,
                inclusion_criteria,
                exclusion_criteria,
                screener,
                ai_reviewer.id,
            )
            total_new += new
            total_accepted += accepted
            total_rejected += rejected
            total_duplicates += dups

        metrics = await _get_or_create_metrics(db, search_execution_id)
        metrics.total_identified += total_new + total_duplicates
        metrics.accepted += total_accepted
        metrics.rejected += total_rejected
        metrics.duplicates += total_duplicates
        metrics.computed_at = datetime.now(UTC)
        await db.commit()

        stopped_early = _snowball_threshold_reached(total_new, snowball_threshold)
        logger.info(
            "run_snowball: completed",
            study_id=study_id,
            direction=direction,
            new=total_new,
            accepted=total_accepted,
            stopped_early=stopped_early,
        )
        return {
            "study_id": study_id,
            "direction": direction,
            "new_non_duplicate_count": total_new,
            "accepted": total_accepted,
            "rejected": total_rejected,
            "duplicates": total_duplicates,
            "stopped_early": stopped_early,
        }
