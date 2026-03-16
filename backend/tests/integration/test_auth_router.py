"""Integration tests for the /api/v1/auth router.

Covers POST /auth/login and GET /auth/me, including 401/403 error paths.
"""

import pytest

from backend.core.auth import create_access_token

BASE = "/api/v1/auth"


class TestLogin:
    """POST /auth/login — credential validation and token issuance."""

    @pytest.mark.asyncio
    async def test_success_returns_token_and_user_info(self, client, alice):
        """Valid credentials return 200 with JWT, token_type, user_id, display_name."""
        user, plain = alice
        resp = await client.post(
            f"{BASE}/login", json={"email": user.email, "password": plain}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["token_type"] == "bearer"
        assert "access_token" in body
        assert len(body["access_token"]) > 20  # non-trivial JWT string
        assert body["user_id"] == user.id
        assert body["display_name"] == "Alice"

    @pytest.mark.asyncio
    async def test_wrong_password_returns_401(self, client, alice):
        """Correct email but wrong password → 401 Unauthorized."""
        user, _ = alice
        resp = await client.post(
            f"{BASE}/login", json={"email": user.email, "password": "notthepassword"}
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_unknown_email_returns_401(self, client):
        """Non-existent email → 401 Unauthorized (no user-enumeration leak)."""
        resp = await client.post(
            f"{BASE}/login", json={"email": "ghost@example.com", "password": "anything"}
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_email_format_returns_422(self, client):
        """Malformed email address in request body → 422 Unprocessable Entity."""
        resp = await client.post(
            f"{BASE}/login", json={"email": "not-an-email", "password": "x"}
        )
        assert resp.status_code == 422


class TestMe:
    """GET /auth/me — current user profile."""

    @pytest.mark.asyncio
    async def test_success_returns_profile_and_empty_groups(self, client, alice):
        """Valid JWT → 200 with id, email, display_name, and empty groups list."""
        user, _ = alice
        token = create_access_token(user_id=user.id)
        resp = await client.get(
            f"{BASE}/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == user.id
        assert body["email"] == "alice@example.com"
        assert body["display_name"] == "Alice"
        assert body["groups"] == []

    @pytest.mark.asyncio
    async def test_no_token_returns_401(self, client):
        """Missing Authorization header → 401 Unauthorized."""
        resp = await client.get(f"{BASE}/me")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_token_returns_401(self, client):
        """Garbage JWT string → 401 Unauthorized."""
        resp = await client.get(
            f"{BASE}/me", headers={"Authorization": "Bearer garbage.token.value"}
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_token_for_nonexistent_user_returns_401(self, client):
        """JWT with a user_id that has no DB row → 401 Unauthorized.

        get_current_user performs a DB lookup for token_version validation;
        a missing user is treated as an invalid credential (401) rather than
        revealing the absence of the account (404).
        """
        token = create_access_token(user_id=999_999)
        resp = await client.get(
            f"{BASE}/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 401
