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
from db.models import Paper
from db.models.candidate import CandidatePaper, CandidatePaperStatus
from db.models.search import SearchString
from db.models.search_exec import SearchExecution, SearchExecutionStatus
from db.models.slr import QualityAssessmentScore
from db.models.study import Reviewer, ReviewerType, StudyMember, StudyMemberRole
from db.models.users import GroupMembership, GroupRole, ResearchGroup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token


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
    """Insert a Reviewer row (not tied to any user) and return its id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        reviewer = Reviewer(study_id=study_id, reviewer_type=ReviewerType.HUMAN)
        session.add(reviewer)
        await session.commit()
        await session.refresh(reviewer)
        return reviewer.id


async def _insert_reviewer_for_user(db_engine, study_id: int, user_id: int) -> int:
    """Insert a human Reviewer row tied to *user_id* and return its id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        reviewer = Reviewer(study_id=study_id, reviewer_type=ReviewerType.HUMAN, user_id=user_id)
        session.add(reviewer)
        await session.commit()
        await session.refresh(reviewer)
        return reviewer.id


async def _insert_score(
    db_engine, candidate_paper_id: int, reviewer_id: int, checklist_item_id: int
) -> None:
    """Insert a QualityAssessmentScore row directly, bypassing the PUT endpoint."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        session.add(
            QualityAssessmentScore(
                candidate_paper_id=candidate_paper_id,
                reviewer_id=reviewer_id,
                checklist_item_id=checklist_item_id,
                score_value=1.0,
                notes=None,
            )
        )
        await session.commit()


async def _add_study_member(
    db_engine, study_id: int, user_id: int, role: StudyMemberRole = StudyMemberRole.MEMBER
) -> None:
    """Insert a StudyMember row so *user_id* passes ``require_study_member``.

    ``_setup_study`` only makes its creating user a member; tests exercising
    a second authenticated user, or a non-member 403 case, must add or
    withhold that membership explicitly.
    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        session.add(StudyMember(study_id=study_id, user_id=user_id, role=role))
        await session.commit()


