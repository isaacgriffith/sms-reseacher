"""Integration tests for the /api/v1/search-strings router.

Covers manual create, list, generate endpoint (mocked agent), test endpoint 202
response, and iteration approval PATCH (T172).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.search import SearchString, SearchStringIteration
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create a group and study, returning the study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Search Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Search Study",
            "topic": "TDD",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    return resp.json()["id"]


async def _insert_search_string(db_engine, study_id: int) -> tuple[int, int]:
    """Insert a SearchString with one iteration directly into the DB.

    Returns:
        Tuple of (search_string_id, iteration_id).
    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        ss = SearchString(
            study_id=study_id,
            version=1,
            string_text='("TDD" OR "test-driven") AND ("code quality")',
            is_active=False,
        )
        session.add(ss)
        await session.flush()
        iteration = SearchStringIteration(
            search_string_id=ss.id,
            iteration_number=1,
            result_set_count=42,
            test_set_recall=0.75,
            ai_adequacy_judgment="Adequate coverage of TDD synonyms.",
        )
        session.add(iteration)
        await session.commit()
        await session.refresh(ss)
        await session.refresh(iteration)
        return ss.id, iteration.id


class TestListSearchStrings:
    """GET /studies/{study_id}/search-strings."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_initially(self, client, alice, db_engine):
        """No search strings returns empty list."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/search-strings",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client, alice, db_engine):
        """No auth header returns 401."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(f"/api/v1/studies/{study_id}/search-strings")
        assert resp.status_code == 401


class TestCreateSearchString:
    """POST /studies/{study_id}/search-strings (manual)."""

    @pytest.mark.asyncio
    async def test_create_manual_search_string(self, client, alice, db_engine):
        """Manual POST creates a new search string with version 1."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.post(
            f"/api/v1/studies/{study_id}/search-strings",
            json={"string_text": '("TDD" OR "test-driven") AND quality'},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["string_text"] == '("TDD" OR "test-driven") AND quality'
        assert body["version"] == 1
        assert body["is_active"] is False
        assert body["study_id"] == study_id

    @pytest.mark.asyncio
    async def test_second_create_increments_version(self, client, alice, db_engine):
        """A second manual POST creates version 2."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await client.post(
            f"/api/v1/studies/{study_id}/search-strings",
            json={"string_text": "first string"},
            headers=_bearer(user.id),
        )
        resp = await client.post(
            f"/api/v1/studies/{study_id}/search-strings",
            json={"string_text": "second string"},
            headers=_bearer(user.id),
        )
        assert resp.json()["version"] == 2

    @pytest.mark.asyncio
    async def test_created_string_appears_in_list(self, client, alice, db_engine):
        """After creation, the string appears in the list endpoint."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await client.post(
            f"/api/v1/studies/{study_id}/search-strings",
            json={"string_text": "findable string"},
            headers=_bearer(user.id),
        )
        list_resp = await client.get(
            f"/api/v1/studies/{study_id}/search-strings",
            headers=_bearer(user.id),
        )
        texts = [s["string_text"] for s in list_resp.json()]
        assert "findable string" in texts


