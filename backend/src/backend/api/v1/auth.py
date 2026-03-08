"""Authentication endpoints: login and current-user profile."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.auth import CurrentUser, create_access_token, get_current_user, verify_password
from backend.core.config import get_logger
from backend.core.database import get_db
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
    """Response body for a successful login."""

    access_token: str
    token_type: str = "bearer"
    user_id: int
    display_name: str


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
    groups: list[GroupSummary]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive a JWT token",
)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    """Validate credentials and return a signed JWT access token.

    Args:
        body: Email and password supplied by the client.
        db: Injected async database session.

    Returns:
        A :class:`LoginResponse` with the JWT and basic user info.

    Raises:
        HTTPException: 401 if the email is not found or the password is wrong.
    """
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last_login_at
    user.last_login_at = datetime.now(UTC)
    await db.commit()

    token = create_access_token(user.id)
    logger.info("user_login", user_id=user.id)
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
        groups=groups,
    )
