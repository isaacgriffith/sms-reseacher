"""Integration tests for GET /admin/health, GET /admin/jobs, POST /admin/jobs/{id}/retry.

Covers:
- Health endpoint returns all four service names
- Non-admin (no group admin role) gets 403
- GET /admin/jobs returns paginated list; status filter applied
- POST /admin/jobs/{id}/retry → 409 when job is not in failed status
- POST /admin/jobs/{id}/retry → 404 when job does not exist
"""

from __future__ import annotations

import uuid
from datetime import datetime, UTC

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker
from unittest.mock import patch, AsyncMock

from backend.core.auth import create_access_token
from db.models.jobs import BackgroundJob, JobStatus, JobType
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _make_group_admin(db_engine, user) -> None:
    """Add user as admin of a fresh research group."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=f"Admin Group {user.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()


async def _insert_job(db_engine, study_id: int, status: JobStatus) -> str:
    """Insert a BackgroundJob row with the given status and return its id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    job_id = str(uuid.uuid4())
    async with maker() as session:
        job = BackgroundJob(
            id=job_id,
            study_id=study_id,
            job_type=JobType.FULL_SEARCH,
            status=status,
            progress_pct=0,
        )
        session.add(job)
        await session.commit()
    return job_id


async def _setup_study(client, db_engine, user) -> int:
    """Create a group + study for the user; returns study_id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=f"Job Group {user.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={"name": "Job Study", "topic": "Test", "study_type": "SMS",
              "research_objectives": [], "research_questions": []},
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


class TestAdminHealth:
    """GET /admin/health."""

    @pytest.mark.asyncio
    async def test_non_admin_gets_403(self, client, bob, db_engine):
        """A user with no group admin role gets 403."""
        user, _ = bob
        # bob has no group memberships → not a group admin
        resp = await client.get("/api/v1/admin/health", headers=_bearer(user.id))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_unauthenticated_gets_401(self, client):
        """Unauthenticated request gets 401."""
        resp = await client.get("/api/v1/admin/health")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_admin_gets_health_response(self, client, alice, db_engine):
        """A group admin receives a health payload with all four service names."""
        from backend.api.v1.admin import ServiceHealth

        user, _ = alice
        await _make_group_admin(db_engine, user)

        with (
            patch("backend.api.v1.admin._probe_database", AsyncMock(
                return_value=ServiceHealth(name="database", status="healthy", latency_ms=1.0)
            )),
            patch("backend.api.v1.admin._probe_redis", AsyncMock(
                return_value=ServiceHealth(name="redis", status="healthy", latency_ms=0.5)
            )),
            patch("backend.api.v1.admin._probe_arq_worker", AsyncMock(
                return_value=ServiceHealth(name="arq_worker", status="healthy", detail="active_jobs=0")
            )),
            patch("backend.api.v1.admin._probe_researcher_mcp", AsyncMock(
                return_value=ServiceHealth(name="researcher_mcp", status="healthy", latency_ms=5.0)
            )),
        ):
            resp = await client.get("/api/v1/admin/health", headers=_bearer(user.id))

        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
        assert "services" in body
        assert "checked_at" in body
        service_names = {s["name"] for s in body["services"]}
        assert {"database", "redis", "arq_worker", "researcher_mcp"} == service_names

    @pytest.mark.asyncio
    async def test_health_response_contains_no_secrets(self, client, alice, db_engine):
        """Health response must not expose any config secret field names."""
        from backend.api.v1.admin import ServiceHealth

        user, _ = alice
        await _make_group_admin(db_engine, user)

        secret_fields = {"database_url", "secret_key", "anthropic_api_key", "redis_url"}

        with (
            patch("backend.api.v1.admin._probe_database", AsyncMock(
                return_value=ServiceHealth(name="database", status="healthy"))),
            patch("backend.api.v1.admin._probe_redis", AsyncMock(
                return_value=ServiceHealth(name="redis", status="healthy"))),
            patch("backend.api.v1.admin._probe_arq_worker", AsyncMock(
                return_value=ServiceHealth(name="arq_worker", status="healthy"))),
            patch("backend.api.v1.admin._probe_researcher_mcp", AsyncMock(
                return_value=ServiceHealth(name="researcher_mcp", status="healthy"))),
        ):
            resp = await client.get("/api/v1/admin/health", headers=_bearer(user.id))

        raw_text = resp.text
        for field in secret_fields:
            assert field not in raw_text, f"Secret field '{field}' found in health response"


class TestAdminJobs:
    """GET /admin/jobs."""

    @pytest.mark.asyncio
    async def test_non_admin_gets_403(self, client, bob, db_engine):
        """A user with no group admin role gets 403."""
        user, _ = bob
        resp = await client.get("/api/v1/admin/jobs", headers=_bearer(user.id))
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_lists_all_jobs_when_no_filter(self, client, alice, db_engine):
        """Without status filter, all jobs across studies are returned."""
        user, _ = alice
        await _make_group_admin(db_engine, user)
        study_id = await _setup_study(client, db_engine, user)
        await _insert_job(db_engine, study_id, JobStatus.FAILED)
        await _insert_job(db_engine, study_id, JobStatus.COMPLETED)

        resp = await client.get("/api/v1/admin/jobs", headers=_bearer(user.id))
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 2

    @pytest.mark.asyncio
    async def test_status_filter_returns_only_failed(self, client, alice, db_engine):
        """status=failed filter returns only failed jobs."""
        user, _ = alice
        await _make_group_admin(db_engine, user)
        study_id = await _setup_study(client, db_engine, user)
        await _insert_job(db_engine, study_id, JobStatus.FAILED)
        await _insert_job(db_engine, study_id, JobStatus.COMPLETED)

        resp = await client.get(
            "/api/v1/admin/jobs?status=failed",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        for item in body["items"]:
            assert item["status"] == "failed"

    @pytest.mark.asyncio
    async def test_invalid_status_returns_422(self, client, alice, db_engine):
        """Invalid status value returns 422."""
        user, _ = alice
        await _make_group_admin(db_engine, user)
        resp = await client.get(
            "/api/v1/admin/jobs?status=bogus",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422


class TestAdminJobRetry:
    """POST /admin/jobs/{job_id}/retry."""

    @pytest.mark.asyncio
    async def test_retry_failed_job_succeeds(self, client, alice, db_engine):
        """Retrying a failed job returns 202 with new and original job IDs."""
        user, _ = alice
        await _make_group_admin(db_engine, user)
        study_id = await _setup_study(client, db_engine, user)
        job_id = await _insert_job(db_engine, study_id, JobStatus.FAILED)

        with patch("arq.create_pool", AsyncMock(side_effect=Exception("no redis"))):
            resp = await client.post(
                f"/api/v1/admin/jobs/{job_id}/retry",
                headers=_bearer(user.id),
            )
        assert resp.status_code == 202
        body = resp.json()
        assert body["original_job_id"] == job_id
        assert "new_job_id" in body

    @pytest.mark.asyncio
    async def test_retry_non_failed_job_returns_409(self, client, alice, db_engine):
        """Retrying a job that is not in 'failed' status returns 409."""
        user, _ = alice
        await _make_group_admin(db_engine, user)
        study_id = await _setup_study(client, db_engine, user)
        job_id = await _insert_job(db_engine, study_id, JobStatus.COMPLETED)

        resp = await client.post(
            f"/api/v1/admin/jobs/{job_id}/retry",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 409
        assert "failed" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_retry_running_job_returns_409(self, client, alice, db_engine):
        """Retrying a running job returns 409."""
        user, _ = alice
        await _make_group_admin(db_engine, user)
        study_id = await _setup_study(client, db_engine, user)
        job_id = await _insert_job(db_engine, study_id, JobStatus.RUNNING)

        resp = await client.post(
            f"/api/v1/admin/jobs/{job_id}/retry",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_retry_missing_job_returns_404(self, client, alice, db_engine):
        """Retrying a non-existent job returns 404."""
        user, _ = alice
        await _make_group_admin(db_engine, user)
        fake_id = str(uuid.uuid4())

        resp = await client.post(
            f"/api/v1/admin/jobs/{fake_id}/retry",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_non_admin_retry_gets_403(self, client, bob, db_engine):
        """A non-admin user cannot retry any job."""
        user, _ = bob
        resp = await client.post(
            "/api/v1/admin/jobs/some-id/retry",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 403
