"""Results endpoints: domain model, classification charts, and export."""

from datetime import UTC, datetime

import arq.connections
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db

router = APIRouter(tags=["results"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Response / request schemas
# ---------------------------------------------------------------------------


class DomainModelResponse(BaseModel):
    """Serialised DomainModel record."""

    id: int
    study_id: int
    version: int
    concepts: list | None
    relationships: list | None
    svg_content: str | None
    generated_at: datetime


class ClassificationSchemeResponse(BaseModel):
    """Serialised ClassificationScheme record."""

    id: int
    study_id: int
    chart_type: str
    version: int
    chart_data: dict | None
    svg_content: str | None
    generated_at: datetime


class ResultsSummaryResponse(BaseModel):
    """Aggregated results for a study."""

    domain_model: DomainModelResponse | None
    charts: list[ClassificationSchemeResponse]


class JobEnqueueResponse(BaseModel):
    """Generic 202 response for an enqueued background job."""

    job_id: str
    study_id: int


class ExportEnqueueRequest(BaseModel):
    """Body for POST /studies/{study_id}/export."""

    format: str = "full_archive"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_latest_domain_model(study_id: int, db: AsyncSession):
    """Return the most recent DomainModel for a study, or None.

    Args:
        study_id: Study to query.
        db: Active async session.

    Returns:
        The :class:`DomainModel` ORM instance or ``None``.

    """
    from db.models.results import DomainModel

    result = await db.execute(
        select(DomainModel)
        .where(DomainModel.study_id == study_id)
        .order_by(DomainModel.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _get_charts(study_id: int, db: AsyncSession) -> list:
    """Return all ClassificationScheme rows for a study (latest version each).

    Args:
        study_id: Study to query.
        db: Active async session.

    Returns:
        List of :class:`ClassificationScheme` ORM instances.

    """
    from db.models.results import ClassificationScheme

    result = await db.execute(
        select(ClassificationScheme)
        .where(ClassificationScheme.study_id == study_id)
        .order_by(ClassificationScheme.chart_type, ClassificationScheme.version.desc())
    )
    return list(result.scalars().all())


def _dm_to_response(dm) -> DomainModelResponse:
    """Serialise a DomainModel ORM row.

    Args:
        dm: :class:`DomainModel` instance.

    Returns:
        A :class:`DomainModelResponse`.

    """
    return DomainModelResponse(
        id=dm.id,
        study_id=dm.study_id,
        version=dm.version,
        concepts=dm.concepts,
        relationships=dm.relationships,
        svg_content=dm.svg_content,
        generated_at=dm.generated_at,
    )


def _chart_to_response(c) -> ClassificationSchemeResponse:
    """Serialise a ClassificationScheme ORM row.

    Args:
        c: :class:`ClassificationScheme` instance.

    Returns:
        A :class:`ClassificationSchemeResponse`.

    """
    return ClassificationSchemeResponse(
        id=c.id,
        study_id=c.study_id,
        chart_type=c.chart_type.value if hasattr(c.chart_type, "value") else str(c.chart_type),
        version=c.version,
        chart_data=c.chart_data,
        svg_content=c.svg_content,
        generated_at=c.generated_at,
    )


# ---------------------------------------------------------------------------
# GET /studies/{study_id}/results
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/results",
    response_model=ResultsSummaryResponse,
    summary="Get generated results for a study",
)
async def get_results(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResultsSummaryResponse:
    """Return the latest domain model and all classification charts for a study."""
    await require_study_member(study_id, current_user, db)

    dm = await _get_latest_domain_model(study_id, db)
    charts = await _get_charts(study_id, db)

    return ResultsSummaryResponse(
        domain_model=_dm_to_response(dm) if dm else None,
        charts=[_chart_to_response(c) for c in charts],
    )


# ---------------------------------------------------------------------------
# POST /studies/{study_id}/results/generate
# ---------------------------------------------------------------------------


@router.post(
    "/studies/{study_id}/results/generate",
    response_model=JobEnqueueResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enqueue a result generation job",
)
async def generate_results(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobEnqueueResponse:
    """Enqueue an ARQ job to generate the domain model and classification charts."""
    from db.models.jobs import BackgroundJob, JobStatus, JobType

    from backend.core.config import get_settings

    await require_study_member(study_id, current_user, db)

    settings = get_settings()
    redis = await arq.connections.create_pool(
        arq.connections.RedisSettings.from_dsn(settings.redis_url)
    )
    job = await redis.enqueue_job("run_generate_results", study_id)
    await redis.close()

    job_id = (
        job.job_id if job else f"generate_results_{study_id}_{int(datetime.now(UTC).timestamp())}"
    )

    bg_job = BackgroundJob(
        id=job_id,
        study_id=study_id,
        job_type=JobType.GENERATE_RESULTS,
        status=JobStatus.QUEUED,
    )
    db.add(bg_job)
    await db.commit()

    logger.info("generate_results: enqueued", study_id=study_id, job_id=job_id)
    return JobEnqueueResponse(job_id=job_id, study_id=study_id)


# ---------------------------------------------------------------------------
# GET /studies/{study_id}/results/charts/{chart_id}/svg
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/results/charts/{chart_id}/svg",
    summary="Return SVG content for a classification chart",
    responses={200: {"content": {"image/svg+xml": {}}}},
)
async def get_chart_svg(
    study_id: int,
    chart_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Return the raw SVG string for a ClassificationScheme chart."""
    from db.models.results import ClassificationScheme

    await require_study_member(study_id, current_user, db)

    result = await db.execute(
        select(ClassificationScheme).where(
            ClassificationScheme.id == chart_id,
            ClassificationScheme.study_id == study_id,
        )
    )
    chart = result.scalar_one_or_none()
    if chart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found")

    svg = chart.svg_content or ""
    return Response(content=svg, media_type="image/svg+xml")


# ---------------------------------------------------------------------------
# GET /studies/{study_id}/results/domain-model/svg
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/results/domain-model/svg",
    summary="Return SVG content for the domain model",
    responses={200: {"content": {"image/svg+xml": {}}}},
)
async def get_domain_model_svg(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Return the raw SVG string for the latest domain model snapshot."""
    await require_study_member(study_id, current_user, db)

    dm = await _get_latest_domain_model(study_id, db)
    if dm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Domain model not generated yet"
        )

    svg = dm.svg_content or ""
    return Response(content=svg, media_type="image/svg+xml")


# ---------------------------------------------------------------------------
# POST /studies/{study_id}/export
# ---------------------------------------------------------------------------


@router.post(
    "/studies/{study_id}/export",
    response_model=JobEnqueueResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enqueue an export job",
)
async def enqueue_export(
    study_id: int,
    body: ExportEnqueueRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobEnqueueResponse:
    """Enqueue a background job to build and store an export archive."""
    from db.models.jobs import BackgroundJob, JobStatus, JobType

    from backend.core.config import get_settings

    await require_study_member(study_id, current_user, db)

    valid_formats = {"svg_only", "json_only", "csv_json", "full_archive"}
    if body.format not in valid_formats:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid format. Must be one of {sorted(valid_formats)}",
        )

    settings = get_settings()
    redis = await arq.connections.create_pool(
        arq.connections.RedisSettings.from_dsn(settings.redis_url)
    )
    job = await redis.enqueue_job("run_export", study_id, body.format)
    await redis.close()

    job_id = (
        job.job_id
        if job
        else f"export_{study_id}_{body.format}_{int(datetime.now(UTC).timestamp())}"
    )

    bg_job = BackgroundJob(
        id=job_id,
        study_id=study_id,
        job_type=JobType.EXPORT,
        status=JobStatus.QUEUED,
    )
    db.add(bg_job)
    await db.commit()

    logger.info("enqueue_export: enqueued", study_id=study_id, format=body.format, job_id=job_id)
    return JobEnqueueResponse(job_id=job_id, study_id=study_id)


# ---------------------------------------------------------------------------
# GET /studies/{study_id}/export/{export_id}/download
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/export/{export_id}/download",
    summary="Download a completed export",
    responses={200: {"content": {"application/octet-stream": {}}}},
)
async def download_export(
    study_id: int,
    export_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Stream the completed export file to the client.

    The ``export_id`` corresponds to a BackgroundJob id of type ``export``.
    On completion the job stores the file path in ``progress_detail.download_url``.
    """
    import os
    import tempfile

    from db.models.jobs import BackgroundJob, JobStatus, JobType

    await require_study_member(study_id, current_user, db)

    result = await db.execute(
        select(BackgroundJob).where(
            BackgroundJob.id == export_id,
            BackgroundJob.study_id == study_id,
            BackgroundJob.job_type == JobType.EXPORT,
        )
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Export not ready (status: {job.status.value})",
        )

    detail = job.progress_detail or {}
    download_url: str = detail.get("download_url", "")

    # Resolve local file path from relative URL — use removeprefix, not lstrip,
    # to avoid stripping individual characters instead of the whole prefix.
    prefix = "/exports/"
    filename = download_url[len(prefix) :] if download_url.startswith(prefix) else download_url
    filepath = os.path.join(tempfile.gettempdir(), "sms_exports", filename)

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Export file not found on server"
        )

    def _iter_file(path: str):
        with open(path, "rb") as fh:
            while chunk := fh.read(65535):
                yield chunk

    media_type = "application/json" if filepath.endswith(".json") else "application/zip"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(_iter_file(filepath), media_type=media_type, headers=headers)
