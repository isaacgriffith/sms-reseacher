"""PUT /me/password — authenticated password change endpoint."""

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.database import get_db
from backend.services.password_service import change_password

router = APIRouter(tags=["me"])


class PasswordChangeRequest(BaseModel):
    """Request body for PUT /me/password."""

    current_password: str
    new_password: str


class PasswordChangeResponse(BaseModel):
    """Response body for a successful password change."""

    message: str


@router.put(
    "/password",
    response_model=PasswordChangeResponse,
    status_code=status.HTTP_200_OK,
    summary="Change the authenticated user's password",
)
async def change_password_endpoint(
    body: PasswordChangeRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PasswordChangeResponse:
    """Change the password for the authenticated user.

    Verifies the current password, enforces complexity, increments the
    ``token_version`` (invalidating all prior sessions), and logs a security
    audit event.

    Args:
        body: Current and new password supplied by the client.
        request: FastAPI request (used to extract client IP).
        current_user: Injected from the validated JWT.
        db: Injected async database session.

    Returns:
        A confirmation message on success.

    Raises:
        HTTPException: 400 if current password is wrong or new equals current.
        HTTPException: 422 if new password fails complexity requirements.
    """
    ip_address = request.client.host if request.client else None
    await change_password(
        db=db,
        user_id=current_user.user_id,
        current_password=body.current_password,
        new_password=body.new_password,
        ip_address=ip_address,
    )
    return PasswordChangeResponse(message="Password changed successfully")
