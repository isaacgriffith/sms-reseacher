"""Administrative health and job management endpoints (FR-045).

Exposes:
- ``GET /admin/health`` — real-time health probe for all system services.
- ``GET /admin/jobs`` — cross-study BackgroundJob list with status filter.
- ``POST /admin/jobs/{job_id}/retry`` — re-enqueue a failed ARQ job.

All endpoints require the calling user to have the ``admin`` role in at least
one research group. No configuration secrets are ever exposed in responses.
"""

import time
import uuid
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger, get_settings
from backend.core.database import get_db
from db.models.jobs import BackgroundJob, JobStatus, JobType
from db.models.users import GroupMembership, GroupRole

router = APIRouter(prefix="/admin", tags=["admin"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ServiceHealth(BaseModel):
    """Health status for a single system service."""

    name: str
    status: str  # "healthy" | "degraded" | "unhealthy"
    latency_ms: float | None = None
    detail: str | None = None


class HealthResponse(BaseModel):
    """System-wide health response."""

    status: str  # "healthy" | "degraded" | "unhealthy"
    services: list[ServiceHealth]
    checked_at: str


class AdminJobResponse(BaseModel):
    """Background job item for the admin jobs list."""

    id: str
    study_id: int
    job_type: str
    status: str
    error_message: str | None
    queued_at: str
    completed_at: str | None


class AdminJobPageResponse(BaseModel):
    """Paginated admin jobs list."""

    items: list[AdminJobResponse]
    total: int
    page: int
    page_size: int


class RetryJobResponse(BaseModel):
    """Response for a successful job retry."""

    new_job_id: str
    original_job_id: str


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------


async def _require_any_group_admin(
    current_user: CurrentUser, db: AsyncSession
) -> None:
    """Raise HTTP 403 if *current_user* is not a group admin in any group.

    Args:
        current_user: The authenticated user making the request.
        db: Active async database session.

    Raises:
        HTTPException: 403 if the user holds no group admin role.
    """
    result = await db.execute(
        select(GroupMembership).where(
            GroupMembership.user_id == current_user.user_id,
            GroupMembership.role == GroupRole.ADMIN,
        ).limit(1)
    )
    if result.scalars().first() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: system admin role required",
        )


# ---------------------------------------------------------------------------
# Health probe helpers
# ---------------------------------------------------------------------------


async def _probe_database(db: AsyncSession) -> ServiceHealth:
    """Probe the database with a trivial query and record latency.

    Args:
        db: Active async database session.

    Returns:
        :class:`ServiceHealth` for the ``database`` service.
    """
    start = time.monotonic()
    try:
        await db.execute(select(func.now()))
        latency = round((time.monotonic() - start) * 1000, 2)
        return ServiceHealth(name="database", status="healthy", latency_ms=latency)
    except Exception as exc:  # noqa: BLE001
        return ServiceHealth(name="database", status="unhealthy", detail=str(exc))


async def _probe_redis() -> ServiceHealth:
    """Probe Redis by pinging via the ARQ pool.

    Returns:
        :class:`ServiceHealth` for the ``redis`` service.
    """
    start = time.monotonic()
    try:
        import redis.asyncio as aioredis

        settings = get_settings()
        client = aioredis.from_url(settings.redis_url)
        await client.ping()
        await client.aclose()
        latency = round((time.monotonic() - start) * 1000, 2)
        return ServiceHealth(name="redis", status="healthy", latency_ms=latency)
    except Exception as exc:  # noqa: BLE001
        return ServiceHealth(name="redis", status="unhealthy", detail=str(exc))


async def _probe_arq_worker(db: AsyncSession) -> ServiceHealth:
    """Estimate ARQ worker health by counting active/queued jobs in the DB.

    Args:
        db: Active async database session.

    Returns:
        :class:`ServiceHealth` for the ``arq_worker`` service.
    """
    try:
        active_result = await db.execute(
            select(func.count()).select_from(BackgroundJob).where(
                BackgroundJob.status == JobStatus.RUNNING
            )
        )
        queued_result = await db.execute(
            select(func.count()).select_from(BackgroundJob).where(
                BackgroundJob.status == JobStatus.QUEUED
            )
        )
        active = active_result.scalar_one()
        queued = queued_result.scalar_one()
        return ServiceHealth(
            name="arq_worker",
            status="healthy",
            detail=f"active_jobs={active} queued_jobs={queued}",
        )
    except Exception as exc:  # noqa: BLE001
        return ServiceHealth(name="arq_worker", status="unhealthy", detail=str(exc))


async def _probe_researcher_mcp() -> ServiceHealth:
    """Probe the researcher-mcp service via an HTTP health check.

    Returns:
        :class:`ServiceHealth` for the ``researcher_mcp`` service.
    """
    start = time.monotonic()
    try:
        settings = get_settings()
        # researcher_mcp_url is the SSE endpoint; derive the base URL
        base = settings.researcher_mcp_url.replace("/sse", "").rstrip("/")
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base}/health")
        latency = round((time.monotonic() - start) * 1000, 2)
        if resp.status_code == 200:
            return ServiceHealth(name="researcher_mcp", status="healthy", latency_ms=latency)
        return ServiceHealth(
            name="researcher_mcp",
            status="degraded",
            latency_ms=latency,
            detail=f"HTTP {resp.status_code} from upstream",
        )
    except Exception as exc:  # noqa: BLE001
        return ServiceHealth(name="researcher_mcp", status="unhealthy", detail=str(exc))


