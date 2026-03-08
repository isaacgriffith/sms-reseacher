"""Integration tests for /api/v1/studies/{study_id}/quality-reports endpoints (T155).

Covers:
- POST /quality-reports → 202 Accepted, BackgroundJob created
- GET /quality-reports → list with total_score
- GET /quality-reports/{id} → rubric details included
- 401 when unauthenticated
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create group + membership + study; return study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Quality Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Quality Study",
            "topic": "Testing quality evaluation",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _insert_quality_report(db_engine, study_id: int) -> int:
    """Insert a QualityReport directly; return its id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        from db.models.results import QualityReport
        report = QualityReport(
            study_id=study_id,
            version=1,
            score_need_for_review=2,
            score_search_strategy=1,
            score_search_evaluation=2,
            score_extraction_classification=2,
            score_study_validity=1,
            total_score=8,
            rubric_details={
                "need_for_review": {"score": 2, "justification": "Clear motivation."},
                "search_strategy": {"score": 1, "justification": "Test-retest missing."},
            },
            recommendations=[
                {"priority": 1, "action": "Perform test-retest.", "target_rubric": "search_strategy"}
            ],
        )
        session.add(report)
        await session.commit()
        await session.refresh(report)
        return report.id


@pytest.mark.asyncio
async def test_post_quality_report_202(client, alice, db_engine) -> None:
    """POST /quality-reports returns 202 and a job_id."""
    user, _ = alice
    study_id = await _setup_study(client, db_engine, user)

    with patch("arq.connections.create_pool") as mock_pool:
        mock_redis = AsyncMock()
        mock_redis.enqueue_job.return_value = AsyncMock(job_id="qe-job-001")
        mock_redis.close = AsyncMock()
        mock_pool.return_value = mock_redis

        resp = await client.post(
            f"/api/v1/studies/{study_id}/quality-reports",
            headers=_bearer(user.id),
        )

    assert resp.status_code == 202
    body = resp.json()
    assert "job_id" in body
    assert body["study_id"] == study_id


@pytest.mark.asyncio
async def test_get_quality_reports_list(client, alice, db_engine) -> None:
    """GET /quality-reports returns a list of report summaries."""
    user, _ = alice
    study_id = await _setup_study(client, db_engine, user)
    await _insert_quality_report(db_engine, study_id)

    resp = await client.get(
        f"/api/v1/studies/{study_id}/quality-reports",
        headers=_bearer(user.id),
    )

    assert resp.status_code == 200
    reports = resp.json()
    assert isinstance(reports, list)
    assert len(reports) == 1
    assert reports[0]["total_score"] == 8
    assert reports[0]["version"] == 1


@pytest.mark.asyncio
async def test_get_quality_report_detail(client, alice, db_engine) -> None:
    """GET /quality-reports/{id} returns rubric details and recommendations."""
    user, _ = alice
    study_id = await _setup_study(client, db_engine, user)
    report_id = await _insert_quality_report(db_engine, study_id)

    resp = await client.get(
        f"/api/v1/studies/{study_id}/quality-reports/{report_id}",
        headers=_bearer(user.id),
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["total_score"] == 8
    assert body["score_need_for_review"] == 2
    assert body["score_search_strategy"] == 1
    assert isinstance(body["rubric_details"], dict)
    assert "need_for_review" in body["rubric_details"]
    assert isinstance(body["recommendations"], list)
    assert len(body["recommendations"]) == 1
    assert body["recommendations"][0]["priority"] == 1


@pytest.mark.asyncio
async def test_get_quality_report_detail_404(client, alice, db_engine) -> None:
    """GET /quality-reports/9999 returns 404 for a non-existent report."""
    user, _ = alice
    study_id = await _setup_study(client, db_engine, user)

    resp = await client.get(
        f"/api/v1/studies/{study_id}/quality-reports/9999",
        headers=_bearer(user.id),
    )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_quality_reports_401_unauthenticated(client, alice, db_engine) -> None:
    """GET /quality-reports returns 401 when no token is provided."""
    user, _ = alice
    study_id = await _setup_study(client, db_engine, user)

    resp = await client.get(f"/api/v1/studies/{study_id}/quality-reports")
    assert resp.status_code == 401
