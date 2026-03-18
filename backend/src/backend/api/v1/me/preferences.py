"""GET /me/preferences and PUT /me/preferences/theme endpoints."""

from db.models.users import ThemePreference, User
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.database import get_db

router = APIRouter(tags=["me"])


class PreferencesResponse(BaseModel):
    """Response body for GET /me/preferences."""

    theme_preference: str
    totp_enabled: bool


class UpdateThemeRequest(BaseModel):
    """Request body for PUT /me/preferences/theme."""

    theme: str


class UpdateThemeResponse(BaseModel):
    """Response body for PUT /me/preferences/theme."""

    theme_preference: str


@router.get(
    "/preferences",
    response_model=PreferencesResponse,
    summary="Return the current user's preferences",
)
async def get_preferences(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PreferencesResponse:
    """Return theme and 2FA preferences for the authenticated user.

    Args:
        current_user: Injected from the validated JWT.
        db: Injected async database session.

    Returns:
        A :class:`PreferencesResponse` with theme and 2FA status.

    Raises:
        HTTPException: 404 if the user record no longer exists.

    """
    result = await db.execute(select(User).where(User.id == current_user.user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return PreferencesResponse(
        theme_preference=user.theme_preference.value,
        totp_enabled=user.totp_enabled,
    )


@router.put(
    "/preferences/theme",
    response_model=UpdateThemeResponse,
    summary="Update the current user's display theme preference",
)
async def update_theme(
    body: UpdateThemeRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UpdateThemeResponse:
    """Set the authenticated user's display theme preference.

    Args:
        body: The new theme value (`light`, `dark`, or `system`).
        current_user: Injected from the validated JWT.
        db: Injected async database session.

    Returns:
        The updated :class:`UpdateThemeResponse`.

    Raises:
        HTTPException: 422 if the theme value is not one of the valid options.
        HTTPException: 404 if the user record no longer exists.

    """
    try:
        new_pref = ThemePreference(body.theme)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="theme must be one of: light, dark, system",
        ) from exc

    result = await db.execute(select(User).where(User.id == current_user.user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.theme_preference = new_pref
    await db.commit()

    return UpdateThemeResponse(theme_preference=new_pref.value)
