"""Integration tests for GET /api/v1/studies/{study_id}/metrics.

Covers:
- Empty totals when study has no search executions
- Per-phase metrics aggregated into totals
- Multiple phases summed correctly
- 401 when unauthenticated
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.search import SearchString
from db.models.search_exec import SearchExecution, SearchExecutionStatus, SearchMetrics
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create group + membership + study; return study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Metrics Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Metrics Study",
            "topic": "TDD",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _insert_execution_with_metrics(
    db_engine,
    study_id: int,
    phase_tag: str,
    total: int,
    accepted: int,
    rejected: int,
    duplicates: int,
) -> int:
    """Insert SearchString → SearchExecution → SearchMetrics; return execution id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        ss = SearchString(study_id=study_id, version=1, string_text="query", is_active=True)
        session.add(ss)
        await session.flush()

        se = SearchExecution(
            study_id=study_id,
            search_string_id=ss.id,
            status=SearchExecutionStatus.COMPLETED,
            phase_tag=phase_tag,
        )
        session.add(se)
        await session.flush()

        m = SearchMetrics(
            search_execution_id=se.id,
            total_identified=total,
            accepted=accepted,
            rejected=rejected,
            duplicates=duplicates,
        )
        session.add(m)
        await session.commit()
        return se.id


class TestGetStudyMetrics:
    """GET /studies/{study_id}/metrics — aggregated search metrics."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token → 401."""
        resp = await client.get("/api/v1/studies/1/metrics")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_empty_phases_and_zero_totals_when_no_executions(
        self, client, alice, db_engine
    ) -> None:
        """No search executions → phases=[], totals all zero."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/metrics", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["study_id"] == study_id
        assert body["phases"] == []
        totals = body["totals"]
        assert totals["total_identified"] == 0
        assert totals["accepted"] == 0
        assert totals["rejected"] == 0
        assert totals["duplicates"] == 0

    @pytest.mark.asyncio
    async def test_single_phase_metrics_returned(self, client, alice, db_engine) -> None:
        """One execution with metrics → one phase entry plus matching totals."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _insert_execution_with_metrics(
            db_engine, study_id, "initial-search",
            total=100, accepted=40, rejected=55, duplicates=5,
        )

        resp = await client.get(
            f"/api/v1/studies/{study_id}/metrics", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["phases"]) == 1
        phase = body["phases"][0]
        assert phase["phase_tag"] == "initial-search"
        assert phase["total_identified"] == 100
        assert phase["accepted"] == 40
        assert phase["rejected"] == 55
        assert phase["duplicates"] == 5

        totals = body["totals"]
        assert totals["total_identified"] == 100
        assert totals["accepted"] == 40

    @pytest.mark.asyncio
    async def test_multiple_phases_aggregated_in_totals(
        self, client, alice, db_engine
    ) -> None:
        """Multiple phases: per-phase entries returned, totals are summed correctly."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _insert_execution_with_metrics(
            db_engine, study_id, "initial-search",
            total=100, accepted=40, rejected=55, duplicates=5,
        )
        await _insert_execution_with_metrics(
            db_engine, study_id, "backward-search-1",
            total=50, accepted=15, rejected=30, duplicates=5,
        )

        resp = await client.get(
            f"/api/v1/studies/{study_id}/metrics", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["phases"]) == 2

        totals = body["totals"]
        assert totals["total_identified"] == 150  # 100 + 50
        assert totals["accepted"] == 55           # 40 + 15
        assert totals["rejected"] == 85           # 55 + 30
        assert totals["duplicates"] == 10         # 5 + 5
        assert totals["phase_tag"] == "all"

    @pytest.mark.asyncio
    async def test_totals_phase_tag_is_all(self, client, alice, db_engine) -> None:
        """Totals entry has phase_tag='all' and search_execution_id=0."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _insert_execution_with_metrics(
            db_engine, study_id, "initial-search",
            total=10, accepted=5, rejected=4, duplicates=1,
        )

        resp = await client.get(
            f"/api/v1/studies/{study_id}/metrics", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        totals = resp.json()["totals"]
        assert totals["phase_tag"] == "all"
        assert totals["search_execution_id"] == 0
