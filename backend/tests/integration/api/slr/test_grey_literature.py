"""Integration tests for SLR grey literature CRUD routes (feature 007, T090).

Covers:
- GET /slr/studies/{id}/grey-literature → 200 with empty list.
- POST /slr/studies/{id}/grey-literature → 201 creates source.
- DELETE /slr/studies/{id}/grey-literature/{source_id} → 204.
- DELETE with missing source → 404.
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Return Bearer token header for the given user id."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create a research group and SLR study, return study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=f"GreyLit Group {user.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Grey Literature SLR Test",
            "topic": "grey literature",
            "study_type": "SLR",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


class TestListGreyLiterature:
    """GET /slr/studies/{id}/grey-literature."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_initially(self, client, db_engine, alice) -> None:
        """Returns 200 with empty sources list when no records exist."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/grey-literature",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["sources"] == []


class TestCreateGreyLiteratureSource:
    """POST /slr/studies/{id}/grey-literature."""

    @pytest.mark.asyncio
    async def test_creates_source_and_returns_201(self, client, db_engine, alice) -> None:
        """Returns 201 with the created source."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.post(
            f"/api/v1/slr/studies/{study_id}/grey-literature",
            json={
                "source_type": "technical_report",
                "title": "Example Technical Report",
                "authors": "Jane Doe",
                "year": 2024,
                "url": "https://example.com/report.pdf",
                "description": "Relevant to our research questions.",
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Example Technical Report"
        assert data["source_type"] == "technical_report"
        assert data["study_id"] == study_id
        assert "id" in data

    @pytest.mark.asyncio
    async def test_created_source_appears_in_list(self, client, db_engine, alice) -> None:
        """Source created via POST appears in subsequent GET."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        await client.post(
            f"/api/v1/slr/studies/{study_id}/grey-literature",
            json={"source_type": "dissertation", "title": "My Dissertation"},
            headers=_bearer(user.id),
        )

        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/grey-literature",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        sources = resp.json()["sources"]
        assert len(sources) == 1
        assert sources[0]["title"] == "My Dissertation"

    @pytest.mark.asyncio
    async def test_invalid_source_type_returns_400(self, client, db_engine, alice) -> None:
        """POST with an invalid source_type returns 400."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.post(
            f"/api/v1/slr/studies/{study_id}/grey-literature",
            json={"source_type": "invalid_type", "title": "Bad Source"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 400


class TestDeleteGreyLiteratureSource:
    """DELETE /slr/studies/{id}/grey-literature/{source_id}."""

    @pytest.mark.asyncio
    async def test_deletes_source_and_returns_204(self, client, db_engine, alice) -> None:
        """Returns 204 after deleting an existing source."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        create_resp = await client.post(
            f"/api/v1/slr/studies/{study_id}/grey-literature",
            json={"source_type": "work_in_progress", "title": "WIP Paper"},
            headers=_bearer(user.id),
        )
        assert create_resp.status_code == 201
        source_id = create_resp.json()["id"]

        delete_resp = await client.delete(
            f"/api/v1/slr/studies/{study_id}/grey-literature/{source_id}",
            headers=_bearer(user.id),
        )
        assert delete_resp.status_code == 204

        # Verify it's gone
        list_resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/grey-literature",
            headers=_bearer(user.id),
        )
        assert list_resp.json()["sources"] == []

    @pytest.mark.asyncio
    async def test_delete_missing_source_returns_404(self, client, db_engine, alice) -> None:
        """Returns 404 when the source does not exist."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.delete(
            f"/api/v1/slr/studies/{study_id}/grey-literature/99999",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_source_from_wrong_study_returns_404(
        self, client, db_engine, alice, bob
    ) -> None:
        """Returns 404 when source belongs to a different study."""
        user_a, _ = alice
        user_b, _ = bob

        study_a = await _setup_study(client, db_engine, user_a)
        study_b = await _setup_study(client, db_engine, user_b)

        # Create source in study_a
        create_resp = await client.post(
            f"/api/v1/slr/studies/{study_a}/grey-literature",
            json={"source_type": "technical_report", "title": "Study A Report"},
            headers=_bearer(user_a.id),
        )
        source_id = create_resp.json()["id"]

        # Try to delete it via study_b path
        resp = await client.delete(
            f"/api/v1/slr/studies/{study_b}/grey-literature/{source_id}",
            headers=_bearer(user_b.id),
        )
        assert resp.status_code == 404
