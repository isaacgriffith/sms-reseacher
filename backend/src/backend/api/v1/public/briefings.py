"""Unauthenticated public Evidence Briefing access endpoints (feature 008).

Routes (no JWT required):
- GET /public/briefings/{token}         -> PublicBriefingResponse
- GET /public/briefings/{token}/export  -> FileResponse (format=pdf|html)

Access control is enforced by the share token mechanism rather than by
standard JWT middleware.  Each token is cryptographically random and
revocable by any study team member.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from db.models.rapid_review import RRThreatToValidity
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services import evidence_briefing_service

router = APIRouter(tags=["public-briefing"])
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class ThreatResponse(BaseModel):
    """Public representation of a threat-to-validity entry."""

    id: int
    threat_type: str
    description: str
    source_detail: str | None

    model_config = {"from_attributes": True}


class PublicBriefingResponse(BaseModel):
    """Evidence Briefing response for unauthenticated public access.

    Excludes internal file paths and sensitive IDs.
    """

    study_id: int
    version_number: int
    status: str
    title: str
    summary: str
    findings: dict
    target_audience: str
    reference_complementary: str | None
    institution_logos: list | None
    threats: list[ThreatResponse]
    generated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_threats(study_id: int, db: AsyncSession) -> list[RRThreatToValidity]:
    """Fetch all threats to validity for a study.

    Args:
        study_id: The Rapid Review study to query.
        db: Active async database session.

    Returns:
        List of :class:`RRThreatToValidity` records.

    """
    result = await db.execute(
        select(RRThreatToValidity).where(RRThreatToValidity.study_id == study_id)
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/briefings/{token}",
    response_model=PublicBriefingResponse,
    summary="Retrieve a published Evidence Briefing via share token",
)
async def get_public_briefing(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> PublicBriefingResponse:
    """Return the currently published Evidence Briefing identified by a share token.

    No authentication is required.  The token must be valid (not revoked and
    not expired).

    Args:
        token: The opaque share token from the URL path.
        db: Injected async database session.

    Returns:
        :class:`PublicBriefingResponse` with briefing content and threats.

    Raises:
        HTTPException: 404 if the token is invalid, revoked, expired, or no
            published briefing exists.

    """
    briefing = await evidence_briefing_service.resolve_token(token, db)
    threats = await _get_threats(briefing.study_id, db)

    threat_responses = [
        ThreatResponse(
            id=t.id,
            threat_type=t.threat_type.value,
            description=t.description,
            source_detail=t.source_detail,
        )
        for t in threats
    ]

    return PublicBriefingResponse(
        study_id=briefing.study_id,
        version_number=briefing.version_number,
        status=briefing.status.value,
        title=briefing.title,
        summary=briefing.summary,
        findings=briefing.findings,
        target_audience=briefing.target_audience,
        reference_complementary=briefing.reference_complementary,
        institution_logos=briefing.institution_logos,
        threats=threat_responses,
        generated_at=briefing.generated_at,
    )


@router.get(
    "/briefings/{token}/export",
    summary="Download a published Evidence Briefing export via share token",
)
async def export_public_briefing(
    token: str,
    format: Literal["pdf", "html"] = Query(..., description="Export format: pdf or html"),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Download the PDF or HTML export of the published briefing for a token.

    No authentication is required.

    Args:
        token: The opaque share token from the URL path.
        format: Desired export format — ``"pdf"`` or ``"html"``.
        db: Injected async database session.

    Returns:
        :class:`~fastapi.responses.FileResponse` with the requested export file.

    Raises:
        HTTPException: 404 if the token is invalid or the export does not exist.

    """
    briefing = await evidence_briefing_service.resolve_token(token, db)

    if format == "pdf":
        if briefing.pdf_path is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF export has not been generated for this briefing.",
            )
        file_path = briefing.pdf_path
        media_type = "application/pdf"
        ext = "pdf"
    else:
        if briefing.html_path is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="HTML export has not been generated for this briefing.",
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
