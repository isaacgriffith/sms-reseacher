"""Unit tests for the health endpoint.

Uses dependency override so no real JWT is required for the health check.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from backend.core.auth import CurrentUser, create_access_token, get_current_user
from backend.main import create_app


def _make_app_with_auth_override():
    """Create a test FastAPI app with auth dependency overridden.

    Returns:
        A :class:`FastAPI` instance whose ``get_current_user`` dependency is
        stubbed out with a pre-authenticated dummy user so that tests do not
        require a real database or valid JWT.
    """
    app = create_app()

    async def _fake_user() -> CurrentUser:
        return CurrentUser(user_id=1)

    app.dependency_overrides[get_current_user] = _fake_user
    return app


@pytest.fixture
async def client() -> AsyncClient:  # type: ignore[misc]
    """Provide an async test client with auth stubbed out.

    Yields:
        An :class:`httpx.AsyncClient` bound to the test FastAPI app.
    """
    app = _make_app_with_auth_override()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c  # type: ignore[misc]


class TestHealthEndpoint:
    """Tests for GET /api/v1/health."""

    async def test_health_returns_200(self, client: AsyncClient) -> None:
        """Health endpoint returns HTTP 200."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200

    async def test_health_returns_ok_status(self, client: AsyncClient) -> None:
        """Health response body contains status=ok."""
        response = await client.get("/api/v1/health")
        assert response.json()["status"] == "ok"

    async def test_health_returns_version(self, client: AsyncClient) -> None:
        """Health response body contains a non-empty version string."""
        response = await client.get("/api/v1/health")
        body = response.json()
        assert "version" in body
        assert body["version"]

    async def test_health_response_content_type(self, client: AsyncClient) -> None:
        """Health response has JSON content type."""
        response = await client.get("/api/v1/health")
        assert "application/json" in response.headers["content-type"]

    async def test_health_unauthenticated_returns_401(self) -> None:
        """Health endpoint returns 401 without a valid token."""
        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            response = await c.get("/api/v1/health")
        assert response.status_code == 401

    async def test_health_with_valid_jwt_returns_200(self) -> None:
        """Health endpoint returns 200 with a real JWT token."""
        app = create_app()
        token = create_access_token(user_id=1)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            response = await c.get(
                "/api/v1/health",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == 200
