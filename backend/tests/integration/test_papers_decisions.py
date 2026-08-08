"""Integration tests for paper decision endpoints.

Covers:
- POST /papers/{id}/decisions: reviewer-not-in-study → 422
- POST /papers/{id}/decisions: is_override=True recorded when overrides_decision_id provided
- POST two disagreeing human decisions → conflict_flag=True on CandidatePaper
- POST /papers/{id}/resolve-conflict clears conflict_flag and sets binding status
- 401 when unauthenticated
"""

from __future__ import annotations

import pytest
from db.models import Paper
from db.models.candidate import CandidatePaper, CandidatePaperStatus
from db.models.search import SearchString
from db.models.search_exec import SearchExecution, SearchExecutionStatus
from db.models.study import Reviewer, ReviewerType
from db.models.users import GroupMembership, GroupRole, ResearchGroup
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create group + membership + study; return study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Decisions Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Decisions Study",
            "topic": "TDD",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _insert_reviewer(
    db_engine, study_id: int, reviewer_type: ReviewerType = ReviewerType.HUMAN
) -> int:
    """Insert a Reviewer record; return reviewer id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        reviewer = Reviewer(study_id=study_id, reviewer_type=reviewer_type)
        session.add(reviewer)
        await session.commit()
        return reviewer.id


async def _insert_candidate_paper(db_engine, study_id: int) -> int:
    """Insert Paper + SearchString + SearchExecution + CandidatePaper; return cp id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        paper = Paper(title="Test Paper", doi=None, authors=[])
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
            current_status=CandidatePaperStatus.PENDING,
        )
        session.add(cp)
        await session.commit()
        return cp.id


