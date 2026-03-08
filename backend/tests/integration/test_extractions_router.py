"""Integration tests for /api/v1/studies/{study_id}/extractions endpoints.

Covers (T151):
- POST /extractions/batch-run → 202 Accepted
- GET /extractions → list with optional status filter
- GET /extractions/{id} → single extraction with audit history
- PATCH /extractions/{id} with correct version_id → 200, audit row created
- PATCH /extractions/{id} with stale version_id → 409 with your_version + current_version
- 401 when unauthenticated
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models import Paper
from db.models.candidate import CandidatePaper, CandidatePaperStatus
from db.models.extraction import DataExtraction, ExtractionFieldAudit, ExtractionStatus
from db.models.search import SearchString
from db.models.search_exec import SearchExecution, SearchExecutionStatus
from db.models.users import GroupMembership, GroupRole, ResearchGroup

# Ensure extraction tables are included in test schema
import db.models.extraction  # noqa: F401


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create group + membership + study; return study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Extraction Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Extraction Study",
            "topic": "Testing extraction",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _insert_candidate_paper(db_engine, study_id: int, *, title: str = "Test Paper") -> int:
    """Insert Paper + SearchString + SearchExecution + CandidatePaper; return cp_id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        paper = Paper(title=title, authors=[])
        session.add(paper)
        await session.flush()

        ss = SearchString(study_id=study_id, version=1, string_text="query", is_active=True)
        session.add(ss)
        await session.flush()

        se = SearchExecution(
            study_id=study_id,
            search_string_id=ss.id,
            status=SearchExecutionStatus.COMPLETED,
            phase_tag="initial-search",
        )
        session.add(se)
        await session.flush()

        cp = CandidatePaper(
            study_id=study_id,
            paper_id=paper.id,
            search_execution_id=se.id,
            phase_tag="initial-search",
            current_status=CandidatePaperStatus.ACCEPTED,
        )
        session.add(cp)
        await session.commit()
        return cp.id


