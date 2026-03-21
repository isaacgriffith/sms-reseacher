"""SLR data synthesis endpoints (feature 007).

Routes:
- GET  /slr/studies/{study_id}/synthesis       → 200
- POST /slr/studies/{study_id}/synthesis       → 202
- GET  /slr/synthesis/{synthesis_id}           → 200 | 404
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import arq.connections
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger, get_settings
from backend.core.database import get_db
from backend.services import synthesis_service

router = APIRouter(tags=["slr-synthesis"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class SynthesisResultResponse(BaseModel):
    """Single synthesis result record.

    Attributes:
        id: Primary key.
        study_id: FK to the owning study.
        approach: Synthesis method (meta_analysis / descriptive / qualitative).
        status: Execution state (pending / running / completed / failed).
        model_type: "fixed" or "random" for meta-analysis runs; None otherwise.
        parameters: Input configuration dict.
        computed_statistics: Pooled/tabulated numeric results.
        forest_plot_svg: SVG string for descriptive forest plot.
        funnel_plot_svg: SVG string for meta-analysis funnel plot.
        qualitative_themes: Theme-to-paper mapping.
        sensitivity_analysis: Subset re-run results.
        error_message: Error detail when status is "failed".
        created_at: Record creation timestamp.
        updated_at: Last modification timestamp.

    """

    id: int
    study_id: int
    approach: str
    status: str
    model_type: str | None
    parameters: dict[str, Any] | None
    computed_statistics: dict[str, Any] | None
    forest_plot_svg: str | None
    funnel_plot_svg: str | None
    qualitative_themes: dict[str, Any] | None
    sensitivity_analysis: dict[str, Any] | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SynthesisListResponse(BaseModel):
    """List of synthesis results for a study."""

    results: list[SynthesisResultResponse]


class StartSynthesisRequest(BaseModel):
    """Request body to start a new synthesis run.

    Attributes:
        approach: Synthesis method ("meta_analysis", "descriptive",
            "qualitative").
        parameters: Approach-specific configuration dict.

    """

    approach: str
    parameters: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/synthesis",
    response_model=SynthesisListResponse,
    summary="List synthesis results for a study",
)
async def list_synthesis_results(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SynthesisListResponse:
    """Return all synthesis results for an SLR study.

    Args:
        study_id: The study whose results to retrieve.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        :class:`SynthesisListResponse` with all records.

    """
    records = await synthesis_service.list_results(study_id, db)
    return SynthesisListResponse(
        results=[SynthesisResultResponse.model_validate(r) for r in records]
    )


@router.post(
    "/studies/{study_id}/synthesis",
    response_model=SynthesisResultResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start a new synthesis run",
)
async def start_synthesis(
    study_id: int,
    body: StartSynthesisRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SynthesisResultResponse:
    """Create a PENDING synthesis record and enqueue the background job.

    Args:
        study_id: The study to synthesise.
        body: Approach and optional parameters.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        The new :class:`SynthesisResultResponse` with ``status="pending"``.

    """
    settings = get_settings()
    arq_pool = await arq.connections.create_pool(
        arq.connections.RedisSettings.from_dsn(settings.redis_url)
    )
    try:
        record = await synthesis_service.start_synthesis(
            study_id=study_id,
            approach=body.approach,
            parameters=body.parameters or {},
            db=db,
            arq_pool=arq_pool,
        )
    finally:
        await arq_pool.close()
    return SynthesisResultResponse.model_validate(record)


@router.get(
    "/synthesis/{synthesis_id}",
    response_model=SynthesisResultResponse,
    summary="Get a synthesis result",
)
async def get_synthesis_result(
    synthesis_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SynthesisResultResponse:
    """Return a single synthesis result by ID.

    Args:
        synthesis_id: Primary key of the synthesis record.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        The :class:`SynthesisResultResponse`.

    Raises:
        HTTPException: 404 if no record is found.

    """
    record = await synthesis_service.get_result(synthesis_id, db)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Synthesis result {synthesis_id} not found.",
        )
    return SynthesisResultResponse.model_validate(record)
