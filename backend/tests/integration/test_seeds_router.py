"""Integration tests for the /api/v1/seeds router.

Covers seed paper CRUD, seed author CRUD, POST /seeds/expert 202 response,
and SeedPaper insertion.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create a group and study, returning the study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Seeds Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Seeds Study",
            "topic": "TDD",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    return resp.json()["id"]


class TestSeedPapers:
    """GET / POST / DELETE /studies/{study_id}/seeds/papers."""

    @pytest.mark.asyncio
    async def test_list_returns_empty_initially(self, client, alice, db_engine):
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/seeds/papers", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_add_by_title(self, client, alice, db_engine):
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.post(
            f"/api/v1/studies/{study_id}/seeds/papers",
            json={"title": "A Great Paper"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["paper"]["title"] == "A Great Paper"
        assert body["added_by"] == "user"

    @pytest.mark.asyncio
    async def test_add_by_doi_creates_paper(self, client, alice, db_engine):
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.post(
            f"/api/v1/studies/{study_id}/seeds/papers",
            json={"doi": "10.1145/test.doi"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        assert resp.json()["paper"]["doi"] == "10.1145/test.doi"

    @pytest.mark.asyncio
    async def test_add_without_id_doi_title_returns_422(self, client, alice, db_engine):
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.post(
            f"/api/v1/studies/{study_id}/seeds/papers",
            json={},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_delete_removes_seed(self, client, alice, db_engine):
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        add_resp = await client.post(
            f"/api/v1/studies/{study_id}/seeds/papers",
            json={"title": "To be deleted"},
            headers=_bearer(user.id),
        )
        seed_id = add_resp.json()["id"]
        del_resp = await client.delete(
            f"/api/v1/studies/{study_id}/seeds/papers/{seed_id}",
            headers=_bearer(user.id),
        )
        assert del_resp.status_code == 204
        # Verify it's gone
        list_resp = await client.get(
            f"/api/v1/studies/{study_id}/seeds/papers", headers=_bearer(user.id)
        )
        assert list_resp.json() == []

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client, alice, db_engine):
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(f"/api/v1/studies/{study_id}/seeds/papers")
        assert resp.status_code == 401


class TestSeedAuthors:
    """GET / POST /studies/{study_id}/seeds/authors."""

    @pytest.mark.asyncio
    async def test_list_authors_empty_initially(self, client, alice, db_engine):
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/studies/{study_id}/seeds/authors", headers=_bearer(user.id)
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_add_author(self, client, alice, db_engine):
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.post(
            f"/api/v1/studies/{study_id}/seeds/authors",
            json={"author_name": "Alice Smith", "institution": "MIT"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["author_name"] == "Alice Smith"
        assert body["institution"] == "MIT"


class TestExpertSeedEndpoint:
    """POST /studies/{study_id}/seeds/expert — expert agent trigger."""

    @pytest.mark.asyncio
    async def test_returns_202_with_job_id(self, client, alice, db_engine):
        """POST /seeds/expert returns 202 with a job_id field."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.post(
            f"/api/v1/studies/{study_id}/seeds/expert",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 202
        body = resp.json()
        assert "job_id" in body
        assert isinstance(body["job_id"], str)
        assert len(body["job_id"]) > 0

    @pytest.mark.asyncio
    async def test_creates_background_job_record(self, client, alice, db_engine):
        """POST /seeds/expert creates a BackgroundJob in the DB."""
        from sqlalchemy import select

        from db.models.jobs import BackgroundJob

        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.post(
            f"/api/v1/studies/{study_id}/seeds/expert",
            headers=_bearer(user.id),
        )
        job_id = resp.json()["job_id"]

        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            result = await session.execute(
                select(BackgroundJob).where(BackgroundJob.id == job_id)
            )
            job = result.scalar_one_or_none()
        assert job is not None
        assert job.study_id == study_id
        assert job.job_type.value == "expert_seed"

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client, alice, db_engine):
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.post(f"/api/v1/studies/{study_id}/seeds/expert")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_study_returns_404(self, client, alice):
        user, _ = alice
        resp = await client.post(
            "/api/v1/studies/99999/seeds/expert",
            headers=_bearer(user.id),
        )
        assert resp.status_code in (404, 403)
