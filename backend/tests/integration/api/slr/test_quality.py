"""Integration tests for SLR quality assessment routes (feature 007, T052).

Covers:
- GET /slr/studies/{id}/quality-checklist → 404 when no checklist exists.
- PUT /slr/studies/{id}/quality-checklist → 200 creates checklist.
- PUT /slr/studies/{id}/quality-checklist → 200 second PUT replaces items.
- GET /slr/papers/{id}/quality-scores → 200 empty reviewer_scores.
- PUT /slr/papers/{id}/quality-scores → 200 filled response.
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.candidate import CandidatePaper, CandidatePaperStatus
from db.models.search import SearchString
from db.models.search_exec import SearchExecution, SearchExecutionStatus
from db.models.slr import QualityAssessmentChecklist, QualityChecklistItem
from db.models.study import Reviewer, ReviewerType
from db.models.users import GroupMembership, GroupRole, ResearchGroup
from db.models import Paper, Study, StudyType, StudyStatus


def _bearer(user_id: int) -> dict[str, str]:
    """Return Bearer token header for the given user id."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create a research group, study, return study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=f"QA Group {user.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "QA SLR Test",
            "topic": "Quality",
            "study_type": "SLR",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _insert_candidate_paper(db_engine, study_id: int) -> int:
    """Insert a minimal accepted CandidatePaper and return its id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        paper = Paper(title="QA Integration Paper", doi="10.9999/qa.integ.1")
        session.add(paper)
        await session.flush()

        search_string = SearchString(
            study_id=study_id,
            version=1,
            string_text="quality AND paper",
            is_active=True,
        )
        session.add(search_string)
        await session.flush()

        exec_row = SearchExecution(
            study_id=study_id,
            search_string_id=search_string.id,
            phase_tag="title_abstract",
            status=SearchExecutionStatus.COMPLETED,
        )
        session.add(exec_row)
        await session.flush()

        cp = CandidatePaper(
            study_id=study_id,
            paper_id=paper.id,
            search_execution_id=exec_row.id,
            phase_tag="title_abstract",
            current_status=CandidatePaperStatus.ACCEPTED,
        )
        session.add(cp)
        await session.commit()
        await session.refresh(cp)
        return cp.id


async def _insert_reviewer(db_engine, study_id: int) -> int:
    """Insert a Reviewer row and return its id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        reviewer = Reviewer(study_id=study_id, reviewer_type=ReviewerType.HUMAN)
        session.add(reviewer)
        await session.commit()
        await session.refresh(reviewer)
        return reviewer.id


_CHECKLIST_BODY = {
    "name": "Standard QA Checklist",
    "description": "Used for integration tests",
    "items": [
        {"order": 1, "question": "Is the study empirical?", "scoring_method": "binary", "weight": 1.0},
        {"order": 2, "question": "Is sample size adequate?", "scoring_method": "scale_1_3", "weight": 2.0},
    ],
}


class TestGetQualityChecklist:
    """GET /slr/studies/{id}/quality-checklist."""

    @pytest.mark.asyncio
    async def test_get_checklist_404(self, client, alice, db_engine) -> None:
        """Returns 404 when no checklist has been created yet."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/quality-checklist",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404


class TestUpsertQualityChecklist:
    """PUT /slr/studies/{id}/quality-checklist."""

    @pytest.mark.asyncio
    async def test_upsert_checklist_creates(self, client, alice, db_engine) -> None:
        """PUT creates a new checklist and returns it with items."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.put(
            f"/api/v1/slr/studies/{study_id}/quality-checklist",
            json=_CHECKLIST_BODY,
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "Standard QA Checklist"
        assert body["study_id"] == study_id
        assert len(body["items"]) == 2

    @pytest.mark.asyncio
    async def test_upsert_checklist_updates(self, client, alice, db_engine) -> None:
        """Second PUT replaces items on the existing checklist."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await client.put(
            f"/api/v1/slr/studies/{study_id}/quality-checklist",
            json=_CHECKLIST_BODY,
            headers=_bearer(user.id),
        )
        updated_body = {
            "name": "Updated Checklist",
            "items": [
                {"order": 1, "question": "Only question?", "scoring_method": "scale_1_5", "weight": 1.0},
            ],
        }
        resp = await client.put(
            f"/api/v1/slr/studies/{study_id}/quality-checklist",
            json=updated_body,
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "Updated Checklist"
        assert len(body["items"]) == 1
        assert body["items"][0]["question"] == "Only question?"


class TestGetQualityScores:
    """GET /slr/papers/{id}/quality-scores."""

    @pytest.mark.asyncio
    async def test_get_quality_scores_empty(self, client, alice, db_engine) -> None:
        """Returns empty reviewer_scores when no scores have been submitted."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        resp = await client.get(
            f"/api/v1/slr/papers/{cp_id}/quality-scores",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["candidate_paper_id"] == cp_id
        assert body["reviewer_scores"] == []


class TestSubmitQualityScores:
    """PUT /slr/papers/{id}/quality-scores."""

    @pytest.mark.asyncio
    async def test_submit_quality_scores(self, client, alice, db_engine) -> None:
        """PUT scores returns a filled PaperScoresResponse."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        reviewer_id = await _insert_reviewer(db_engine, study_id)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        # First create the checklist
        cl_resp = await client.put(
            f"/api/v1/slr/studies/{study_id}/quality-checklist",
            json={
                "name": "Test CL",
                "items": [
                    {"order": 1, "question": "Q?", "scoring_method": "binary", "weight": 1.0},
                ],
            },
            headers=_bearer(user.id),
        )
        assert cl_resp.status_code == 200
        item_id = cl_resp.json()["items"][0]["id"]

        scores_body = {
            "reviewer_id": reviewer_id,
            "scores": [
                {"checklist_item_id": item_id, "score_value": 1.0, "notes": "Good"},
            ],
        }
        resp = await client.put(
            f"/api/v1/slr/papers/{cp_id}/quality-scores",
            json=scores_body,
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["candidate_paper_id"] == cp_id
        assert len(body["reviewer_scores"]) == 1
        assert body["reviewer_scores"][0]["reviewer_id"] == reviewer_id
        assert body["reviewer_scores"][0]["aggregate_quality_score"] == 1.0
