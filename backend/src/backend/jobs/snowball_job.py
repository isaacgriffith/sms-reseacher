"""ARQ background job for snowball sampling.

Split out of ``search_job.py``: snowballing is a distinct discovery strategy
that walks citation edges from papers already accepted, rather than querying a
database with a search string, and keeping the two together pushed
``search_job.py`` over the 800-line maximum that plan.md C2 exists to hold it
under.

It shares the screening pipeline and the failure handling with the full search
rather than restating either — a fault must fail the run here for exactly the
reasons it does there.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from backend.core.config import get_logger
from backend.jobs.screening_pipeline import (  # noqa: PLC2701 — same package
    _build_screener_with_context,
    _load_criteria,
    _process_single_candidate,
    _record_paper_decision,
    _run_screening_pass,
)
from backend.jobs.search_job import (  # noqa: PLC2701 — same package
    _fail_search_run,
    _get_or_create_ai_reviewer,
    _get_or_create_metrics,
)

logger = get_logger(__name__)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


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
    from db.models.jobs import JobStatus
    from db.models.search_exec import SearchExecution, SearchExecutionStatus
    from sqlalchemy import select

    from backend.core.database import _session_maker  # noqa: PLC2701

    async with _session_maker() as db:
        study_result = await db.execute(select(Study).where(Study.id == study_id))
        study = study_result.scalar_one_or_none()
        if study is None:
            return {"error": "study not found"}

        search_exec = (
            await db.execute(
                select(SearchExecution).where(SearchExecution.id == search_execution_id)
            )
        ).scalar_one_or_none()
        bg_job = await _find_snowball_job(db, study_id)
        bg_job_id = bg_job.id if bg_job else None

        now = datetime.now(UTC)
        if search_exec is not None:
            search_exec.status = SearchExecutionStatus.RUNNING
            search_exec.started_at = now
        if bg_job is not None:
            bg_job.status = JobStatus.RUNNING
            bg_job.started_at = now
        await db.commit()

        try:
            return await _execute_snowball_sweep(
                db,
                study,
                phase_tag,
                paper_dois,
                direction,
                search_execution_id,
                search_exec,
                bg_job,
            )
        except Exception as exc:
            await _fail_search_run(db, search_execution_id, bg_job_id, exc)
            raise


async def _find_snowball_job(db: AsyncSession, study_id: int) -> Any:
    """Return the study's in-flight snowball job, or None.

    Snowballing has no enqueue site yet, so a run frequently has no job row at
    all. Returning None rather than failing keeps the status reporting optional
    without making the caller special-case it.
    """
    from db.models.jobs import BackgroundJob, JobStatus, JobType
    from sqlalchemy import select

    result = await db.execute(
        select(BackgroundJob).where(
            BackgroundJob.study_id == study_id,
            BackgroundJob.job_type == JobType.SNOWBALL_SEARCH,
            BackgroundJob.status.in_([JobStatus.QUEUED, JobStatus.RUNNING]),
        )
    )
    return result.scalars().first()


async def _execute_snowball_sweep(
    db: AsyncSession,
    study: Any,
    phase_tag: str,
    paper_dois: list[str],
    direction: str,
    search_execution_id: int,
    search_exec: Any,
    bg_job: Any,
) -> dict:
    """Snowball from each seed DOI, screening every paper it turns up.

    Split out for the same reason as :func:`_execute_search_sweep`: the caller
    owns one ``try``, so anything raised in here leaves the execution and job
    marked failed rather than sitting at ``running`` for ever.

    Args:
        db: Active async session, already carrying the run's started state.
        study: The :class:`Study` being snowballed, for its threshold.
        phase_tag: Phase label, e.g. ``"backward-search-1"``.
        paper_dois: Seed DOIs to snowball from.
        direction: ``"backward"`` (references) or ``"forward"`` (citations).
        search_execution_id: The execution to record results against.
        search_exec: The :class:`SearchExecution` row, already RUNNING.
        bg_job: The :class:`BackgroundJob` row, or None if the run has none.

    Returns:
        Summary dict with counts and whether the threshold stopped it early.

    """
    from db.models.jobs import JobStatus
    from db.models.search_exec import SearchExecutionStatus

    from backend.core.config import get_settings

    study_id = study.id
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

    now = datetime.now(UTC)
    if search_exec is not None:
        search_exec.status = SearchExecutionStatus.COMPLETED
        search_exec.completed_at = now
    if bg_job is not None:
        bg_job.status = JobStatus.COMPLETED
        bg_job.progress_pct = 100
        bg_job.completed_at = now
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
