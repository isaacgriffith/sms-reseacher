"""SLR phase-gate status endpoint (feature 007).

Routes:
- GET /slr/studies/{study_id}/phases → 200
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.database import get_db
from backend.services.slr_phase_gate import get_slr_unlocked_phases
from backend.services.slr_protocol_service import get_protocol

router = APIRouter(tags=["slr-phases"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class SLRPhasesResponse(BaseModel):
    """Response body for GET /slr/studies/{study_id}/phases."""

    study_id: int
    unlocked_phases: list[int]
    protocol_status: str | None
    quality_complete: bool
    synthesis_complete: bool


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/phases",
    response_model=SLRPhasesResponse,
    summary="Get SLR phase unlock status",
)
async def get_slr_phases(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SLRPhasesResponse:
    """Return the current phase unlock status for an SLR study.

    Computes which phases are accessible based on protocol validation,
    search completion, quality assessment progress, and synthesis status.

    Args:
        study_id: The SLR study to evaluate.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        :class:`SLRPhasesResponse` with unlocked phases and status flags.

    """
    unlocked = await get_slr_unlocked_phases(study_id, db)

    protocol = await get_protocol(study_id, db)
    protocol_status: str | None = protocol.status.value if protocol is not None else None

    quality_complete = 4 in unlocked
    synthesis_complete = 5 in unlocked

    return SLRPhasesResponse(
        study_id=study_id,
        unlocked_phases=unlocked,
        protocol_status=protocol_status,
        quality_complete=quality_complete,
        synthesis_complete=synthesis_complete,
    )
