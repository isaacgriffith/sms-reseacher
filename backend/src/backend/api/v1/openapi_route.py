"""Authenticated OpenAPI schema endpoint."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from backend.core.auth import CurrentUser, get_current_user

router = APIRouter(tags=["openapi"])


@router.get(
    "/openapi.json",
    include_in_schema=False,
    summary="Return the OpenAPI schema (requires authentication)",
)
async def get_openapi_schema(
    request: Request,
    _: CurrentUser = Depends(get_current_user),
) -> JSONResponse:
    """Return the application's OpenAPI schema.

    Args:
        request: The incoming request (used to access the app instance).
        _: Injected current user — ensures only authenticated users can access.

    Returns:
        The full OpenAPI schema as a JSON response.
    """
    return JSONResponse(request.app.openapi())
