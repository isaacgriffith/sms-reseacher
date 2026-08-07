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
from db.models.jobs import BackgroundJob, JobStatus, JobType
from db.models.search import SearchString
from db.models.users import GroupMembership, GroupRole, ResearchGroup


async def _add_job(db_engine, study_id: int, job_type: JobType, job_status: JobStatus) -> None:
    """Insert a BackgroundJob for *study_id*."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        session.add(
            BackgroundJob(
                id=f"job-{study_id}-{job_type.value}-{job_status.value}",
                study_id=study_id,
                job_type=job_type,
                status=job_status,
            )
        )
        await session.commit()


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user, group_name: str = "Search Lab") -> int:
    """Create a group + membership + study; return study id.

    ``group_name`` is a parameter because ``research_group.name`` is UNIQUE, so
    a test needing two studies must name their groups distinctly.
    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=group_name)
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


class TestFullSearchInFlightGuard:
    """FR-026 — refuse a second automated pass over the same papers.

    The guard was one-directional when snowballing gained it: a snowball was
    refused while a full search ran, but not the reverse, so a full search
    could still be started on top of a running snowball. Both screen every
    candidate they create, so either order interleaves.
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize("blocking_type", [JobType.FULL_SEARCH, JobType.SNOWBALL_SEARCH])
    @pytest.mark.parametrize("blocking_status", [JobStatus.QUEUED, JobStatus.RUNNING])
    async def test_refuses_while_another_pass_is_in_flight(
        self, client, alice, db_engine, blocking_type, blocking_status
    ) -> None:
        """409 while any non-terminal automated pass is running for the study."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)
        await _add_job(db_engine, study_id, blocking_type, blocking_status)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/searches",
            json={},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_names_the_run_that_blocked_it(self, client, alice, db_engine) -> None:
        """The 409 payload identifies the blocking run, snowball included."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)
        await _add_job(db_engine, study_id, JobType.SNOWBALL_SEARCH, JobStatus.RUNNING)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/searches",
            json={},
            headers=_bearer(user.id),
        )
        detail = resp.json()["detail"]
        assert detail["blocking_job_type"] == "snowball_search"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("terminal_status", [JobStatus.COMPLETED, JobStatus.FAILED])
    async def test_ignores_finished_runs(self, client, alice, db_engine, terminal_status) -> None:
        """A finished run does not block a new one."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)
        await _add_job(db_engine, study_id, JobType.FULL_SEARCH, terminal_status)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/searches",
            json={},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 202

    @pytest.mark.asyncio
    async def test_a_second_search_is_refused_while_the_first_is_queued(
        self, client, alice, db_engine
    ) -> None:
        """Starting a search twice refuses the second.

        The first call leaves its own BackgroundJob queued, so this exercises
        the guard against real state rather than a fixture.
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_search_string(db_engine, study_id)

        first = await client.post(
            f"/api/v1/studies/{study_id}/searches", json={}, headers=_bearer(user.id)
        )
        second = await client.post(
            f"/api/v1/studies/{study_id}/searches", json={}, headers=_bearer(user.id)
        )

        assert first.status_code == 202
        assert second.status_code == 409

    @pytest.mark.asyncio
    async def test_another_studys_run_does_not_block(self, client, alice, db_engine) -> None:
        """The guard is per study, not global.

        Two studies are screened independently, so a run on one must not stop
        a run on the other.
        """
        user, _ = alice
        busy_study = await _setup_study(client, db_engine, user, group_name="Busy Lab")
        other_study = await _setup_study(client, db_engine, user, group_name="Other Lab")
        await _add_search_string(db_engine, other_study)
        await _add_job(db_engine, busy_study, JobType.FULL_SEARCH, JobStatus.RUNNING)

        resp = await client.post(
            f"/api/v1/studies/{other_study}/searches",
            json={},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 202


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
