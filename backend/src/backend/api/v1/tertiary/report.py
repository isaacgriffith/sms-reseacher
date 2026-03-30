"""Tertiary Study report endpoint (feature 009, Phase 7).

Route:
- GET /tertiary/studies/{study_id}/report?format=json|csv|markdown
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services.tertiary_report_service import TertiaryReportService

router = APIRouter(tags=["tertiary-report"])
logger = get_logger(__name__)

_service = TertiaryReportService()

# MIME type and filename suffix by format.
_FORMAT_META: dict[str, tuple[str, str]] = {
    "json": ("application/json", "json"),
    "csv": ("text/csv", "csv"),
    "markdown": ("text/markdown", "md"),
}


@router.get(
    "/studies/{study_id}/report",
    summary="Generate and download a Tertiary Study report",
)
async def get_tertiary_report(
    study_id: int,
    format: str = "json",
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate and stream a Tertiary Study report in the requested format.

    Builds the full report from the study's protocol, synthesis results,
    candidate papers, and tertiary data extractions, including the
    ``landscape_of_secondary_studies`` section.

    Args:
        study_id: The integer ID of the Tertiary Study to report on.
        format: Output format — one of ``json``, ``csv``, ``markdown``.
            Defaults to ``json``.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        A :class:`StreamingResponse` with ``Content-Disposition: attachment``
        and the appropriate ``Content-Type`` header.

    Raises:
        HTTPException: 404 if the study does not exist or is not TERTIARY type.
        HTTPException: 409 if the study has not reached Phase 5 (no completed
            synthesis result).
        HTTPException: 400 if an unsupported format is requested.

    """
    from fastapi import HTTPException, status

    if format not in _FORMAT_META:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f"Unsupported format '{format}'. Choose from: json, csv, markdown."),
        )

    logger.info("get_tertiary_report: request", study_id=study_id, format=format)

    report = await _service.generate_report(study_id, db)

    mime_type, suffix = _FORMAT_META[format]
    filename = f"tertiary-report-{study_id}.{suffix}"

    if format == "json":
        content = report.to_json()
    elif format == "csv":
        content = report.to_csv()
    else:
        content = report.to_markdown()

    return StreamingResponse(
        iter([content]),
        media_type=mime_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
