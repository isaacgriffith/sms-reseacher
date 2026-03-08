"""Validity discussion endpoints: GET, PUT, and AI generate (US7)."""

from __future__ import annotations

import arq.connections
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db

router = APIRouter(tags=["validity"])
logger = get_logger(__name__)

_VALIDITY_DIMS = (
    "descriptive",
    "theoretical",
    "generalizability_internal",
    "generalizability_external",
    "interpretive",
    "repeatability",
)


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class ValidityResponse(BaseModel):
    """Six validity discussion dimensions for a study."""

    descriptive: str | None = None
    theoretical: str | None = None
    generalizability_internal: str | None = None
    generalizability_external: str | None = None
    interpretive: str | None = None
    repeatability: str | None = None


class ValidityUpdateRequest(BaseModel):
    """Partial update request — any subset of the six validity dimensions."""

    descriptive: str | None = None
    theoretical: str | None = None
    generalizability_internal: str | None = None
    generalizability_external: str | None = None
    interpretive: str | None = None
    repeatability: str | None = None


class ValidityGenerateResponse(BaseModel):
    """202 Accepted response for POST /validity/generate."""

    job_id: str
    study_id: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _load_study(study_id: int, db: AsyncSession):
    """Load a Study by ID or raise 404.

    Args:
        study_id: Study primary key.
        db: Active async session.

    Returns:
        The :class:`Study` ORM instance.

    Raises:
        HTTPException: 404 if the study does not exist.
    """
    from db.models import Study

    result = await db.execute(select(Study).where(Study.id == study_id))
    study = result.scalar_one_or_none()
    if study is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    return study


def _validity_to_response(study) -> ValidityResponse:
    """Extract validity fields from a Study ORM row.

    Args:
        study: :class:`Study` ORM instance.

    Returns:
        A :class:`ValidityResponse` with the current validity data.
    """
    data: dict = study.validity or {}
    return ValidityResponse(**{dim: data.get(dim) for dim in _VALIDITY_DIMS})


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/validity",
    response_model=ValidityResponse,
    summary="Get validity discussion for a study",
)
async def get_validity(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ValidityResponse:
    """Return the current validity discussion dimensions for the study."""
    await require_study_member(study_id, current_user, db)
    study = await _load_study(study_id, db)
    return _validity_to_response(study)


@router.put(
    "/studies/{study_id}/validity",
    response_model=ValidityResponse,
    summary="Update validity discussion for a study",
)
async def update_validity(
    study_id: int,
    body: ValidityUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ValidityResponse:
    """Merge the supplied validity fields into the study's validity JSON.

    Only fields explicitly set in the request body are overwritten; omitted
    fields retain their current values.
    """
    await require_study_member(study_id, current_user, db)
    study = await _load_study(study_id, db)

    current: dict = dict(study.validity or {})
    for dim in _VALIDITY_DIMS:
        val = getattr(body, dim)
        if val is not None:
            current[dim] = val

    study.validity = current
    await db.commit()
    await db.refresh(study)

    logger.info("update_validity: saved", study_id=study_id)
    return _validity_to_response(study)


@router.post(
    "/studies/{study_id}/validity/generate",
    response_model=ValidityGenerateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="AI-generate validity discussion pre-fill",
)
async def generate_validity(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ValidityGenerateResponse:
    """Enqueue a background job that calls ValidityAgent to pre-fill all six dimensions."""
    from datetime import datetime, timezone

    from backend.core.config import get_settings
    from db.models.jobs import BackgroundJob, JobStatus, JobType

    await require_study_member(study_id, current_user, db)

    settings = get_settings()
    redis = await arq.connections.create_pool(
        arq.connections.RedisSettings.from_dsn(settings.redis_url)
    )
    job = await redis.enqueue_job("run_validity_prefill", study_id)
    await redis.close()

    job_id = (
        job.job_id
        if job
        else f"validity_prefill_{study_id}_{int(datetime.now(timezone.utc).timestamp())}"
    )

    bg_job = BackgroundJob(
        id=job_id,
        study_id=study_id,
        job_type=JobType.VALIDITY_PREFILL,
        status=JobStatus.QUEUED,
    )
    db.add(bg_job)
    await db.commit()

    logger.info("generate_validity: enqueued", study_id=study_id, job_id=job_id)
    return ValidityGenerateResponse(job_id=job_id, study_id=study_id)
