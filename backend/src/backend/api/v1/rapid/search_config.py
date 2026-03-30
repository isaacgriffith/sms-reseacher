"""Rapid Review search configuration endpoint (feature 008).

Routes:
- PUT /rapid/studies/{study_id}/search-config → 200
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
from backend.services import rr_protocol_service

router = APIRouter(tags=["rapid-search-config"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class SearchRestrictionItem(BaseModel):
    """A single search restriction with type and optional detail."""

    type: str
    source_detail: str = ""


class SearchConfigRequest(BaseModel):
    """Request body for PUT /rapid/studies/{study_id}/search-config."""

    restrictions: list[SearchRestrictionItem] = []
    single_reviewer_mode: bool | None = None
    single_source_acknowledged: bool | None = None


class ThreatResponse(BaseModel):
    """Threat-to-validity response body."""

    id: int
    study_id: int
    threat_type: str
    description: str
    source_detail: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.put(
    "/studies/{study_id}/search-config",
    response_model=list[ThreatResponse],
    summary="Configure search restrictions and single-reviewer mode",
)
async def configure_search(
    study_id: int,
    body: SearchConfigRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ThreatResponse]:
    """Configure search restrictions and reviewer mode for a Rapid Review.

    Idempotently upserts ``RRThreatToValidity`` rows for each restriction
    type (``YEAR_RANGE``, ``LANGUAGE``, ``GEOGRAPHY``, ``STUDY_DESIGN``).
    Toggles ``single_reviewer_mode`` on the protocol and manages the
    corresponding ``SINGLE_REVIEWER`` threat.

    Args:
        study_id: The Rapid Review study to configure.
        body: Restrictions, reviewer mode toggle, and acknowledgment flag.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        Updated list of all :class:`ThreatResponse` objects for the study.

    """
    await require_study_member(study_id, current_user, db)

    restrictions = [{"type": r.type, "source_detail": r.source_detail} for r in body.restrictions]
    await rr_protocol_service.configure_search_restrictions(study_id, restrictions, db)

    if body.single_reviewer_mode is not None:
        await rr_protocol_service.set_single_reviewer_mode(study_id, body.single_reviewer_mode, db)

    if body.single_source_acknowledged is not None:
        protocol = await rr_protocol_service.get_or_create_protocol(study_id, db)
        protocol.single_source_acknowledged = body.single_source_acknowledged
        await db.flush()

    await db.commit()
    logger.info("search_config_updated", study_id=study_id)

    result = await db.execute(
        select(RRThreatToValidity)
        .where(RRThreatToValidity.study_id == study_id)
        .order_by(RRThreatToValidity.id)
    )
    threats = result.scalars().all()
    return [ThreatResponse.model_validate(t) for t in threats]
