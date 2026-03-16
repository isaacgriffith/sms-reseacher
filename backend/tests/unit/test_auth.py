"""Unit tests for backend.core.auth — get_current_user, password helpers, token claims."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from backend.core.auth import (
    CurrentUser,
    create_access_token,
    create_partial_token,
    get_current_user,
    hash_password,
    require_study_member,
    verify_password,
)


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------


def test_hash_and_verify_password_match():
    hashed = hash_password("s3cr3t!")
    assert hashed != "s3cr3t!"
    assert verify_password("s3cr3t!", hashed)


def test_verify_password_wrong_plain():
    hashed = hash_password("correct")
    assert not verify_password("wrong", hashed)


# ---------------------------------------------------------------------------
# create_access_token — iat and ver claims
# ---------------------------------------------------------------------------


def test_create_access_token_includes_iat_and_ver():
    """Full access token must carry iat and ver claims."""
    from jose import jwt

    from backend.core.config import get_settings

    settings = get_settings()
    token = create_access_token(user_id=7, token_version=3)
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload["sub"] == "7"
    assert payload["ver"] == 3
    assert "iat" in payload
    assert "exp" in payload


def test_create_access_token_default_ver_is_zero():
    """Default token_version is 0 for backward compatibility."""
    from jose import jwt

    from backend.core.config import get_settings

    settings = get_settings()
    token = create_access_token(user_id=1)
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload["ver"] == 0


# ---------------------------------------------------------------------------
# create_partial_token
# ---------------------------------------------------------------------------


def test_create_partial_token_has_stage_claim():
    """Partial token must carry stage=totp_required."""
    from jose import jwt

    from backend.core.config import get_settings

    settings = get_settings()
    token = create_partial_token(user_id=42)
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload["stage"] == "totp_required"
    assert payload["sub"] == "42"


# ---------------------------------------------------------------------------
# get_current_user helpers
# ---------------------------------------------------------------------------


def _make_db_mock(token_version: int = 0) -> AsyncMock:
    """Return an AsyncMock db that returns a User stub with given token_version."""
    db = AsyncMock()
    user_stub = MagicMock()
    user_stub.token_version = token_version
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user_stub
    db.execute.return_value = result_mock
    return db


# ---------------------------------------------------------------------------
# get_current_user
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_no_token_raises_401():
    db = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=None, db=db)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token_raises_401():
    db = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token="not.a.valid.jwt", db=db)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_valid_token_correct_version():
    """Valid token with matching token_version succeeds."""
    token = create_access_token(user_id=42, token_version=0)
    db = _make_db_mock(token_version=0)
    user = await get_current_user(token=token, db=db)
    assert user.user_id == 42
    assert user.is_authenticated


@pytest.mark.asyncio
async def test_get_current_user_stale_token_version_raises_401():
    """Token with outdated ver (password changed) must be rejected."""
    token = create_access_token(user_id=5, token_version=0)
    db = _make_db_mock(token_version=1)  # version incremented by password change
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=token, db=db)
    assert exc_info.value.status_code == 401
    assert "Session expired" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_partial_token_raises_401():
    """Partial (2FA-pending) token must be rejected for protected endpoints."""
    token = create_partial_token(user_id=10)
    db = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=token, db=db)
    assert exc_info.value.status_code == 401
    assert "incomplete" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_current_user_user_not_found_raises_401():
    """Token valid but user deleted from DB must raise 401."""
    token = create_access_token(user_id=99, token_version=0)
    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None  # user deleted
    db.execute.return_value = result_mock
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=token, db=db)
    assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# require_study_member — TREF6: 403 path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_require_study_member_raises_403_when_not_member():
    """Non-member must receive HTTP 403, not 404."""
    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock

    user = CurrentUser(user_id=1)
    with pytest.raises(HTTPException) as exc_info:
        await require_study_member(study_id=99, current_user=user, db=db)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_require_study_member_passes_when_member():
    """Study member must not raise."""
    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = MagicMock()  # found
    db.execute.return_value = result_mock

    user = CurrentUser(user_id=1)
    await require_study_member(study_id=99, current_user=user, db=db)  # no exception
