"""Rapid Review Evidence Briefing endpoints (feature 008).

Routes:
- GET  /rapid/studies/{study_id}/briefings                     -> list[BriefingSummaryResponse]
- POST /rapid/studies/{study_id}/briefings                     -> 202 with job_id
- GET  /rapid/studies/{study_id}/briefings/{briefing_id}       -> BriefingResponse
- POST /rapid/studies/{study_id}/briefings/{briefing_id}/publish -> BriefingResponse
- GET  /rapid/studies/{study_id}/briefings/{briefing_id}/export  -> FileResponse
- POST /rapid/studies/{study_id}/briefings/{briefing_id}/share-token -> 201 ShareTokenResponse
- DELETE /rapid/studies/{study_id}/briefings/share-token/{token} -> 204
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

import arq.connections
from db.models.jobs import BackgroundJob, JobStatus, JobType
from db.models.rapid_review import EvidenceBriefing
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger, get_settings
from backend.core.database import get_db
from backend.services import evidence_briefing_service, narrative_synthesis_service

router = APIRouter(tags=["rapid-briefing"])
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class BriefingSummaryResponse(BaseModel):
    """Condensed briefing response for list views."""

    id: int
    study_id: int
    version_number: int
    status: str
    title: str
    generated_at: datetime
    pdf_available: bool
    html_available: bool

    model_config = {"from_attributes": True}


class BriefingResponse(BaseModel):
    """Full briefing response including content fields."""

    id: int
    study_id: int
    version_number: int
    status: str
    title: str
    summary: str
    findings: dict
    target_audience: str
    reference_complementary: str | None
    institution_logos: list | None
    generated_at: datetime
    pdf_available: bool
    html_available: bool

    model_config = {"from_attributes": True}


class BriefingJobResponse(BaseModel):
    """Response body for POST /briefings (202 Accepted)."""

    job_id: str
    status: str
    estimated_version_number: int


class ShareTokenResponse(BaseModel):
    """Response body for POST /share-token."""

    token: str
    share_url: str
    briefing_id: int
    created_at: datetime
    revoked_at: datetime | None
    expires_at: datetime | None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_summary(briefing: EvidenceBriefing) -> BriefingSummaryResponse:
    """Build a :class:`BriefingSummaryResponse` from an ORM record.

    Args:
        briefing: The :class:`EvidenceBriefing` ORM instance.

    Returns:
        A populated :class:`BriefingSummaryResponse`.

    """
    return BriefingSummaryResponse(
        id=briefing.id,
        study_id=briefing.study_id,
        version_number=briefing.version_number,
        status=briefing.status.value,
        title=briefing.title,
        generated_at=briefing.generated_at,
        pdf_available=briefing.pdf_path is not None,
        html_available=briefing.html_path is not None,
    )


def _to_full(briefing: EvidenceBriefing) -> BriefingResponse:
    """Build a :class:`BriefingResponse` from an ORM record.

    Args:
        briefing: The :class:`EvidenceBriefing` ORM instance.

    Returns:
        A populated :class:`BriefingResponse`.

    """
    return BriefingResponse(
        id=briefing.id,
        study_id=briefing.study_id,
        version_number=briefing.version_number,
        status=briefing.status.value,
        title=briefing.title,
        summary=briefing.summary,
        findings=briefing.findings,
        target_audience=briefing.target_audience,
        reference_complementary=briefing.reference_complementary,
        institution_logos=briefing.institution_logos,
        generated_at=briefing.generated_at,
        pdf_available=briefing.pdf_path is not None,
        html_available=briefing.html_path is not None,
    )


async def _get_briefing_or_404(
    briefing_id: int,
    study_id: int,
    db: AsyncSession,
) -> EvidenceBriefing:
    """Fetch a briefing by ID and verify it belongs to the given study.

    Args:
        briefing_id: Primary key of the briefing.
        study_id: Expected owning study ID.
        db: Active async database session.

    Returns:
        The :class:`EvidenceBriefing` ORM instance.

    Raises:
        HTTPException: 404 if not found or belongs to a different study.

    """
    result = await db.execute(select(EvidenceBriefing).where(EvidenceBriefing.id == briefing_id))
    briefing = result.scalar_one_or_none()
    if briefing is None or briefing.study_id != study_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence Briefing {briefing_id} not found.",
        )
    return briefing


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/briefings",
    response_model=list[BriefingSummaryResponse],
    summary="List Evidence Briefing versions for a study",
)
async def list_briefings(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BriefingSummaryResponse]:
    """Return all Evidence Briefing versions for a study, newest first.

    Args:
        study_id: The Rapid Review study to query.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        List of :class:`BriefingSummaryResponse` ordered by version descending.

    """
    await require_study_member(study_id, current_user, db)
    briefings = await evidence_briefing_service.get_briefings_for_study(study_id, db)
    return [_to_summary(b) for b in briefings]


@router.post(
    "/studies/{study_id}/briefings",
    response_model=BriefingJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enqueue Evidence Briefing generation",
)
async def create_briefing(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BriefingJobResponse:
    """Create a new Evidence Briefing version and enqueue HTML/PDF generation.

    Requires all narrative synthesis sections to be complete (``is_complete=True``).

    Args:
        study_id: The Rapid Review study to generate a briefing for.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        :class:`BriefingJobResponse` with job ID and estimated version number.

    Raises:
        HTTPException: 422 if synthesis is not complete.

    """
    await require_study_member(study_id, current_user, db)

    # Gate on synthesis completion
    synthesis_done = await narrative_synthesis_service.is_synthesis_complete(study_id, db)
    if not synthesis_done:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "All narrative synthesis sections must be marked complete "
                "before generating an Evidence Briefing."
            ),
        )

    # Create briefing record
    briefing = await evidence_briefing_service.create_new_version(study_id, db)

    # Build job ID
    ts = int(datetime.now(UTC).timestamp())
    job_id = f"rr_briefing_{briefing.id}_{ts}"

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
        await arq_pool.enqueue_job(
            "run_generate_evidence_briefing",
            briefing_id=briefing.id,
            _job_id=job_id,
        )
    finally:
        await arq_pool.close()

    logger.info(
        "evidence_briefing_enqueued",
        study_id=study_id,
        briefing_id=briefing.id,
        job_id=job_id,
    )
    return BriefingJobResponse(
        job_id=job_id,
        status="queued",
        estimated_version_number=briefing.version_number,
    )


@router.get(
    "/studies/{study_id}/briefings/{briefing_id}",
    response_model=BriefingResponse,
    summary="Get a specific Evidence Briefing version",
)
async def get_briefing(
    study_id: int,
    briefing_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BriefingResponse:
    """Return full details of a specific Evidence Briefing version.

    Args:
        study_id: The owning Rapid Review study.
        briefing_id: Primary key of the briefing to retrieve.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        :class:`BriefingResponse` with all content fields.

    Raises:
        HTTPException: 404 if the briefing does not exist or belongs to a
            different study.

    """
    await require_study_member(study_id, current_user, db)
    briefing = await _get_briefing_or_404(briefing_id, study_id, db)
    return _to_full(briefing)


@router.post(
    "/studies/{study_id}/briefings/{briefing_id}/publish",
    response_model=BriefingResponse,
    summary="Publish an Evidence Briefing version",
)
async def publish_briefing(
    study_id: int,
    briefing_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BriefingResponse:
    """Atomically promote a briefing version to PUBLISHED status.

    Any previously published version for the same study is demoted to DRAFT.

    Args:
        study_id: The owning Rapid Review study.
        briefing_id: Primary key of the briefing to publish.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        Updated :class:`BriefingResponse` with ``status=published``.

    Raises:
        HTTPException: 404 if the briefing is not found.

    """
    await require_study_member(study_id, current_user, db)
    await _get_briefing_or_404(briefing_id, study_id, db)
    briefing = await evidence_briefing_service.publish_version(briefing_id, db)
    return _to_full(briefing)


@router.get(
    "/studies/{study_id}/briefings/{briefing_id}/export",
    summary="Download a rendered Evidence Briefing as PDF or HTML",
)
async def export_briefing(
    study_id: int,
    briefing_id: int,
    format: Literal["pdf", "html"] = Query(..., description="Export format: pdf or html"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Download the rendered PDF or HTML export of an Evidence Briefing.

    Args:
        study_id: The owning Rapid Review study.
        briefing_id: Primary key of the briefing to export.
        format: Desired export format — ``"pdf"`` or ``"html"``.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        :class:`~fastapi.responses.FileResponse` with the requested file.

    Raises:
        HTTPException: 404 if the briefing or the requested export file does
            not exist.

    """
    await require_study_member(study_id, current_user, db)
    briefing = await _get_briefing_or_404(briefing_id, study_id, db)

    if format == "pdf":
        if briefing.pdf_path is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF export has not been generated yet for this briefing.",
            )
        file_path = briefing.pdf_path
        media_type = "application/pdf"
        ext = "pdf"
    else:
        if briefing.html_path is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="HTML export has not been generated yet for this briefing.",
            )
        file_path = briefing.html_path
        media_type = "text/html"
        ext = "html"

    filename = f"evidence-briefing-v{briefing.version_number}.{ext}"
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/studies/{study_id}/briefings/{briefing_id}/share-token",
    response_model=ShareTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a share token for unauthenticated briefing access",
)
async def create_share_token(
    study_id: int,
    briefing_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShareTokenResponse:
    """Generate an opaque share token for the study's published briefing.

    The token always resolves to the currently published version, not the
    specific version recorded at token creation time.

    Args:
        study_id: The owning Rapid Review study.
        briefing_id: Primary key of the briefing to associate the token with.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Returns:
        :class:`ShareTokenResponse` with the token and share URL.

    Raises:
        HTTPException: 404 if the briefing is not found.
        HTTPException: 422 if no published version exists for the study.

    """
    await require_study_member(study_id, current_user, db)
    await _get_briefing_or_404(briefing_id, study_id, db)

    token_record = await evidence_briefing_service.create_share_token(
        briefing_id=briefing_id,
        created_by_user_id=current_user.user_id,
        db=db,
    )

    return ShareTokenResponse(
        token=token_record.token,
        share_url=f"/public/briefings/{token_record.token}",
        briefing_id=token_record.briefing_id,
        created_at=token_record.created_at,
        revoked_at=token_record.revoked_at,
        expires_at=token_record.expires_at,
    )


@router.delete(
    "/studies/{study_id}/briefings/share-token/{token}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a share token",
)
async def revoke_share_token(
    study_id: int,
    token: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Revoke a share token, preventing future access via that token.

    Args:
        study_id: The owning Rapid Review study (used for membership check).
        token: The raw token string to revoke.
        current_user: JWT-authenticated user; must be a study member.
        db: Injected async database session.

    Raises:
        HTTPException: 404 if the token is not found.

    """
    await require_study_member(study_id, current_user, db)
    await evidence_briefing_service.revoke_token(token, db)
    logger.info("share_token_revoked_by_user", study_id=study_id, user_id=current_user.user_id)
