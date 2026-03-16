"""Authentication endpoints: login, TOTP second step, and current-user profile."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.auth import (
    CurrentUser,
    create_access_token,
    create_partial_token,
    get_current_user,
    verify_password,
)
from backend.core.config import get_logger, get_settings
from backend.core.database import get_db
from backend.services.totp_service import (
    check_and_enforce_lockout,
    record_failed_attempt,
    verify_backup_code,
)
from backend.core import totp as totp_module
from backend.core.encryption import decrypt_secret
from db.models.users import GroupMembership, User

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    """Body for POST /auth/login."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Response body for a successful login (no 2FA)."""

    access_token: str
    token_type: str = "bearer"
    user_id: int
    display_name: str


class LoginTotpRequiredResponse(BaseModel):
    """Response body when 2FA is required."""

    requires_totp: bool = True
    partial_token: str


class TotpLoginRequest(BaseModel):
    """Body for POST /auth/login/totp."""

    partial_token: str
    totp_code: str


class GroupSummary(BaseModel):
    """Compact group info embedded in the /me response."""

    id: int
    name: str
    role: str


class MeResponse(BaseModel):
    """Response body for GET /auth/me."""

    id: int
    email: str
    display_name: str
    theme_preference: str
    totp_enabled: bool
    groups: list[GroupSummary]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive a JWT token or TOTP challenge",
)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Validate credentials and return a signed JWT or a TOTP challenge.

    If the user has 2FA enabled, returns ``{requires_totp: true, partial_token}``
    instead of the full access token.

    Args:
        body: Email and password supplied by the client.
        db: Injected async database session.

    Returns:
        :class:`LoginResponse` or :class:`LoginTotpRequiredResponse`.

    Raises:
        HTTPException: 401 if credentials are invalid.
        HTTPException: 429 if the account is locked.
    """
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login_at = datetime.now(UTC)
    await db.commit()

    if user.totp_enabled:
        await check_and_enforce_lockout(db, user)
        partial_token = create_partial_token(user.id)
        logger.info("user_login_totp_required", user_id=user.id)
        return LoginTotpRequiredResponse(partial_token=partial_token)

    token = create_access_token(user.id, token_version=user.token_version or 0)
    logger.info("user_login", user_id=user.id)
    return LoginResponse(
        access_token=token,
        user_id=user.id,
        display_name=user.display_name,
    )


@router.post(
    "/login/totp",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete login for 2FA-enabled accounts",
)
async def login_totp(body: TotpLoginRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    """Validate a partial token and TOTP code to complete login.

    Falls back to backup code verification if the TOTP code fails.

    Args:
        body: Partial token from ``/auth/login`` and a 6-digit TOTP code.
        db: Injected async database session.

    Returns:
        A :class:`LoginResponse` with a full JWT on success.

    Raises:
        HTTPException: 401 if the partial token is invalid or expired.
        HTTPException: 422 if the TOTP code and backup code are both invalid.
        HTTPException: 429 if the account is locked.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            body.partial_token, settings.secret_key, algorithms=[settings.algorithm]
        )
        if payload.get("stage") != "totp_required":
            raise ValueError("not a partial token")
        user_id = int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.totp_enabled or not user.totp_secret_encrypted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await check_and_enforce_lockout(db, user)

    secret = decrypt_secret(user.totp_secret_encrypted)
    totp_valid = totp_module.verify_code(secret, body.totp_code)

    if not totp_valid:
        # Try backup code as fallback
        backup_valid = await verify_backup_code(db, user_id, body.totp_code)
        if not backup_valid:
            await record_failed_attempt(db, user)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Invalid TOTP code",
            )

    # Success — reset failure counter
    user.totp_failed_attempts = 0
    user.totp_locked_until = None
    await db.commit()

    token = create_access_token(user.id, token_version=user.token_version or 0)
    logger.info("user_login_totp_success", user_id=user.id)
    return LoginResponse(
        access_token=token,
        user_id=user.id,
        display_name=user.display_name,
    )


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Return the current authenticated user's profile",
)
async def me(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MeResponse:
    """Return the profile and group memberships for the authenticated user.

    Args:
        current_user: Injected from the validated JWT.
        db: Injected async database session.

    Returns:
        A :class:`MeResponse` with user details and group list.

    Raises:
        HTTPException: 404 if the user record no longer exists.
    """
    result = await db.execute(
        select(User)
        .where(User.id == current_user.user_id)
        .options(selectinload(User.memberships).selectinload(GroupMembership.group))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    groups = [
        GroupSummary(id=m.group.id, name=m.group.name, role=m.role.value)
        for m in user.memberships
    ]
    return MeResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        theme_preference=user.theme_preference.value,
        totp_enabled=user.totp_enabled,
        groups=groups,
    )
