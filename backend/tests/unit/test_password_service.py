"""Unit tests for backend.services.password_service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from backend.core.auth import hash_password
from backend.services.password_service import _meets_complexity, change_password


# ---------------------------------------------------------------------------
# Complexity helper
# ---------------------------------------------------------------------------


def test_complexity_short():
    assert not _meets_complexity("Short1!")


def test_complexity_no_uppercase():
    assert not _meets_complexity("longpassword1!")


def test_complexity_no_digit():
    assert not _meets_complexity("LongPassword!!")


def test_complexity_no_special():
    assert not _meets_complexity("LongPassword12")


def test_complexity_valid():
    assert _meets_complexity("LongPass12!xyz")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_user(password: str = "CurrentPass12!", token_version: int = 0) -> MagicMock:
    user = MagicMock()
    user.hashed_password = hash_password(password)
    user.token_version = token_version
    return user


def _make_db(user: MagicMock | None) -> AsyncMock:
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    db.execute.return_value = result
    return db


# ---------------------------------------------------------------------------
# change_password scenarios
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_user_not_found_raises_404():
    db = _make_db(None)
    with pytest.raises(HTTPException) as exc_info:
        await change_password(db, user_id=99, current_password="x", new_password="y")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_wrong_current_password_raises_400():
    user = _make_user("CurrentPass12!")
    db = _make_db(user)
    with pytest.raises(HTTPException) as exc_info:
        await change_password(db, user_id=1, current_password="WrongPass12!", new_password="NewPass12!")
    assert exc_info.value.status_code == 400
    assert "incorrect" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_complexity_failure_raises_422():
    user = _make_user("CurrentPass12!")
    db = _make_db(user)
    with pytest.raises(HTTPException) as exc_info:
        await change_password(db, user_id=1, current_password="CurrentPass12!", new_password="weak")
    assert exc_info.value.status_code == 422  # noqa: PLR2004
    assert "complexity" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_same_password_raises_400():
    current = "CurrentPass12!"
    user = _make_user(current)
    db = _make_db(user)
    with pytest.raises(HTTPException) as exc_info:
        await change_password(db, user_id=1, current_password=current, new_password=current)
    assert exc_info.value.status_code == 400
    assert "differ" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_success_increments_token_version():
    current = "CurrentPass12!"
    user = _make_user(current, token_version=2)
    db = _make_db(user)

    with patch("backend.services.password_service.create_security_audit_event", new_callable=AsyncMock):
        await change_password(db, user_id=1, current_password=current, new_password="NewPass12!xyz")

    assert user.token_version == 3
    db.commit.assert_called_once()
