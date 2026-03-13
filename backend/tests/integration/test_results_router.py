"""Integration tests for /api/v1/studies/{study_id}/results endpoints.

Covers (T153):
- GET /results → 200 with domain_model + charts summary
- POST /results/generate → 202 Accepted
- GET /results/charts/{id}/svg → 200 Content-Type image/svg+xml
- GET /results/domain-model/svg → 200 Content-Type image/svg+xml
- POST /export → 202 Accepted
- GET /export/{export_id}/download → 200 when file exists
- 401 when unauthenticated
- 404 when chart/domain-model not found
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.users import GroupMembership, GroupRole, ResearchGroup

# Ensure results tables are included in the in-memory schema
import db.models.results  # noqa: F401


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create group + membership + study; return study_id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Results Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Results Study",
            "topic": "Testing results",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _insert_domain_model(db_engine, study_id: int) -> int:
    """Insert a DomainModel row; return its id."""
    from db.models.results import DomainModel

    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        dm = DomainModel(
            study_id=study_id,
            version=1,
            concepts=[{"name": "Concept A", "definition": "Def A", "attributes": []}],
            relationships=[{"from": "Concept A", "to": "Concept A", "label": "self", "type": "other"}],
            svg_content="<svg><circle/></svg>",
            generated_at=datetime.now(timezone.utc),
        )
        session.add(dm)
        await session.commit()
        return dm.id


async def _insert_chart(db_engine, study_id: int, chart_type: str = "venue") -> int:
    """Insert a ClassificationScheme row; return its id."""
    from db.models.results import ChartType, ClassificationScheme

    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        cs = ClassificationScheme(
            study_id=study_id,
            chart_type=ChartType(chart_type),
            version=1,
            chart_data={"ICSE": 3},
            svg_content="<svg><rect/></svg>",
            generated_at=datetime.now(timezone.utc),
        )
        session.add(cs)
        await session.commit()
        return cs.id


# ---------------------------------------------------------------------------
# GET /studies/{study_id}/results
# ---------------------------------------------------------------------------


class TestGetResults:
    """GET /studies/{study_id}/results"""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token → 401."""
        resp = await client.get("/api/v1/studies/1/results")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_200_with_empty_results(self, client, alice, db_engine) -> None:
        """GET results returns 200 with null domain_model and empty charts list."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.get(f"/api/v1/studies/{study_id}/results", headers=_bearer(user.id))
        assert resp.status_code == 200
        body = resp.json()
        assert body["domain_model"] is None
        assert body["charts"] == []

    @pytest.mark.asyncio
    async def test_returns_domain_model_and_charts(self, client, alice, db_engine) -> None:
        """GET results includes domain model and chart summary when data exists."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _insert_domain_model(db_engine, study_id)
        await _insert_chart(db_engine, study_id, "venue")

        resp = await client.get(f"/api/v1/studies/{study_id}/results", headers=_bearer(user.id))
        assert resp.status_code == 200
        body = resp.json()
        assert body["domain_model"] is not None
        assert body["domain_model"]["version"] == 1
        assert len(body["charts"]) == 1
        assert body["charts"][0]["chart_type"] == "venue"


# ---------------------------------------------------------------------------
# POST /studies/{study_id}/results/generate
# ---------------------------------------------------------------------------


