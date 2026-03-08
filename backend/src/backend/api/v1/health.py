"""Health-check endpoint."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger, get_settings

router = APIRouter(tags=["health"])
logger = get_logger(__name__)


class HealthResponse(BaseModel):
    """Response schema for the health endpoint."""

    status: str
    version: str


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health(
    _current_user: CurrentUser = Depends(get_current_user),
) -> HealthResponse:
    """Return application health status.

    Args:
        _current_user: Injected via auth stub (unused in MVP).

    Returns:
        A :class:`HealthResponse` with ``status="ok"`` and the
        current application version.
    """
    settings = get_settings()
    logger.debug("health_check_called")
    return HealthResponse(status="ok", version=settings.app_version)
