"""Tertiary Study protocol endpoints (feature 009).

Routes:
- GET  /tertiary/studies/{study_id}/protocol          → 200 | 404
- PUT  /tertiary/studies/{study_id}/protocol          → 200 | 409 | 422
- POST /tertiary/studies/{study_id}/protocol/validate → 202 | 409
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import arq.connections
import structlog
from db.models import Study, StudyType
from db.models.tertiary import TertiaryProtocolStatus, TertiaryStudyProtocol
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger, get_settings
from backend.core.database import get_db
from backend.services.tertiary_qa_service import get_or_create_default_secondary_study_checklist

router = APIRouter(tags=["tertiary-protocol"])
logger = get_logger(__name__)

_structlog = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class TertiaryProtocolResponse(BaseModel):
    """Full Tertiary Study protocol response body."""

    id: int
    study_id: int
    status: str
    background: str | None
    research_questions: list[str] | None
    secondary_study_types: list[str] | None
    inclusion_criteria: list[str] | None
    exclusion_criteria: list[str] | None
    recency_cutoff_year: int | None
    search_strategy: str | None
    quality_threshold: float | None
    synthesis_approach: str | None
    dissemination_strategy: str | None
    version_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TertiaryProtocolUpdate(BaseModel):
    """Request body for PUT /tertiary/studies/{study_id}/protocol — all fields optional."""

    background: str | None = None
    research_questions: list[str] | None = None
    secondary_study_types: list[str] | None = None
    inclusion_criteria: list[str] | None = None
    exclusion_criteria: list[str] | None = None
    recency_cutoff_year: int | None = None
    search_strategy: str | None = None
    quality_threshold: float | None = None
    synthesis_approach: str | None = None
    dissemination_strategy: str | None = None
    version_id: int | None = None


class ValidateProtocolResponse(BaseModel):
    """Response body for POST /protocol/validate."""

    job_id: str
    status: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _require_tertiary_study(
    study_id: int,
    current_user: CurrentUser,
    db: AsyncSession,
) -> Study:
    """Resolve the study and enforce TERTIARY type and membership.

    Args:
        study_id: Study to resolve.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        The resolved :class:`Study` instance.

    Raises:
        HTTPException: 404 if not found or not of type TERTIARY.

    """
    await require_study_member(study_id, current_user, db)
    result = await db.execute(select(Study).where(Study.id == study_id))
    study = result.scalar_one_or_none()
    if study is None or study.study_type != StudyType.TERTIARY:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tertiary Study not found.",
        )
    return study


async def _get_or_create_protocol(study_id: int, db: AsyncSession) -> TertiaryStudyProtocol:
    """Return the protocol for *study_id*, creating a draft if absent.

    Args:
        study_id: The Tertiary Study to look up.
        db: Async database session.

    Returns:
        Existing or newly-created :class:`TertiaryStudyProtocol`.

    """
    result = await db.execute(
        select(TertiaryStudyProtocol).where(TertiaryStudyProtocol.study_id == study_id)
    )
    protocol = result.scalar_one_or_none()
    if protocol is None:
        protocol = TertiaryStudyProtocol(
            study_id=study_id,
            status=TertiaryProtocolStatus.DRAFT,
        )
        db.add(protocol)
        await db.flush()
    return protocol


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/protocol",
    response_model=TertiaryProtocolResponse,
    summary="Get Tertiary Study protocol",
)
async def get_protocol(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TertiaryProtocolResponse:
    """Return the protocol for a Tertiary Study, auto-creating a draft if absent.

    Args:
        study_id: The Tertiary Study whose protocol to retrieve.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        The :class:`TertiaryProtocolResponse`.

    Raises:
        HTTPException: 404 if the study is not found or not of type TERTIARY.

    """
    await _require_tertiary_study(study_id, current_user, db)
    protocol = await _get_or_create_protocol(study_id, db)
    # Auto-seed the default secondary-study QA checklist so it is ready for
    # Phase 4 as soon as the protocol is first accessed.
    await get_or_create_default_secondary_study_checklist(study_id, db)
    await db.commit()
    await db.refresh(protocol)
    return TertiaryProtocolResponse.model_validate(protocol)


@router.put(
    "/studies/{study_id}/protocol",
    response_model=TertiaryProtocolResponse,
    summary="Update Tertiary Study protocol",
)
async def update_protocol(
    study_id: int,
    body: TertiaryProtocolUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TertiaryProtocolResponse:
    """Update the Tertiary Study protocol (partial update).

    Performs an optimistic-lock check on ``version_id`` when provided.

    Args:
        study_id: The Tertiary Study whose protocol to update.
        body: Fields to update (all optional).
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        The updated :class:`TertiaryProtocolResponse`.

    Raises:
        HTTPException: 404 if study not found or not TERTIARY type.
        HTTPException: 409 if ``version_id`` is stale.

    """
    await _require_tertiary_study(study_id, current_user, db)
    protocol = await _get_or_create_protocol(study_id, db)

    # Optimistic locking: reject if the client's version_id is stale.
    if body.version_id is not None and body.version_id != protocol.version_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Protocol was modified by another request (version_id mismatch).",
        )

    update_data: dict[str, Any] = body.model_dump(exclude={"version_id"}, exclude_none=True)
    for field, value in update_data.items():
        setattr(protocol, field, value)

    await db.commit()
    await db.refresh(protocol)
    _structlog.info("tertiary_protocol_updated", study_id=study_id, version_id=protocol.version_id)
    return TertiaryProtocolResponse.model_validate(protocol)


@router.post(
    "/studies/{study_id}/protocol/validate",
    response_model=ValidateProtocolResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Validate Tertiary Study protocol",
)
async def validate_protocol(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ValidateProtocolResponse:
    """Transition the protocol to ``validated`` and enqueue an AI review job.

    Args:
        study_id: The Tertiary Study whose protocol to validate.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        :class:`ValidateProtocolResponse` with ``job_id`` and ``status``.

    Raises:
        HTTPException: 404 if study not found or not TERTIARY type.
        HTTPException: 409 if protocol is already validated.

    """
    await _require_tertiary_study(study_id, current_user, db)
    result = await db.execute(
        select(TertiaryStudyProtocol).where(TertiaryStudyProtocol.study_id == study_id)
    )
    protocol = result.scalar_one_or_none()
    if protocol is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No protocol found for this study.",
        )
    if protocol.status == TertiaryProtocolStatus.VALIDATED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Protocol is already validated.",
        )

    protocol.status = TertiaryProtocolStatus.VALIDATED
    await db.commit()
    await db.refresh(protocol)

    settings = get_settings()
    arq_pool = await arq.connections.create_pool(
        arq.connections.RedisSettings.from_dsn(settings.redis_url)
    )
    try:
        job = await arq_pool.enqueue_job(
            "run_tertiary_protocol_review",
            study_id=study_id,
            protocol_id=protocol.id,
        )
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to enqueue protocol review job.",
            )
        job_id: str = job.job_id
    finally:
        await arq_pool.close()

    _structlog.info(
        "tertiary_protocol_validated",
        study_id=study_id,
        job_id=job_id,
    )
    return ValidateProtocolResponse(job_id=job_id, status="queued")
