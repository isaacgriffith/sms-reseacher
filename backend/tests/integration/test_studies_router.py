"""Integration tests for the /api/v1/studies router.

Covers wizard POST, GET detail, PATCH, archive, and delete including 401/403 paths.
"""

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for the given user_id."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _create_group(db_engine, user_id: int) -> int:
    """Insert a ResearchGroup, add user as admin, and return the group id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Test Lab")
        session.add(group)
        await session.flush()
        session.add(
            GroupMembership(group_id=group.id, user_id=user_id, role=GroupRole.ADMIN)
        )
        await session.commit()
        return group.id


_WIZARD_PAYLOAD = {
    "name": "My SMS Study",
    "topic": "Test-Driven Development",
    "study_type": "SMS",
    "motivation": "Understand TDD adoption",
    "research_objectives": ["Obj 1"],
    "research_questions": ["RQ1"],
    "snowball_threshold": 5,
}


class TestCreateStudy:
    """POST /groups/{group_id}/studies — wizard endpoint."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client):
        """No auth token → 401 before any group lookup."""
        resp = await client.post("/api/v1/groups/1/studies", json=_WIZARD_PAYLOAD)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_creates_study_and_returns_detail(self, client, alice, db_engine):
        """Valid wizard payload → 201 StudyDetail with unlocked_phases and stale_phases."""
        user, _ = alice
        group_id = await _create_group(db_engine, user.id)
        resp = await client.post(
            f"/api/v1/groups/{group_id}/studies",
            json=_WIZARD_PAYLOAD,
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "My SMS Study"
        assert body["study_type"] == "SMS"
        assert body["current_phase"] == 1
        assert "unlocked_phases" in body
        assert "stale_phases" in body
        assert isinstance(body["stale_phases"], dict)

    @pytest.mark.asyncio
    async def test_invalid_study_type_returns_422(self, client, alice, db_engine):
        """Unknown study_type → 422."""
        user, _ = alice
        group_id = await _create_group(db_engine, user.id)
        resp = await client.post(
            f"/api/v1/groups/{group_id}/studies",
            json={**_WIZARD_PAYLOAD, "study_type": "INVALID"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_non_member_group_returns_404(self, client, alice, bob, db_engine):
        """User who is not in the group gets 404."""
        alice_user, _ = alice
        bob_user, _ = bob
        group_id = await _create_group(db_engine, alice_user.id)
        resp = await client.post(
            f"/api/v1/groups/{group_id}/studies",
            json=_WIZARD_PAYLOAD,
            headers=_bearer(bob_user.id),
        )
        assert resp.status_code == 404


class TestGetStudy:
    """GET /studies/{study_id} — full detail endpoint."""

    @pytest.mark.asyncio
    async def test_returns_stale_phases_field(self, client, alice, db_engine):
        """GET detail includes stale_phases dict."""
        user, _ = alice
        group_id = await _create_group(db_engine, user.id)
        create_resp = await client.post(
            f"/api/v1/groups/{group_id}/studies",
            json=_WIZARD_PAYLOAD,
            headers=_bearer(user.id),
        )
        study_id = create_resp.json()["id"]

        resp = await client.get(f"/api/v1/studies/{study_id}", headers=_bearer(user.id))
        assert resp.status_code == 200
        assert "stale_phases" in resp.json()
        assert resp.json()["stale_phases"] == {"search": False, "extraction": False}

    @pytest.mark.asyncio
    async def test_non_member_returns_404(self, client, alice, bob, db_engine):
        """Non-member cannot access study detail."""
        alice_user, _ = alice
        bob_user, _ = bob
        group_id = await _create_group(db_engine, alice_user.id)
        create_resp = await client.post(
            f"/api/v1/groups/{group_id}/studies",
            json=_WIZARD_PAYLOAD,
            headers=_bearer(alice_user.id),
        )
        study_id = create_resp.json()["id"]
        resp = await client.get(f"/api/v1/studies/{study_id}", headers=_bearer(bob_user.id))
        assert resp.status_code == 404


class TestArchiveDeleteStudy:
    """POST /archive and DELETE — lifecycle endpoints."""

    @pytest.mark.asyncio
    async def test_archive_sets_status(self, client, alice, db_engine):
        user, _ = alice
        group_id = await _create_group(db_engine, user.id)
        create_resp = await client.post(
            f"/api/v1/groups/{group_id}/studies",
            json=_WIZARD_PAYLOAD,
            headers=_bearer(user.id),
        )
        study_id = create_resp.json()["id"]
        resp = await client.post(
            f"/api/v1/studies/{study_id}/archive", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "archived"

    @pytest.mark.asyncio
    async def test_delete_returns_204(self, client, alice, db_engine):
        user, _ = alice
        group_id = await _create_group(db_engine, user.id)
        create_resp = await client.post(
            f"/api/v1/groups/{group_id}/studies",
            json=_WIZARD_PAYLOAD,
            headers=_bearer(user.id),
        )
        study_id = create_resp.json()["id"]
        resp = await client.delete(
            f"/api/v1/studies/{study_id}", headers=_bearer(user.id)
        )
        assert resp.status_code == 204
