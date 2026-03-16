"""POST /me/2fa/* — TOTP enrollment, confirmation, disabling, and backup code endpoints."""

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.database import get_db
from backend.services import totp_service
from db.models.users import User

router = APIRouter(tags=["me"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_user(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


# ---------------------------------------------------------------------------
# POST /me/2fa/setup
# ---------------------------------------------------------------------------


class SetupResponse(BaseModel):
    qr_code_image: str
    manual_key: str
    issuer: str


@router.post(
    "/2fa/setup",
    response_model=SetupResponse,
    status_code=status.HTTP_200_OK,
    summary="Begin 2FA enrollment",
)
async def setup_2fa(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SetupResponse:
    """Initiate 2FA setup — returns a QR code and manual key.

    Args:
        current_user: Injected from the validated JWT.
        db: Injected async database session.

    Returns:
        QR image (base64 PNG), manual TOTP key, and issuer name.

    Raises:
        HTTPException: 409 if 2FA is already enabled.
    """
    user = await _get_user(db, current_user.user_id)
    data = await totp_service.initiate_2fa_setup(db, user)
    return SetupResponse(
        qr_code_image=data.qr_code_image,
        manual_key=data.manual_key,
        issuer=data.issuer,
    )


# ---------------------------------------------------------------------------
# POST /me/2fa/confirm
# ---------------------------------------------------------------------------


class ConfirmRequest(BaseModel):
    totp_code: str


class ConfirmResponse(BaseModel):
    backup_codes: list[str]


@router.post(
    "/2fa/confirm",
    response_model=ConfirmResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm 2FA enrollment with a valid TOTP code",
)
async def confirm_2fa(
    body: ConfirmRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConfirmResponse:
    """Confirm 2FA setup and receive one-time backup codes.

    Args:
        body: The 6-digit TOTP code from the authenticator app.
        current_user: Injected from the validated JWT.
        db: Injected async database session.

    Returns:
        10 single-use backup codes. Display once — not retrievable again.

    Raises:
        HTTPException: 409 if already enabled; 422 if code invalid.
    """
    user = await _get_user(db, current_user.user_id)
    codes = await totp_service.confirm_2fa_setup(db, user, body.totp_code)
    return ConfirmResponse(backup_codes=codes)


# ---------------------------------------------------------------------------
# POST /me/2fa/disable
# ---------------------------------------------------------------------------


class DisableRequest(BaseModel):
    password: str
    totp_code: str


class DisableResponse(BaseModel):
    message: str


@router.post(
    "/2fa/disable",
    response_model=DisableResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable 2FA",
)
async def disable_2fa(
    body: DisableRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DisableResponse:
    """Disable 2FA after verifying password and TOTP code.

    Args:
        body: Current password and TOTP code.
        request: FastAPI request (for client IP).
        current_user: Injected from the validated JWT.
        db: Injected async database session.

    Returns:
        Confirmation message.

    Raises:
        HTTPException: 400 if password incorrect; 422 if TOTP code invalid.
    """
    user = await _get_user(db, current_user.user_id)
    await totp_service.disable_2fa(db, user, body.password, body.totp_code, _client_ip(request))
    return DisableResponse(message="Two-factor authentication disabled")


# ---------------------------------------------------------------------------
# POST /me/2fa/backup-codes/regenerate
# ---------------------------------------------------------------------------


class RegenerateRequest(BaseModel):
    password: str
    totp_code: str


class RegenerateResponse(BaseModel):
    backup_codes: list[str]


@router.post(
    "/2fa/backup-codes/regenerate",
    response_model=RegenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Regenerate backup codes",
)
async def regenerate_backup_codes(
    body: RegenerateRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RegenerateResponse:
    """Regenerate backup codes — invalidates all previous codes.

    Args:
        body: Current password and TOTP code.
        request: FastAPI request (for client IP).
        current_user: Injected from the validated JWT.
        db: Injected async database session.

    Returns:
        10 new backup codes.

    Raises:
        HTTPException: 400 if password incorrect; 422 if TOTP code invalid.
    """
    user = await _get_user(db, current_user.user_id)
    codes = await totp_service.regenerate_backup_codes(
        db, user, body.password, body.totp_code, _client_ip(request)
    )
    return RegenerateResponse(backup_codes=codes)
