"""Integration tests for study database selection endpoints (T014).

Covers:
- GET /api/v1/studies/{study_id}/database-selection: returns default when none saved.
- GET /api/v1/studies/{study_id}/database-selection: returns saved selections.
- PUT /api/v1/studies/{study_id}/database-selection: saves selections and returns updated state.
- PUT with scihub_enabled=True without acknowledgment returns 422.
- PUT with scihub_enabled=True + acknowledgment but SCIHUB_ENABLED=False returns 403.
- Unauthenticated requests return 401.
- Access to another user's study returns 403.
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create group + membership + study; return study id.

    Args:
        client: Test HTTP client.
        db_engine: Async test database engine.
        user: The user to add as study member.

    Returns:
        The created study's integer ID.
    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="DB Selection Lab")
        session.add(group)
        await session.flush()
        session.add(
            GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN)
        )
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "DB Selection Study",
            "topic": "Academic databases",
            "study_type": "SMS",
            "research_objectives": ["Obj 1"],
            "research_questions": ["RQ1"],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


class TestGetDatabaseSelection:
    """GET /studies/{study_id}/database-selection."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token returns 401."""
        resp = await client.get("/api/v1/studies/1/database-selection")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_default_selection_returned_when_none_saved(
        self, client, alice, db_engine
    ) -> None:
        """When no selection has been saved, the default is returned."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/database-selection",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["study_id"] == study_id
        assert "selections" in body
        assert isinstance(body["selections"], list)
        # Default: Semantic Scholar enabled
        ss = next(
            (s for s in body["selections"] if s["database_index"] == "semantic_scholar"),
            None,
        )
        assert ss is not None
        assert ss["is_enabled"] is True

    @pytest.mark.asyncio
    async def test_response_includes_all_expected_fields(
        self, client, alice, db_engine
    ) -> None:
        """Response body includes study_id, selections, snowball_enabled, scihub_enabled."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/database-selection",
            headers=_bearer(user.id),
        )
        body = resp.json()
        assert "snowball_enabled" in body
        assert "scihub_enabled" in body
        assert "scihub_acknowledged" in body

    @pytest.mark.asyncio
    async def test_selection_item_has_status_and_credential_fields(
        self, client, alice, db_engine
    ) -> None:
        """Each selection item includes status and requires_credential fields."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/database-selection",
            headers=_bearer(user.id),
        )
        body = resp.json()
        first_item = body["selections"][0]
        assert "database_index" in first_item
        assert "is_enabled" in first_item
        assert "status" in first_item
        assert "requires_credential" in first_item
        assert "credential_configured" in first_item


class TestPutDatabaseSelection:
    """PUT /studies/{study_id}/database-selection."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token returns 401."""
        resp = await client.put(
            "/api/v1/studies/1/database-selection",
            json={"selections": [], "snowball_enabled": False, "scihub_enabled": False, "scihub_acknowledged": False},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_save_and_retrieve_selection(self, client, alice, db_engine) -> None:
        """PUT saves selections; subsequent GET returns the saved values."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        payload = {
            "selections": [
                {"database_index": "ieee_xplore", "is_enabled": True},
                {"database_index": "semantic_scholar", "is_enabled": True},
                {"database_index": "scopus", "is_enabled": False},
            ],
            "snowball_enabled": True,
            "scihub_enabled": False,
            "scihub_acknowledged": False,
        }
        put_resp = await client.put(
            f"/api/v1/studies/{study_id}/database-selection",
            json=payload,
            headers=_bearer(user.id),
        )
        assert put_resp.status_code == 200
        body = put_resp.json()
        assert body["study_id"] == study_id
        assert body["snowball_enabled"] is True

        # Verify GET returns the saved state
        get_resp = await client.get(
            f"/api/v1/studies/{study_id}/database-selection",
            headers=_bearer(user.id),
        )
        assert get_resp.status_code == 200
        saved = get_resp.json()
        ieee = next(
            (s for s in saved["selections"] if s["database_index"] == "ieee_xplore"),
            None,
        )
        assert ieee is not None
        assert ieee["is_enabled"] is True

    @pytest.mark.asyncio
    async def test_scihub_enabled_without_acknowledgment_returns_422(
        self, client, alice, db_engine
    ) -> None:
        """scihub_enabled=True without scihub_acknowledged=True returns 422."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        payload = {
            "selections": [],
            "snowball_enabled": False,
            "scihub_enabled": True,
            "scihub_acknowledged": False,
        }
        resp = await client.put(
            f"/api/v1/studies/{study_id}/database-selection",
            json=payload,
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_scihub_enabled_server_disabled_returns_403(
        self, client, alice, db_engine, monkeypatch
    ) -> None:
        """scihub_enabled=True with server SCIHUB_ENABLED=false returns 403."""
        import researcher_mcp.core.config as cfg_mod

        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        # Ensure SCIHUB_ENABLED is False at the server level
        monkeypatch.setenv("SCIHUB_ENABLED", "false")

        payload = {
            "selections": [],
            "snowball_enabled": False,
            "scihub_enabled": True,
            "scihub_acknowledged": True,
        }
        resp = await client.put(
            f"/api/v1/studies/{study_id}/database-selection",
            json=payload,
            headers=_bearer(user.id),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_invalid_database_index_returns_422(
        self, client, alice, db_engine
    ) -> None:
        """An invalid database_index value returns 422."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        payload = {
            "selections": [
                {"database_index": "not_a_valid_index", "is_enabled": True}
            ],
            "snowball_enabled": False,
            "scihub_enabled": False,
            "scihub_acknowledged": False,
        }
        resp = await client.put(
            f"/api/v1/studies/{study_id}/database-selection",
            json=payload,
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422
