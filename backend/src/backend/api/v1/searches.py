"""Search execution endpoints: trigger full search and snowballing, list executions."""

import uuid
from datetime import UTC, datetime
from typing import Literal

from db.models import Paper, Study
from db.models.candidate import CandidatePaper, CandidatePaperStatus
from db.models.jobs import BackgroundJob, JobStatus, JobType
from db.models.search import SearchString
from db.models.search_exec import SearchExecution, SearchExecutionStatus
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db

router = APIRouter(tags=["searches"])
logger = get_logger(__name__)

#: Job types that screen a study's candidates. Two at once would interleave
#: over the same papers, so any one in flight blocks the others (FR-026).
_SCREENING_JOB_TYPES = (JobType.FULL_SEARCH, JobType.SNOWBALL_SEARCH)

#: A job in any other state has finished and blocks nothing.
_IN_FLIGHT_STATUSES = (JobStatus.QUEUED, JobStatus.RUNNING)


class StartSearchRequest(BaseModel):
    """Body for POST /studies/{study_id}/searches."""

    databases: list[str] = ["acm", "ieee", "scopus"]
    phase_tag: str = "initial-search"


class SearchExecutionResponse(BaseModel):
    """Response for a search execution."""

    id: int
    study_id: int
    search_string_id: int
    status: str
    phase_tag: str
    databases_queried: list[str] | None
    job_id: str | None


