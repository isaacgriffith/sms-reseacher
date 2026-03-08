"""Placeholder tests for the health endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """Provide an async test client bound to the FastAPI app."""
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
