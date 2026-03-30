"""Rapid Review quality appraisal configuration endpoints (feature 008).

Routes:
- GET /rapid/studies/{study_id}/quality-config → 200
- PUT /rapid/studies/{study_id}/quality-config → 200
"""

from __future__ import annotations

from datetime import datetime

from db.models.rapid_review import RRQualityAppraisalMode, RRThreatToValidity
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services import rr_protocol_service

router = APIRouter(tags=["rapid-quality"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class QualityConfigResponse(BaseModel):
    """Response body for GET /rapid/studies/{study_id}/quality-config."""

    quality_appraisal_mode: str
    threats: list[ThreatResponse]

    model_config = {"from_attributes": True}


class ThreatResponse(BaseModel):
    """Threat-to-validity response body."""

    id: int
    study_id: int
    threat_type: str
    description: str
    source_detail: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class QualityConfigRequest(BaseModel):
    """Request body for PUT /rapid/studies/{study_id}/quality-config."""

    mode: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/quality-config",
    response_model=QualityConfigResponse,
    summary="Get quality appraisal configuration",
)
async def get_quality_config(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QualityConfigResponse:
    """Return the current quality appraisal mode and related threats.

    Args:
        study_id: The Rapid Review study to query.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        :class:`QualityConfigResponse` with mode and threat list.

    """
    await require_study_member(study_id, current_user, db)
    protocol = await rr_protocol_service.get_or_create_protocol(study_id, db)

    threat_result = await db.execute(
        select(RRThreatToValidity)
        .where(RRThreatToValidity.study_id == study_id)
        .order_by(RRThreatToValidity.id)
    )
    threats = threat_result.scalars().all()

    return QualityConfigResponse(
        quality_appraisal_mode=protocol.quality_appraisal_mode.value,
        threats=[ThreatResponse.model_validate(t) for t in threats],
    )


@router.put(
    "/studies/{study_id}/quality-config",
    response_model=QualityConfigResponse,
    summary="Set quality appraisal mode",
)
async def set_quality_config(
    study_id: int,
    body: QualityConfigRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QualityConfigResponse:
    """Set the quality appraisal mode for a Rapid Review study.

    Modes:
    - ``full``: Standard quality appraisal (no automatic threat created).
    - ``peer_reviewed_only``: Excludes non-peer-reviewed papers and creates a
      ``QA_SIMPLIFIED`` threat.
    - ``skipped``: No appraisal performed; creates a ``QA_SKIPPED`` threat.

    Args:
        study_id: The Rapid Review study to configure.
        body: Request body containing the target mode string.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        Updated :class:`QualityConfigResponse` with new mode and threats.

    """
    await require_study_member(study_id, current_user, db)

    try:
        mode = RRQualityAppraisalMode(body.mode)
    except ValueError as exc:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid quality appraisal mode: {body.mode!r}",
        ) from exc

    await rr_protocol_service.set_quality_appraisal_mode(study_id, mode, db)
    await db.commit()

    logger.info("quality_config_updated", study_id=study_id, mode=mode.value)

    protocol = await rr_protocol_service.get_or_create_protocol(study_id, db)
    threat_result = await db.execute(
        select(RRThreatToValidity)
        .where(RRThreatToValidity.study_id == study_id)
        .order_by(RRThreatToValidity.id)
    )
    threats = threat_result.scalars().all()

    return QualityConfigResponse(
        quality_appraisal_mode=protocol.quality_appraisal_mode.value,
        threats=[ThreatResponse.model_validate(t) for t in threats],
    )
