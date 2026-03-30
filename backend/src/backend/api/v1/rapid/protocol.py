"""Rapid Review protocol endpoints (feature 008).

Routes:
- GET  /rapid/studies/{study_id}/protocol          → 200 | 404
- PUT  /rapid/studies/{study_id}/protocol          → 200 | 409
- POST /rapid/studies/{study_id}/protocol/validate → 200 | 422
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services import rr_protocol_service

router = APIRouter(tags=["rapid-protocol"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class RRProtocolResponse(BaseModel):
    """Full Rapid Review protocol response body."""

    id: int
    study_id: int
    status: str
    practical_problem: str | None
    research_questions: list[str] | None
    time_budget_days: int | None
    effort_budget_hours: int | None
    context_restrictions: list[dict[str, Any]] | None
    dissemination_medium: str | None
    problem_scoping_notes: str | None
    search_strategy_notes: str | None
    inclusion_criteria: list[str] | None
    exclusion_criteria: list[str] | None
    single_reviewer_mode: bool
    single_source_acknowledged: bool
    quality_appraisal_mode: str
    version_id: int
    research_gap_warnings: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RRProtocolUpdateRequest(BaseModel):
    """Request body for PUT /rapid/studies/{study_id}/protocol — all fields optional."""

    practical_problem: str | None = None
    research_questions: list[str] | None = None
    time_budget_days: int | None = None
    effort_budget_hours: int | None = None
    context_restrictions: list[dict[str, Any]] | None = None
    dissemination_medium: str | None = None
    problem_scoping_notes: str | None = None
    search_strategy_notes: str | None = None
    inclusion_criteria: list[str] | None = None
    exclusion_criteria: list[str] | None = None
    single_source_acknowledged: bool | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/protocol",
    response_model=RRProtocolResponse,
    summary="Get the Rapid Review protocol",
)
async def get_protocol(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RRProtocolResponse:
    """Retrieve the Rapid Review protocol for a study (creates if absent).

    Args:
        study_id: The Rapid Review study to retrieve the protocol for.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        The :class:`RRProtocolResponse` for the study.

    """
    await require_study_member(study_id, current_user, db)
    protocol = await rr_protocol_service.get_or_create_protocol(study_id, db)
    await db.commit()

    warnings: list[str] = []
    if protocol.research_questions:
        warnings = rr_protocol_service.detect_research_gap_questions(protocol.research_questions)

    resp = RRProtocolResponse.model_validate(protocol)
    resp.research_gap_warnings = warnings
    return resp


@router.put(
    "/studies/{study_id}/protocol",
    response_model=RRProtocolResponse,
    summary="Update the Rapid Review protocol",
)
async def update_protocol(
    study_id: int,
    body: RRProtocolUpdateRequest,
    acknowledge_invalidation: bool = Query(default=False),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RRProtocolResponse:
    """Update the Rapid Review protocol.

    If the protocol is currently ``VALIDATED``, reset to ``DRAFT`` and
    invalidate all collected papers.  Pass
    ``?acknowledge_invalidation=true`` to confirm.

    Args:
        study_id: The study whose protocol to update.
        body: Partial update fields.
        acknowledge_invalidation: Confirm cascading paper invalidation.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        Updated :class:`RRProtocolResponse`.

    """
    await require_study_member(study_id, current_user, db)
    data = body.model_dump(exclude_none=True)
    protocol = await rr_protocol_service.update_protocol(
        study_id, data, acknowledge_invalidation, db
    )
    await db.commit()

    warnings: list[str] = []
    if protocol.research_questions:
        warnings = rr_protocol_service.detect_research_gap_questions(protocol.research_questions)

    resp = RRProtocolResponse.model_validate(protocol)
    resp.research_gap_warnings = warnings
    return resp


@router.post(
    "/studies/{study_id}/protocol/validate",
    response_model=RRProtocolResponse,
    summary="Validate the Rapid Review protocol",
)
async def validate_protocol(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RRProtocolResponse:
    """Attempt to validate the Rapid Review protocol.

    Runs pre-validation checks: stakeholder exists, non-empty research
    questions, non-empty practical problem.  On success protocol status
    becomes ``VALIDATED`` and phase 2 is unlocked.

    Args:
        study_id: The study whose protocol to validate.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        Updated :class:`RRProtocolResponse` with ``status=VALIDATED``.

    """
    await require_study_member(study_id, current_user, db)
    protocol = await rr_protocol_service.validate_protocol(study_id, db)
    await db.commit()
    return RRProtocolResponse.model_validate(protocol)