class TestGenerateSearchString:
    """POST /studies/{study_id}/search-strings/generate."""

    @pytest.mark.asyncio
    async def test_generate_returns_201_with_mocked_agent(self, client, alice, db_engine):
        """Generate endpoint returns 201 and creates a SearchString when agent is mocked."""
        from agents.services.search_builder import SearchStringResult, TermGroup

        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        # Set up PICO (required by generate endpoint)
        await client.put(
            f"/api/v1/studies/{study_id}/pico",
            json={
                "variant": "PICO",
                "population": "software engineers",
                "intervention": "TDD",
                "comparison": "no TDD",
                "outcome": "code quality",
            },
            headers=_bearer(user.id),
        )

        mock_result = SearchStringResult(
            search_string='("TDD" OR "test-driven") AND "code quality"',
            terms_used=[TermGroup(component="intervention", terms=["TDD", "test-driven"])],
            expansion_notes="Expanded via thesaurus.",
        )

        with patch(
            "agents.services.search_builder.SearchStringBuilderAgent",
        ) as MockAgent:
            MockAgent.return_value.run = AsyncMock(return_value=mock_result)
            resp = await client.post(
                f"/api/v1/studies/{study_id}/search-strings/generate",
                headers=_bearer(user.id),
            )

        assert resp.status_code == 201
        body = resp.json()
        assert body["created_by_agent"] == "search-builder"
        assert body["string_text"] == '("TDD" OR "test-driven") AND "code quality"'

    @pytest.mark.asyncio
    async def test_generate_requires_pico(self, client, alice, db_engine):
        """Generate endpoint returns 422 if PICO has not been saved."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.post(
            f"/api/v1/studies/{study_id}/search-strings/generate",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422


class TestTestSearchString:
    """POST /studies/{study_id}/search-strings/{id}/test."""

    @pytest.mark.asyncio
    async def test_test_endpoint_returns_202(self, client, alice, db_engine):
        """POST .../test returns 202 even when Redis is unavailable (mocked ARQ)."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        ss_id, _ = await _insert_search_string(db_engine, study_id)

        mock_pool = MagicMock()
        mock_job = MagicMock()
        mock_job.job_id = "test-job-id-123"
        mock_pool.enqueue_job = AsyncMock(return_value=mock_job)
        mock_pool.aclose = AsyncMock()

        with patch("arq.create_pool", AsyncMock(return_value=mock_pool)):
            resp = await client.post(
                f"/api/v1/studies/{study_id}/search-strings/{ss_id}/test",
                json={"databases": ["acm", "ieee"]},
                headers=_bearer(user.id),
            )

        assert resp.status_code == 202
        body = resp.json()
        assert "job_id" in body
        assert body["search_string_id"] == ss_id

    @pytest.mark.asyncio
    async def test_test_endpoint_returns_404_for_missing_string(self, client, alice, db_engine):
        """Test endpoint returns 404 for a non-existent search string."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.post(
            f"/api/v1/studies/{study_id}/search-strings/99999/test",
            json={},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_test_endpoint_job_id_in_response_body(self, client, alice, db_engine):
        """POST .../test 202 response must include job_id field (FR-027a)."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        ss_id, _ = await _insert_search_string(db_engine, study_id)

        mock_pool = MagicMock()
        mock_job = MagicMock()
        mock_job.job_id = "fr027a-job-abc"
        mock_pool.enqueue_job = AsyncMock(return_value=mock_job)
        mock_pool.aclose = AsyncMock()

        with patch("arq.create_pool", AsyncMock(return_value=mock_pool)):
            resp = await client.post(
                f"/api/v1/studies/{study_id}/search-strings/{ss_id}/test",
                json={"databases": ["acm"]},
                headers=_bearer(user.id),
            )

        assert resp.status_code == 202
        body = resp.json()
        assert body.get("job_id") == "fr027a-job-abc", (
            f"FR-027a: job_id must be returned in 202 response body, got {body}"
        )


class TestIterationApprovalPatch:
    """PATCH /studies/{study_id}/search-strings/{id}/iterations/{iter_id}."""

    @pytest.mark.asyncio
    async def test_approve_sets_human_approved_true(self, client, alice, db_engine):
        """PATCH with human_approved=true sets iteration.human_approved to True."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        ss_id, iter_id = await _insert_search_string(db_engine, study_id)

        resp = await client.patch(
            f"/api/v1/studies/{study_id}/search-strings/{ss_id}/iterations/{iter_id}",
            json={"human_approved": True},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["human_approved"] is True

    @pytest.mark.asyncio
    async def test_approve_sets_search_string_is_active(self, client, alice, db_engine):
        """Approving an iteration (human_approved=true) sets SearchString.is_active=true."""
        from sqlalchemy import select

        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        ss_id, iter_id = await _insert_search_string(db_engine, study_id)

        await client.patch(
            f"/api/v1/studies/{study_id}/search-strings/{ss_id}/iterations/{iter_id}",
            json={"human_approved": True},
            headers=_bearer(user.id),
        )

        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            result = await session.execute(
                select(SearchString).where(SearchString.id == ss_id)
            )
            ss = result.scalar_one()
        assert ss.is_active is True

    @pytest.mark.asyncio
    async def test_reject_does_not_set_is_active(self, client, alice, db_engine):
        """Rejecting an iteration (human_approved=false) does not set SearchString.is_active."""
        from sqlalchemy import select

        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        ss_id, iter_id = await _insert_search_string(db_engine, study_id)

        await client.patch(
            f"/api/v1/studies/{study_id}/search-strings/{ss_id}/iterations/{iter_id}",
            json={"human_approved": False},
            headers=_bearer(user.id),
        )

        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            result = await session.execute(
                select(SearchString).where(SearchString.id == ss_id)
            )
            ss = result.scalar_one()
        assert ss.is_active is False

    @pytest.mark.asyncio
    async def test_patch_returns_404_for_missing_iteration(self, client, alice, db_engine):
        """PATCH with non-existent iteration_id returns 404."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        ss_id, _ = await _insert_search_string(db_engine, study_id)

        resp = await client.patch(
            f"/api/v1/studies/{study_id}/search-strings/{ss_id}/iterations/99999",
            json={"human_approved": True},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_patch_returns_404_for_iteration_wrong_study(self, client, alice, db_engine):
        """PATCH returns 404 if the search string does not belong to the given study."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        ss_id, iter_id = await _insert_search_string(db_engine, study_id)

        resp = await client.patch(
            f"/api/v1/studies/99999/search-strings/{ss_id}/iterations/{iter_id}",
            json={"human_approved": True},
            headers=_bearer(user.id),
        )
        assert resp.status_code in (403, 404)