class TestSubmitDecision:
    """POST /studies/{study_id}/papers/{candidate_id}/decisions."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token → 401."""
        resp = await client.post("/api/v1/studies/1/papers/1/decisions", json={})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_reviewer_not_in_study_returns_422(self, client, alice, bob, db_engine) -> None:
        """Reviewer that belongs to a different study → 422."""
        alice_user, _ = alice
        study_id = await _setup_study(client, db_engine, alice_user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        # Reviewer inserted for a different (fake) study
        wrong_study_id = study_id + 999
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            reviewer = Reviewer(study_id=wrong_study_id, reviewer_type=ReviewerType.HUMAN)
            session.add(reviewer)
            await session.commit()
            wrong_reviewer_id = reviewer.id

        resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": wrong_reviewer_id,
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(alice_user.id),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_accepted_decision_recorded(self, client, alice, db_engine) -> None:
        """Valid accepted decision → 201 with correct decision field."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer_id = await _insert_reviewer(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": reviewer_id,
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["decision"] == "accepted"
        assert body["reviewer_id"] == reviewer_id
        assert body["is_override"] is False

    @pytest.mark.asyncio
    async def test_is_override_true_when_overrides_decision_id_provided(
        self, client, alice, db_engine
    ) -> None:
        """Providing overrides_decision_id sets is_override=True on the new decision."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer_id = await _insert_reviewer(db_engine, study_id)

        # First decision
        resp1 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": reviewer_id,
                "decision": "rejected",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        assert resp1.status_code == 201
        first_decision_id = resp1.json()["id"]

        # Override decision — observed_status is the outcome of the first decision,
        # since that is what current_status became after resp1.
        resp2 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": reviewer_id,
                "decision": "accepted",
                "observed_status": "rejected",
                "reasons": [],
                "overrides_decision_id": first_decision_id,
            },
            headers=_bearer(user.id),
        )
        assert resp2.status_code == 201
        body = resp2.json()
        assert body["is_override"] is True
        assert body["overrides_decision_id"] == first_decision_id

    @pytest.mark.asyncio
    async def test_two_disagreeing_human_reviewers_sets_conflict_flag(
        self, client, alice, db_engine
    ) -> None:
        """Two human reviewers with different decisions set conflict_flag=True."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer1_id = await _insert_reviewer(db_engine, study_id, ReviewerType.HUMAN)
        reviewer2_id = await _insert_reviewer(db_engine, study_id, ReviewerType.HUMAN)

        # Reviewer 1: accepted
        resp1 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": reviewer1_id,
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        assert resp1.status_code == 201

        # Reviewer 2: rejected → should trigger conflict. Reviewer 2 observes the
        # candidate after reviewer 1's decision moved current_status to "accepted".
        resp2 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": reviewer2_id,
                "decision": "rejected",
                "observed_status": "accepted",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        assert resp2.status_code == 201

        # Check CandidatePaper has conflict_flag=True via GET
        get_resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}",
            headers=_bearer(user.id),
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["conflict_flag"] is True

    @pytest.mark.asyncio
    async def test_agreeing_human_reviewers_no_conflict(self, client, alice, db_engine) -> None:
        """Two human reviewers with the same decision → conflict_flag=False."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer1_id = await _insert_reviewer(db_engine, study_id, ReviewerType.HUMAN)
        reviewer2_id = await _insert_reviewer(db_engine, study_id, ReviewerType.HUMAN)

        # Reviewer 1 observes "pending"; reviewer 2 observes "accepted" — the status
        # left behind by reviewer 1's decision, since both decide "accepted".
        for rid, observed in [(reviewer1_id, "pending"), (reviewer2_id, "accepted")]:
            resp = await client.post(
                f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
                json={
                    "reviewer_id": rid,
                    "decision": "accepted",
                    "observed_status": observed,
                    "reasons": [],
                },
                headers=_bearer(user.id),
            )
            assert resp.status_code == 201

        get_resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}",
            headers=_bearer(user.id),
        )
        assert get_resp.json()["conflict_flag"] is False

    @pytest.mark.asyncio
    async def test_decision_with_reasons_list_stored(self, client, alice, db_engine) -> None:
        """Reasons list is persisted and returned in response."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer_id = await _insert_reviewer(db_engine, study_id)

        reasons = [{"criterion_id": 1, "criterion_type": "inclusion", "text": "Peer-reviewed"}]
        resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": reviewer_id,
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": reasons,
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["reasons"] is not None
        assert len(body["reasons"]) == 1
        assert body["reasons"][0]["text"] == "Peer-reviewed"

    @pytest.mark.asyncio
    async def test_stale_observed_status_returns_409_with_both_statuses(
        self, client, alice, db_engine
    ) -> None:
        """observed_status differing from stored current_status → 409 stale_state.

        The body must carry both observed_status and current_status so the client
        can show what changed (FR-025, FR-027).
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer1_id = await _insert_reviewer(db_engine, study_id, ReviewerType.HUMAN)
        reviewer2_id = await _insert_reviewer(db_engine, study_id, ReviewerType.HUMAN)

        # Reviewer 1 decides, moving current_status from "pending" to "accepted".
        resp1 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": reviewer1_id,
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        assert resp1.status_code == 201

        # Reviewer 2 still believes the paper is "pending" — stale view.
        resp2 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": reviewer2_id,
                "decision": "rejected",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        assert resp2.status_code == 409
        detail = resp2.json()["detail"]
        assert detail["error"] == "stale_state"
        assert detail["observed_status"] == "pending"
        assert detail["current_status"] == "accepted"

    @pytest.mark.asyncio
    async def test_unacknowledged_prior_decision_returns_409_with_prior_decision(
        self, client, alice, db_engine
    ) -> None:
        """A second decision by the SAME reviewer with no overrides_decision_id → 409.

        The detail must carry the reviewer's earlier decision (FR-022).
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer_id = await _insert_reviewer(db_engine, study_id)

        resp1 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": reviewer_id,
                "decision": "rejected",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        assert resp1.status_code == 201
        first_decision_id = resp1.json()["id"]

        # Second submission by the same reviewer, no overrides_decision_id. Its
        # observed_status matches the current stored status ("rejected"), so it
        # clears the stale-state check and reaches the unacknowledged-prior check.
        resp2 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": reviewer_id,
                "decision": "accepted",
                "observed_status": "rejected",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        assert resp2.status_code == 409
        detail = resp2.json()["detail"]
        assert detail["error"] == "unacknowledged_prior_decision"
        prior = detail["prior_decision"]
        assert prior["id"] == first_decision_id
        assert prior["decision"] == "rejected"

    @pytest.mark.asyncio
    async def test_override_resubmission_retains_original_and_clears_no_conflict(
        self, client, alice, db_engine
    ) -> None:
        """Resubmitting with overrides_decision_id succeeds and does not conflict.

        Expect 201, is_override True, original decision row retained, and
        conflict_flag NOT set (a correction by the same reviewer is not a
        disagreement between reviewers).
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer_id = await _insert_reviewer(db_engine, study_id)

        resp1 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": reviewer_id,
                "decision": "rejected",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        assert resp1.status_code == 201
        first_decision_id = resp1.json()["id"]

        resp2 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": reviewer_id,
                "decision": "accepted",
                "observed_status": "rejected",
                "reasons": [],
                "overrides_decision_id": first_decision_id,
            },
            headers=_bearer(user.id),
        )
        assert resp2.status_code == 201
        body = resp2.json()
        assert body["is_override"] is True

        # Original decision row is retained, not deleted or overwritten.
        decisions_resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            headers=_bearer(user.id),
        )
        assert decisions_resp.status_code == 200
        decision_ids = {d["id"] for d in decisions_resp.json()}
        assert first_decision_id in decision_ids
        assert body["id"] in decision_ids
        assert len(decisions_resp.json()) == 2

        # A self-override must not be counted as a reviewer disagreement.
        get_resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}",
            headers=_bearer(user.id),
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["conflict_flag"] is False


