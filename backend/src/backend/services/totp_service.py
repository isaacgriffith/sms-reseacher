"""Two-factor authentication lifecycle service.

Manages TOTP 2FA setup, confirmation, disabling, backup code generation and
redemption, and brute-force lockout enforcement.
"""

import secrets
import string
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import bcrypt
from db.models.backup_codes import BackupCode
from db.models.security_audit import SecurityEventType
from db.models.users import User
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core import totp as totp_module
from backend.core.auth import verify_password
from backend.core.config import get_logger, get_settings
from backend.core.encryption import decrypt_secret, encrypt_secret
from backend.services.audit_service import create_security_audit_event

logger = get_logger(__name__)

_BACKUP_CODE_LENGTH = 10
_BACKUP_CODE_COUNT = 10
_ALPHABET = string.ascii_uppercase + string.digits


# ---------------------------------------------------------------------------
# Data transfer objects
# ---------------------------------------------------------------------------


@dataclass
class TOTPSetupData:
    """Returned by :func:`initiate_2fa_setup`."""

    qr_code_image: str
    manual_key: str
    issuer: str


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _generate_backup_code() -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(_BACKUP_CODE_LENGTH))


def _hash_backup_code(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _check_backup_code(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


async def _load_user(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# ---------------------------------------------------------------------------
# Lockout
# ---------------------------------------------------------------------------


async def check_and_enforce_lockout(db: AsyncSession, user: User) -> None:
    """Raise HTTP 429 if the user's account is currently locked.

    Args:
        db: Active async database session.
        user: The User ORM object to check.

    Raises:
        HTTPException: 429 with lockout expiry in the detail if locked.

    """
    locked_until = user.totp_locked_until
    if locked_until is not None:
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=UTC)
        if locked_until > datetime.now(UTC):
            expiry = locked_until.strftime("%Y-%m-%dT%H:%M:%SZ")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed attempts. Account locked until {expiry}",
            )


async def record_failed_attempt(db: AsyncSession, user: User) -> None:
    """Increment the TOTP failure counter and lock the account if threshold reached.

    Args:
        db: Active async database session.
        user: The User ORM object to update.

    """
    settings = get_settings()
    user.totp_failed_attempts = (user.totp_failed_attempts or 0) + 1
    if user.totp_failed_attempts >= settings.totp_lockout_attempts:
        user.totp_locked_until = datetime.now(UTC) + timedelta(
            minutes=settings.totp_lockout_minutes
        )
        await create_security_audit_event(
            db=db,
            user_id=user.id,
            event_type=SecurityEventType.TOTP_LOCKED,
        )
        logger.warning("totp_account_locked", user_id=user.id)
    await db.commit()


# ---------------------------------------------------------------------------
# Setup / confirm
# ---------------------------------------------------------------------------


async def initiate_2fa_setup(db: AsyncSession, user: User) -> TOTPSetupData:
    """Begin 2FA enrollment by generating and storing an encrypted TOTP secret.

    The secret is stored encrypted in ``user.totp_secret_encrypted`` but 2FA
    is not activated until :func:`confirm_2fa_setup` is called with a valid code.

    Args:
        db: Active async database session.
        user: The authenticated User ORM object.

    Returns:
        A :class:`TOTPSetupData` with QR image, manual key, and issuer name.

    Raises:
        HTTPException: 409 if 2FA is already enabled on this account.

    """
    if user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Two-factor authentication is already enabled",
        )

    settings = get_settings()
    secret = totp_module.generate_secret()
    user.totp_secret_encrypted = encrypt_secret(secret)
    await db.commit()

    uri = totp_module.get_provisioning_uri(secret, user.email, settings.totp_issuer_name)
    qr_image = totp_module.generate_qr_base64(uri)

    return TOTPSetupData(
        qr_code_image=qr_image,
        manual_key=secret,
        issuer=settings.totp_issuer_name,
    )


async def confirm_2fa_setup(db: AsyncSession, user: User, totp_code: str) -> list[str]:
    """Confirm 2FA enrollment with a valid TOTP code and return backup codes.

    Activates 2FA, generates 10 single-use backup codes, and logs an audit event.

    Args:
        db: Active async database session.
        user: The authenticated User ORM object.
        totp_code: The 6-digit TOTP code from the authenticator app.

    Returns:
        A list of 10 plaintext backup codes. Display once — not retrievable again.

    Raises:
        HTTPException: 409 if 2FA is already enabled.
        HTTPException: 422 if the TOTP code is invalid or no pending setup exists.

    """
    if user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Two-factor authentication is already enabled",
        )
    if not user.totp_secret_encrypted:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No pending 2FA setup found. Start setup first.",
        )

    secret = decrypt_secret(user.totp_secret_encrypted)
    if not totp_module.verify_code(secret, totp_code):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid TOTP code. Please try again.",
        )

    user.totp_enabled = True
    user.totp_failed_attempts = 0
    user.totp_locked_until = None

    plaintext_codes: list[str] = []
    for _ in range(_BACKUP_CODE_COUNT):
        plain = _generate_backup_code()
        plaintext_codes.append(plain)
        db.add(BackupCode(user_id=user.id, hashed_code=_hash_backup_code(plain)))

    await create_security_audit_event(
        db=db, user_id=user.id, event_type=SecurityEventType.TOTP_ENABLED
    )
    await db.commit()
    logger.info("totp_enabled", user_id=user.id)
    return plaintext_codes


