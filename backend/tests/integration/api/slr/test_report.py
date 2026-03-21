"""Integration tests for SLR report export routes (feature 007, T084).

Covers:
- GET /slr/studies/{id}/export/slr-report → 422 when no completed synthesis.
- GET /slr/studies/{id}/export/slr-report?format=markdown → 200 with attachment.
- GET /slr/studies/{id}/export/slr-report?format=json → 200 with application/json.
- GET /slr/studies/{id}/export/slr-report?format=csv → 200 with text/csv.
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
        group = ResearchGroup(name=f"Report Group {user.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Report SLR Test",
            "topic": "report export",
            "study_type": "SLR",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _insert_completed_synthesis(db_engine, study_id: int) -> None:
    """Insert a completed SynthesisResult directly into the DB."""
    from db.models.slr import SynthesisResult, SynthesisApproach, SynthesisStatus

    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        sr = SynthesisResult(
            study_id=study_id,
            approach=SynthesisApproach.DESCRIPTIVE,
            status=SynthesisStatus.COMPLETED,
            computed_statistics={"n_studies": 3},
        )
        session.add(sr)
        await session.commit()


class TestExportSLRReportNoSynthesis:
    """GET /slr/studies/{id}/export/slr-report without completed synthesis."""

    @pytest.mark.asyncio
    async def test_returns_422_when_no_completed_synthesis(
        self, client, db_engine, alice
    ) -> None:
        """Returns 422 when no completed synthesis result exists for the study."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/export/slr-report",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422


class TestExportSLRReportMarkdown:
    """GET /slr/studies/{id}/export/slr-report?format=markdown."""

    @pytest.mark.asyncio
    async def test_returns_200_with_attachment_header(
        self, client, db_engine, alice
    ) -> None:
        """Returns 200 with Content-Disposition attachment header for markdown."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _insert_completed_synthesis(db_engine, study_id)

        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/export/slr-report?format=markdown",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert "attachment" in resp.headers.get("content-disposition", "")
        assert "text/markdown" in resp.headers.get("content-type", "")


class TestExportSLRReportJSON:
    """GET /slr/studies/{id}/export/slr-report?format=json."""

    @pytest.mark.asyncio
    async def test_returns_200_with_json_mime(
        self, client, db_engine, alice
    ) -> None:
        """Returns 200 with application/json content type for JSON export."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _insert_completed_synthesis(db_engine, study_id)

        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/export/slr-report?format=json",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("content-type", "")
        data = resp.json()
        assert data["study_id"] == study_id


class TestExportSLRReportCSV:
    """GET /slr/studies/{id}/export/slr-report?format=csv."""

    @pytest.mark.asyncio
    async def test_returns_200_with_csv_mime(
        self, client, db_engine, alice
    ) -> None:
        """Returns 200 with text/csv content type for CSV export."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _insert_completed_synthesis(db_engine, study_id)

        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/export/slr-report?format=csv",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")
