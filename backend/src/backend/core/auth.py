"""JWT bearer-token authentication and password hashing helpers.

Provides:
- ``hash_password`` / ``verify_password`` — bcrypt helpers
- ``create_access_token`` — sign a JWT (includes ``iat`` and ``ver`` claims)
- ``create_partial_token`` — short-lived token for the 2FA login step
- ``get_current_user`` — FastAPI dependency that validates a Bearer JWT and
  enforces ``token_version`` to support session invalidation on password change
- ``require_study_member`` — shared guard that raises HTTP 403 for non-members
"""

from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_logger, get_settings
from backend.core.database import get_db

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*.

    Args:
        plain: The plaintext password to hash.

    Returns:
        A bcrypt-encoded string suitable for storage.

    """
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Return ``True`` if *plain* matches *hashed*.

    Args:
        plain: The plaintext password provided by the user.
        hashed: The stored bcrypt hash.

    Returns:
        ``True`` if they match, ``False`` otherwise.

    """
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ---------------------------------------------------------------------------
# JWT tokens
# ---------------------------------------------------------------------------


def create_access_token(
    user_id: int,
    token_version: int = 0,
    *,
    extra_claims: dict | None = None,
) -> str:
    """Create and sign a JWT access token for *user_id*.

    The token includes ``iat`` (issued-at) and ``ver`` (token version) claims
    in addition to the standard ``sub`` and ``exp`` claims.  On password change
    the caller must pass the updated ``token_version`` so that prior tokens
    with a stale ``ver`` are rejected by :func:`get_current_user`.

    Args:
        user_id: The primary key of the authenticated user.
        token_version: The current ``User.token_version`` value; embedded as
            the ``ver`` claim.  Defaults to ``0`` for backward compatibility.
        extra_claims: Optional additional claims to embed in the token.

    Returns:
        A signed JWT string.

    """
    settings = get_settings()
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict = {
        "sub": str(user_id),
        "exp": expire,
        "iat": now,
        "ver": token_version,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_partial_token(user_id: int) -> str:
    """Create a short-lived partial JWT for the 2FA login step.

    The token carries ``stage: "totp_required"`` and expires in 5 minutes.
    :func:`get_current_user` rejects partial tokens so they cannot be used to
    access protected resources — only the ``/auth/login/totp`` endpoint accepts
    them.

    Args:
        user_id: The primary key of the user who passed password authentication.

    Returns:
        A signed short-lived JWT string.

    """
    settings = get_settings()
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=5)
    payload: dict = {
        "sub": str(user_id),
        "exp": expire,
        "iat": now,
        "stage": "totp_required",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------


class CurrentUser:
    """Authenticated user extracted from a validated JWT."""

    def __init__(self, user_id: int, is_authenticated: bool = True) -> None:
        """Initialise a current user.

        Args:
            user_id: The database primary key of the user.
            is_authenticated: Whether the JWT was valid.

        """
        self.user_id = user_id
        self.is_authenticated = is_authenticated

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<CurrentUser id={self.user_id} authenticated={self.is_authenticated}>"


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """FastAPI dependency: validate a Bearer JWT and return the current user.

    Raises ``HTTP 401`` if the token is missing, expired, invalid, carries a
    ``stage`` claim (partial token), or has a stale ``ver`` (token_version
    mismatch caused by a password change that invalidated prior sessions).

    Args:
        token: Raw bearer token from the ``Authorization`` header, or ``None``.
        db: Injected async database session used for token_version check.

    Returns:
        A :class:`CurrentUser` with ``is_authenticated=True``.

    Raises:
        HTTPException: 401 if the token is absent, invalid, partial, or stale.

    """
    from db.models.users import User  # local import avoids circular dependency at module load

    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exc

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        sub: str | None = payload.get("sub")
        if sub is None:
            raise credentials_exc
        user_id = int(sub)
    except (JWTError, ValueError) as exc:
        logger.warning("auth_token_invalid")
        raise credentials_exc from exc

    # Reject partial tokens — only valid for the /auth/login/totp step.
    if payload.get("stage") == "totp_required":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication incomplete",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token_version to detect password-change session invalidation.
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exc

    token_ver: int = payload.get("ver", 0)
    if token_ver != user.token_version:
        logger.warning("auth_token_version_mismatch", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(user_id=user_id)


# ---------------------------------------------------------------------------
# Shared study-membership guard (TREF6 — replaces 8 private duplicates)
# ---------------------------------------------------------------------------


async def require_study_member(
    study_id: int,
    current_user: CurrentUser,
    db: AsyncSession,
) -> None:
    """Raise HTTP 403 if *current_user* is not a member of *study_id*.

    Use this shared guard instead of per-router private ``_require_study_member``
    functions to enforce DRY (Principle II) and correct error semantics
    (403 Forbidden, not 404 Not Found).

    Args:
        study_id: The study to check membership against.
        current_user: The authenticated user.
        db: An active async database session.

    Raises:
        HTTPException: 403 if the user is not a study member.

    """
    from db.models.study import StudyMember

    result = await db.execute(
        select(StudyMember).where(
            StudyMember.study_id == study_id,
            StudyMember.user_id == current_user.user_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: not a member of this study",
        )
