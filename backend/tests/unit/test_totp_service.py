"""Unit tests for backend.services.totp_service."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from backend.core.auth import hash_password
from backend.services.totp_service import (
    TOTPSetupData,
    check_and_enforce_lockout,
    confirm_2fa_setup,
    disable_2fa,
    initiate_2fa_setup,
    record_failed_attempt,
    regenerate_backup_codes,
    verify_backup_code,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_user(**kwargs) -> MagicMock:
    defaults = dict(
        id=1,
        email="user@example.com",
        hashed_password=hash_password("Pass12!word"),
        totp_enabled=False,
        totp_secret_encrypted=None,
        totp_failed_attempts=0,
        totp_locked_until=None,
    )
    defaults.update(kwargs)
    return MagicMock(**defaults)


def _make_db(scalar_result=None) -> AsyncMock:
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_result
    result.scalars.return_value.all.return_value = []
    db.execute.return_value = result
    return db


# ---------------------------------------------------------------------------
# check_and_enforce_lockout
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_lockout_not_locked():
    user = _make_user(totp_locked_until=None)
    db = _make_db()
    await check_and_enforce_lockout(db, user)  # no exception


@pytest.mark.asyncio
async def test_lockout_already_expired():
    past = datetime.now(UTC) - timedelta(minutes=1)
    user = _make_user(totp_locked_until=past)
    db = _make_db()
    await check_and_enforce_lockout(db, user)  # no exception


@pytest.mark.asyncio
async def test_lockout_active_raises_429():
    future = datetime.now(UTC) + timedelta(minutes=5)
    user = _make_user(totp_locked_until=future)
    db = _make_db()
    with pytest.raises(HTTPException) as exc_info:
        await check_and_enforce_lockout(db, user)
    assert exc_info.value.status_code == 429
    assert "locked until" in exc_info.value.detail.lower()


# ---------------------------------------------------------------------------
# record_failed_attempt
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_record_failed_attempt_increments_counter():
    user = _make_user(totp_failed_attempts=2)
    db = _make_db()
    with patch("backend.services.totp_service.create_security_audit_event", new_callable=AsyncMock):
        await record_failed_attempt(db, user)
    assert user.totp_failed_attempts == 3
    assert user.totp_locked_until is None


@pytest.mark.asyncio
async def test_record_failed_attempt_locks_at_threshold():
    user = _make_user(totp_failed_attempts=4)  # one more = 5 = threshold
    db = _make_db()
    with patch("backend.services.totp_service.create_security_audit_event", new_callable=AsyncMock):
        await record_failed_attempt(db, user)
    assert user.totp_failed_attempts == 5
    assert user.totp_locked_until is not None
    assert user.totp_locked_until > datetime.now(UTC)


# ---------------------------------------------------------------------------
# initiate_2fa_setup
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_initiate_setup_already_enabled_raises_409():
    user = _make_user(totp_enabled=True)
    db = _make_db()
    with pytest.raises(HTTPException) as exc_info:
        await initiate_2fa_setup(db, user)
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_initiate_setup_returns_setup_data():
    user = _make_user()
    db = _make_db()
    result = await initiate_2fa_setup(db, user)
    assert isinstance(result, TOTPSetupData)
    assert result.qr_code_image  # non-empty base64
    assert result.manual_key  # non-empty secret
    assert user.totp_secret_encrypted is not None


# ---------------------------------------------------------------------------
# confirm_2fa_setup
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_confirm_setup_already_enabled_raises_409():
    user = _make_user(totp_enabled=True)
    db = _make_db()
    with pytest.raises(HTTPException) as exc_info:
        await confirm_2fa_setup(db, user, "123456")
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_confirm_setup_no_pending_secret_raises_422():
    user = _make_user(totp_secret_encrypted=None)
    db = _make_db()
    with pytest.raises(HTTPException) as exc_info:
        await confirm_2fa_setup(db, user, "123456")
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_confirm_setup_wrong_code_raises_422():
    from backend.core.encryption import encrypt_secret
    from backend.core.totp import generate_secret
    secret = generate_secret()
    user = _make_user(totp_secret_encrypted=encrypt_secret(secret))
    db = _make_db()
    with pytest.raises(HTTPException) as exc_info:
        with patch("backend.services.totp_service.create_security_audit_event", new_callable=AsyncMock):
            await confirm_2fa_setup(db, user, "000000")
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_confirm_setup_valid_code_enables_2fa():
    import pyotp
    from backend.core.encryption import encrypt_secret
    from backend.core.totp import generate_secret
    secret = generate_secret()
    user = _make_user(totp_secret_encrypted=encrypt_secret(secret))
    db = _make_db()
    valid_code = pyotp.TOTP(secret).now()
    with patch("backend.services.totp_service.create_security_audit_event", new_callable=AsyncMock):
        codes = await confirm_2fa_setup(db, user, valid_code)
    assert user.totp_enabled is True
    assert len(codes) == 10
    assert all(len(c) == 10 for c in codes)


# ---------------------------------------------------------------------------
# disable_2fa
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_disable_wrong_password_raises_400():
    user = _make_user(totp_enabled=True)
    db = _make_db()
    with pytest.raises(HTTPException) as exc_info:
        await disable_2fa(db, user, "wrongpassword", "123456")
    assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# verify_backup_code
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_verify_backup_code_no_codes_returns_false():
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    db.execute.return_value = result
    found = await verify_backup_code(db, user_id=1, code="ABCD1234EF")
    assert found is False
