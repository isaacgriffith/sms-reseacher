"""SLR report export endpoint (feature 007, Phase 8).

Route:
- GET /slr/studies/{study_id}/export/slr-report?format=markdown
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services import slr_report_service

router = APIRouter(tags=["slr-report"])
logger = get_logger(__name__)


@router.get(
    "/studies/{study_id}/export/slr-report",
    summary="Export SLR report in the requested format",
)
async def export_slr_report(
    study_id: int,
    format: str = "markdown",
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Generate and stream an SLR report in the requested format.

    Builds the full SLR report from the study's protocol, synthesis results,
    candidate papers, and data extractions, then serialises it to the
    requested format and returns it as a downloadable attachment.

    Args:
        study_id: The integer ID of the study to report on.
        format: Output format — one of ``markdown``, ``latex``, ``json``, ``csv``.
            Defaults to ``markdown``.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        A :class:`StreamingResponse` with ``Content-Disposition: attachment``
        and the appropriate ``Content-Type`` header.

    Raises:
        HTTPException: 404 if the study does not exist.
        HTTPException: 422 if no completed synthesis result exists.
        HTTPException: 400 if an unsupported format is requested.

    """
    logger.info("export_slr_report: request", study_id=study_id, format=format)

    report = await slr_report_service.generate_report(study_id, db)
    content, mime_type, filename = slr_report_service.export_report(report, format)

    return StreamingResponse(
        iter([content]),
        media_type=mime_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
