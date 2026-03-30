"""Rapid Review narrative synthesis endpoints (feature 008).

Routes:
- GET  /rapid/studies/{study_id}/synthesis
- PUT  /rapid/studies/{study_id}/synthesis/{section_id}
- POST /rapid/studies/{study_id}/synthesis/{section_id}/ai-draft
- POST /rapid/studies/{study_id}/synthesis/complete
"""

from __future__ import annotations

from datetime import UTC, datetime

import arq.connections
from db.models.jobs import BackgroundJob, JobStatus, JobType
from db.models.rapid_review import RRNarrativeSynthesisSection
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger, get_settings
from backend.core.database import get_db
from backend.services import narrative_synthesis_service, rr_protocol_service

router = APIRouter(tags=["rapid-synthesis"])
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class NarrativeSectionResponse(BaseModel):
    """Response body for a single narrative synthesis section."""

    id: int
    study_id: int
    rq_index: int
    research_question: str
    narrative_text: str | None
    ai_draft_text: str | None
    is_complete: bool
    ai_draft_job_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SectionUpdateRequest(BaseModel):
    """Request body for PUT /synthesis/{section_id}."""

    narrative_text: str | None = None
    is_complete: bool | None = None


class AIDraftResponse(BaseModel):
    """Response body for POST /synthesis/{section_id}/ai-draft."""

    job_id: str
    section_id: int
    status: str


class SynthesisCompleteResponse(BaseModel):
    """Response body for POST /synthesis/complete."""

    synthesis_complete: bool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_active_draft_job_id(
    section_id: int,
    study_id: int,
    db: AsyncSession,
) -> str | None:
    """Return the job ID of an active (QUEUED/RUNNING) draft job for a section.

    Args:
        section_id: The synthesis section primary key.
        study_id: The owning study ID.
        db: Active async database session.

    Returns:
        The job ID string, or ``None`` if no active job exists.

    """
    job_prefix = f"rr_narrative_draft_{section_id}_"
    result = await db.execute(
        select(BackgroundJob).where(
            BackgroundJob.id.like(f"{job_prefix}%"),
            BackgroundJob.study_id == study_id,
            BackgroundJob.status.in_([JobStatus.QUEUED, JobStatus.RUNNING]),
        )
    )
    job = result.scalars().first()
    return job.id if job is not None else None


