"""Integration tests for authenticated GET /api/v1/openapi.json endpoint."""

import pytest
from httpx import AsyncClient

from backend.core.auth import create_access_token


@pytest.mark.asyncio
async def test_openapi_unauthenticated_returns_401(client: AsyncClient):
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_openapi_authenticated_returns_200(client: AsyncClient, alice):
    user, _ = alice
    token = create_access_token(user_id=user.id, token_version=0)
    resp = await client.get(
        "/api/v1/openapi.json",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "openapi" in data
    assert "paths" in data
    assert len(data["paths"]) > 0
