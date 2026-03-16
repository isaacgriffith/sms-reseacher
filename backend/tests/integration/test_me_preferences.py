"""Integration tests for GET /api/v1/me/preferences and PUT /api/v1/me/preferences/theme."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.users import User


async def _get_user(db_engine, user_id: int) -> User:
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one()


# ---------------------------------------------------------------------------
# GET /me/preferences
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_preferences_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/v1/me/preferences")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_preferences_returns_defaults(client: AsyncClient, alice, db_engine):
    user, _ = alice
    token = create_access_token(user_id=user.id, token_version=0)
    resp = await client.get(
        "/api/v1/me/preferences",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["theme_preference"] in ("light", "dark", "system")
    assert isinstance(data["totp_enabled"], bool)


# ---------------------------------------------------------------------------
# PUT /me/preferences/theme
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_theme_dark(client: AsyncClient, alice, db_engine):
    user, _ = alice
    token = create_access_token(user_id=user.id, token_version=0)
    resp = await client.put(
        "/api/v1/me/preferences/theme",
        json={"theme": "dark"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["theme_preference"] == "dark"

    updated = await _get_user(db_engine, user.id)
    assert updated.theme_preference.value == "dark"


@pytest.mark.asyncio
async def test_update_theme_system(client: AsyncClient, alice, db_engine):
    user, _ = alice
    token = create_access_token(user_id=user.id, token_version=0)
    resp = await client.put(
        "/api/v1/me/preferences/theme",
        json={"theme": "system"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["theme_preference"] == "system"


@pytest.mark.asyncio
async def test_update_theme_invalid_value(client: AsyncClient, alice, db_engine):
    user, _ = alice
    token = create_access_token(user_id=user.id, token_version=0)
    resp = await client.put(
        "/api/v1/me/preferences/theme",
        json={"theme": "rainbow"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
    assert "light, dark, system" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_update_theme_unauthenticated(client: AsyncClient):
    resp = await client.put("/api/v1/me/preferences/theme", json={"theme": "dark"})
    assert resp.status_code == 401
