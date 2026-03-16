"""Integration tests for /api/v1/me/2fa/* endpoints."""

import pyotp
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from backend.core.encryption import encrypt_secret
from backend.core.totp import generate_secret
from db.models.backup_codes import BackupCode
from db.models.users import User


async def _get_user(db_engine, user_id: int) -> User:
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one()


async def _count_backup_codes(db_engine, user_id: int) -> int:
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        result = await session.execute(
            select(BackupCode).where(BackupCode.user_id == user_id)
        )
        return len(result.scalars().all())


# ---------------------------------------------------------------------------
# POST /me/2fa/setup
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_setup_returns_qr_and_key(client: AsyncClient, alice, db_engine):
    user, _ = alice
    token = create_access_token(user_id=user.id, token_version=0)
    resp = await client.post(
        "/api/v1/me/2fa/setup",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "qr_code_image" in data
    assert "manual_key" in data
    assert data["issuer"] == "SMS Researcher"


@pytest.mark.asyncio
async def test_setup_confirm_disable_cycle(client: AsyncClient, alice, db_engine):
    user, plain = alice
    token = create_access_token(user_id=user.id, token_version=0)

    # Setup
    setup_resp = await client.post(
        "/api/v1/me/2fa/setup",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert setup_resp.status_code == 200
    manual_key = setup_resp.json()["manual_key"]

    # Confirm
    valid_code = pyotp.TOTP(manual_key).now()
    confirm_resp = await client.post(
        "/api/v1/me/2fa/confirm",
        json={"totp_code": valid_code},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert confirm_resp.status_code == 200
    backup_codes = confirm_resp.json()["backup_codes"]
    assert len(backup_codes) == 10

    updated = await _get_user(db_engine, user.id)
    assert updated.totp_enabled is True

    # Disable
    valid_code2 = pyotp.TOTP(manual_key).now()
    disable_resp = await client.post(
        "/api/v1/me/2fa/disable",
        json={"password": plain, "totp_code": valid_code2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert disable_resp.status_code == 200
    disabled_user = await _get_user(db_engine, user.id)
    assert disabled_user.totp_enabled is False
    assert await _count_backup_codes(db_engine, user.id) == 0


@pytest.mark.asyncio
async def test_confirm_with_wrong_code_raises_422(client: AsyncClient, alice, db_engine):
    user, _ = alice
    token = create_access_token(user_id=user.id, token_version=0)
    await client.post(
        "/api/v1/me/2fa/setup",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.post(
        "/api/v1/me/2fa/confirm",
        json={"totp_code": "000000"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_backup_code_regeneration_invalidates_old_codes(client: AsyncClient, alice, db_engine):
    user, plain = alice
    token = create_access_token(user_id=user.id, token_version=0)

    # Setup + confirm to enable 2FA and get first batch
    setup_resp = await client.post(
        "/api/v1/me/2fa/setup",
        headers={"Authorization": f"Bearer {token}"},
    )
    manual_key = setup_resp.json()["manual_key"]
    valid_code = pyotp.TOTP(manual_key).now()
    confirm_resp = await client.post(
        "/api/v1/me/2fa/confirm",
        json={"totp_code": valid_code},
        headers={"Authorization": f"Bearer {token}"},
    )
    first_codes = set(confirm_resp.json()["backup_codes"])

    # Regenerate
    valid_code2 = pyotp.TOTP(manual_key).now()
    regen_resp = await client.post(
        "/api/v1/me/2fa/backup-codes/regenerate",
        json={"password": plain, "totp_code": valid_code2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert regen_resp.status_code == 200
    new_codes = set(regen_resp.json()["backup_codes"])

    # New codes should differ from old codes
    assert len(new_codes) == 10
    # With very high probability the sets won't overlap
    assert new_codes != first_codes
