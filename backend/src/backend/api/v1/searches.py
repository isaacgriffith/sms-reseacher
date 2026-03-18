"""Search execution endpoints: trigger full search and retrieve executions."""

from datetime import UTC, datetime

from db.models import Study
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

    # Find the active search string
    ss_result = await db.execute(
        select(SearchString).where(
            SearchString.study_id == study_id,
            SearchString.is_active.is_(True),
        )
    )
    ss = ss_result.scalars().first()
    if ss is None:
        # Fall back to the latest version
        ss_result2 = await db.execute(
            select(SearchString)
            .where(SearchString.study_id == study_id)
            .order_by(SearchString.version.desc())
        )
        ss = ss_result2.scalars().first()

    if ss is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No search string found for this study. Create one first.",
        )

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
