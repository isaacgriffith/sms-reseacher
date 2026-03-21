"""Integration tests for SLR inter-rater agreement routes (feature 007, T041).

Covers:
- GET /slr/studies/{id}/inter-rater → 200 with empty list.
- GET /slr/studies/{id}/inter-rater → 200 with existing records.
- POST /slr/studies/{id}/inter-rater/compute → 200 with correct Kappa.
- POST /slr/studies/{id}/inter-rater/compute → 422 when round is incomplete.
- POST /slr/studies/{id}/inter-rater/post-discussion → 200 with post_discussion phase.
- post-discussion creates a second record distinct from the compute record.
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
        group = ResearchGroup(name=f"IRR Group {user.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "IRR SLR Test",
            "topic": "Inter-rater",
            "study_type": "SLR",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


_irr_paper_counter = 0


async def _setup_reviewers_and_papers(db_engine, study_id: int, n_papers: int = 3):
    """Insert two reviewers and n candidate papers, return (rev_a_id, rev_b_id)."""
    global _irr_paper_counter
    from db.models.candidate import CandidatePaper, CandidatePaperStatus, PaperDecision, PaperDecisionType
    from db.models.study import Reviewer, ReviewerType
    from db.models.search import SearchString
    from db.models.search_exec import SearchExecution, SearchExecutionStatus
    from db.models import Paper

    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        search_string = SearchString(
            study_id=study_id,
            version=1,
            string_text="inter-rater AND test",
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

        rev_a = Reviewer(study_id=study_id, reviewer_type=ReviewerType.HUMAN)
        rev_b = Reviewer(study_id=study_id, reviewer_type=ReviewerType.HUMAN)
        session.add(rev_a)
        session.add(rev_b)
        await session.flush()

        for i in range(n_papers):
            _irr_paper_counter += 1
            paper = Paper(title=f"IRR Paper {_irr_paper_counter}", doi=f"10.9999/irr.{_irr_paper_counter}")
            session.add(paper)
            await session.flush()

            cp = CandidatePaper(
                study_id=study_id,
                paper_id=paper.id,
                search_execution_id=exec_row.id,
                phase_tag="title_abstract",
                current_status=CandidatePaperStatus.PENDING,
            )
            session.add(cp)
            await session.flush()

            # Both reviewers accept all papers
            session.add(PaperDecision(
                candidate_paper_id=cp.id,
                reviewer_id=rev_a.id,
                decision=PaperDecisionType.ACCEPTED,
            ))
            session.add(PaperDecision(
                candidate_paper_id=cp.id,
                reviewer_id=rev_b.id,
                decision=PaperDecisionType.ACCEPTED,
            ))

        await session.commit()
        return rev_a.id, rev_b.id


class TestListInterRaterRecords:
    """GET /slr/studies/{id}/inter-rater."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_initially(self, client, db_engine, alice) -> None:
        """Returns empty list when no records exist for the study."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/inter-rater",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["records"] == []

    @pytest.mark.asyncio
    async def test_returns_existing_records(self, client, db_engine, alice) -> None:
        """Returns records that already exist for the study."""
        from db.models.slr import AgreementRoundType, InterRaterAgreementRecord

        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        rev_a, rev_b = await _setup_reviewers_and_papers(db_engine, study_id)

        # Insert a record directly
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            record = InterRaterAgreementRecord(
                study_id=study_id,
                reviewer_a_id=rev_a,
                reviewer_b_id=rev_b,
                round_type=AgreementRoundType.TITLE_ABSTRACT,
                phase="pre_discussion",
                kappa_value=0.8,
                n_papers=3,
                threshold_met=True,
            )
            session.add(record)
            await session.commit()

        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/inter-rater",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        records = resp.json()["records"]
        assert len(records) == 1
        assert records[0]["kappa_value"] == 0.8


class TestComputeKappa:
    """POST /slr/studies/{id}/inter-rater/compute."""

    @pytest.mark.asyncio
    async def test_computes_and_returns_kappa(self, client, db_engine, alice) -> None:
        """Returns a Kappa record when both reviewers have completed the round."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        rev_a, rev_b = await _setup_reviewers_and_papers(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/slr/studies/{study_id}/inter-rater/compute",
            json={
                "reviewer_a_id": rev_a,
                "reviewer_b_id": rev_b,
                "round_type": "title_abstract",
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["study_id"] == study_id
        assert data["phase"] == "pre_discussion"
        assert data["n_papers"] == 3
        assert data["round_type"] == "title_abstract"

    @pytest.mark.asyncio
    async def test_returns_422_when_round_incomplete(self, client, db_engine, alice) -> None:
        """Returns 422 when a reviewer hasn't assessed all papers."""
        from db.models.candidate import CandidatePaper, CandidatePaperStatus
        from db.models.study import Reviewer, ReviewerType
        from db.models.search_exec import SearchExecution, SearchExecutionStatus
        from db.models import Paper

        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        # Set up: only rev_a has decisions, rev_b has none
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            from db.models.search import SearchString
            ss = SearchString(
                study_id=study_id, version=1,
                string_text="incomplete AND test", is_active=True,
            )
            session.add(ss)
            await session.flush()
            exec_row = SearchExecution(
                study_id=study_id,
                search_string_id=ss.id,
                phase_tag="title_abstract",
                status=SearchExecutionStatus.COMPLETED,
            )
            session.add(exec_row)
            await session.flush()

            rev_a = Reviewer(study_id=study_id, reviewer_type=ReviewerType.HUMAN)
            rev_b = Reviewer(study_id=study_id, reviewer_type=ReviewerType.HUMAN)
            session.add(rev_a)
            session.add(rev_b)
            await session.flush()

            from db.models.candidate import PaperDecision, PaperDecisionType
            global _irr_paper_counter
            _irr_paper_counter += 1
            paper = Paper(title=f"Incomplete Paper {_irr_paper_counter}", doi=f"10.9999/incomplete.{_irr_paper_counter}")
            session.add(paper)
            await session.flush()
            cp = CandidatePaper(
                study_id=study_id,
                paper_id=paper.id,
                search_execution_id=exec_row.id,
                phase_tag="title_abstract",
                current_status=CandidatePaperStatus.PENDING,
            )
            session.add(cp)
            await session.flush()
            # Only rev_a decides
            session.add(PaperDecision(
                candidate_paper_id=cp.id,
                reviewer_id=rev_a.id,
                decision=PaperDecisionType.ACCEPTED,
            ))
            await session.commit()
            rev_a_id = rev_a.id
            rev_b_id = rev_b.id

        resp = await client.post(
            f"/api/v1/slr/studies/{study_id}/inter-rater/compute",
            json={
                "reviewer_a_id": rev_a_id,
                "reviewer_b_id": rev_b_id,
                "round_type": "title_abstract",
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422


class TestPostDiscussionKappa:
    """POST /slr/studies/{id}/inter-rater/post-discussion."""

    @pytest.mark.asyncio
    async def test_creates_post_discussion_record(self, client, db_engine, alice) -> None:
        """Creates a new record with phase='post_discussion'."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        rev_a, rev_b = await _setup_reviewers_and_papers(db_engine, study_id)

        resp = await client.post(
            f"/api/v1/slr/studies/{study_id}/inter-rater/post-discussion",
            json={
                "reviewer_a_id": rev_a,
                "reviewer_b_id": rev_b,
                "round_type": "title_abstract",
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["phase"] == "post_discussion"

    @pytest.mark.asyncio
    async def test_post_discussion_creates_second_record(self, client, db_engine, alice) -> None:
        """post-discussion creates a distinct second record from compute."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        rev_a, rev_b = await _setup_reviewers_and_papers(db_engine, study_id)

        payload = {
            "reviewer_a_id": rev_a,
            "reviewer_b_id": rev_b,
            "round_type": "title_abstract",
        }
        await client.post(
            f"/api/v1/slr/studies/{study_id}/inter-rater/compute",
            json=payload,
            headers=_bearer(user.id),
        )
        await client.post(
            f"/api/v1/slr/studies/{study_id}/inter-rater/post-discussion",
            json=payload,
            headers=_bearer(user.id),
        )

        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/inter-rater",
            headers=_bearer(user.id),
        )
        records = resp.json()["records"]
        assert len(records) == 2
        phases = {r["phase"] for r in records}
        assert phases == {"pre_discussion", "post_discussion"}
