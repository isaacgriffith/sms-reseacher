"""Integration tests for POST /api/v1/studies/{study_id}/searches and GET list.

Covers:
- 202 response with job_id and search_execution_id when active search string exists
- 422 when no search string is configured for the study
- GET list returns existing executions
- 401 when unauthenticated
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.search import SearchString
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create a group + membership + study; return study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Search Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Search Study",
            "topic": "TDD",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _add_search_string(db_engine, study_id: int, active: bool = True) -> int:
    """Insert a SearchString and return its id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        ss = SearchString(
            study_id=study_id,
            version=1,
            string_text="TDD AND (quality OR testing)",
            is_active=active,
        )
        session.add(ss)
        await session.commit()
        return ss.id


class TestStartFullSearch:
    """POST /studies/{study_id}/searches — enqueue search job."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token → 401."""
        resp = await client.post("/api/v1/studies/1/searches", json={})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_no_search_string_returns_422(self, client, alice, db_engine) -> None:
        """No search string for the study → 422 Unprocessable Entity."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.post(
            f"/api/v1/studies/{study_id}/searches",
            json={"databases": ["acm"], "phase_tag": "initial-search"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_with_active_search_string_returns_202(
        self, client, alice, db_engine
    ) -> None:
        """Active search string → 202 with job_id and search_execution_id."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id, active=True)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/searches",
            json={"databases": ["acm", "ieee"], "phase_tag": "initial-search"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 202
        body = resp.json()
        assert "job_id" in body
        assert "search_execution_id" in body
        assert isinstance(body["job_id"], str)
        assert isinstance(body["search_execution_id"], int)

    @pytest.mark.asyncio
    async def test_with_inactive_string_falls_back_to_latest(
        self, client, alice, db_engine
    ) -> None:
        """No active string → falls back to latest version → 202."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id, active=False)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/searches",
            json={},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 202

    @pytest.mark.asyncio
    async def test_response_body_has_correct_fields(
        self, client, alice, db_engine
    ) -> None:
        """Response payload contains job_id (str) and search_execution_id (int)."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/searches",
            json={"phase_tag": "test-phase"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 202
        body = resp.json()
        assert set(body.keys()) >= {"job_id", "search_execution_id"}


class TestListSearches:
    """GET /studies/{study_id}/searches — list executions."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth → 401."""
        resp = await client.get("/api/v1/studies/1/searches")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_empty_list_when_no_searches(self, client, alice, db_engine) -> None:
        """No executions yet → empty list."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/searches", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_returns_execution_after_enqueue(self, client, alice, db_engine) -> None:
        """Triggering a search creates a SearchExecution visible in list."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)

        await client.post(
            f"/api/v1/studies/{study_id}/searches",
            json={},
            headers=_bearer(user.id),
        )
        resp = await client.get(
            f"/api/v1/studies/{study_id}/searches", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["study_id"] == study_id
        assert "status" in items[0]
