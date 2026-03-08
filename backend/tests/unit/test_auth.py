"""Unit tests for backend.core.auth — get_current_user, password helpers, require_study_member."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from backend.core.auth import (
    CurrentUser,
    create_access_token,
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
# get_current_user
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_no_token_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=None)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token="not.a.valid.jwt")
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    token = create_access_token(user_id=42)
    user = await get_current_user(token=token)
    assert user.user_id == 42
    assert user.is_authenticated


# ---------------------------------------------------------------------------
# require_study_member — TREF6: 403 path (test written BEFORE implementation)
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