class TestGenerateResults:
    """POST /studies/{study_id}/results/generate"""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        resp = await client.post("/api/v1/studies/1/results/generate")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_202_and_job_id(self, client, alice, db_engine) -> None:
        """POST /generate enqueues an ARQ job and returns 202."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        mock_job = AsyncMock()
        mock_job.job_id = "gen_results_job_1"
        mock_pool = AsyncMock()
        mock_pool.enqueue_job = AsyncMock(return_value=mock_job)
        mock_pool.close = AsyncMock()

        with patch("arq.connections.create_pool", AsyncMock(return_value=mock_pool)):
            resp = await client.post(
                f"/api/v1/studies/{study_id}/results/generate",
                headers=_bearer(user.id),
            )

        assert resp.status_code == 202
        body = resp.json()
        assert "job_id" in body
        assert body["study_id"] == study_id


# ---------------------------------------------------------------------------
# GET /studies/{study_id}/results/charts/{chart_id}/svg
# ---------------------------------------------------------------------------


class TestChartSvg:
    """GET /studies/{study_id}/results/charts/{chart_id}/svg"""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        resp = await client.get("/api/v1/studies/1/results/charts/999/svg")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_svg_content_type(self, client, alice, db_engine) -> None:
        """Chart SVG endpoint returns Content-Type image/svg+xml."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        chart_id = await _insert_chart(db_engine, study_id, "year")

        resp = await client.get(
            f"/api/v1/studies/{study_id}/results/charts/{chart_id}/svg",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert "image/svg+xml" in resp.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_returns_404_for_missing_chart(self, client, alice, db_engine) -> None:
        """Non-existent chart_id → 404."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/results/charts/99999/svg",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /studies/{study_id}/results/domain-model/svg
# ---------------------------------------------------------------------------


class TestDomainModelSvg:
    """GET /studies/{study_id}/results/domain-model/svg"""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        resp = await client.get("/api/v1/studies/1/results/domain-model/svg")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_svg_content_type(self, client, alice, db_engine) -> None:
        """Domain model SVG endpoint returns Content-Type image/svg+xml."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _insert_domain_model(db_engine, study_id)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/results/domain-model/svg",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert "image/svg+xml" in resp.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_returns_404_when_no_domain_model(self, client, alice, db_engine) -> None:
        """No domain model generated → 404."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/results/domain-model/svg",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /studies/{study_id}/export
# ---------------------------------------------------------------------------


class TestEnqueueExport:
    """POST /studies/{study_id}/export"""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        resp = await client.post("/api/v1/studies/1/export", json={"format": "json_only"})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_202_and_job_id(self, client, alice, db_engine) -> None:
        """POST /export enqueues an ARQ job and returns 202."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        mock_job = AsyncMock()
        mock_job.job_id = "export_job_1"
        mock_pool = AsyncMock()
        mock_pool.enqueue_job = AsyncMock(return_value=mock_job)
        mock_pool.close = AsyncMock()

        with patch("arq.connections.create_pool", AsyncMock(return_value=mock_pool)):
            resp = await client.post(
                f"/api/v1/studies/{study_id}/export",
                json={"format": "json_only"},
                headers=_bearer(user.id),
            )

        assert resp.status_code == 202
        body = resp.json()
        assert "job_id" in body

    @pytest.mark.asyncio
    async def test_returns_422_for_invalid_format(self, client, alice, db_engine) -> None:
        """Invalid format string → 422."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/export",
            json={"format": "invalid_format"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /studies/{study_id}/export/{export_id}/download
# ---------------------------------------------------------------------------


class TestDownloadExport:
    """GET /studies/{study_id}/export/{export_id}/download"""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        resp = await client.get("/api/v1/studies/1/export/some-job-id/download")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_200_for_completed_export(self, client, alice, db_engine) -> None:
        """Completed export job with existing file → 200 streamed response."""
        import os
        import tempfile

        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        # Create a completed BackgroundJob pointing to a real temp file
        job_id = f"export_{study_id}_json_only_9999"
        filename = f"{job_id}.json"
        export_dir = os.path.join(tempfile.gettempdir(), "sms_exports")
        os.makedirs(export_dir, exist_ok=True)
        filepath = os.path.join(export_dir, filename)
        with open(filepath, "wb") as fh:
            fh.write(b'{"study": "test"}')

        try:
            from db.models.jobs import BackgroundJob, JobStatus, JobType

            maker = async_sessionmaker(db_engine, expire_on_commit=False)
            async with maker() as session:
                bg_job = BackgroundJob(
                    id=job_id,
                    study_id=study_id,
                    job_type=JobType.EXPORT,
                    status=JobStatus.COMPLETED,
                    progress_pct=100,
                    progress_detail={"download_url": f"/exports/{filename}", "size_bytes": 17},
                )
                session.add(bg_job)
                await session.commit()

            resp = await client.get(
                f"/api/v1/studies/{study_id}/export/{job_id}/download",
                headers=_bearer(user.id),
            )
            assert resp.status_code == 200
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    @pytest.mark.asyncio
    async def test_returns_409_for_not_yet_complete(self, client, alice, db_engine) -> None:
        """Export job still running → 409."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        from db.models.jobs import BackgroundJob, JobStatus, JobType

        job_id = f"export_{study_id}_running_9998"
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            bg_job = BackgroundJob(
                id=job_id,
                study_id=study_id,
                job_type=JobType.EXPORT,
                status=JobStatus.RUNNING,
            )
            session.add(bg_job)
            await session.commit()

        resp = await client.get(
            f"/api/v1/studies/{study_id}/export/{job_id}/download",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 409
