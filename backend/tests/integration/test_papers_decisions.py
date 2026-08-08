"""Integration tests for paper decision endpoints.

Covers:
- POST /papers/{id}/decisions: reviewer_id is resolved from the session, not
  the request body (TFIX4) — a non-member is rejected with 403
- POST /papers/{id}/decisions: is_override=True recorded when overrides_decision_id provided
- POST two disagreeing human decisions (by two different users) → conflict_flag=True
- POST /papers/{id}/resolve-conflict clears conflict_flag and sets binding status
- 401 when unauthenticated
"""

from __future__ import annotations

import pytest
from db.models import Paper
from db.models.candidate import CandidatePaper, CandidatePaperStatus
from db.models.search import SearchString
from db.models.search_exec import SearchExecution, SearchExecutionStatus
from db.models.study import Reviewer, StudyMember, StudyMemberRole
from db.models.users import GroupMembership, GroupRole, ResearchGroup
from sqlalchemy import select
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


async def _add_study_member(
    db_engine, study_id: int, user_id: int, role: StudyMemberRole = StudyMemberRole.MEMBER
) -> None:
    """Insert a StudyMember row so *user_id* passes ``require_study_member``.

    ``_setup_study`` only makes its creating user a member; tests that need a
    second authenticated user (e.g. two disagreeing human reviewers) must add
    that user as a study member explicitly or they 403 before ever reaching
    the reviewer-resolution logic under test.
    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        session.add(StudyMember(study_id=study_id, user_id=user_id, role=role))
        await session.commit()


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
    async def test_non_member_returns_403(self, client, alice, bob, db_engine) -> None:
        """A user who is not a member of the study → 403.

        TFIX4 removed ``reviewer_id`` from the request body — there is no
        longer a client-supplied reviewer to validate against the study, so
        the guarantee that matters is study membership itself
        (``require_study_member``), checked before reviewer resolution.
        """
        alice_user, _ = alice
        bob_user, _ = bob
        study_id = await _setup_study(client, db_engine, alice_user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(bob_user.id),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_accepted_decision_recorded(self, client, alice, db_engine) -> None:
        """Valid accepted decision → 201 with correct decision field.

        No pre-existing Reviewer row is created for alice — the session
        resolver creates one on demand (TFIX4 / FR-005).
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["decision"] == "accepted"
        assert isinstance(body["reviewer_id"], int)
        assert body["is_override"] is False

    @pytest.mark.asyncio
    async def test_is_override_true_when_overrides_decision_id_provided(
        self, client, alice, db_engine
    ) -> None:
        """Providing overrides_decision_id sets is_override=True on the new decision."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        # First decision
        resp1 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
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
        self, client, alice, bob, db_engine
    ) -> None:
        """Two different users deciding differently set conflict_flag=True.

        Each authenticates separately, so the two reviewer rows are resolved
        from their own sessions rather than supplied by the caller.
        """
        alice_user, _ = alice
        bob_user, _ = bob
        study_id = await _setup_study(client, db_engine, alice_user)
        await _add_study_member(db_engine, study_id, bob_user.id)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        # Alice: accepted
        resp1 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(alice_user.id),
        )
        assert resp1.status_code == 201

        # Bob: rejected → should trigger conflict. Bob observes the candidate
        # after alice's decision moved current_status to "accepted".
        resp2 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "decision": "rejected",
                "observed_status": "accepted",
                "reasons": [],
            },
            headers=_bearer(bob_user.id),
        )
        assert resp2.status_code == 201

        # Check CandidatePaper has conflict_flag=True via GET
        get_resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}",
            headers=_bearer(alice_user.id),
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["conflict_flag"] is True

    @pytest.mark.asyncio
    async def test_agreeing_human_reviewers_no_conflict(
        self, client, alice, bob, db_engine
    ) -> None:
        """Two different users deciding the same way leave conflict_flag False.

        Agreement is not disagreement, however many reviewers recorded it.
        """
        alice_user, _ = alice
        bob_user, _ = bob
        study_id = await _setup_study(client, db_engine, alice_user)
        await _add_study_member(db_engine, study_id, bob_user.id)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        # Alice observes "pending"; bob observes "accepted" — the status left
        # behind by alice's decision, since both decide "accepted".
        for uid, observed in [(alice_user.id, "pending"), (bob_user.id, "accepted")]:
            resp = await client.post(
                f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
                json={
                    "decision": "accepted",
                    "observed_status": observed,
                    "reasons": [],
                },
                headers=_bearer(uid),
            )
            assert resp.status_code == 201

        get_resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}",
            headers=_bearer(alice_user.id),
        )
        assert get_resp.json()["conflict_flag"] is False

    @pytest.mark.asyncio
    async def test_decision_with_reasons_list_stored(self, client, alice, db_engine) -> None:
        """Reasons list is persisted and returned in response."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        reasons = [{"criterion_id": 1, "criterion_type": "inclusion", "text": "Peer-reviewed"}]
        resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
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

        # First decision, moving current_status from "pending" to "accepted".
        resp1 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        assert resp1.status_code == 201

        # Same reviewer still believes the paper is "pending" — stale view. The
        # stale-state check (order 5) fires before the unacknowledged-prior
        # check (order 6), so this 409s as stale_state even though it is also
        # this reviewer's second decision.
        resp2 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
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

        resp1 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "decision": "rejected",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        assert resp1.status_code == 201
        first_decision_id = resp1.json()["id"]

        # Second submission by the same authenticated user (session-resolved to
        # the same reviewer), no overrides_decision_id. Its observed_status
        # matches the current stored status ("rejected"), so it clears the
        # stale-state check and reaches the unacknowledged-prior check.
        resp2 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
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

        resp1 = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
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


