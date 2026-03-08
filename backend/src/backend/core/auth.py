"""Stub JWT bearer-token authentication middleware.

This module provides placeholder stubs for JWT-based authentication.
Routes declare their dependency via ``Depends(get_current_user)``.

Full implementation (token validation, user lookup, refresh tokens)
is deferred to a later feature; the stub structure ensures no route
changes are needed when auth is fully wired up.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from backend.core.config import get_logger

logger = get_logger(__name__)

# Token URL is a placeholder; auth endpoints are added in a later feature.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


class CurrentUser:
    """Placeholder user object returned by the auth stub.

    Replaced by a real ORM-backed user model when authentication
    is fully implemented.
    """

    def __init__(self, user_id: str = "anonymous", is_authenticated: bool = False) -> None:
        """Initialise a placeholder user.

        Args:
            user_id: A stable identifier for the user.
            is_authenticated: Whether a valid token was presented.
        """
        self.user_id = user_id
        self.is_authenticated = is_authenticated

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<CurrentUser id={self.user_id!r} authenticated={self.is_authenticated}>"


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
) -> CurrentUser:
    """Stub dependency that extracts (but does not validate) a bearer token.

    In the MVP harness this always returns an unauthenticated placeholder
    so routes can be exercised without credentials.  When auth is
    implemented, replace the body of this function with real JWT
    validation — the ``Depends(get_current_user)`` call sites need
    no changes.

    Args:
        token: Raw bearer token extracted from the ``Authorization`` header,
               or ``None`` if the header is absent.

    Returns:
        A :class:`CurrentUser` instance.  Currently always unauthenticated.
    """
    if token:
        logger.debug("auth_stub_token_received", token_prefix=token[:8] + "...")
        return CurrentUser(user_id="stub-user", is_authenticated=False)

    return CurrentUser()
