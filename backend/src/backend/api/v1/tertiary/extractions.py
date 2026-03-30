"""Tertiary Study data extraction endpoints (feature 009).

Routes:
- GET  /tertiary/studies/{study_id}/extractions                     → 200
- GET  /tertiary/studies/{study_id}/extractions/{extraction_id}     → 200 | 404
- PUT  /tertiary/studies/{study_id}/extractions/{extraction_id}     → 200 | 409
- POST /tertiary/studies/{study_id}/extractions/ai-assist           → 202 | 503
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import arq.connections
import structlog
from db.models import Paper, Study, StudyType
from db.models.candidate import CandidatePaper
from db.models.tertiary import TertiaryDataExtraction
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger, get_settings
from backend.core.database import get_db
from backend.services.tertiary_extraction_service import TertiaryExtractionService

router = APIRouter(tags=["tertiary-extractions"])
logger = get_logger(__name__)
_structlog = structlog.get_logger(__name__)

_svc = TertiaryExtractionService()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class TertiaryExtractionResponse(BaseModel):
    """Full extraction record response."""

    id: int
    candidate_paper_id: int
    paper_title: str | None
    secondary_study_type: str | None
    research_questions_addressed: list[str] | None
    databases_searched: list[str] | None
    study_period_start: int | None
    study_period_end: int | None
    primary_study_count: int | None
    synthesis_approach_used: str | None
    key_findings: str | None
    research_gaps: str | None
    reviewer_quality_rating: float | None
    extraction_status: str
    extracted_by_agent: str | None
    validated_by_reviewer_id: int | None
    version_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TertiaryExtractionUpdate(BaseModel):
    """Request body for PUT /extractions/{id} — all fields optional."""

    secondary_study_type: str | None = None
    research_questions_addressed: list[str] | None = None
    databases_searched: list[str] | None = None
    study_period_start: int | None = None
    study_period_end: int | None = None
    primary_study_count: int | None = None
    synthesis_approach_used: str | None = None
    key_findings: str | None = None
    research_gaps: str | None = None
    reviewer_quality_rating: float | None = None
    extraction_status: str | None = None
    version_id: int | None = None


class AiAssistResponse(BaseModel):
    """Response body for POST /extractions/ai-assist (202 Accepted)."""

    job_id: str
    status: str
    paper_count: int


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


async def _resolve_paper_title(candidate_paper_id: int, db: AsyncSession) -> str | None:
    """Return the title of the Paper linked to *candidate_paper_id*.

    Args:
        candidate_paper_id: The candidate paper to look up.
        db: Active async database session.

    Returns:
        The paper title string, or ``None`` if not found.

    """
    result = await db.execute(
        select(Paper.title)
        .join(CandidatePaper, CandidatePaper.paper_id == Paper.id)
        .where(CandidatePaper.id == candidate_paper_id)
    )
    row = result.one_or_none()
    return row[0] if row else None


def _to_response(
    extraction: TertiaryDataExtraction,
    paper_title: str | None,
) -> TertiaryExtractionResponse:
    """Convert an ORM extraction record to a response model.

    Args:
        extraction: The :class:`TertiaryDataExtraction` ORM instance.
        paper_title: Pre-resolved paper title for this extraction.

    Returns:
        :class:`TertiaryExtractionResponse`.

    """
    return TertiaryExtractionResponse(
        id=extraction.id,
        candidate_paper_id=extraction.candidate_paper_id,
        paper_title=paper_title,
        secondary_study_type=extraction.secondary_study_type,
        research_questions_addressed=extraction.research_questions_addressed,
        databases_searched=extraction.databases_searched,
        study_period_start=extraction.study_period_start,
        study_period_end=extraction.study_period_end,
        primary_study_count=extraction.primary_study_count,
        synthesis_approach_used=extraction.synthesis_approach_used,
        key_findings=extraction.key_findings,
        research_gaps=extraction.research_gaps,
        reviewer_quality_rating=extraction.reviewer_quality_rating,
        extraction_status=extraction.extraction_status,
        extracted_by_agent=extraction.extracted_by_agent,
        validated_by_reviewer_id=extraction.validated_by_reviewer_id,
        version_id=extraction.version_id,
        created_at=extraction.created_at,
        updated_at=extraction.updated_at,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/extractions",
    response_model=list[TertiaryExtractionResponse],
    summary="List tertiary extraction records",
)
async def list_extractions(
    study_id: int,
    extraction_status: str | None = Query(default=None, alias="status"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TertiaryExtractionResponse]:
    """List all TertiaryDataExtraction records for a study.

    Auto-creates pending extraction stubs for any accepted papers that do not
    yet have a record before returning the list.

    Args:
        study_id: The Tertiary Study whose extractions to list.
        extraction_status: Optional filter by extraction status.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        List of :class:`TertiaryExtractionResponse`.

    Raises:
        HTTPException: 404 if study not found or not of type TERTIARY.

    """
    await _require_tertiary_study(study_id, current_user, db)

    # Ensure stubs exist for all accepted papers.
    await _svc.ensure_extraction_records(study_id, db)
    await db.commit()

    # Fetch all extractions for this study via CandidatePaper join.
    query = (
        select(TertiaryDataExtraction)
        .join(CandidatePaper, TertiaryDataExtraction.candidate_paper_id == CandidatePaper.id)
        .where(CandidatePaper.study_id == study_id)
    )
    if extraction_status:
        query = query.where(TertiaryDataExtraction.extraction_status == extraction_status)

    result = await db.execute(query)
    extractions = list(result.scalars().all())

    # Bulk-resolve paper titles.
    title_map: dict[int, str | None] = {}
    if extractions:
        cp_ids = [e.candidate_paper_id for e in extractions]
        titles_result = await db.execute(
            select(CandidatePaper.id, Paper.title)
            .join(Paper, CandidatePaper.paper_id == Paper.id)
            .where(CandidatePaper.id.in_(cp_ids))
        )
        title_map = {row[0]: row[1] for row in titles_result.all()}

    return [_to_response(e, title_map.get(e.candidate_paper_id)) for e in extractions]


@router.get(
    "/studies/{study_id}/extractions/{extraction_id}",
    response_model=TertiaryExtractionResponse,
    summary="Get a single tertiary extraction record",
)
async def get_extraction(
    study_id: int,
    extraction_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TertiaryExtractionResponse:
    """Fetch a single extraction record, verifying it belongs to *study_id*.

    Args:
        study_id: The Tertiary Study that owns the extraction.
        extraction_id: Primary key of the extraction record.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        :class:`TertiaryExtractionResponse`.

    Raises:
        HTTPException: 404 if study or extraction not found.

    """
    await _require_tertiary_study(study_id, current_user, db)

    result = await db.execute(
        select(TertiaryDataExtraction)
        .join(CandidatePaper, TertiaryDataExtraction.candidate_paper_id == CandidatePaper.id)
        .where(
            TertiaryDataExtraction.id == extraction_id,
            CandidatePaper.study_id == study_id,
        )
    )
    extraction = result.scalar_one_or_none()
    if extraction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extraction record not found.",
        )

    title = await _resolve_paper_title(extraction.candidate_paper_id, db)
    return _to_response(extraction, title)


@router.put(
    "/studies/{study_id}/extractions/{extraction_id}",
    response_model=TertiaryExtractionResponse,
    summary="Update a tertiary extraction record",
)
async def update_extraction(
    study_id: int,
    extraction_id: int,
    body: TertiaryExtractionUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TertiaryExtractionResponse:
    """Update extraction fields (human review).

    Performs an optimistic-lock check on ``version_id`` when provided.

    Args:
        study_id: The Tertiary Study that owns the extraction.
        extraction_id: Primary key of the extraction record.
        body: Fields to update (all optional).
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        The updated :class:`TertiaryExtractionResponse`.

    Raises:
        HTTPException: 404 if study or extraction not found.
        HTTPException: 409 if ``version_id`` is stale.

    """
    await _require_tertiary_study(study_id, current_user, db)

    result = await db.execute(
        select(TertiaryDataExtraction)
        .join(CandidatePaper, TertiaryDataExtraction.candidate_paper_id == CandidatePaper.id)
        .where(
            TertiaryDataExtraction.id == extraction_id,
            CandidatePaper.study_id == study_id,
        )
    )
    extraction = result.scalar_one_or_none()
    if extraction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extraction record not found.",
        )

    if body.version_id is not None and body.version_id != extraction.version_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Extraction was modified by another request (version_id mismatch).",
        )

    update_data: dict[str, Any] = body.model_dump(exclude={"version_id"}, exclude_none=True)
    for field, value in update_data.items():
        setattr(extraction, field, value)

    await db.commit()
    await db.refresh(extraction)

    _structlog.info(
        "tertiary_extraction_updated",
        study_id=study_id,
        extraction_id=extraction_id,
        status=extraction.extraction_status,
    )

    title = await _resolve_paper_title(extraction.candidate_paper_id, db)
    return _to_response(extraction, title)


@router.post(
    "/studies/{study_id}/extractions/ai-assist",
    response_model=AiAssistResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger AI-assisted extraction pre-fill",
)
async def ai_assist_extractions(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AiAssistResponse:
    """Enqueue an ARQ job to AI-pre-fill all pending extraction records.

    Args:
        study_id: The Tertiary Study to process.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        :class:`AiAssistResponse` with job_id, status, and paper_count.

    Raises:
        HTTPException: 404 if study not found or not TERTIARY type.
        HTTPException: 503 if the job could not be enqueued.

    """
    await _require_tertiary_study(study_id, current_user, db)

    # Count pending extractions to include in the response.
    count_result = await db.execute(
        select(TertiaryDataExtraction)
        .join(CandidatePaper, TertiaryDataExtraction.candidate_paper_id == CandidatePaper.id)
        .where(
            CandidatePaper.study_id == study_id,
            TertiaryDataExtraction.extraction_status == "pending",
        )
    )
    pending_count = len(list(count_result.scalars().all()))

    settings = get_settings()
    arq_pool = await arq.connections.create_pool(
        arq.connections.RedisSettings.from_dsn(settings.redis_url)
    )
    try:
        job = await arq_pool.enqueue_job("run_tertiary_extraction", study_id=study_id)
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to enqueue extraction job.",
            )
        job_id: str = job.job_id
    finally:
        await arq_pool.close()

    _structlog.info(
        "tertiary_ai_assist_enqueued",
        study_id=study_id,
        job_id=job_id,
        paper_count=pending_count,
    )
    return AiAssistResponse(job_id=job_id, status="queued", paper_count=pending_count)