# ---------------------------------------------------------------------------
# Disable
# ---------------------------------------------------------------------------


async def disable_2fa(
    db: AsyncSession,
    user: User,
    password: str,
    totp_code: str,
    ip_address: str | None = None,
) -> None:
    """Disable 2FA after verifying the user's password and a TOTP code.

    Args:
        db: Active async database session.
        user: The authenticated User ORM object.
        password: Current plaintext password for verification.
        totp_code: Current 6-digit TOTP code.
        ip_address: Client IP for the audit log (optional).

    Raises:
        HTTPException: 400 if the password is incorrect.
        HTTPException: 422 if the TOTP code is invalid.

    """
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    if not user.totp_secret_encrypted:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="2FA is not configured",
        )

    secret = decrypt_secret(user.totp_secret_encrypted)
    if not totp_module.verify_code(secret, totp_code):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid TOTP code",
        )

    user.totp_enabled = False
    user.totp_secret_encrypted = None
    user.totp_failed_attempts = 0
    user.totp_locked_until = None

    # Delete all backup codes for this user
    codes = await db.execute(select(BackupCode).where(BackupCode.user_id == user.id))
    for code in codes.scalars().all():
        await db.delete(code)

    await create_security_audit_event(
        db=db,
        user_id=user.id,
        event_type=SecurityEventType.TOTP_DISABLED,
        ip_address=ip_address,
    )
    await db.commit()
    logger.info("totp_disabled", user_id=user.id)


# ---------------------------------------------------------------------------
# Backup codes
# ---------------------------------------------------------------------------


async def regenerate_backup_codes(
    db: AsyncSession,
    user: User,
    password: str,
    totp_code: str,
    ip_address: str | None = None,
) -> list[str]:
    """Regenerate backup codes after verifying credentials.

    Deletes all existing codes and generates a fresh batch of 10.

    Args:
        db: Active async database session.
        user: The authenticated User ORM object.
        password: Current plaintext password.
        totp_code: Current 6-digit TOTP code.
        ip_address: Client IP for the audit log (optional).

    Returns:
        A list of 10 new plaintext backup codes.

    Raises:
        HTTPException: 400 if password is incorrect.
        HTTPException: 422 if TOTP code is invalid or 2FA not enabled.

    """
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    if not user.totp_enabled or not user.totp_secret_encrypted:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="2FA is not enabled",
        )

    secret = decrypt_secret(user.totp_secret_encrypted)
    if not totp_module.verify_code(secret, totp_code):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid TOTP code",
        )

    # Delete old codes
    old_codes = await db.execute(select(BackupCode).where(BackupCode.user_id == user.id))
    for code in old_codes.scalars().all():
        await db.delete(code)

    plaintext_codes: list[str] = []
    for _ in range(_BACKUP_CODE_COUNT):
        plain = _generate_backup_code()
        plaintext_codes.append(plain)
        db.add(BackupCode(user_id=user.id, hashed_code=_hash_backup_code(plain)))

    await create_security_audit_event(
        db=db,
        user_id=user.id,
        event_type=SecurityEventType.BACKUP_CODES_REGENERATED,
        ip_address=ip_address,
    )
    await db.commit()
    logger.info("backup_codes_regenerated", user_id=user.id)
    return plaintext_codes


async def verify_backup_code(db: AsyncSession, user_id: int, code: str) -> bool:
    """Check if *code* matches an unused backup code for *user_id*.

    Marks the code as used if found.

    Args:
        db: Active async database session.
        user_id: The user's primary key.
        code: The plaintext backup code supplied by the user.

    Returns:
        ``True`` if a matching unused code was found and consumed.

    """
    result = await db.execute(
        select(BackupCode).where(
            BackupCode.user_id == user_id,
            BackupCode.used_at.is_(None),
        )
    )
    for backup in result.scalars().all():
        if _check_backup_code(code, backup.hashed_code):
            backup.used_at = datetime.now(UTC)
            await db.commit()
            return True
    return False