async def _insert_extraction(
    db_engine,
    candidate_paper_id: int,
    *,
    version_id: int = 1,
    extraction_status: ExtractionStatus = ExtractionStatus.AI_COMPLETE,
) -> int:
    """Insert a DataExtraction for *candidate_paper_id*; return extraction_id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        ext = DataExtraction(
            candidate_paper_id=candidate_paper_id,
            research_type="evaluation",
            venue_type="conference",
            venue_name="ICSE",
            author_details=[{"name": "Alice", "institution": "MIT", "locale": "US"}],
            summary="A test summary.",
            open_codings=[{"code": "productivity", "definition": "speed", "evidence_quote": "faster"}],
            keywords=["TDD", "agile"],
            question_data={"RQ1": "Yes"},
            extraction_status=extraction_status,
            version_id=version_id,
            extracted_by_agent="ExtractorAgent",
        )
        session.add(ext)
        await session.commit()
        return ext.id


class TestBatchRun:
    """POST /studies/{study_id}/extractions/batch-run → 202."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token → 401."""
        resp = await client.post("/api/v1/studies/1/extractions/batch-run")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_batch_run_returns_202(self, client, alice, db_engine) -> None:
        """POST batch-run enqueues a job and returns 202 with job_id."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        mock_job = AsyncMock()
        mock_job.job_id = "test-job-123"

        mock_pool = AsyncMock()
        mock_pool.enqueue_job = AsyncMock(return_value=mock_job)
        mock_pool.close = AsyncMock()

        with patch("arq.connections.create_pool", return_value=mock_pool):
            resp = await client.post(
                f"/api/v1/studies/{study_id}/extractions/batch-run",
                headers=_bearer(user.id),
            )

        assert resp.status_code == 202
        body = resp.json()
        assert "job_id" in body
        assert body["study_id"] == study_id


class TestListExtractions:
    """GET /studies/{study_id}/extractions."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token → 401."""
        resp = await client.get("/api/v1/studies/1/extractions")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_empty_list_when_no_extractions(self, client, alice, db_engine) -> None:
        """No extractions → empty list."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/extractions", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_returns_inserted_extraction(self, client, alice, db_engine) -> None:
        """Inserted extraction is returned in the list."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        await _insert_extraction(db_engine, cp_id)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/extractions", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["candidate_paper_id"] == cp_id
        assert items[0]["research_type"] == "evaluation"

    @pytest.mark.asyncio
    async def test_status_filter(self, client, alice, db_engine) -> None:
        """?status=validated returns only validated extractions."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp1 = await _insert_candidate_paper(db_engine, study_id, title="Paper 1")
        cp2 = await _insert_candidate_paper(db_engine, study_id, title="Paper 2")
        await _insert_extraction(db_engine, cp1, extraction_status=ExtractionStatus.VALIDATED)
        await _insert_extraction(db_engine, cp2, extraction_status=ExtractionStatus.AI_COMPLETE)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/extractions?status=validated",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["extraction_status"] == "validated"


class TestGetExtraction:
    """GET /studies/{study_id}/extractions/{id}."""

    @pytest.mark.asyncio
    async def test_returns_extraction_with_audit_history(self, client, alice, db_engine) -> None:
        """GET single extraction includes audit_history list."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        ext_id = await _insert_extraction(db_engine, cp_id)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/extractions/{ext_id}",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == ext_id
        assert "audit_history" in body
        assert isinstance(body["audit_history"], list)

    @pytest.mark.asyncio
    async def test_returns_404_for_unknown_extraction(self, client, alice, db_engine) -> None:
        """Non-existent extraction → 404."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/extractions/99999",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404


class TestPatchExtraction:
    """PATCH /studies/{study_id}/extractions/{id} — optimistic locking."""

    @pytest.mark.asyncio
    async def test_patch_with_correct_version_succeeds(self, client, alice, db_engine) -> None:
        """PATCH with matching version_id → 200 and fields updated."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        ext_id = await _insert_extraction(db_engine, cp_id, version_id=1)

        resp = await client.patch(
            f"/api/v1/studies/{study_id}/extractions/{ext_id}",
            json={"version_id": 1, "venue_type": "journal", "summary": "Updated summary."},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["venue_type"] == "journal"
        assert body["summary"] == "Updated summary."
        assert body["extraction_status"] == "human_reviewed"

    @pytest.mark.asyncio
    async def test_patch_with_stale_version_returns_409(self, client, alice, db_engine) -> None:
        """PATCH with stale version_id → 409 with your_version and current_version."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        ext_id = await _insert_extraction(db_engine, cp_id, version_id=1)

        # First patch succeeds, bumping version to 2
        resp1 = await client.patch(
            f"/api/v1/studies/{study_id}/extractions/{ext_id}",
            json={"version_id": 1, "venue_type": "journal"},
            headers=_bearer(user.id),
        )
        assert resp1.status_code == 200

        # Second patch with stale version_id=1 → 409
        resp2 = await client.patch(
            f"/api/v1/studies/{study_id}/extractions/{ext_id}",
            json={"version_id": 1, "summary": "Stale attempt"},
            headers=_bearer(user.id),
        )
        assert resp2.status_code == 409
        detail = resp2.json()["detail"]
        assert detail["error"] == "conflict"
        assert "your_version" in detail
        assert "current_version" in detail

    @pytest.mark.asyncio
    async def test_patch_creates_field_audit_rows(self, client, alice, db_engine) -> None:
        """Successful PATCH creates ExtractionFieldAudit rows for changed fields."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        ext_id = await _insert_extraction(db_engine, cp_id, version_id=1)

        resp = await client.patch(
            f"/api/v1/studies/{study_id}/extractions/{ext_id}",
            json={"version_id": 1, "venue_type": "journal", "summary": "New summary"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200

        # Verify audit rows via GET
        detail_resp = await client.get(
            f"/api/v1/studies/{study_id}/extractions/{ext_id}",
            headers=_bearer(user.id),
        )
        assert detail_resp.status_code == 200
        audit = detail_resp.json()["audit_history"]
        assert len(audit) >= 1
        field_names = {a["field_name"] for a in audit}
        assert "venue_type" in field_names or "summary" in field_names

    @pytest.mark.asyncio
    async def test_unauthenticated_patch_returns_401(self, client) -> None:
        """No auth token → 401."""
        resp = await client.patch(
            "/api/v1/studies/1/extractions/1",
            json={"version_id": 1, "venue_type": "journal"},
        )
        assert resp.status_code == 401
