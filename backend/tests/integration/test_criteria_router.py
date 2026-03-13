"""Integration tests for the /api/v1/criteria router.

Covers GET/POST/DELETE for inclusion and exclusion criteria.
"""

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create a group and study, returning the study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Criteria Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Criteria Study",
            "topic": "TDD",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    return resp.json()["id"]


class TestInclusionCriteria:
    """GET / POST / DELETE /studies/{study_id}/criteria/inclusion."""

    @pytest.mark.asyncio
    async def test_list_empty_initially(self, client, alice, db_engine):
        """No criteria returns empty list."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/criteria/inclusion",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_add_criterion(self, client, alice, db_engine):
        """POST adds a new inclusion criterion."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.post(
            f"/api/v1/studies/{study_id}/criteria/inclusion",
            json={"description": "Must be empirical study", "order_index": 0},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["description"] == "Must be empirical study"
        assert body["study_id"] == study_id

    @pytest.mark.asyncio
    async def test_list_returns_added_criterion(self, client, alice, db_engine):
        """Criteria added via POST appear in subsequent GET."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await client.post(
            f"/api/v1/studies/{study_id}/criteria/inclusion",
            json={"description": "Peer-reviewed only", "order_index": 0},
            headers=_bearer(user.id),
        )
        resp = await client.get(
            f"/api/v1/studies/{study_id}/criteria/inclusion",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        descriptions = [c["description"] for c in resp.json()]
        assert "Peer-reviewed only" in descriptions

    @pytest.mark.asyncio
    async def test_delete_criterion(self, client, alice, db_engine):
        """DELETE removes the criterion; subsequent GET no longer returns it."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        add_resp = await client.post(
            f"/api/v1/studies/{study_id}/criteria/inclusion",
            json={"description": "To be deleted", "order_index": 0},
            headers=_bearer(user.id),
        )
        criterion_id = add_resp.json()["id"]

        del_resp = await client.delete(
            f"/api/v1/studies/{study_id}/criteria/inclusion/{criterion_id}",
            headers=_bearer(user.id),
        )
        assert del_resp.status_code == 204

        list_resp = await client.get(
            f"/api/v1/studies/{study_id}/criteria/inclusion",
            headers=_bearer(user.id),
        )
        assert list_resp.json() == []

    @pytest.mark.asyncio
    async def test_delete_nonexistent_returns_404(self, client, alice, db_engine):
        """Deleting a missing criterion returns 404."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.delete(
            f"/api/v1/studies/{study_id}/criteria/inclusion/99999",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client, alice, db_engine):
        """No auth header returns 401."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(f"/api/v1/studies/{study_id}/criteria/inclusion")
        assert resp.status_code == 401


class TestExclusionCriteria:
    """GET / POST / DELETE /studies/{study_id}/criteria/exclusion."""

    @pytest.mark.asyncio
    async def test_list_empty_initially(self, client, alice, db_engine):
        """No criteria returns empty list."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/criteria/exclusion",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_add_exclusion_criterion(self, client, alice, db_engine):
        """POST adds a new exclusion criterion."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.post(
            f"/api/v1/studies/{study_id}/criteria/exclusion",
            json={"description": "No grey literature", "order_index": 0},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        assert resp.json()["description"] == "No grey literature"

    @pytest.mark.asyncio
    async def test_inclusion_and_exclusion_are_independent(self, client, alice, db_engine):
        """Inclusion and exclusion criteria lists are independent."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await client.post(
            f"/api/v1/studies/{study_id}/criteria/inclusion",
            json={"description": "Inclusion only", "order_index": 0},
            headers=_bearer(user.id),
        )
        await client.post(
            f"/api/v1/studies/{study_id}/criteria/exclusion",
            json={"description": "Exclusion only", "order_index": 0},
            headers=_bearer(user.id),
        )
        inc = await client.get(
            f"/api/v1/studies/{study_id}/criteria/inclusion",
            headers=_bearer(user.id),
        )
        exc = await client.get(
            f"/api/v1/studies/{study_id}/criteria/exclusion",
            headers=_bearer(user.id),
        )
        inc_descs = [c["description"] for c in inc.json()]
        exc_descs = [c["description"] for c in exc.json()]
        assert "Inclusion only" in inc_descs
        assert "Exclusion only" not in inc_descs
        assert "Exclusion only" in exc_descs
        assert "Inclusion only" not in exc_descs