class TestResolveConflict:
    """POST /studies/{study_id}/papers/{candidate_id}/resolve-conflict."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token → 401."""
        resp = await client.post("/api/v1/studies/1/papers/1/resolve-conflict", json={})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_resolve_clears_conflict_flag(self, client, alice, db_engine) -> None:
        """Resolving a conflict sets conflict_flag=False on the candidate."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer1_id = await _insert_reviewer(db_engine, study_id, ReviewerType.HUMAN)
        reviewer2_id = await _insert_reviewer(db_engine, study_id, ReviewerType.HUMAN)

        # Create conflict. Reviewer 1 observes "pending"; reviewer 2 observes
        # "accepted" — the status left behind by reviewer 1's decision.
        for rid, dec, observed in [
            (reviewer1_id, "accepted", "pending"),
            (reviewer2_id, "rejected", "accepted"),
        ]:
            await client.post(
                f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
                json={
                    "reviewer_id": rid,
                    "decision": dec,
                    "observed_status": observed,
                    "reasons": [],
                },
                headers=_bearer(user.id),
            )

        # Resolve
        resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/resolve-conflict",
            json={"reviewer_id": reviewer1_id, "decision": "accepted", "reasons": []},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        assert resp.json()["is_override"] is True

        # Verify conflict cleared
        get_resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}",
            headers=_bearer(user.id),
        )
        assert get_resp.json()["conflict_flag"] is False

    @pytest.mark.asyncio
    async def test_resolve_sets_binding_status(self, client, alice, db_engine) -> None:
        """Resolve-conflict updates CandidatePaper status to the binding decision."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer1_id = await _insert_reviewer(db_engine, study_id, ReviewerType.HUMAN)
        reviewer2_id = await _insert_reviewer(db_engine, study_id, ReviewerType.HUMAN)

        for rid, dec, observed in [
            (reviewer1_id, "accepted", "pending"),
            (reviewer2_id, "rejected", "accepted"),
        ]:
            await client.post(
                f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
                json={
                    "reviewer_id": rid,
                    "decision": dec,
                    "observed_status": observed,
                    "reasons": [],
                },
                headers=_bearer(user.id),
            )

        await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/resolve-conflict",
            json={"reviewer_id": reviewer1_id, "decision": "rejected", "reasons": []},
            headers=_bearer(user.id),
        )

        get_resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}",
            headers=_bearer(user.id),
        )
        assert get_resp.json()["current_status"] == "rejected"

    @pytest.mark.asyncio
    async def test_resolve_without_conflict_returns_422(self, client, alice, db_engine) -> None:
        """Calling resolve-conflict when no conflict exists → 422."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer_id = await _insert_reviewer(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/resolve-conflict",
            json={"reviewer_id": reviewer_id, "decision": "accepted", "reasons": []},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422


class TestListDecisions:
    """GET /studies/{study_id}/papers/{candidate_id}/decisions."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth → 401."""
        resp = await client.get("/api/v1/studies/1/papers/1/decisions")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_empty_list_when_no_decisions(self, client, alice, db_engine) -> None:
        """No decisions yet → empty list."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_returns_decision_after_submission(self, client, alice, db_engine) -> None:
        """Decision history shows submitted decision in order."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)
        reviewer_id = await _insert_reviewer(db_engine, study_id)

        await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "reviewer_id": reviewer_id,
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )

        resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["decision"] == "accepted"
        assert items[0]["reviewer_id"] == reviewer_id
