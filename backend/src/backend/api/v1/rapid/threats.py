"""Rapid Review threats-to-validity read-only endpoint (feature 008).

Routes:
- GET /rapid/studies/{study_id}/threats → list[ThreatResponse]

Threats are auto-created by the service layer when search restrictions,
single-reviewer mode, or quality appraisal omissions are applied.  They
are never created directly by the researcher.
"""

from __future__ import annotations

from datetime import datetime

from db.models.rapid_review import RRThreatToValidity
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db

router = APIRouter(tags=["rapid-threats"])
logger = get_logger(__name__)


class ThreatResponse(BaseModel):
    """Threat-to-validity response body."""

    id: int
    study_id: int
    threat_type: str
    description: str
    source_detail: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get(
    "/studies/{study_id}/threats",
    response_model=list[ThreatResponse],
    summary="List threats to validity",
)
async def list_threats(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ThreatResponse]:
    """Return all threats-to-validity for a Rapid Review study.

    Threats are auto-created by the service layer; they are never created
    directly by the researcher.

    Args:
        study_id: The study to list threats for.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        List of :class:`ThreatResponse` objects ordered by creation time.

    """
    await require_study_member(study_id, current_user, db)
    result = await db.execute(
        select(RRThreatToValidity)
        .where(RRThreatToValidity.study_id == study_id)
        .order_by(RRThreatToValidity.created_at)
    )
    threats = result.scalars().all()
    return [ThreatResponse.model_validate(t) for t in threats]
