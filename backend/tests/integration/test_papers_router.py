"""Integration tests for /api/v1/studies/{study_id}/papers endpoints.

Covers:
- GET /papers → paginated list, status filter, phase_tag filter
- GET /papers/{candidate_id} → detail, 404 for unknown
- 401 when unauthenticated
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models import Paper
from db.models.candidate import CandidatePaper, CandidatePaperStatus
from db.models.search_exec import SearchExecution, SearchExecutionStatus
from db.models.search import SearchString
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create group + membership + study; return study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Papers Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Papers Study",
            "topic": "TDD",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _insert_candidate_paper(
    db_engine,
    study_id: int,
    *,
    title: str = "Test Paper",
    doi: str | None = None,
    phase_tag: str = "initial-search",
    status: CandidatePaperStatus = CandidatePaperStatus.PENDING,
) -> tuple[int, int]:
    """Insert Paper + SearchString + SearchExecution + CandidatePaper; return (paper_id, cp_id)."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        # Insert Paper
        paper = Paper(title=title, doi=doi, authors=[])
        session.add(paper)
        await session.flush()

        # Insert SearchString + SearchExecution for the FK
        ss = SearchString(study_id=study_id, version=1, string_text="test query", is_active=True)
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

        cp = CandidatePaper(
            study_id=study_id,
            paper_id=paper.id,
            search_execution_id=se.id,
            phase_tag=phase_tag,
            current_status=status,
        )
        session.add(cp)
        await session.commit()
        return paper.id, cp.id


class TestListCandidatePapers:
    """GET /studies/{study_id}/papers — paginated list with filters."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token → 401."""
        resp = await client.get("/api/v1/studies/1/papers")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_empty_list_when_no_papers(self, client, alice, db_engine) -> None:
        """No candidates → empty list."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/papers", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_returns_candidate_paper_with_paper_detail(
        self, client, alice, db_engine
    ) -> None:
        """Inserted candidate paper is returned with nested paper object."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _insert_candidate_paper(db_engine, study_id, title="My Test Paper", doi="10.1/test")

        resp = await client.get(
            f"/api/v1/studies/{study_id}/papers", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        cp = items[0]
        assert cp["study_id"] == study_id
        assert cp["paper"]["title"] == "My Test Paper"
        assert cp["paper"]["doi"] == "10.1/test"
        assert "current_status" in cp
        assert "phase_tag" in cp

    @pytest.mark.asyncio
    async def test_status_filter_accepted(self, client, alice, db_engine) -> None:
        """status=accepted filter returns only accepted papers."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _insert_candidate_paper(
            db_engine, study_id, title="Accepted", status=CandidatePaperStatus.ACCEPTED
        )
        await _insert_candidate_paper(
            db_engine, study_id, title="Rejected", doi="10.1/rej",
            status=CandidatePaperStatus.REJECTED
        )

        resp = await client.get(
            f"/api/v1/studies/{study_id}/papers?status=accepted", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["current_status"] == "accepted"

    @pytest.mark.asyncio
    async def test_status_filter_rejected(self, client, alice, db_engine) -> None:
        """status=rejected filter returns only rejected papers."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _insert_candidate_paper(
            db_engine, study_id, title="Paper A", status=CandidatePaperStatus.ACCEPTED
        )
        await _insert_candidate_paper(
            db_engine, study_id, title="Paper B", doi="10.1/b",
            status=CandidatePaperStatus.REJECTED,
        )

        resp = await client.get(
            f"/api/v1/studies/{study_id}/papers?status=rejected", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        items = resp.json()
        assert all(i["current_status"] == "rejected" for i in items)

    @pytest.mark.asyncio
    async def test_phase_tag_filter(self, client, alice, db_engine) -> None:
        """phase_tag filter returns only papers with matching phase."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _insert_candidate_paper(
            db_engine, study_id, title="Phase1 Paper", phase_tag="initial-search"
        )
        await _insert_candidate_paper(
            db_engine, study_id, title="Snowball Paper", doi="10.1/snow",
            phase_tag="backward-search-1"
        )

        resp = await client.get(
            f"/api/v1/studies/{study_id}/papers?phase_tag=initial-search",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["phase_tag"] == "initial-search"

    @pytest.mark.asyncio
    async def test_pagination_with_offset_and_limit(self, client, alice, db_engine) -> None:
        """offset and limit parameters control which records are returned."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        for i in range(5):
            await _insert_candidate_paper(
                db_engine, study_id, title=f"Paper {i}", doi=f"10.1/p{i}"
            )

        resp = await client.get(
            f"/api/v1/studies/{study_id}/papers?offset=2&limit=2",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestGetCandidatePaper:
    """GET /studies/{study_id}/papers/{candidate_id} — detail."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth → 401."""
        resp = await client.get("/api/v1/studies/1/papers/1")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_candidate_paper_detail(self, client, alice, db_engine) -> None:
        """Valid candidate_id returns full detail response."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        _, cp_id = await _insert_candidate_paper(
            db_engine, study_id, title="Detail Paper", doi="10.1/detail"
        )

        resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == cp_id
        assert body["paper"]["title"] == "Detail Paper"

    @pytest.mark.asyncio
    async def test_unknown_candidate_returns_404(self, client, alice, db_engine) -> None:
        """Non-existent candidate_id → 404."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/99999", headers=_bearer(user.id)
        )
        assert resp.status_code == 404