async def _build_section_response(
    section: RRNarrativeSynthesisSection,
    rqs: list[str],
    db: AsyncSession,
) -> NarrativeSectionResponse:
    """Build a :class:`NarrativeSectionResponse` from a section ORM object.

    Args:
        section: The ORM section record.
        rqs: Research question strings from the protocol.
        db: Active async database session.

    Returns:
        A populated :class:`NarrativeSectionResponse`.

    """
    rq_text = rqs[section.rq_index] if section.rq_index < len(rqs) else ""
    ai_job_id = await _get_active_draft_job_id(section.id, section.study_id, db)
    return NarrativeSectionResponse(
        id=section.id,
        study_id=section.study_id,
        rq_index=section.rq_index,
        research_question=rq_text,
        narrative_text=section.narrative_text,
        ai_draft_text=section.ai_draft_text,
        is_complete=section.is_complete,
        ai_draft_job_id=ai_job_id,
        created_at=section.created_at,
        updated_at=section.updated_at,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/synthesis",
    response_model=list[NarrativeSectionResponse],
    summary="List narrative synthesis sections",
)
async def list_synthesis_sections(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[NarrativeSectionResponse]:
    """Return all narrative synthesis sections for a study.

    Sections are auto-created when the protocol is first validated.  One
    section exists per entry in ``RapidReviewProtocol.research_questions``.

    Args:
        study_id: The Rapid Review study to query.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        List of :class:`NarrativeSectionResponse` ordered by ``rq_index``.

    """
    await require_study_member(study_id, current_user, db)
    protocol = await rr_protocol_service.get_or_create_protocol(study_id, db)
    rqs: list[str] = protocol.research_questions or []
    sections = await narrative_synthesis_service.get_or_create_sections(study_id, db)
    return [await _build_section_response(s, rqs, db) for s in sections]


@router.put(
    "/studies/{study_id}/synthesis/{section_id}",
    response_model=NarrativeSectionResponse,
    summary="Update a narrative synthesis section",
)
async def update_synthesis_section(
    study_id: int,
    section_id: int,
    body: SectionUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NarrativeSectionResponse:
    """Update the narrative text or completion status of a synthesis section.

    Args:
        study_id: The Rapid Review study.
        section_id: Primary key of the section to update.
        body: Fields to update (all optional).
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        Updated :class:`NarrativeSectionResponse`.

    Raises:
        HTTPException: 404 if the section does not exist or belongs to a
            different study.

    """
    await require_study_member(study_id, current_user, db)

    section = await narrative_synthesis_service.update_section(
        section_id=section_id,
        narrative_text=body.narrative_text,
        is_complete=body.is_complete,
        db=db,
    )
    if section is None or section.study_id != study_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Synthesis section {section_id} not found.",
        )

    await db.commit()
    protocol = await rr_protocol_service.get_or_create_protocol(study_id, db)
    rqs: list[str] = protocol.research_questions or []
    return await _build_section_response(section, rqs, db)


@router.post(
    "/studies/{study_id}/synthesis/{section_id}/ai-draft",
    response_model=AIDraftResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enqueue AI narrative draft generation",
)
async def request_ai_draft(
    study_id: int,
    section_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AIDraftResponse:
    """Enqueue an ARQ background job to generate an AI draft for a section.

    Returns ``409 Conflict`` if a draft job is already queued or running for
    this section.

    Args:
        study_id: The Rapid Review study.
        section_id: Primary key of the synthesis section.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        :class:`AIDraftResponse` with job ID and status.

    Raises:
        HTTPException: 404 if the section does not exist.
        HTTPException: 409 if a draft job is already active.

    """
    await require_study_member(study_id, current_user, db)

    # Verify section exists and belongs to study
    section_result = await db.execute(
        select(RRNarrativeSynthesisSection).where(
            RRNarrativeSynthesisSection.id == section_id,
            RRNarrativeSynthesisSection.study_id == study_id,
        )
    )
    section = section_result.scalar_one_or_none()
    if section is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Synthesis section {section_id} not found.",
        )

    # 409 guard: reject if already running
    existing_job_id = await _get_active_draft_job_id(section_id, study_id, db)
    if existing_job_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"An AI draft job is already active for section {section_id}: {existing_job_id}"
            ),
        )

    # Build deterministic-ish job ID
    ts = int(datetime.now(UTC).timestamp())
    job_id = f"rr_narrative_draft_{section_id}_{ts}"

    # Create BackgroundJob record
    bg_job = BackgroundJob(
        id=job_id,
        study_id=study_id,
        job_type=JobType.BATCH_EXTRACTION,  # reuse closest existing type
        status=JobStatus.QUEUED,
    )
    db.add(bg_job)
    await db.commit()

    # Enqueue ARQ job
    settings = get_settings()
    arq_pool = await arq.connections.create_pool(
        arq.connections.RedisSettings.from_dsn(settings.redis_url)
    )
    try:
        await arq_pool.enqueue_job("run_narrative_draft", section_id=section_id, _job_id=job_id)
    finally:
        await arq_pool.close()

    logger.info("ai_draft_enqueued", study_id=study_id, section_id=section_id, job_id=job_id)
    return AIDraftResponse(job_id=job_id, section_id=section_id, status="queued")


@router.post(
    "/studies/{study_id}/synthesis/complete",
    response_model=SynthesisCompleteResponse,
    summary="Finalise narrative synthesis",
)
async def complete_synthesis(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SynthesisCompleteResponse:
    """Mark the overall synthesis as complete, gating Evidence Briefing generation.

    All sections must have ``is_complete = True``.

    Args:
        study_id: The Rapid Review study.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        :class:`SynthesisCompleteResponse` with ``synthesis_complete=True``.

    Raises:
        HTTPException: 422 if any sections are not yet complete.

    """
    await require_study_member(study_id, current_user, db)

    sections = await narrative_synthesis_service.get_or_create_sections(study_id, db)
    incomplete_indices = [s.rq_index for s in sections if not s.is_complete]

    if incomplete_indices:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "detail": (
                    "All synthesis sections must be marked complete before "
                    "synthesis can be finalised."
                ),
                "incomplete_sections": incomplete_indices,
            },
        )

    logger.info("synthesis_complete", study_id=study_id)
    return SynthesisCompleteResponse(synthesis_complete=True)
