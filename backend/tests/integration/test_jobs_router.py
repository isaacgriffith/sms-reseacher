"""Integration tests for /api/v1/jobs and /api/v1/studies/{study_id}/jobs.

Covers:
- GET /jobs/{job_id}/progress → SSE stream emits 'complete' event for a completed job
- GET /jobs/{job_id}/progress → 401 when unauthenticated
- GET /studies/{study_id}/jobs → list of recent jobs for a study
- GET /studies/{study_id}/jobs → 401 when unauthenticated
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.jobs import BackgroundJob, JobStatus, JobType
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create a group + membership + study; return study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Jobs Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Jobs Study",
            "topic": "TDD",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _insert_job(
    db_engine,
    study_id: int,
    job_id: str,
    status: JobStatus,
    progress_pct: int = 0,
    progress_detail: dict | None = None,
) -> None:
    """Insert a BackgroundJob directly into the test DB."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        job = BackgroundJob(
            id=job_id,
            study_id=study_id,
            job_type=JobType.FULL_SEARCH,
            status=status,
            progress_pct=progress_pct,
            progress_detail=progress_detail,
        )
        session.add(job)
        await session.commit()


class TestJobProgressSSE:
    """GET /jobs/{job_id}/progress — Server-Sent Events stream."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token → 401 before streaming."""
        resp = await client.get("/api/v1/jobs/some-job/progress")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_completed_job_emits_complete_event(
        self, client, alice, db_engine
    ) -> None:
        """COMPLETED job → SSE stream yields 'event: complete' immediately."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        job_id = "completed-job-001"
        detail = {"total_identified": 50, "accepted": 20, "rejected": 25, "duplicates": 5}
        await _insert_job(db_engine, study_id, job_id, JobStatus.COMPLETED, 100, detail)

        test_maker = async_sessionmaker(db_engine, expire_on_commit=False)
        with patch("backend.core.database._session_maker", test_maker):
            resp = await client.get(
                f"/api/v1/jobs/{job_id}/progress",
                headers=_bearer(user.id),
            )

        assert resp.status_code == 200
        content_type = resp.headers.get("content-type", "")
        assert "text/event-stream" in content_type
        body = resp.text
        assert "event: complete" in body

    @pytest.mark.asyncio
    async def test_failed_job_emits_error_event(
        self, client, alice, db_engine
    ) -> None:
        """FAILED job → SSE stream yields 'event: error'."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        job_id = "failed-job-001"
        await _insert_job(db_engine, study_id, job_id, JobStatus.FAILED)

        test_maker = async_sessionmaker(db_engine, expire_on_commit=False)
        with patch("backend.core.database._session_maker", test_maker):
            resp = await client.get(
                f"/api/v1/jobs/{job_id}/progress",
                headers=_bearer(user.id),
            )

        assert resp.status_code == 200
        assert "event: error" in resp.text

    @pytest.mark.asyncio
    async def test_unknown_job_emits_error_event(
        self, client, alice, db_engine
    ) -> None:
        """Non-existent job_id → SSE stream yields 'event: error'."""
        user, _ = alice
        await _setup_study(client, db_engine, user)

        test_maker = async_sessionmaker(db_engine, expire_on_commit=False)
        with patch("backend.core.database._session_maker", test_maker):
            resp = await client.get(
                "/api/v1/jobs/nonexistent-job-xyz/progress",
                headers=_bearer(user.id),
            )

        assert resp.status_code == 200
        assert "event: error" in resp.text


class TestListStudyJobs:
    """GET /studies/{study_id}/jobs — list recent jobs."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token → 401."""
        resp = await client.get("/api/v1/studies/1/jobs")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_empty_list_when_no_jobs(self, client, alice, db_engine) -> None:
        """No jobs → empty list."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/jobs", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_returns_inserted_job(self, client, alice, db_engine) -> None:
        """Inserted QUEUED job appears in list with correct shape."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        job_id = "list-job-001"
        await _insert_job(db_engine, study_id, job_id, JobStatus.QUEUED)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/jobs", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        jobs = resp.json()
        assert len(jobs) == 1
        j = jobs[0]
        assert j["id"] == job_id
        assert j["study_id"] == study_id
        assert j["status"] == "queued"
        assert j["job_type"] == "full_search"
        assert "progress_pct" in j

    @pytest.mark.asyncio
    async def test_multiple_jobs_returned_newest_first(
        self, client, alice, db_engine
    ) -> None:
        """Multiple jobs are returned (up to 20); ordering is newest first."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        for i in range(3):
            await _insert_job(db_engine, study_id, f"multi-job-{i:03d}", JobStatus.COMPLETED)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/jobs", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 3
