"""SLR grey literature CRUD endpoints (feature 007, Phase 8).

Routes:
- GET  /slr/studies/{study_id}/grey-literature       → 200 list
- POST /slr/studies/{study_id}/grey-literature       → 201 created source
- DELETE /slr/studies/{study_id}/grey-literature/{source_id} → 204 deleted
"""

from __future__ import annotations

from datetime import datetime

from db.models.slr import GreyLiteratureSource, GreyLiteratureType
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger
from backend.core.database import get_db

router = APIRouter(tags=["slr-grey-literature"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class GreyLiteratureSourceResponse(BaseModel):
    """Response schema for a single grey literature source.

    Attributes:
        id: Primary key.
        study_id: FK to the parent study.
        source_type: The :class:`GreyLiteratureType` value string.
        title: Source title.
        authors: Author string, or ``None``.
        year: Publication year, or ``None``.
        url: URL, or ``None``.
        description: Relevance description, or ``None``.
        created_at: Creation timestamp.
        updated_at: Last-update timestamp.

    """

    id: int
    study_id: int
    source_type: str
    title: str
    authors: str | None
    year: int | None
    url: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GreyLiteratureListResponse(BaseModel):
    """Wrapper response for a list of grey literature sources."""

    sources: list[GreyLiteratureSourceResponse]


class CreateGreyLiteratureSourceRequest(BaseModel):
    """Request body for creating a grey literature source.

    Attributes:
        source_type: One of the :class:`GreyLiteratureType` string values.
        title: Required source title.
        authors: Optional author string.
        year: Optional publication year.
        url: Optional URL.
        description: Optional relevance note.

    """

    source_type: str
    title: str
    authors: str | None = None
    year: int | None = None
    url: str | None = None
    description: str | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/grey-literature",
    response_model=GreyLiteratureListResponse,
    summary="List grey literature sources for a study",
)
async def list_grey_literature(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GreyLiteratureListResponse:
    """Return all grey literature sources for the given study.

    Args:
        study_id: The integer study ID.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        :class:`GreyLiteratureListResponse` containing the source list.

    """
    result = await db.execute(
        select(GreyLiteratureSource)
        .where(GreyLiteratureSource.study_id == study_id)
        .order_by(GreyLiteratureSource.created_at)
    )
    sources = list(result.scalars().all())
    return GreyLiteratureListResponse(
        sources=[GreyLiteratureSourceResponse.model_validate(s) for s in sources]
    )


@router.post(
    "/studies/{study_id}/grey-literature",
    response_model=GreyLiteratureSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a grey literature source to a study",
)
async def create_grey_literature_source(
    study_id: int,
    body: CreateGreyLiteratureSourceRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GreyLiteratureSourceResponse:
    """Create a new grey literature source for the given study.

    Args:
        study_id: The integer study ID.
        body: Source fields to set.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        The newly created :class:`GreyLiteratureSourceResponse`.

    Raises:
        HTTPException: 400 if ``source_type`` is not a valid
            :class:`GreyLiteratureType` value.

    """
    try:
        source_type = GreyLiteratureType(body.source_type)
    except ValueError:
        valid = [t.value for t in GreyLiteratureType]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source_type '{body.source_type}'. Valid values: {valid}.",
        ) from None

    source = GreyLiteratureSource(
        study_id=study_id,
        source_type=source_type,
        title=body.title,
        authors=body.authors,
        year=body.year,
        url=body.url,
        description=body.description,
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)

    logger.info(
        "create_grey_literature_source: created",
        study_id=study_id,
        source_id=source.id,
        source_type=source_type.value,
    )
    return GreyLiteratureSourceResponse.model_validate(source)


@router.delete(
    "/studies/{study_id}/grey-literature/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a grey literature source",
)
async def delete_grey_literature_source(
    study_id: int,
    source_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a grey literature source.

    Args:
        study_id: The integer study ID (used to verify ownership).
        source_id: The integer source ID to delete.
        current_user: JWT-authenticated user.
        db: Async database session.

    Raises:
        HTTPException: 404 if the source does not exist or does not belong
            to the given study.

    """
    result = await db.execute(
        select(GreyLiteratureSource).where(
            GreyLiteratureSource.id == source_id,
            GreyLiteratureSource.study_id == study_id,
        )
    )
    source = result.scalar_one_or_none()
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grey literature source {source_id} not found for study {study_id}.",
        )

    await db.delete(source)
    await db.commit()

    logger.info(
        "delete_grey_literature_source: deleted",
        study_id=study_id,
        source_id=source_id,
    )
