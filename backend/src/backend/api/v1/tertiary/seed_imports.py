"""Tertiary Study seed-import endpoints (feature 009).

Routes:
- GET  /tertiary/studies/{study_id}/seed-imports  → 200 list
- POST /tertiary/studies/{study_id}/seed-imports  → 201 | 404 | 409 | 422
"""

from __future__ import annotations

from datetime import datetime

import structlog
from db.models import Study, StudyType
from db.models.tertiary import SecondaryStudySeedImport
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services.tertiary_extraction_service import TertiaryExtractionService

router = APIRouter(tags=["tertiary-seed-imports"])
logger = get_logger(__name__)
_structlog = structlog.get_logger(__name__)

_svc = TertiaryExtractionService()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class SeedImportSummary(BaseModel):
    """Single seed import item in the list response."""

    id: int
    target_study_id: int
    source_study_id: int
    source_study_title: str | None
    source_study_type: str | None
    imported_at: datetime
    records_added: int
    records_skipped: int
    imported_by_user_id: int | None

    model_config = {"from_attributes": True}


class SeedImportResponse(BaseModel):
    """Response body for POST /seed-imports (201 Created)."""

    id: int
    records_added: int
    records_skipped: int
    imported_at: datetime

    model_config = {"from_attributes": True}


class CreateSeedImportRequest(BaseModel):
    """Request body for POST /seed-imports."""

    source_study_id: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _require_tertiary_study(
    study_id: int,
    current_user: CurrentUser,
    db: AsyncSession,
) -> Study:
    """Resolve the study and assert it is of type TERTIARY.

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


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/seed-imports",
    response_model=list[SeedImportSummary],
    summary="List seed imports for a Tertiary Study",
)
async def list_seed_imports(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SeedImportSummary]:
    """Return all seed import audit records for a Tertiary Study.

    Each record includes the source study's title and type resolved via a
    joined query.

    Args:
        study_id: The Tertiary Study whose imports to list.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        List of :class:`SeedImportSummary` objects.

    Raises:
        HTTPException: 404 if the study is not found or not of type TERTIARY.

    """
    await _require_tertiary_study(study_id, current_user, db)

    imports_result = await db.execute(
        select(SecondaryStudySeedImport).where(SecondaryStudySeedImport.target_study_id == study_id)
    )
    import_records = list(imports_result.scalars().all())

    # Resolve source study titles/types in bulk.
    source_ids = {r.source_study_id for r in import_records}
    study_map: dict[int, Study] = {}
    if source_ids:
        src_result = await db.execute(select(Study).where(Study.id.in_(source_ids)))
        study_map = {s.id: s for s in src_result.scalars().all()}

    summaries: list[SeedImportSummary] = []
    for imp in import_records:
        src = study_map.get(imp.source_study_id)
        summaries.append(
            SeedImportSummary(
                id=imp.id,
                target_study_id=imp.target_study_id,
                source_study_id=imp.source_study_id,
                source_study_title=src.name if src else None,
                source_study_type=src.study_type.value if src else None,
                imported_at=imp.imported_at,
                records_added=imp.records_added,
                records_skipped=imp.records_skipped,
                imported_by_user_id=imp.imported_by_user_id,
            )
        )
    return summaries


@router.post(
    "/studies/{study_id}/seed-imports",
    response_model=SeedImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import included papers from a platform study",
)
async def create_seed_import(
    study_id: int,
    body: CreateSeedImportRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SeedImportResponse:
    """Import included (accepted) papers from a source study into this Tertiary Study.

    Deduplicates by shared ``paper_id``; duplicate papers are counted as
    skipped rather than re-inserted.  A 409 is returned if an import from the
    same source study has already been performed.

    Args:
        study_id: The Tertiary Study receiving the seed papers.
        body: Request body containing ``source_study_id``.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        :class:`SeedImportResponse` with record counts.

    Raises:
        HTTPException: 404 if the target or source study is not found.
        HTTPException: 409 if an import from this source study already exists.
        HTTPException: 422 if the source study has no included papers.

    """
    await _require_tertiary_study(study_id, current_user, db)

    # Verify source study exists.
    src_result = await db.execute(select(Study).where(Study.id == body.source_study_id))
    source_study = src_result.scalar_one_or_none()
    if source_study is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source study {body.source_study_id} not found.",
        )

    # Check for duplicate import (same source → same target).
    dup_result = await db.execute(
        select(SecondaryStudySeedImport).where(
            SecondaryStudySeedImport.target_study_id == study_id,
            SecondaryStudySeedImport.source_study_id == body.source_study_id,
        )
    )
    if dup_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"An import from study {body.source_study_id} already exists "
                "for this Tertiary Study."
            ),
        )

    try:
        import_record = await _svc.import_seed_study(
            target_study_id=study_id,
            source_study_id=body.source_study_id,
            user_id=current_user.user_id,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    await db.commit()
    await db.refresh(import_record)

    _structlog.info(
        "seed_import_created",
        target_study_id=study_id,
        source_study_id=body.source_study_id,
        records_added=import_record.records_added,
        records_skipped=import_record.records_skipped,
    )
    return SeedImportResponse.model_validate(import_record)