def _overall_status(services: list[ServiceHealth]) -> str:
    """Derive the aggregate health status from individual service statuses.

    Args:
        services: List of per-service health objects.

    Returns:
        ``"healthy"``, ``"degraded"``, or ``"unhealthy"``.
    """
    statuses = {s.status for s in services}
    if "unhealthy" in statuses:
        return "unhealthy"
    if "degraded" in statuses:
        return "degraded"
    return "healthy"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System health dashboard",
)
async def get_health(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HealthResponse:
    """Probe all system services and return their health status.

    Probes: database, Redis, ARQ worker, and researcher-mcp. No secrets or
    configuration values are included in the response payload (FR-046).

    Args:
        current_user: Injected from the validated JWT; must be a group admin.
        db: Injected async database session.

    Returns:
        :class:`HealthResponse` with per-service status and aggregate status.

    Raises:
        HTTPException: 403 if the caller does not hold a group admin role.
    """
    await _require_any_group_admin(current_user, db)

    db_health, redis_health, arq_health, mcp_health = (
        await _probe_database(db),
        await _probe_redis(),
        await _probe_arq_worker(db),
        await _probe_researcher_mcp(),
    )
    services = [db_health, redis_health, arq_health, mcp_health]
    return HealthResponse(
        status=_overall_status(services),
        services=services,
        checked_at=datetime.now(UTC).isoformat(),
    )


@router.get(
    "/jobs",
    response_model=AdminJobPageResponse,
    summary="List background jobs across all studies",
)
async def list_admin_jobs(
    job_status: str | None = Query(None, alias="status", description="Filter by job status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AdminJobPageResponse:
    """Return a paginated cross-study list of background jobs.

    Defaults to showing all statuses when ``status`` is omitted.

    Args:
        job_status: Optional filter — one of ``queued``, ``running``,
            ``completed``, or ``failed``.
        page: 1-based page number (default: 1).
        page_size: Number of items per page (default: 50, max: 200).
        current_user: Injected from the validated JWT; must be a group admin.
        db: Injected async database session.

    Returns:
        :class:`AdminJobPageResponse` with paginated job items.

    Raises:
        HTTPException: 403 if the caller does not hold a group admin role.
        HTTPException: 422 if *job_status* is not a valid :class:`JobStatus` value.
    """
    await _require_any_group_admin(current_user, db)

    query = select(BackgroundJob)
    count_query = select(func.count()).select_from(BackgroundJob)

    if job_status is not None:
        try:
            status_enum = JobStatus(job_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status value: {job_status!r}",
            )
        query = query.where(BackgroundJob.status == status_enum)
        count_query = count_query.where(BackgroundJob.status == status_enum)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(BackgroundJob.queued_at.desc()).offset(offset).limit(page_size)
    jobs_result = await db.execute(query)
    jobs = jobs_result.scalars().all()

    items = [
        AdminJobResponse(
            id=j.id,
            study_id=j.study_id,
            job_type=j.job_type.value,
            status=j.status.value,
            error_message=j.error_message,
            queued_at=j.queued_at.isoformat(),
            completed_at=j.completed_at.isoformat() if j.completed_at else None,
        )
        for j in jobs
    ]
    return AdminJobPageResponse(items=items, total=total, page=page, page_size=page_size)


@router.post(
    "/jobs/{job_id}/retry",
    response_model=RetryJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Re-enqueue a failed background job",
)
async def retry_job(
    job_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RetryJobResponse:
    """Re-enqueue a failed background job as a new ARQ task.

    The original job record is unchanged (immutable history). A new
    ``BackgroundJob`` row is created and the ARQ task is enqueued using the
    same job type and study_id.

    Args:
        job_id: The primary key of the :class:`BackgroundJob` to retry.
        current_user: Injected from the validated JWT; must be a group admin.
        db: Injected async database session.

    Returns:
        :class:`RetryJobResponse` with the new and original job IDs.

    Raises:
        HTTPException: 403 if the caller does not hold a group admin role.
        HTTPException: 404 if the job is not found.
        HTTPException: 409 if the job is not in ``failed`` status.
    """
    await _require_any_group_admin(current_user, db)

    result = await db.execute(
        select(BackgroundJob).where(BackgroundJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if job.status != JobStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot retry job in status {job.status.value!r}; must be 'failed'",
        )

    new_job_id = str(uuid.uuid4())
    arq_function = _arq_function_for_type(job.job_type)

    try:
        from arq import create_pool
        from arq.connections import RedisSettings

        settings = get_settings()
        redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        arq_job = await redis.enqueue_job(arq_function, job.study_id, new_job_id)
        await redis.aclose()
        if arq_job:
            new_job_id = arq_job.job_id
    except Exception as exc:
        logger.warning("retry_job: redis unavailable", error=str(exc))

    new_bg_job = BackgroundJob(
        id=new_job_id,
        study_id=job.study_id,
        job_type=job.job_type,
        status=JobStatus.QUEUED,
        progress_pct=0,
    )
    db.add(new_bg_job)
    await db.commit()

    logger.info("job_retried", original_job_id=job_id, new_job_id=new_job_id)
    return RetryJobResponse(new_job_id=new_job_id, original_job_id=job_id)


def _arq_function_for_type(job_type: JobType) -> str:
    """Return the ARQ task function name for a given job type.

    Args:
        job_type: The :class:`JobType` enum value to look up.

    Returns:
        The registered ARQ task function name as a string.
    """
    _map = {
        JobType.FULL_SEARCH: "run_full_search",
        JobType.SNOWBALL_SEARCH: "run_snowball_search",
        JobType.BATCH_EXTRACTION: "run_batch_extraction",
        JobType.GENERATE_RESULTS: "run_generate_results",
        JobType.EXPORT: "run_export",
        JobType.QUALITY_EVAL: "run_quality_eval",
        JobType.VALIDITY_PREFILL: "run_validity_prefill",
        JobType.EXPERT_SEED: "run_expert_seed_suggestion",
    }
    return _map.get(job_type, "run_generic_job")
