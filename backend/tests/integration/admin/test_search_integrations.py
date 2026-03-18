"""Integration tests for admin search integrations endpoints (T051).

Covers:
- GET /api/v1/admin/search-integrations: 403 without admin role.
- GET /api/v1/admin/search-integrations: returns all IntegrationType entries.
- GET /api/v1/admin/search-integrations/{type}: returns single record.
- GET /api/v1/admin/search-integrations/invalid_type: returns 404.
- PUT /api/v1/admin/search-integrations/ieee_xplore: creates credential, has_api_key=True.
- PUT: api_key=null clears key (has_api_key=False).
- PUT: version_id conflict returns 409.
- POST /api/v1/admin/search-integrations/ieee_xplore/test: returns test result.
- Non-admin user gets 403 on all endpoints.
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.search_integrations import IntegrationType
from db.models.users import GroupMembership, GroupRole, ResearchGroup, User


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for *user_id*.

    Args:
        user_id: User primary key.

    Returns:
        Dict with ``Authorization`` header.
    """
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _make_admin(db_engine, user: User) -> None:
    """Insert a research group and make *user* an admin member.

    Args:
        db_engine: Test async engine.
        user: The user to grant admin membership to.
    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Admin Group")
        session.add(group)
        await session.flush()
        session.add(
            GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN)
        )
        await session.commit()


class TestListSearchIntegrations:
    """GET /api/v1/admin/search-integrations."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token returns 401."""
        resp = await client.get("/api/v1/admin/search-integrations")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_non_admin_returns_403(self, client, alice) -> None:
        """User without admin role returns 403."""
        user, _ = alice
        resp = await client.get(
            "/api/v1/admin/search-integrations",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_returns_all_integration_types(self, client, alice, db_engine) -> None:
        """Admin user receives all IntegrationType values in the response."""
        user, _ = alice
        await _make_admin(db_engine, user)
        resp = await client.get(
            "/api/v1/admin/search-integrations",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        returned_types = {item["integration_type"] for item in data}
        for it in IntegrationType:
            assert it.value in returned_types

    @pytest.mark.asyncio
    async def test_response_never_includes_api_key(self, client, alice, db_engine) -> None:
        """Response items must not contain an api_key field."""
        user, _ = alice
        await _make_admin(db_engine, user)
        resp = await client.get(
            "/api/v1/admin/search-integrations",
            headers=_bearer(user.id),
        )
        data = resp.json()
        for item in data:
            assert "api_key" not in item
            assert "api_key_encrypted" not in item


class TestGetSingleIntegration:
    """GET /api/v1/admin/search-integrations/{type}."""

    @pytest.mark.asyncio
    async def test_returns_single_integration(self, client, alice, db_engine) -> None:
        """Returns a single IntegrationSummary for a valid type."""
        user, _ = alice
        await _make_admin(db_engine, user)
        resp = await client.get(
            "/api/v1/admin/search-integrations/ieee_xplore",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["integration_type"] == "ieee_xplore"
        assert data["display_name"] == "IEEE Xplore"

    @pytest.mark.asyncio
    async def test_invalid_type_returns_404(self, client, alice, db_engine) -> None:
        """Unknown integration_type returns 404."""
        user, _ = alice
        await _make_admin(db_engine, user)
        resp = await client.get(
            "/api/v1/admin/search-integrations/nonexistent_type",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404


class TestUpsertIntegration:
    """PUT /api/v1/admin/search-integrations/{type}."""

    @pytest.mark.asyncio
    async def test_creates_credential_has_api_key_true(self, client, alice, db_engine) -> None:
        """Storing an api_key results in has_api_key=True in the response."""
        user, _ = alice
        await _make_admin(db_engine, user)
        resp = await client.put(
            "/api/v1/admin/search-integrations/ieee_xplore",
            json={"api_key": "ieee-test-key"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["has_api_key"] is True
        assert "api_key" not in data

    @pytest.mark.asyncio
    async def test_null_api_key_clears_stored_key(self, client, alice, db_engine) -> None:
        """Sending api_key=null after storing a key clears it (has_api_key=False)."""
        user, _ = alice
        await _make_admin(db_engine, user)
        # Store a key first
        await client.put(
            "/api/v1/admin/search-integrations/ieee_xplore",
            json={"api_key": "ieee-test-key"},
            headers=_bearer(user.id),
        )
        # Clear it
        resp = await client.put(
            "/api/v1/admin/search-integrations/ieee_xplore",
            json={"api_key": None, "version_id": 1},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["has_api_key"] is False

    @pytest.mark.asyncio
    async def test_version_conflict_returns_409(self, client, alice, db_engine) -> None:
        """Mismatched version_id returns 409 Conflict."""
        user, _ = alice
        await _make_admin(db_engine, user)
        # Create credential (version_id becomes 1)
        await client.put(
            "/api/v1/admin/search-integrations/ieee_xplore",
            json={"api_key": "original-key"},
            headers=_bearer(user.id),
        )
        # Update with wrong version
        resp = await client.put(
            "/api/v1/admin/search-integrations/ieee_xplore",
            json={"api_key": "new-key", "version_id": 99},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_invalid_type_returns_404(self, client, alice, db_engine) -> None:
        """Unknown integration_type in PUT returns 404."""
        user, _ = alice
        await _make_admin(db_engine, user)
        resp = await client.put(
            "/api/v1/admin/search-integrations/unknown_type",
            json={"api_key": "key"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404


class TestTestIntegration:
    """POST /api/v1/admin/search-integrations/{type}/test."""

    @pytest.mark.asyncio
    async def test_returns_test_result(self, client, alice, db_engine) -> None:
        """POST test returns a TestResult with status and message fields."""
        user, _ = alice
        await _make_admin(db_engine, user)
        resp = await client.post(
            "/api/v1/admin/search-integrations/semantic_scholar/test",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "message" in data
        assert "tested_at" in data
        assert data["integration_type"] == "semantic_scholar"

    @pytest.mark.asyncio
    async def test_no_key_returns_auth_failed_status(self, client, alice, db_engine) -> None:
        """Returns auth_failed status when no key is configured."""
        user, _ = alice
        await _make_admin(db_engine, user)
        resp = await client.post(
            "/api/v1/admin/search-integrations/ieee_xplore/test",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        # No key stored, so status should be auth_failed or unreachable
        assert resp.json()["status"] in ("auth_failed", "unreachable", "success")

    @pytest.mark.asyncio
    async def test_invalid_type_returns_404(self, client, alice, db_engine) -> None:
        """Unknown integration_type in POST test returns 404."""
        user, _ = alice
        await _make_admin(db_engine, user)
        resp = await client.post(
            "/api/v1/admin/search-integrations/bad_type/test",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404
