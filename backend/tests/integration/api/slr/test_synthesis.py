"""Integration tests for SLR synthesis routes (feature 007, T071).

Covers:
- GET /slr/studies/{id}/synthesis → 200 with empty list.
- POST /slr/studies/{id}/synthesis → 202 with PENDING status.
- GET /slr/synthesis/{id} → 200 with the result.
- GET /slr/synthesis/9999 → 404.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

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
        group = ResearchGroup(name=f"Synthesis Group {user.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Synthesis SLR Test",
            "topic": "data synthesis",
            "study_type": "SLR",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _make_arq_pool() -> AsyncMock:
    """Return a minimal mock ARQ pool."""
    pool = AsyncMock()
    pool.enqueue_job = AsyncMock()
    pool.close = AsyncMock()
    return pool


class TestListSynthesisResults:
    """GET /slr/studies/{id}/synthesis."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_initially(self, client, db_engine, alice) -> None:
        """Returns 200 with empty results list when no records exist."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        with patch(
            "backend.api.v1.slr.synthesis.arq.connections.create_pool",
            return_value=_make_arq_pool(),
        ):
            resp = await client.get(
                f"/api/v1/slr/studies/{study_id}/synthesis",
                headers=_bearer(user.id),
            )

        assert resp.status_code == 200
        assert resp.json()["results"] == []


class TestStartSynthesis:
    """POST /slr/studies/{id}/synthesis."""

    @pytest.mark.asyncio
    async def test_returns_202_with_pending_status(self, client, db_engine, alice) -> None:
        """Returns 202 with a PENDING synthesis result."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        mock_pool = _make_arq_pool()

        with patch(
            "backend.api.v1.slr.synthesis.arq.connections.create_pool",
            return_value=mock_pool,
        ):
            resp = await client.post(
                f"/api/v1/slr/studies/{study_id}/synthesis",
                json={"approach": "qualitative", "parameters": {"themes": []}},
                headers=_bearer(user.id),
            )

        assert resp.status_code == 202, resp.text
        body = resp.json()
        assert body["status"] == "pending"
        assert body["study_id"] == study_id
        assert body["approach"] == "qualitative"

    @pytest.mark.asyncio
    async def test_enqueues_arq_job(self, client, db_engine, alice) -> None:
        """POST enqueues an ARQ run_synthesis job."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        mock_pool = _make_arq_pool()

        with patch(
            "backend.api.v1.slr.synthesis.arq.connections.create_pool",
            return_value=mock_pool,
        ):
            resp = await client.post(
                f"/api/v1/slr/studies/{study_id}/synthesis",
                json={"approach": "descriptive", "parameters": {"papers": []}},
                headers=_bearer(user.id),
            )

        assert resp.status_code == 202
        synthesis_id = resp.json()["id"]
        mock_pool.enqueue_job.assert_called_once_with(
            "run_synthesis", synthesis_id=synthesis_id
        )


class TestGetSynthesisResult:
    """GET /slr/synthesis/{id}."""

    @pytest.mark.asyncio
    async def test_returns_200_for_existing_result(self, client, db_engine, alice) -> None:
        """Returns 200 with the synthesis result."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        mock_pool = _make_arq_pool()

        with patch(
            "backend.api.v1.slr.synthesis.arq.connections.create_pool",
            return_value=mock_pool,
        ):
            create_resp = await client.post(
                f"/api/v1/slr/studies/{study_id}/synthesis",
                json={"approach": "qualitative", "parameters": {}},
                headers=_bearer(user.id),
            )
        assert create_resp.status_code == 202
        synthesis_id = create_resp.json()["id"]

        resp = await client.get(
            f"/api/v1/slr/synthesis/{synthesis_id}",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == synthesis_id

    @pytest.mark.asyncio
    async def test_returns_404_for_missing_id(self, client, db_engine, alice) -> None:
        """Returns 404 when synthesis_id does not exist."""
        user, _ = alice

        resp = await client.get(
            "/api/v1/slr/synthesis/9999",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404
