"""Rapid Review practitioner stakeholder endpoints (feature 008).

Routes:
- GET    /rapid/studies/{study_id}/stakeholders
- POST   /rapid/studies/{study_id}/stakeholders                  → 201
- PUT    /rapid/studies/{study_id}/stakeholders/{stakeholder_id} → 200 | 404
- DELETE /rapid/studies/{study_id}/stakeholders/{stakeholder_id} → 204
"""

from __future__ import annotations

from datetime import datetime

from db.models.rapid_review import (
    PractitionerStakeholder,
    RapidReviewProtocol,
    RRInvolvementType,
    RRProtocolStatus,
)
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services import rr_protocol_service

router = APIRouter(tags=["rapid-stakeholders"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class StakeholderResponse(BaseModel):
    """Practitioner stakeholder response body."""

    id: int
    study_id: int
    name: str
    role_title: str
    organisation: str
    involvement_type: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StakeholderCreateRequest(BaseModel):
    """Request body for creating a practitioner stakeholder."""

    name: str
    role_title: str
    organisation: str
    involvement_type: str


class StakeholderUpdateRequest(BaseModel):
    """Request body for updating a practitioner stakeholder — all fields optional."""

    name: str | None = None
    role_title: str | None = None
    organisation: str | None = None
    involvement_type: str | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/stakeholders",
    response_model=list[StakeholderResponse],
    summary="List practitioner stakeholders",
)
async def list_stakeholders(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[StakeholderResponse]:
    """Return all practitioner stakeholders for a Rapid Review study.

    Args:
        study_id: The study to list stakeholders for.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        Ordered list of :class:`StakeholderResponse` objects.

    """
    await require_study_member(study_id, current_user, db)
    result = await db.execute(
        select(PractitionerStakeholder)
        .where(PractitionerStakeholder.study_id == study_id)
        .order_by(PractitionerStakeholder.id)
    )
    stakeholders = result.scalars().all()
    return [StakeholderResponse.model_validate(s) for s in stakeholders]


@router.post(
    "/studies/{study_id}/stakeholders",
    response_model=StakeholderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a practitioner stakeholder",
)
async def create_stakeholder(
    study_id: int,
    body: StakeholderCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StakeholderResponse:
    """Add a new practitioner stakeholder to the study.

    Args:
        study_id: The study to add the stakeholder to.
        body: Stakeholder details.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        The created :class:`StakeholderResponse`.

    """
    await require_study_member(study_id, current_user, db)
    try:
        involvement = RRInvolvementType(body.involvement_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid involvement_type: {body.involvement_type}",
        ) from exc

    stakeholder = PractitionerStakeholder(
        study_id=study_id,
        name=body.name,
        role_title=body.role_title,
        organisation=body.organisation,
        involvement_type=involvement,
    )
    db.add(stakeholder)
    await db.flush()
    await db.commit()
    logger.info("stakeholder_created", study_id=study_id, stakeholder_id=stakeholder.id)
    return StakeholderResponse.model_validate(stakeholder)


@router.put(
    "/studies/{study_id}/stakeholders/{stakeholder_id}",
    response_model=StakeholderResponse,
    summary="Update a practitioner stakeholder",
)
async def update_stakeholder(
    study_id: int,
    stakeholder_id: int,
    body: StakeholderUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StakeholderResponse:
    """Update a practitioner stakeholder's details.

    Args:
        study_id: The study the stakeholder belongs to.
        stakeholder_id: The stakeholder to update.
        body: Fields to update (all optional).
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        Updated :class:`StakeholderResponse`.

    Raises:
        HTTPException: 404 if stakeholder not found.

    """
    await require_study_member(study_id, current_user, db)
    result = await db.execute(
        select(PractitionerStakeholder).where(
            PractitionerStakeholder.id == stakeholder_id,
            PractitionerStakeholder.study_id == study_id,
        )
    )
    stakeholder = result.scalar_one_or_none()
    if stakeholder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stakeholder not found")

    if body.name is not None:
        stakeholder.name = body.name
    if body.role_title is not None:
        stakeholder.role_title = body.role_title
    if body.organisation is not None:
        stakeholder.organisation = body.organisation
    if body.involvement_type is not None:
        try:
            stakeholder.involvement_type = RRInvolvementType(body.involvement_type)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid involvement_type: {body.involvement_type}",
            ) from exc

    await db.flush()
    await db.commit()
    return StakeholderResponse.model_validate(stakeholder)


@router.delete(
    "/studies/{study_id}/stakeholders/{stakeholder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a practitioner stakeholder",
)
async def delete_stakeholder(
    study_id: int,
    stakeholder_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a practitioner stakeholder.

    If this is the last stakeholder and the protocol is ``VALIDATED``,
    the protocol is reset to ``DRAFT`` and all papers are invalidated.

    Args:
        study_id: The study the stakeholder belongs to.
        stakeholder_id: The stakeholder to delete.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Raises:
        HTTPException: 404 if stakeholder not found.

    """
    await require_study_member(study_id, current_user, db)
    result = await db.execute(
        select(PractitionerStakeholder).where(
            PractitionerStakeholder.id == stakeholder_id,
            PractitionerStakeholder.study_id == study_id,
        )
    )
    stakeholder = result.scalar_one_or_none()
    if stakeholder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stakeholder not found")

    # Count remaining stakeholders to detect if this is the last one.
    count_result = await db.execute(
        select(PractitionerStakeholder).where(PractitionerStakeholder.study_id == study_id)
    )
    all_stakeholders = count_result.scalars().all()
    is_last = len(all_stakeholders) == 1 and all_stakeholders[0].id == stakeholder_id

    if is_last:
        protocol_result = await db.execute(
            select(RapidReviewProtocol).where(RapidReviewProtocol.study_id == study_id)
        )
        protocol = protocol_result.scalar_one_or_none()
        if protocol is not None and protocol.status == RRProtocolStatus.VALIDATED:
            protocol.status = RRProtocolStatus.DRAFT
            await rr_protocol_service.invalidate_papers_for_study(study_id, db)
            logger.info("protocol_reset_on_last_stakeholder_delete", study_id=study_id)

    await db.delete(stakeholder)
    await db.flush()
    await db.commit()
    logger.info("stakeholder_deleted", study_id=study_id, stakeholder_id=stakeholder_id)
