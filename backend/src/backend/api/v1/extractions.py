"""Extraction endpoints: list, detail, patch with optimistic locking, batch-run."""

from datetime import UTC, datetime

import arq.connections
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import StaleDataError

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db

router = APIRouter(tags=["extractions"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Response / request schemas
# ---------------------------------------------------------------------------


class FieldAuditResponse(BaseModel):
    """One field-level edit record."""

    id: int
    field_name: str
    original_value: object
    new_value: object
    changed_by_user_id: int
    changed_at: datetime


class ExtractionResponse(BaseModel):
    """Full data extraction for a candidate paper."""

    id: int
    candidate_paper_id: int
    research_type: str
    venue_type: str
    venue_name: str | None
    author_details: list | None
    summary: str | None
    open_codings: list | None
    keywords: list | None
    question_data: dict | None
    extraction_status: str
    version_id: int
    extracted_by_agent: str | None
    validated_by_reviewer_id: int | None
    conflict_flag: bool
    created_at: datetime
    updated_at: datetime
    audit_history: list[FieldAuditResponse] = []


class PatchExtractionRequest(BaseModel):
    """Body for PATCH /studies/{study_id}/extractions/{id}.

    ``version_id`` must match the current DB value (optimistic locking).
    Only fields that are present (non-None) are applied; omitting a field
    means "leave unchanged".
    """

    version_id: int
    venue_type: str | None = None
    venue_name: str | None = None
    author_details: list | None = None
    summary: str | None = None
    open_codings: list | None = None
    keywords: list | None = None
    question_data: dict | None = None
    research_type: str | None = None


class ReviewExtractionRequest(BaseModel):
    """Body for POST /studies/{study_id}/extractions/{id}/review.

    ``version_id`` must match the current DB value, the same optimistic-locking
    contract :class:`PatchExtractionRequest` uses. Nothing else is accepted:
    appraisal records *that* a human checked the extraction, never *what* it
    says. An endpoint that could do both would let "confirmed as written" and
    "rewritten" arrive as one indistinguishable event.
    """

    version_id: int


class BatchRunResponse(BaseModel):
    """Response for POST batch-run."""

    job_id: str
    study_id: int


class ConflictResponse(BaseModel):
    """HTTP 409 body when a stale version_id is detected."""

    error: str
    your_version: dict
    current_version: dict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_PATCHABLE_FIELDS = (
    "venue_type",
    "venue_name",
    "author_details",
    "summary",
    "open_codings",
    "keywords",
    "question_data",
    "research_type",
)


async def _load_extraction(study_id: int, extraction_id: int, db: AsyncSession):
    """Load a DataExtraction that belongs to the given study, or raise 404.

    Args:
        study_id: Owning study.
        extraction_id: DataExtraction primary key.
        db: Active async session.

    Returns:
        The :class:`DataExtraction` instance.

    Raises:
        HTTPException: 404 if the extraction does not exist or is not in
            the specified study.

    """
    from db.models.candidate import CandidatePaper
    from db.models.extraction import DataExtraction

    result = await db.execute(
        select(DataExtraction)
        .join(CandidatePaper, DataExtraction.candidate_paper_id == CandidatePaper.id)
        .where(
            DataExtraction.id == extraction_id,
            CandidatePaper.study_id == study_id,
        )
    )
    extraction = result.scalar_one_or_none()
    if extraction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extraction not found")
    return extraction


def _to_extraction_dict(extraction) -> dict:
    """Serialize a DataExtraction to a plain dict for conflict responses.

    Args:
        extraction: The :class:`DataExtraction` ORM instance.

    Returns:
        A JSON-serialisable dict of extraction fields.

    """
    return {
        "id": extraction.id,
        "candidate_paper_id": extraction.candidate_paper_id,
        "research_type": extraction.research_type.value
        if hasattr(extraction.research_type, "value")
        else str(extraction.research_type),
        "venue_type": extraction.venue_type,
        "venue_name": extraction.venue_name,
        "author_details": extraction.author_details,
        "summary": extraction.summary,
        "open_codings": extraction.open_codings,
        "keywords": extraction.keywords,
        "question_data": extraction.question_data,
        "extraction_status": extraction.extraction_status.value
        if hasattr(extraction.extraction_status, "value")
        else str(extraction.extraction_status),
        "version_id": extraction.version_id,
        "conflict_flag": extraction.conflict_flag,
    }


def _to_extraction_response(extraction, audit_rows: list) -> ExtractionResponse:
    """Build an ExtractionResponse from an ORM row.

    Args:
        extraction: :class:`DataExtraction` ORM instance.
        audit_rows: List of :class:`ExtractionFieldAudit` instances.

    Returns:
        A populated :class:`ExtractionResponse`.

    """
    return ExtractionResponse(
        id=extraction.id,
        candidate_paper_id=extraction.candidate_paper_id,
        research_type=extraction.research_type.value
        if hasattr(extraction.research_type, "value")
        else str(extraction.research_type),
        venue_type=extraction.venue_type,
        venue_name=extraction.venue_name,
        author_details=extraction.author_details,
        summary=extraction.summary,
        open_codings=extraction.open_codings,
        keywords=extraction.keywords,
        question_data=extraction.question_data,
        extraction_status=extraction.extraction_status.value
        if hasattr(extraction.extraction_status, "value")
        else str(extraction.extraction_status),
        version_id=extraction.version_id,
        extracted_by_agent=extraction.extracted_by_agent,
        validated_by_reviewer_id=extraction.validated_by_reviewer_id,
        conflict_flag=extraction.conflict_flag,
        created_at=extraction.created_at,
        updated_at=extraction.updated_at,
        audit_history=[
            FieldAuditResponse(
                id=a.id,
                field_name=a.field_name,
                original_value=a.original_value,
                new_value=a.new_value,
                changed_by_user_id=a.changed_by_user_id,
                changed_at=a.changed_at,
            )
            for a in audit_rows
        ],
    )


# ---------------------------------------------------------------------------
# T086: GET list + detail + batch-run
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/extractions",
    response_model=list[ExtractionResponse],
    summary="List extractions for a study",
)
async def list_extractions(
    study_id: int,
    extraction_status: str | None = Query(None, alias="status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ExtractionResponse]:
    """Return paginated extractions, optionally filtered by status."""
    await require_study_member(study_id, current_user, db)

    from db.models.candidate import CandidatePaper
    from db.models.extraction import DataExtraction

    query = (
        select(DataExtraction)
        .join(CandidatePaper, DataExtraction.candidate_paper_id == CandidatePaper.id)
        .where(CandidatePaper.study_id == study_id)
    )
    if extraction_status:
        query = query.where(DataExtraction.extraction_status == extraction_status)

    query = query.order_by(DataExtraction.id).offset(offset).limit(limit)
    result = await db.execute(query)
    extractions = result.scalars().all()
    return [_to_extraction_response(e, []) for e in extractions]


@router.get(
    "/studies/{study_id}/extractions/{extraction_id}",
    response_model=ExtractionResponse,
    summary="Get a single extraction with audit history",
)
async def get_extraction(
    study_id: int,
    extraction_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExtractionResponse:
    """Return one extraction with its full field-edit audit history."""
    await require_study_member(study_id, current_user, db)

    from db.models.extraction import ExtractionFieldAudit

    extraction = await _load_extraction(study_id, extraction_id, db)

    audit_result = await db.execute(
        select(ExtractionFieldAudit)
        .where(ExtractionFieldAudit.extraction_id == extraction_id)
        .order_by(ExtractionFieldAudit.changed_at)
    )
    audit_rows = list(audit_result.scalars().all())
    return _to_extraction_response(extraction, audit_rows)


@router.post(
    "/studies/{study_id}/extractions/batch-run",
    response_model=BatchRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enqueue a batch extraction job",
)
async def batch_run_extractions(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BatchRunResponse:
    """Enqueue a background job to extract all accepted papers in the study."""
    from datetime import datetime

    from db.models.jobs import BackgroundJob, JobStatus, JobType

    from backend.core.config import get_settings

    await require_study_member(study_id, current_user, db)

    settings = get_settings()
    redis = await arq.connections.create_pool(
        arq.connections.RedisSettings.from_dsn(settings.redis_url)
    )
    job = await redis.enqueue_job("run_batch_extraction", study_id)
    await redis.close()

    job_id = (
        job.job_id if job else f"batch_extraction_{study_id}_{int(datetime.now(UTC).timestamp())}"
    )

    bg_job = BackgroundJob(
        id=job_id,
        study_id=study_id,
        job_type=JobType.BATCH_EXTRACTION,
        status=JobStatus.QUEUED,
    )
    db.add(bg_job)
    await db.commit()

    logger.info("batch_run_extractions: enqueued", study_id=study_id, job_id=job_id)
    return BatchRunResponse(job_id=job_id, study_id=study_id)


# ---------------------------------------------------------------------------
# T087: PATCH with optimistic locking + field audit
# ---------------------------------------------------------------------------


@router.patch(
    "/studies/{study_id}/extractions/{extraction_id}",
    response_model=ExtractionResponse,
    summary="Update extraction fields (optimistic locking)",
    responses={
        409: {
            "description": "Concurrent edit conflict — version_id is stale",
            "model": ConflictResponse,
        }
    },
)
async def patch_extraction(
    study_id: int,
    extraction_id: int,
    body: PatchExtractionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExtractionResponse:
    """Apply field-level edits with optimistic locking.

    SQLAlchemy's version_id_col increments automatically on each UPDATE.
    If ``body.version_id`` does not match the DB row, SQLAlchemy raises
    :class:`StaleDataError` after ``session.flush()``. This endpoint
    catches that error, rolls back, re-queries the current state, and
    returns HTTP 409 with both the caller's submitted version and the
    current DB version so the client can show a diff/merge UI.

    On success, creates an :class:`ExtractionFieldAudit` row for each
    changed field.
    """
    await require_study_member(study_id, current_user, db)

    from db.models.extraction import ExtractionFieldAudit, ExtractionStatus

    extraction = await _load_extraction(study_id, extraction_id, db)

    # Explicit optimistic locking check — reliable across PostgreSQL and SQLite.
    # SQLAlchemy's StaleDataError is a fallback for cases where the DB-level row
    # count is 0; the explicit check here ensures the 409 response is always
    # returned when the caller's version_id differs from the current DB value.
    if extraction.version_id != body.version_id:
        submitted_dict = _to_extraction_dict(extraction)
        submitted_dict["version_id"] = body.version_id
        current_dict = _to_extraction_dict(extraction)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "conflict",
                "your_version": submitted_dict,
                "current_version": current_dict,
            },
        )

    # Stash submitted state for any StaleDataError fallback below
    submitted_dict = _to_extraction_dict(extraction)

    changed_fields: list[tuple[str, object, object]] = []
    for field in _PATCHABLE_FIELDS:
        new_val = getattr(body, field)
        if new_val is None:
            continue
        old_val = getattr(extraction, field)
        # Normalise enum values for comparison
        old_cmp = old_val.value if hasattr(old_val, "value") else old_val
        if old_cmp != new_val:
            changed_fields.append((field, old_cmp, new_val))
            setattr(extraction, field, new_val)

    if changed_fields:
        extraction.extraction_status = ExtractionStatus.HUMAN_REVIEWED

    try:
        await db.flush()
    except StaleDataError as exc:
        await db.rollback()
        fresh = await _load_extraction(study_id, extraction_id, db)
        current_dict = _to_extraction_dict(fresh)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "conflict",
                "your_version": submitted_dict,
                "current_version": current_dict,
            },
        ) from exc

    # Create audit rows for each changed field
    for field_name, original, new_value in changed_fields:
        audit = ExtractionFieldAudit(
            extraction_id=extraction_id,
            field_name=field_name,
            original_value=original if isinstance(original, (dict, list)) else str(original),
            new_value=new_value if isinstance(new_value, (dict, list)) else str(new_value),
            changed_by_user_id=current_user.user_id,
        )
        db.add(audit)

    await db.commit()
    await db.refresh(extraction)

    audit_result = await db.execute(
        select(ExtractionFieldAudit)
        .where(ExtractionFieldAudit.extraction_id == extraction_id)
        .order_by(ExtractionFieldAudit.changed_at)
    )
    audit_rows = list(audit_result.scalars().all())
    return _to_extraction_response(extraction, audit_rows)


# ---------------------------------------------------------------------------
# TFIX10: recording an appraisal that changes nothing
# ---------------------------------------------------------------------------


@router.post(
    "/studies/{study_id}/extractions/{extraction_id}/review",
    response_model=ExtractionResponse,
    summary="Record that a human has appraised this extraction",
    responses={
        409: {
            "description": "Concurrent edit conflict — version_id is stale",
            "model": ConflictResponse,
        },
        422: {"description": "The extraction is still pending — there is nothing to appraise"},
    },
)
async def review_extraction(
    study_id: int,
    extraction_id: int,
    body: ReviewExtractionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExtractionResponse:
    """Mark an extraction human-reviewed without altering any extracted field.

    ``patch_extraction`` promotes an extraction to ``human_reviewed`` only when
    a field value actually changes, so agreement was previously unrecordable:
    a reviewer who read an AI pre-fill and found it correct left it sitting at
    ``ai_complete`` indefinitely. That matters now that ``phase_gate`` no
    longer accepts ``ai_complete`` (TFIX10) — without this endpoint the gate
    would ask "did somebody *edit* the AI?" while claiming to ask "did somebody
    *check* it", and would pay reviewers in unlocked phases for making a token
    edit that invents a disagreement. ``01-slr.md`` 2.4 objects to "extraction
    decoupled from appraisal"; appraisal that confirms is still appraisal.

    Idempotent: an extraction already at ``human_reviewed`` or ``validated`` is
    returned unchanged, without an UPDATE, so a repeated click cannot bump
    ``version_id`` out from under someone else's open edit form.

    Args:
        study_id: Study owning the extraction; caller must be a member.
        extraction_id: The extraction to mark reviewed.
        body: Carries the caller's observed ``version_id``.
        current_user: Authenticated caller, resolved to a study Reviewer.
        db: Active async session.

    Returns:
        The extraction, with its audit history.

    Raises:
        HTTPException: 404 if the extraction is not in this study, 409 if
            ``version_id`` is stale, 422 if the extraction is still pending.

    """
    from db.models.extraction import ExtractionFieldAudit, ExtractionStatus

    from backend.api.v1.papers import resolve_session_reviewer

    await require_study_member(study_id, current_user, db)

    extraction = await _load_extraction(study_id, extraction_id, db)

    if extraction.extraction_status == ExtractionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Extraction is still pending — there is no extracted data to appraise. "
                "Run extraction first, or enter the data directly."
            ),
        )

    if extraction.version_id != body.version_id:
        current_dict = _to_extraction_dict(extraction)
        submitted_dict = dict(current_dict)
        submitted_dict["version_id"] = body.version_id
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "conflict",
                "your_version": submitted_dict,
                "current_version": current_dict,
            },
        )

    already_appraised = extraction.extraction_status in (
        ExtractionStatus.HUMAN_REVIEWED,
        ExtractionStatus.VALIDATED,
    )
    if not already_appraised:
        reviewer = await resolve_session_reviewer(study_id, current_user, db)
        extraction.extraction_status = ExtractionStatus.HUMAN_REVIEWED
        # Who appraised it. The column predates this endpoint and is read back
        # by both extraction APIs, but nothing had ever written to it.
        extraction.validated_by_reviewer_id = reviewer.id
        await db.commit()
        await db.refresh(extraction)
        logger.info(
            "review_extraction: marked human_reviewed",
            study_id=study_id,
            extraction_id=extraction_id,
            reviewer_id=reviewer.id,
        )

    audit_result = await db.execute(
        select(ExtractionFieldAudit)
        .where(ExtractionFieldAudit.extraction_id == extraction_id)
        .order_by(ExtractionFieldAudit.changed_at)
    )
    return _to_extraction_response(extraction, list(audit_result.scalars().all()))
