"""Health-check endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.config import get_logger, get_settings

router = APIRouter(tags=["health"])
logger = get_logger(__name__)


class HealthResponse(BaseModel):
    """Response schema for the health endpoint."""

    status: str
    version: str


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health() -> HealthResponse:
    """Return application health status.

    Deliberately unauthenticated: this endpoint is polled by infrastructure
    that has no credentials — the Docker Compose healthcheck, container
    orchestrators, load balancers, and CI readiness probes. Requiring a JWT
    made every one of those report the service as permanently unhealthy.

    It exposes only liveness and the application version, no user or
    system data.

    Returns:
        A :class:`HealthResponse` with ``status="ok"`` and the
        current application version.

    """
    settings = get_settings()
    logger.debug("health_check_called")
    return HealthResponse(status="ok", version=settings.app_version)