@router.post(
    "/studies/{study_id}/searches",
    response_model=dict,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger a full search execution",
)
async def start_full_search(
    study_id: int,
    body: StartSearchRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create a SearchExecution and enqueue the ``run_full_search`` ARQ job.

    Requires an active search string. Creates a BackgroundJob record and
    returns ``{job_id, search_execution_id}``.
    """
    await require_study_member(study_id, current_user, db)

    ss = await _resolve_search_string(db, study_id)

    # Create SearchExecution record
    search_exec = SearchExecution(
        study_id=study_id,
        search_string_id=ss.id,
        status=SearchExecutionStatus.PENDING,
        phase_tag=body.phase_tag,
        databases_queried=body.databases,
    )
    db.add(search_exec)
    await db.flush()

    # Enqueue ARQ job
    job_id: str | None = None
    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        from backend.core.config import get_settings

        settings = get_settings()
        redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        job = await redis.enqueue_job("run_full_search", study_id, search_exec.id)
        await redis.aclose()
        job_id = job.job_id if job else None
    except Exception as exc:
        logger.warning("start_full_search: redis unavailable: %s", exc)

    search_exec.job_id = job_id

    # Stamp search_run_at on the study for staleness tracking
    study_result = await db.execute(select(Study).where(Study.id == study_id))
    study = study_result.scalar_one_or_none()
    if study is not None:
        study.search_run_at = datetime.now(UTC)

    # Create BackgroundJob record
    import uuid

    from db.models.jobs import BackgroundJob, JobStatus, JobType

    bg_id = job_id or str(uuid.uuid4())
    bg_job = BackgroundJob(
        id=bg_id,
        study_id=study_id,
        job_type=JobType.FULL_SEARCH,
        status=JobStatus.QUEUED,
        progress_pct=0,
    )
    db.add(bg_job)
    await db.commit()

    return {"job_id": bg_id, "search_execution_id": search_exec.id}


class StartSnowballRequest(BaseModel):
    """Body for POST /studies/{study_id}/snowball."""

    direction: Literal["backward", "forward"]
    paper_dois: list[str] | None = None


async def _resolve_search_string(db: AsyncSession, study_id: int) -> SearchString:
    """Return the study's active search string, or its latest version.

    Raises:
        HTTPException: 422 if the study has no search string at all.

    """
    result = await db.execute(
        select(SearchString).where(
            SearchString.study_id == study_id,
            SearchString.is_active.is_(True),
        )
    )
    ss = result.scalars().first()
    if ss is None:
        fallback = await db.execute(
            select(SearchString)
            .where(SearchString.study_id == study_id)
            .order_by(SearchString.version.desc())
        )
        ss = fallback.scalars().first()
    if ss is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No search string found for this study. Create one first.",
        )
    return ss


async def _reject_if_screening_in_flight(db: AsyncSession, study_id: int) -> None:
    """Refuse a new automated pass while one is already running (FR-026).

    Two passes would interleave over the same candidates, each screening papers
    the other is still creating.

    Raises:
        HTTPException: 409 naming the blocking run, so the UI can say which one
            is in the way rather than only that something is.

    """
    result = await db.execute(
        select(BackgroundJob).where(
            BackgroundJob.study_id == study_id,
            BackgroundJob.job_type.in_(_SCREENING_JOB_TYPES),
            BackgroundJob.status.in_(_IN_FLIGHT_STATUSES),
        )
    )
    blocking = result.scalars().first()
    if blocking is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Another automated pass is already running for this study.",
                "blocking_job_id": blocking.id,
                "blocking_job_type": blocking.job_type.value,
            },
        )


async def _accepted_paper_dois(db: AsyncSession, study_id: int) -> list[str]:
    """Return the DOIs of the study's accepted papers, in candidate order.

    These are the seeds snowballing means by default: walk citations from the
    papers that survived screening. Papers without a DOI are skipped, since
    neither ``get_references`` nor ``get_citations`` can resolve them.
    """
    result = await db.execute(
        select(Paper.doi)
        .join(CandidatePaper, CandidatePaper.paper_id == Paper.id)
        .where(
            CandidatePaper.study_id == study_id,
            CandidatePaper.current_status == CandidatePaperStatus.ACCEPTED,
            Paper.doi.is_not(None),
        )
        .order_by(CandidatePaper.id)
    )
    # The NULL filter is in the query; the comprehension restates it because
    # `Paper.doi` is nullable in the model and mypy cannot read the WHERE.
    return [doi for doi in result.scalars().all() if doi is not None]


@router.post(
    "/studies/{study_id}/snowball",
    response_model=dict,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger a snowball sampling run",
)
async def start_snowball(
    study_id: int,
    body: StartSnowballRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create a SearchExecution and enqueue the ``run_snowball`` ARQ job.

    Walks citations from a set of seed papers — references for ``backward``,
    citations for ``forward`` — screening whatever it finds. Seeds default to
    the study's accepted papers, which is what snowballing means in a mapping
    study.

    Closes G22: the job was registered with ARQ and reachable from nothing.

    Args:
        study_id: The study to snowball for.
        body: Direction, and optionally explicit seed DOIs.
        current_user: The authenticated caller; must be a study member.
        db: Active async database session.

    Returns:
        ``{job_id, search_execution_id, seed_count}``.

    Raises:
        HTTPException: 403 if the caller is not a study member, 409 if another
            automated pass is in flight, 422 if the study has no search string
            or nothing to snowball from.

    """
    await require_study_member(study_id, current_user, db)
    await _reject_if_screening_in_flight(db, study_id)

    ss = await _resolve_search_string(db, study_id)

    paper_dois = body.paper_dois or await _accepted_paper_dois(db, study_id)
    if not paper_dois:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "No seed papers to snowball from. Accept at least one paper, "
                "or supply paper_dois explicitly."
            ),
        )

    # The tag separates candidates by how they were found. One tag for both
    # directions would merge them in the PRISMA funnel.
    phase_tag = f"{body.direction}-search"

    search_exec = SearchExecution(
        study_id=study_id,
        search_string_id=ss.id,
        status=SearchExecutionStatus.PENDING,
        phase_tag=phase_tag,
    )
    db.add(search_exec)
    await db.flush()

    job_id: str | None = None
    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        from backend.core.config import get_settings

        settings = get_settings()
        redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        job = await redis.enqueue_job(
            "run_snowball",
            study_id,
            phase_tag,
            paper_dois,
            body.direction,
            search_exec.id,
        )
        await redis.aclose()
        job_id = job.job_id if job else None
    except Exception as exc:
        logger.warning("start_snowball: redis unavailable: %s", exc)

    search_exec.job_id = job_id

    bg_id = job_id or str(uuid.uuid4())
    db.add(
        BackgroundJob(
            id=bg_id,
            study_id=study_id,
            job_type=JobType.SNOWBALL_SEARCH,
            status=JobStatus.QUEUED,
            progress_pct=0,
        )
    )
    await db.commit()

    logger.info(
        "start_snowball: enqueued",
        study_id=study_id,
        direction=body.direction,
        seed_count=len(paper_dois),
        job_id=bg_id,
    )
    return {
        "job_id": bg_id,
        "search_execution_id": search_exec.id,
        "seed_count": len(paper_dois),
    }


@router.get(
    "/studies/{study_id}/searches",
    response_model=list[SearchExecutionResponse],
    summary="List search executions for a study",
)
async def list_searches(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SearchExecutionResponse]:
    """Return all search executions for a study, newest first."""
    await require_study_member(study_id, current_user, db)

    result = await db.execute(
        select(SearchExecution)
        .where(SearchExecution.study_id == study_id)
        .order_by(SearchExecution.id.desc())
    )
    executions = result.scalars().all()
    return [
        SearchExecutionResponse(
            id=se.id,
            study_id=se.study_id,
            search_string_id=se.search_string_id,
            status=se.status.value,
            phase_tag=se.phase_tag,
            databases_queried=se.databases_queried,
            job_id=se.job_id,
        )
        for se in executions
    ]