_CHECKLIST_BODY = {
    "name": "Standard QA Checklist",
    "description": "Used for integration tests",
    "items": [
        {
            "order": 1,
            "question": "Is the study empirical?",
            "scoring_method": "binary",
            "weight": 1.0,
        },
        {
            "order": 2,
            "question": "Is sample size adequate?",
            "scoring_method": "scale_1_3",
            "weight": 2.0,
        },
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

    @pytest.mark.asyncio
    async def test_get_checklist_non_member_returns_403(
        self, client, alice, bob, db_engine
    ) -> None:
        """A user who is not a study member is rejected before checklist lookup (TFIX5, part 4).

        The router imports only ``get_current_user`` and never checks study
        membership, so today any authenticated user can read a checklist
        belonging to a study they do not belong to.
        """
        alice_user, _ = alice
        bob_user, _ = bob
        study_id = await _setup_study(client, db_engine, alice_user)
        create_resp = await client.put(
            f"/api/v1/slr/studies/{study_id}/quality-checklist",
            json=_CHECKLIST_BODY,
            headers=_bearer(alice_user.id),
        )
        assert create_resp.status_code == 200

        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/quality-checklist",
            headers=_bearer(bob_user.id),
        )
        assert resp.status_code == 403


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
                {
                    "order": 1,
                    "question": "Only question?",
                    "scoring_method": "scale_1_5",
                    "weight": 1.0,
                },
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

    @pytest.mark.asyncio
    async def test_upsert_checklist_non_member_returns_403(
        self, client, alice, bob, db_engine
    ) -> None:
        """A non-member cannot create or replace a study's checklist (TFIX5, part 4)."""
        alice_user, _ = alice
        bob_user, _ = bob
        study_id = await _setup_study(client, db_engine, alice_user)

        resp = await client.put(
            f"/api/v1/slr/studies/{study_id}/quality-checklist",
            json=_CHECKLIST_BODY,
            headers=_bearer(bob_user.id),
        )
        assert resp.status_code == 403


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

    @pytest.mark.asyncio
    async def test_get_quality_scores_non_member_returns_403(
        self, client, alice, bob, db_engine
    ) -> None:
        """A user who is not a member of the paper's study cannot read its scores (TFIX5, part 4).

        The route derives ``study_id`` from the candidate paper itself and
        never checks that the caller belongs to it.
        """
        alice_user, _ = alice
        bob_user, _ = bob
        study_id = await _setup_study(client, db_engine, alice_user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        resp = await client.get(
            f"/api/v1/slr/papers/{cp_id}/quality-scores",
            headers=_bearer(bob_user.id),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_get_quality_scores_viewer_reviewer_id_none_when_never_scored(
        self, client, alice, db_engine
    ) -> None:
        """viewer_reviewer_id is None, and present, when the caller never scored (TFIX5, part 4).

        A GET must resolve the caller's own reviewer id by lookup only — it
        must never create a Reviewer row, since scoring is a write action and
        this is a read.
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        resp = await client.get(
            f"/api/v1/slr/papers/{cp_id}/quality-scores",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "viewer_reviewer_id" in body
        assert body["viewer_reviewer_id"] is None

    @pytest.mark.asyncio
    async def test_get_quality_scores_viewer_reviewer_id_matches_callers_own_reviewer(
        self, client, alice, db_engine
    ) -> None:
        """viewer_reviewer_id identifies the caller's own scores among reviewers' (TFIX5, part 4).

        This is what replaces the ``reviewerId`` prop the unreachable
        QualityScoreForm used to be hardcoded to (``reviewerId={0}`` in
        studyTypeDispatch.tsx) — the client can no longer know its own
        reviewer id without the server telling it.
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer_id = await _insert_reviewer_for_user(db_engine, study_id, user.id)

        cl_resp = await client.put(
            f"/api/v1/slr/studies/{study_id}/quality-checklist",
            json=_CHECKLIST_BODY,
            headers=_bearer(user.id),
        )
        assert cl_resp.status_code == 200
        item_id = cl_resp.json()["items"][0]["id"]
        await _insert_score(db_engine, cp_id, reviewer_id, item_id)

        resp = await client.get(
            f"/api/v1/slr/papers/{cp_id}/quality-scores",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["viewer_reviewer_id"] == reviewer_id


class TestSubmitQualityScores:
    """PUT /slr/papers/{id}/quality-scores."""

    @pytest.mark.asyncio
    async def test_submit_quality_scores(self, client, alice, db_engine) -> None:
        """PUT scores returns a filled PaperScoresResponse.

        No pre-existing Reviewer row is created for alice, and the request
        body carries no ``reviewer_id`` — the reviewer is resolved from her
        session and created on demand, the same contract TFIX4 established
        for screening decisions (TFIX5, part 2; see
        ``backend/api/v1/papers.py::resolve_session_reviewer``).
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
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
        assert body["reviewer_scores"][0]["aggregate_quality_score"] == 1.0

        # The reviewer_id was resolved from alice's session, not supplied by
        # the client — confirm it matches her own Reviewer row.
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            result = await session.execute(
                select(Reviewer.id).where(
                    Reviewer.study_id == study_id, Reviewer.user_id == user.id
                )
            )
            alice_reviewer_id = result.scalar_one()
        assert body["reviewer_scores"][0]["reviewer_id"] == alice_reviewer_id

    @pytest.mark.asyncio
    async def test_submit_quality_scores_non_member_returns_403(
        self, client, alice, bob, db_engine
    ) -> None:
        """A user who is not a study member cannot submit scores for its papers (TFIX5, part 4).

        The request still carries the (deprecated) ``reviewer_id`` field so
        this test isolates the membership defect from the reviewer_id-removal
        defect covered elsewhere in this class — after both are fixed, an
        extra field is simply ignored and this assertion still holds.
        """
        alice_user, _ = alice
        bob_user, _ = bob
        study_id = await _setup_study(client, db_engine, alice_user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer_id = await _insert_reviewer(db_engine, study_id)

        cl_resp = await client.put(
            f"/api/v1/slr/studies/{study_id}/quality-checklist",
            json=_CHECKLIST_BODY,
            headers=_bearer(alice_user.id),
        )
        assert cl_resp.status_code == 200
        item_id = cl_resp.json()["items"][0]["id"]

        resp = await client.put(
            f"/api/v1/slr/papers/{cp_id}/quality-scores",
            json={
                "reviewer_id": reviewer_id,
                "scores": [{"checklist_item_id": item_id, "score_value": 1.0}],
            },
            headers=_bearer(bob_user.id),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_two_different_users_submitting_scores_produce_different_reviewer_ids(
        self, client, alice, bob, db_engine
    ) -> None:
        """Two study members scoring the same paper are attributed distinct reviewer_ids.

        This is the property that makes inter-rater agreement meaningful — a
        client-supplied ``reviewer_id`` cannot guarantee it (TFIX5, part 2).
        Neither request carries a ``reviewer_id``; each is resolved from its
        own caller's session.
        """
        alice_user, _ = alice
        bob_user, _ = bob
        study_id = await _setup_study(client, db_engine, alice_user)
        await _add_study_member(db_engine, study_id, bob_user.id)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        cl_resp = await client.put(
            f"/api/v1/slr/studies/{study_id}/quality-checklist",
            json=_CHECKLIST_BODY,
            headers=_bearer(alice_user.id),
        )
        assert cl_resp.status_code == 200
        item_id = cl_resp.json()["items"][0]["id"]

        for uid in (alice_user.id, bob_user.id):
            resp = await client.put(
                f"/api/v1/slr/papers/{cp_id}/quality-scores",
                json={"scores": [{"checklist_item_id": item_id, "score_value": 1.0}]},
                headers=_bearer(uid),
            )
            assert resp.status_code == 200

        get_resp = await client.get(
            f"/api/v1/slr/papers/{cp_id}/quality-scores",
            headers=_bearer(alice_user.id),
        )
        assert get_resp.status_code == 200
        reviewer_ids = {r["reviewer_id"] for r in get_resp.json()["reviewer_scores"]}
        assert len(reviewer_ids) == 2

    @pytest.mark.asyncio
    async def test_submit_quality_scores_ignores_client_supplied_reviewer_id(
        self, client, alice, db_engine
    ) -> None:
        """A reviewer_id in the request body must not override the session reviewer (TFIX5, part 2).

        A client that sends an arbitrary ``reviewer_id`` — here, a reviewer
        that belongs to no one — must not be able to attribute its scores to
        it; the score must land under alice's own resolved reviewer
        regardless of what she sends.
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        victim_reviewer_id = await _insert_reviewer(db_engine, study_id)

        cl_resp = await client.put(
            f"/api/v1/slr/studies/{study_id}/quality-checklist",
            json=_CHECKLIST_BODY,
            headers=_bearer(user.id),
        )
        assert cl_resp.status_code == 200
        item_id = cl_resp.json()["items"][0]["id"]

        resp = await client.put(
            f"/api/v1/slr/papers/{cp_id}/quality-scores",
            json={
                "reviewer_id": victim_reviewer_id,
                "scores": [{"checklist_item_id": item_id, "score_value": 1.0}],
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        reviewer_ids = {r["reviewer_id"] for r in resp.json()["reviewer_scores"]}
        assert victim_reviewer_id not in reviewer_ids
