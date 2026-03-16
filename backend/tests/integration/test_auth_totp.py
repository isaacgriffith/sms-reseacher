"""Integration tests for 2FA login flow (POST /auth/login + /auth/login/totp)."""

import pyotp
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token, hash_password
from backend.core.encryption import encrypt_secret
from backend.core.totp import generate_secret
from db.models.backup_codes import BackupCode
from db.models.users import User


async def _enable_totp(db_engine, user_id: int) -> str:
    """Enable TOTP for the user and return the secret."""
    secret = generate_secret()
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        u = result.scalar_one()
        u.totp_enabled = True
        u.totp_secret_encrypted = encrypt_secret(secret)
        await session.commit()
    return secret


async def _add_backup_code(db_engine, user_id: int, plain: str) -> None:
    import bcrypt
    hashed = bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        session.add(BackupCode(user_id=user_id, hashed_code=hashed))
        await session.commit()


# ---------------------------------------------------------------------------
# POST /auth/login — 2FA path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_with_totp_returns_requires_totp(client: AsyncClient, alice, db_engine):
    user, plain = alice
    await _enable_totp(db_engine, user.id)
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": plain},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["requires_totp"] is True
    assert "partial_token" in data


@pytest.mark.asyncio
async def test_login_without_totp_returns_full_jwt(client: AsyncClient, alice, db_engine):
    user, plain = alice
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": plain},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "requires_totp" not in data


# ---------------------------------------------------------------------------
# POST /auth/login/totp
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_totp_valid_code_returns_full_jwt(client: AsyncClient, alice, db_engine):
    user, plain = alice
    secret = await _enable_totp(db_engine, user.id)
    # First, get the partial token
    resp1 = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": plain},
    )
    partial_token = resp1.json()["partial_token"]
    valid_code = pyotp.TOTP(secret).now()
    resp2 = await client.post(
        "/api/v1/auth/login/totp",
        json={"partial_token": partial_token, "totp_code": valid_code},
    )
    assert resp2.status_code == 200
    assert "access_token" in resp2.json()


@pytest.mark.asyncio
async def test_login_totp_invalid_code_422(client: AsyncClient, alice, db_engine):
    user, plain = alice
    await _enable_totp(db_engine, user.id)
    resp1 = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": plain},
    )
    partial_token = resp1.json()["partial_token"]
    resp2 = await client.post(
        "/api/v1/auth/login/totp",
        json={"partial_token": partial_token, "totp_code": "000000"},
    )
    assert resp2.status_code == 422


@pytest.mark.asyncio
async def test_login_totp_5_failures_locks_account(client: AsyncClient, alice, db_engine):
    user, plain = alice
    await _enable_totp(db_engine, user.id)
    resp1 = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": plain},
    )
    partial_token = resp1.json()["partial_token"]
    # 5 bad attempts
    for _ in range(5):
        await client.post(
            "/api/v1/auth/login/totp",
            json={"partial_token": partial_token, "totp_code": "000000"},
        )
    # 6th attempt — should get 429
    resp = await client.post(
        "/api/v1/auth/login/totp",
        json={"partial_token": partial_token, "totp_code": "000000"},
    )
    assert resp.status_code == 429
    assert "locked" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_backup_code_works_once(client: AsyncClient, alice, db_engine):
    user, plain = alice
    backup_plain = "ABCD1234EF"
    await _enable_totp(db_engine, user.id)
    await _add_backup_code(db_engine, user.id, backup_plain)
    resp1 = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": plain},
    )
    partial_token = resp1.json()["partial_token"]
    # Use backup code
    resp2 = await client.post(
        "/api/v1/auth/login/totp",
        json={"partial_token": partial_token, "totp_code": backup_plain},
    )
    assert resp2.status_code == 200
    # Reuse same backup code — should fail
    resp3 = await client.post(
        "/api/v1/auth/login/totp",
        json={"partial_token": partial_token, "totp_code": backup_plain},
    )
    assert resp3.status_code == 422


@pytest.mark.asyncio
async def test_partial_token_rejected_by_protected_endpoint(client: AsyncClient, alice, db_engine):
    user, plain = alice
    await _enable_totp(db_engine, user.id)
    resp1 = await client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": plain},
    )
    partial_token = resp1.json()["partial_token"]
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {partial_token}"},
    )
    assert resp.status_code == 401