class TestDecisionAnnotation:
    """annotation is a free-text field distinct from `reasons` (TFIX3, FR-002)."""

    @pytest.mark.asyncio
    async def test_annotation_persisted_and_returned_from_submit_decision(
        self, client, alice, db_engine
    ) -> None:
        """An annotation sent with a decision is persisted and echoed back."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": [],
                "annotation": "Strong empirical evidence, worth a closer read.",
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        assert resp.json()["annotation"] == "Strong empirical evidence, worth a closer read."

    @pytest.mark.asyncio
    async def test_annotation_defaults_to_null_not_empty_string(
        self, client, alice, db_engine
    ) -> None:
        """A decision with no annotation returns null, not an empty string."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        assert resp.json()["annotation"] is None

    @pytest.mark.asyncio
    async def test_annotation_returned_from_list_decisions(self, client, alice, db_engine) -> None:
        """An annotation set on submission is readable back via GET .../decisions."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": [],
                "annotation": "Follow up with authors about dataset access.",
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
        assert items[0]["annotation"] == "Follow up with authors about dataset access."

    @pytest.mark.asyncio
    async def test_annotation_survives_resolve_conflict_path(
        self, client, alice, bob, db_engine
    ) -> None:
        """An annotation sent with a conflict resolution is persisted and returned."""
        alice_user, _ = alice
        bob_user, _ = bob
        study_id = await _setup_study(client, db_engine, alice_user)
        await _add_study_member(db_engine, study_id, bob_user.id)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        for uid, dec, observed in [
            (alice_user.id, "accepted", "pending"),
            (bob_user.id, "rejected", "accepted"),
        ]:
            await client.post(
                f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
                json={
                    "decision": dec,
                    "observed_status": observed,
                    "reasons": [],
                },
                headers=_bearer(uid),
            )

        resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/resolve-conflict",
            json={
                "decision": "accepted",
                "reasons": [],
                "annotation": "Binding call: alice's inclusion criteria reading is correct.",
            },
            headers=_bearer(alice_user.id),
        )
        assert resp.status_code == 201
        assert (
            resp.json()["annotation"]
            == "Binding call: alice's inclusion criteria reading is correct."
        )


class TestResolveConflict:
    """POST /studies/{study_id}/papers/{candidate_id}/resolve-conflict."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token → 401."""
        resp = await client.post("/api/v1/studies/1/papers/1/resolve-conflict", json={})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_resolve_clears_conflict_flag(self, client, alice, bob, db_engine) -> None:
        """Resolving a conflict sets conflict_flag=False on the candidate."""
        alice_user, _ = alice
        bob_user, _ = bob
        study_id = await _setup_study(client, db_engine, alice_user)
        await _add_study_member(db_engine, study_id, bob_user.id)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        # Create conflict. Alice observes "pending"; bob observes "accepted" —
        # the status left behind by alice's decision.
        for uid, dec, observed in [
            (alice_user.id, "accepted", "pending"),
            (bob_user.id, "rejected", "accepted"),
        ]:
            await client.post(
                f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
                json={
                    "decision": dec,
                    "observed_status": observed,
                    "reasons": [],
                },
                headers=_bearer(uid),
            )

        # Resolve
        resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/resolve-conflict",
            json={"decision": "accepted", "reasons": []},
            headers=_bearer(alice_user.id),
        )
        assert resp.status_code == 201
        assert resp.json()["is_override"] is True

        # Verify conflict cleared
        get_resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}",
            headers=_bearer(alice_user.id),
        )
        assert get_resp.json()["conflict_flag"] is False

    @pytest.mark.asyncio
    async def test_resolve_sets_binding_status(self, client, alice, bob, db_engine) -> None:
        """Resolve-conflict updates CandidatePaper status to the binding decision."""
        alice_user, _ = alice
        bob_user, _ = bob
        study_id = await _setup_study(client, db_engine, alice_user)
        await _add_study_member(db_engine, study_id, bob_user.id)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        for uid, dec, observed in [
            (alice_user.id, "accepted", "pending"),
            (bob_user.id, "rejected", "accepted"),
        ]:
            await client.post(
                f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
                json={
                    "decision": dec,
                    "observed_status": observed,
                    "reasons": [],
                },
                headers=_bearer(uid),
            )

        await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/resolve-conflict",
            json={"decision": "rejected", "reasons": []},
            headers=_bearer(alice_user.id),
        )

        get_resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}",
            headers=_bearer(alice_user.id),
        )
        assert get_resp.json()["current_status"] == "rejected"

    @pytest.mark.asyncio
    async def test_resolve_without_conflict_returns_422(self, client, alice, db_engine) -> None:
        """Calling resolve-conflict when no conflict exists → 422."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/resolve-conflict",
            json={"decision": "accepted", "reasons": []},
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

        post_resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "decision": "accepted",
                "observed_status": "pending",
                "reasons": [],
            },
            headers=_bearer(user.id),
        )
        reviewer_id = post_resp.json()["reviewer_id"]

        resp = await client.get(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["decision"] == "accepted"
        assert items[0]["reviewer_id"] == reviewer_id


class TestSessionReviewerResolution:
    """Reviewer identity is resolved from the session (TFIX4), never the request body."""

    @pytest.mark.asyncio
    async def test_decisions_attributed_to_calling_users_reviewer(
        self, client, alice, bob, db_engine
    ) -> None:
        """A decision is attributed to the calling user's own reviewer row.

        Two users deciding on one candidate produce two distinct reviewer_ids,
        each mapping back to the user who authenticated — the guarantee TFIX4
        exists to provide, and the one a client-supplied reviewer_id could not
        make.
        """
        alice_user, _ = alice
        bob_user, _ = bob
        study_id = await _setup_study(client, db_engine, alice_user)
        await _add_study_member(db_engine, study_id, bob_user.id)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        alice_resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={"decision": "accepted", "observed_status": "pending", "reasons": []},
            headers=_bearer(alice_user.id),
        )
        assert alice_resp.status_code == 201
        alice_reviewer_id = alice_resp.json()["reviewer_id"]

        bob_resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={"decision": "rejected", "observed_status": "accepted", "reasons": []},
            headers=_bearer(bob_user.id),
        )
        assert bob_resp.status_code == 201
        bob_reviewer_id = bob_resp.json()["reviewer_id"]

        assert alice_reviewer_id != bob_reviewer_id

        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            alice_reviewer = await session.get(Reviewer, alice_reviewer_id)
            bob_reviewer = await session.get(Reviewer, bob_reviewer_id)
        assert alice_reviewer is not None
        assert bob_reviewer is not None
        assert alice_reviewer.user_id == alice_user.id
        assert bob_reviewer.user_id == bob_user.id

    @pytest.mark.asyncio
    async def test_member_with_no_reviewer_row_gets_one_created_on_demand(
        self, client, alice, db_engine
    ) -> None:
        """A member with no reviewer row can still screen, and gets exactly one.

        Reviewer rows are otherwise created only at study creation, so a member
        added later had no row and no way to record a decision at all. FR-005
        requires that any member can. The second decision must reuse the row
        rather than mint another, or one researcher would look like several.
        """
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        cp_id = await _insert_candidate_paper(db_engine, study_id)

        first_resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={"decision": "rejected", "observed_status": "pending", "reasons": []},
            headers=_bearer(user.id),
        )
        assert first_resp.status_code == 201
        first_reviewer_id = first_resp.json()["reviewer_id"]

        second_resp = await client.post(
            f"/api/v1/studies/{study_id}/papers/{cp_id}/decisions",
            json={
                "decision": "accepted",
                "observed_status": "rejected",
                "reasons": [],
                "overrides_decision_id": first_resp.json()["id"],
            },
            headers=_bearer(user.id),
        )
        assert second_resp.status_code == 201
        assert second_resp.json()["reviewer_id"] == first_reviewer_id

        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            result = await session.execute(
                select(Reviewer).where(
                    Reviewer.study_id == study_id,
                    Reviewer.user_id == user.id,
                )
            )
            reviewer_rows = result.scalars().all()
        assert len(reviewer_rows) == 1
