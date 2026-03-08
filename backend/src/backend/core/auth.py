"""JWT bearer-token authentication and password hashing helpers.

Provides:
- ``hash_password`` / ``verify_password`` — bcrypt helpers
- ``create_access_token`` — sign a JWT
- ``get_current_user`` — FastAPI dependency that validates a Bearer JWT
- ``require_study_member`` — shared guard that raises HTTP 403 for non-members
"""

from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from backend.core.config import get_logger, get_settings

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


def create_access_token(user_id: int, *, extra_claims: dict | None = None) -> str:
    """Create and sign a JWT access token for *user_id*.

    Args:
        user_id: The primary key of the authenticated user.
        extra_claims: Optional additional claims to embed in the token.

    Returns:
        A signed JWT string.
    """
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict = {"sub": str(user_id), "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
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
) -> CurrentUser:
    """FastAPI dependency: validate a Bearer JWT and return the current user.

    Raises ``HTTP 401`` if the token is missing, expired, or invalid.

    Args:
        token: Raw bearer token from the ``Authorization`` header, or ``None``.

    Returns:
        A :class:`CurrentUser` with ``is_authenticated=True``.

    Raises:
        HTTPException: 401 if the token is absent or invalid.
    """
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
    except (JWTError, ValueError):
        logger.warning("auth_token_invalid")
        raise credentials_exc

    return CurrentUser(user_id=user_id)


# ---------------------------------------------------------------------------
# Shared study-membership guard (TREF6 — replaces 8 private duplicates)
# ---------------------------------------------------------------------------


async def require_study_member(
    study_id: int,
    current_user: "CurrentUser",
    db: "AsyncSession",
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
    from sqlalchemy import select

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
