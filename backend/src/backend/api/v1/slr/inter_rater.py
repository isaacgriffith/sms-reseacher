"""SLR inter-rater agreement endpoints (feature 007).

Routes:
- GET  /slr/studies/{study_id}/inter-rater               → 200
- POST /slr/studies/{study_id}/inter-rater/compute       → 200 | 422
- POST /slr/studies/{study_id}/inter-rater/post-discussion → 200 | 422
"""

from __future__ import annotations

from datetime import datetime

from db.models.slr import AgreementRoundType
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services import inter_rater_service

router = APIRouter(tags=["slr-inter-rater"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class InterRaterRecordResponse(BaseModel):
    """Single inter-rater agreement record."""

    id: int
    study_id: int
    reviewer_a_id: int
    reviewer_b_id: int
    round_type: str
    phase: str
    kappa_value: float | None
    kappa_undefined_reason: str | None
    n_papers: int
    threshold_met: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class InterRaterListResponse(BaseModel):
    """List of inter-rater records for a study."""

    records: list[InterRaterRecordResponse]


class ComputeKappaRequest(BaseModel):
    """Request body for compute and post-discussion endpoints."""

    reviewer_a_id: int
    reviewer_b_id: int
    round_type: AgreementRoundType


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/inter-rater",
    response_model=InterRaterListResponse,
    summary="List inter-rater agreement records",
)
async def list_inter_rater_records(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterRaterListResponse:
    """Return all Kappa records for an SLR study.

    Args:
        study_id: The study whose records to retrieve.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        :class:`InterRaterListResponse` with all records.

    """
    records = await inter_rater_service.get_records(study_id, db)
    return InterRaterListResponse(
        records=[InterRaterRecordResponse.model_validate(r) for r in records]
    )


@router.post(
    "/studies/{study_id}/inter-rater/compute",
    response_model=InterRaterRecordResponse,
    summary="Compute inter-rater Kappa",
)
async def compute_kappa(
    study_id: int,
    body: ComputeKappaRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterRaterRecordResponse:
    """Compute Cohen's Kappa for two reviewers' pre-discussion assessments.

    Args:
        study_id: The study to compute Kappa for.
        body: Reviewer IDs and round type.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        The new :class:`InterRaterRecordResponse`.

    Raises:
        HTTPException: 422 if either reviewer has incomplete assessments.

    """
    record = await inter_rater_service.compute_and_store_kappa(
        study_id=study_id,
        reviewer_a_id=body.reviewer_a_id,
        reviewer_b_id=body.reviewer_b_id,
        round_type=body.round_type,
        phase="pre_discussion",
        db=db,
    )
    return InterRaterRecordResponse.model_validate(record)


@router.post(
    "/studies/{study_id}/inter-rater/post-discussion",
    response_model=InterRaterRecordResponse,
    summary="Record post-discussion Kappa",
)
async def post_discussion_kappa(
    study_id: int,
    body: ComputeKappaRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InterRaterRecordResponse:
    """Record Kappa after the Think-Aloud discussion workflow is complete.

    Args:
        study_id: The study to record post-discussion Kappa for.
        body: Reviewer IDs and round type.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        A new :class:`InterRaterRecordResponse` with ``phase="post_discussion"``.

    Raises:
        HTTPException: 422 if either reviewer has incomplete assessments.

    """
    record = await inter_rater_service.compute_and_store_kappa(
        study_id=study_id,
        reviewer_a_id=body.reviewer_a_id,
        reviewer_b_id=body.reviewer_b_id,
        round_type=body.round_type,
        phase="post_discussion",
        db=db,
    )
    return InterRaterRecordResponse.model_validate(record)
