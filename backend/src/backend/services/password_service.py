"""Password change service.

Handles the business logic for changing a user's password: current password
verification, complexity enforcement, same-password rejection, token version
increment, and security audit event emission.
"""

import re
from datetime import UTC, datetime

from db.models.security_audit import SecurityEventType
from db.models.users import User
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import hash_password, verify_password
from backend.core.config import get_logger
from backend.services.audit_service import create_security_audit_event

logger = get_logger(__name__)

_COMPLEXITY_REQUIREMENTS = {
    "min_length": 12,
    "requires_uppercase": True,
    "requires_digit": True,
    "requires_special": True,
}


def _meets_complexity(password: str) -> bool:
    """Return True if *password* satisfies all complexity requirements."""
    if len(password) < 12:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]", password):
        return False
    return True


async def change_password(
    db: AsyncSession,
    user_id: int,
    current_password: str,
    new_password: str,
    ip_address: str | None = None,
) -> None:
    """Change the password for a user and invalidate all existing sessions.

    Verifies the current password, enforces complexity rules, rejects
    same-as-current passwords, increments ``token_version`` to invalidate
    all prior JWTs, and emits a ``PASSWORD_CHANGED`` security audit event.

    Args:
        db: An active async database session.
        user_id: Primary key of the user changing their password.
        current_password: The user's existing plaintext password.
        new_password: The desired new plaintext password.
        ip_address: Client IP address for the audit log (optional).

    Raises:
        HTTPException: 400 if ``current_password`` is wrong.
        HTTPException: 400 if ``new_password`` equals the current password.
        HTTPException: 422 if ``new_password`` fails complexity requirements.
        HTTPException: 404 if the user record does not exist.

    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    if not _meets_complexity(new_password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Password does not meet complexity requirements",
            headers={"X-Requirements": str(_COMPLEXITY_REQUIREMENTS)},
        )

    if verify_password(new_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must differ from current password",
        )

    user.hashed_password = hash_password(new_password)
    user.token_version = (user.token_version or 0) + 1
    user.password_changed_at = datetime.now(UTC)

    await create_security_audit_event(
        db=db,
        user_id=user_id,
        event_type=SecurityEventType.PASSWORD_CHANGED,
        ip_address=ip_address,
    )

    await db.commit()
    logger.info("password_changed", user_id=user_id)
