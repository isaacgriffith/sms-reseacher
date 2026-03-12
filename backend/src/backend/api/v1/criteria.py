"""Inclusion and exclusion criteria endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger
from backend.core.database import get_db
from db.models.criteria import ExclusionCriterion, InclusionCriterion
from db.models.study import StudyMember

router = APIRouter(tags=["criteria"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class CriterionResponse(BaseModel):
    """Response for a single criterion."""

    id: int
    study_id: int
    description: str
    order_index: int


class AddCriterionRequest(BaseModel):
    """Body for POST criterion endpoints."""

    description: str
    order_index: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _require_study_member(
    study_id: int, current_user: CurrentUser, db: AsyncSession
) -> None:
    result = await db.execute(
        select(StudyMember).where(
            StudyMember.study_id == study_id,
            StudyMember.user_id == current_user.user_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")


# ---------------------------------------------------------------------------
# Inclusion Criteria
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/criteria/inclusion",
    response_model=list[CriterionResponse],
    summary="List inclusion criteria for a study",
)
async def list_inclusion_criteria(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CriterionResponse]:
    """Return all inclusion criteria for a study ordered by order_index."""
    await _require_study_member(study_id, current_user, db)

    result = await db.execute(
        select(InclusionCriterion)
        .where(InclusionCriterion.study_id == study_id)
        .order_by(InclusionCriterion.order_index, InclusionCriterion.id)
    )
    return [
        CriterionResponse(
            id=c.id,
            study_id=c.study_id,
            description=c.description,
            order_index=c.order_index,
        )
        for c in result.scalars().all()
    ]


@router.post(
    "/studies/{study_id}/criteria/inclusion",
    response_model=CriterionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an inclusion criterion",
)
async def add_inclusion_criterion(
    study_id: int,
    body: AddCriterionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CriterionResponse:
    """Add a new inclusion criterion to a study."""
    await _require_study_member(study_id, current_user, db)

    criterion = InclusionCriterion(
        study_id=study_id,
        description=body.description,
        order_index=body.order_index,
    )
    db.add(criterion)
    await db.commit()

    return CriterionResponse(
        id=criterion.id,
        study_id=criterion.study_id,
        description=criterion.description,
        order_index=criterion.order_index,
    )


@router.delete(
    "/studies/{study_id}/criteria/inclusion/{criterion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an inclusion criterion",
)
async def delete_inclusion_criterion(
    study_id: int,
    criterion_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an inclusion criterion from a study."""
    await _require_study_member(study_id, current_user, db)

    result = await db.execute(
        select(InclusionCriterion).where(
            InclusionCriterion.id == criterion_id,
            InclusionCriterion.study_id == study_id,
        )
    )
    criterion = result.scalar_one_or_none()
    if criterion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Criterion not found"
        )

    await db.delete(criterion)
    await db.commit()


# ---------------------------------------------------------------------------
# Exclusion Criteria
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/criteria/exclusion",
    response_model=list[CriterionResponse],
    summary="List exclusion criteria for a study",
)
async def list_exclusion_criteria(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CriterionResponse]:
    """Return all exclusion criteria for a study ordered by order_index."""
    await _require_study_member(study_id, current_user, db)

    result = await db.execute(
        select(ExclusionCriterion)
        .where(ExclusionCriterion.study_id == study_id)
        .order_by(ExclusionCriterion.order_index, ExclusionCriterion.id)
    )
    return [
        CriterionResponse(
            id=c.id,
            study_id=c.study_id,
            description=c.description,
            order_index=c.order_index,
        )
        for c in result.scalars().all()
    ]


@router.post(
    "/studies/{study_id}/criteria/exclusion",
    response_model=CriterionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an exclusion criterion",
)
async def add_exclusion_criterion(
    study_id: int,
    body: AddCriterionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CriterionResponse:
    """Add a new exclusion criterion to a study."""
    await _require_study_member(study_id, current_user, db)

    criterion = ExclusionCriterion(
        study_id=study_id,
        description=body.description,
        order_index=body.order_index,
    )
    db.add(criterion)
    await db.commit()

    return CriterionResponse(
        id=criterion.id,
        study_id=criterion.study_id,
        description=criterion.description,
        order_index=criterion.order_index,
    )


@router.delete(
    "/studies/{study_id}/criteria/exclusion/{criterion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an exclusion criterion",
)
async def delete_exclusion_criterion(
    study_id: int,
    criterion_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an exclusion criterion from a study."""
    await _require_study_member(study_id, current_user, db)

    result = await db.execute(
        select(ExclusionCriterion).where(
            ExclusionCriterion.id == criterion_id,
            ExclusionCriterion.study_id == study_id,
        )
    )
    criterion = result.scalar_one_or_none()
    if criterion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Criterion not found"
        )

    await db.delete(criterion)
    await db.commit()
