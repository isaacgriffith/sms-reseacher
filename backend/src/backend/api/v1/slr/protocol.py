"""SLR protocol review endpoints (feature 007).

Routes:
- GET  /slr/studies/{study_id}/protocol            → 200 | 404
- PUT  /slr/studies/{study_id}/protocol            → 200 | 409
- POST /slr/studies/{study_id}/protocol/submit-for-review → 202 | 422
- POST /slr/studies/{study_id}/protocol/validate   → 200 | 422
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import arq.connections
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger, get_settings
from backend.core.database import get_db
from backend.services import slr_protocol_service

router = APIRouter(tags=["slr-protocol"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class ProtocolResponse(BaseModel):
    """Full protocol response body."""

    id: int
    study_id: int
    status: str
    background: str | None
    rationale: str | None
    research_questions: list[str] | None
    pico_population: str | None
    pico_intervention: str | None
    pico_comparison: str | None
    pico_outcome: str | None
    pico_context: str | None
    search_strategy: str | None
    inclusion_criteria: list[str] | None
    exclusion_criteria: list[str] | None
    data_extraction_strategy: str | None
    synthesis_approach: str | None
    dissemination_strategy: str | None
    timetable: str | None
    review_report: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProtocolUpsertRequest(BaseModel):
    """Request body for PUT /protocol — all fields optional."""

    background: str | None = None
    rationale: str | None = None
    research_questions: list[str] | None = None
    pico_population: str | None = None
    pico_intervention: str | None = None
    pico_comparison: str | None = None
    pico_outcome: str | None = None
    pico_context: str | None = None
    search_strategy: str | None = None
    inclusion_criteria: list[str] | None = None
    exclusion_criteria: list[str] | None = None
    data_extraction_strategy: str | None = None
    synthesis_approach: str | None = None
    dissemination_strategy: str | None = None
    timetable: str | None = None


class SubmitForReviewResponse(BaseModel):
    """Response body for submit-for-review."""

    job_id: str
    status: str


class ValidateProtocolResponse(BaseModel):
    """Response body for validate."""

    status: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/protocol",
    response_model=ProtocolResponse,
    summary="Get SLR review protocol",
)
async def get_protocol(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProtocolResponse:
    """Return the current review protocol for an SLR study.

    Args:
        study_id: The study whose protocol to retrieve.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        The :class:`ProtocolResponse` for the study's protocol.

    Raises:
        HTTPException: 404 if no protocol exists for this study.

    """
    protocol = await slr_protocol_service.get_protocol(study_id, db)
    if protocol is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No protocol found for this study.",
        )
    return ProtocolResponse.model_validate(protocol)


@router.put(
    "/studies/{study_id}/protocol",
    response_model=ProtocolResponse,
    summary="Create or update SLR review protocol",
)
async def upsert_protocol(
    study_id: int,
    body: ProtocolUpsertRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProtocolResponse:
    """Create or update the draft protocol for an SLR study.

    Args:
        study_id: The study to create or update the protocol for.
        body: Protocol field values to apply.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        The updated :class:`ProtocolResponse`.

    Raises:
        HTTPException: 409 if the protocol is already validated.

    """
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    protocol = await slr_protocol_service.upsert_protocol(study_id, data, db)
    return ProtocolResponse.model_validate(protocol)


@router.post(
    "/studies/{study_id}/protocol/submit-for-review",
    response_model=SubmitForReviewResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit SLR protocol for AI review",
)
async def submit_for_review(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SubmitForReviewResponse:
    """Submit the protocol to the ProtocolReviewerAgent via an ARQ job.

    Args:
        study_id: The study whose protocol to submit.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        :class:`SubmitForReviewResponse` with ``job_id`` and ``status``.

    Raises:
        HTTPException: 404 if no protocol exists.
        HTTPException: 422 if required fields are missing.

    """
    settings = get_settings()
    arq_pool = await arq.connections.create_pool(
        arq.connections.RedisSettings.from_dsn(settings.redis_url)
    )
    try:
        job_id = await slr_protocol_service.submit_for_review(study_id, db, arq_pool)
    finally:
        await arq_pool.close()

    return SubmitForReviewResponse(job_id=job_id, status="under_review")


@router.post(
    "/studies/{study_id}/protocol/validate",
    response_model=ValidateProtocolResponse,
    summary="Validate SLR protocol",
)
async def validate_protocol(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ValidateProtocolResponse:
    """Approve and validate the reviewed SLR protocol.

    Unlocks Phase 2 (database search) for this study.

    Args:
        study_id: The study whose protocol to validate.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        :class:`ValidateProtocolResponse` with ``status="validated"``.

    Raises:
        HTTPException: 404 if no protocol exists.
        HTTPException: 422 if the protocol has not been reviewed yet.

    """
    await slr_protocol_service.validate_protocol(study_id, db)
    return ValidateProtocolResponse(status="validated")
