"""Integration tests for PUT /api/v1/me/password."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token, verify_password
from db.models.users import User
from sqlalchemy import select


async def _login_token(db_engine, user_id: int, token_version: int = 0) -> str:
    return create_access_token(user_id=user_id, token_version=token_version)


async def _get_user(db_engine, user_id: int) -> User:
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_change_password_wrong_current(client: AsyncClient, alice, db_engine):
    user, _plain = alice
    token = await _login_token(db_engine, user.id)
    resp = await client.put(
        "/api/v1/me/password",
        json={"current_password": "wrongpassword", "new_password": "NewPass12!abc"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert "incorrect" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_complexity_failure(client: AsyncClient, alice, db_engine):
    user, plain = alice
    token = await _login_token(db_engine, user.id)
    resp = await client.put(
        "/api/v1/me/password",
        json={"current_password": plain, "new_password": "weak"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
    assert "complexity" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_same_as_current(client: AsyncClient, alice, db_engine):
    user, plain = alice
    token = await _login_token(db_engine, user.id)
    resp = await client.put(
        "/api/v1/me/password",
        json={"current_password": plain, "new_password": plain},
        headers={"Authorization": f"Bearer {token}"},
    )
    # plain is "password123" — fails complexity first (no uppercase/special)
    # so we'll use a valid "same" password via fixture override test below
    assert resp.status_code in (400, 422)


@pytest.mark.asyncio
async def test_change_password_same_complex_password(client: AsyncClient, db_engine, alice):
    """When current == new and both pass complexity, return 400."""
    user, _ = alice
    # Re-hash with a complex password to test the same-password rejection path
    from sqlalchemy.ext.asyncio import async_sessionmaker
    from backend.core.auth import hash_password

    complex_pw = "ComplexPass12!"
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        result = await session.execute(select(User).where(User.id == user.id))
        u = result.scalar_one()
        u.hashed_password = hash_password(complex_pw)
        await session.commit()

    token = create_access_token(user_id=user.id, token_version=0)
    resp = await client.put(
        "/api/v1/me/password",
        json={"current_password": complex_pw, "new_password": complex_pw},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert "differ" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_success_increments_token_version(client: AsyncClient, alice, db_engine):
    user, plain = alice
    # alice default password "password123" lacks complexity; use a complex one
    from backend.core.auth import hash_password
    from sqlalchemy.ext.asyncio import async_sessionmaker

    complex_current = "OldPass12!xyz"
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        result = await session.execute(select(User).where(User.id == user.id))
        u = result.scalar_one()
        u.hashed_password = hash_password(complex_current)
        original_version = u.token_version or 0
        await session.commit()

    token = create_access_token(user_id=user.id, token_version=original_version)
    resp = await client.put(
        "/api/v1/me/password",
        json={"current_password": complex_current, "new_password": "NewPass12!abc"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Password changed successfully"

    updated = await _get_user(db_engine, user.id)
    assert updated.token_version == original_version + 1
    assert verify_password("NewPass12!abc", updated.hashed_password)


@pytest.mark.asyncio
async def test_change_password_old_jwt_rejected_after_change(client: AsyncClient, alice, db_engine):
    """Old token (stale token_version) should be rejected after password change."""
    user, _ = alice
    from backend.core.auth import hash_password
    from sqlalchemy.ext.asyncio import async_sessionmaker

    complex_current = "OldPass12!xyz"
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        result = await session.execute(select(User).where(User.id == user.id))
        u = result.scalar_one()
        u.hashed_password = hash_password(complex_current)
        u.token_version = 0
        await session.commit()

    old_token = create_access_token(user_id=user.id, token_version=0)
    # Perform password change
    resp = await client.put(
        "/api/v1/me/password",
        json={"current_password": complex_current, "new_password": "NewPass12!abc"},
        headers={"Authorization": f"Bearer {old_token}"},
    )
    assert resp.status_code == 200

    # Old token (ver=0) should now be rejected; DB has token_version=1
    resp2 = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {old_token}"})
    assert resp2.status_code == 401
