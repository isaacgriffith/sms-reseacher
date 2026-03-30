"""Integration tests for Tertiary Study protocol routes (feature 009, T044).

Covers:
- GET /tertiary/studies/{id}/protocol → 200 auto-creates draft when none exists.
- PUT /tertiary/studies/{id}/protocol → 200 updates fields.
- PUT /tertiary/studies/{id}/protocol → 200 increments version_id on update.
- PUT /tertiary/studies/{id}/protocol → 409 when stale version_id is provided.
- POST /tertiary/studies/{id}/protocol/validate → 202 transitions status to validated.
- POST /tertiary/studies/{id}/protocol/validate → 409 when already validated.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Return a Bearer token Authorization header.

    Args:
        user_id: User id for the token subject.

    Returns:
        Dict suitable for use as ``headers`` in httpx requests.
    """
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_tertiary_study(client, db_engine, user) -> int:
    """Create a ResearchGroup and Tertiary Study, return the study id.

    Args:
        client: The httpx AsyncClient.
        db_engine: The per-test async engine.
        user: The acting user.

    Returns:
        Integer study id.
    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=f"Tertiary Group {user.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Tertiary Protocol Integration Test",
            "topic": "Tertiary review",
            "study_type": "Tertiary",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# Tests: GET protocol
# ---------------------------------------------------------------------------


class TestGetProtocol:
    """GET /tertiary/studies/{id}/protocol."""

    @pytest.mark.asyncio
    async def test_auto_creates_draft_on_first_get(self, client, alice, db_engine) -> None:
        """GET auto-creates a draft protocol when none exists."""
        user, _ = alice
        study_id = await _setup_tertiary_study(client, db_engine, user)

        resp = await client.get(
            f"/api/v1/tertiary/studies/{study_id}/protocol",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["study_id"] == study_id
        assert body["status"] == "draft"

    @pytest.mark.asyncio
    async def test_get_returns_same_protocol_on_repeat(self, client, alice, db_engine) -> None:
        """Calling GET twice returns the same protocol id."""
        user, _ = alice
        study_id = await _setup_tertiary_study(client, db_engine, user)

        first = await client.get(
            f"/api/v1/tertiary/studies/{study_id}/protocol",
            headers=_bearer(user.id),
        )
        second = await client.get(
            f"/api/v1/tertiary/studies/{study_id}/protocol",
            headers=_bearer(user.id),
        )
        assert first.json()["id"] == second.json()["id"]

    @pytest.mark.asyncio
    async def test_get_returns_error_for_nonexistent_study(self, client, alice, db_engine) -> None:
        """GET returns 4xx for a study that does not exist (membership check first)."""
        user, _ = alice
        resp = await client.get(
            "/api/v1/tertiary/studies/99999/protocol",
            headers=_bearer(user.id),
        )
        # The membership guard fires before the study-type guard, returning 403.
        assert resp.status_code in (403, 404)


# ---------------------------------------------------------------------------
# Tests: PUT protocol
# ---------------------------------------------------------------------------


class TestUpdateProtocol:
    """PUT /tertiary/studies/{id}/protocol."""

    @pytest.mark.asyncio
    async def test_put_updates_background(self, client, alice, db_engine) -> None:
        """PUT updates the background field of the protocol."""
        user, _ = alice
        study_id = await _setup_tertiary_study(client, db_engine, user)

        resp = await client.put(
            f"/api/v1/tertiary/studies/{study_id}/protocol",
            json={"background": "This is the background."},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["background"] == "This is the background."

    @pytest.mark.asyncio
    async def test_put_increments_version_id(self, client, alice, db_engine) -> None:
        """PUT increments the version_id each time."""
        user, _ = alice
        study_id = await _setup_tertiary_study(client, db_engine, user)

        r1 = await client.put(
            f"/api/v1/tertiary/studies/{study_id}/protocol",
            json={"background": "v1"},
            headers=_bearer(user.id),
        )
        v1 = r1.json()["version_id"]

        r2 = await client.put(
            f"/api/v1/tertiary/studies/{study_id}/protocol",
            json={"background": "v2"},
            headers=_bearer(user.id),
        )
        v2 = r2.json()["version_id"]

        assert v2 > v1

    @pytest.mark.asyncio
    async def test_put_returns_409_with_stale_version_id(self, client, alice, db_engine) -> None:
        """PUT returns 409 when the client's version_id is stale."""
        user, _ = alice
        study_id = await _setup_tertiary_study(client, db_engine, user)

        # First update to advance version.
        r1 = await client.put(
            f"/api/v1/tertiary/studies/{study_id}/protocol",
            json={"background": "first"},
            headers=_bearer(user.id),
        )
        v1 = r1.json()["version_id"]

        # Second update advances version again.
        await client.put(
            f"/api/v1/tertiary/studies/{study_id}/protocol",
            json={"background": "second"},
            headers=_bearer(user.id),
        )

        # Third update with stale v1 should 409.
        r3 = await client.put(
            f"/api/v1/tertiary/studies/{study_id}/protocol",
            json={"background": "stale", "version_id": v1},
            headers=_bearer(user.id),
        )
        assert r3.status_code == 409


# ---------------------------------------------------------------------------
# Tests: POST validate
# ---------------------------------------------------------------------------


class TestValidateProtocol:
    """POST /tertiary/studies/{id}/protocol/validate."""

    @pytest.mark.asyncio
    async def test_validate_transitions_to_validated(self, client, alice, db_engine) -> None:
        """POST validate transitions status from draft to validated."""
        user, _ = alice
        study_id = await _setup_tertiary_study(client, db_engine, user)

        # Ensure a draft protocol exists.
        await client.get(
            f"/api/v1/tertiary/studies/{study_id}/protocol",
            headers=_bearer(user.id),
        )

        mock_job = MagicMock()
        mock_job.job_id = "tertiary-job-123"
        mock_pool = MagicMock()
        mock_pool.enqueue_job = AsyncMock(return_value=mock_job)
        mock_pool.close = AsyncMock()

        with patch("arq.connections.create_pool", new_callable=AsyncMock, return_value=mock_pool):
            resp = await client.post(
                f"/api/v1/tertiary/studies/{study_id}/protocol/validate",
                headers=_bearer(user.id),
            )

        assert resp.status_code == 202
        body = resp.json()
        assert body["status"] == "queued"
        assert "job_id" in body

        # Verify status was actually set.
        get_resp = await client.get(
            f"/api/v1/tertiary/studies/{study_id}/protocol",
            headers=_bearer(user.id),
        )
        assert get_resp.json()["status"] == "validated"

    @pytest.mark.asyncio
    async def test_validate_returns_409_when_already_validated(
        self, client, alice, db_engine
    ) -> None:
        """POST validate returns 409 when protocol is already validated."""
        user, _ = alice
        study_id = await _setup_tertiary_study(client, db_engine, user)

        # Trigger first validation.
        await client.get(
            f"/api/v1/tertiary/studies/{study_id}/protocol",
            headers=_bearer(user.id),
        )
        mock_job = MagicMock()
        mock_job.job_id = "job-1"
        mock_pool = MagicMock()
        mock_pool.enqueue_job = AsyncMock(return_value=mock_job)
        mock_pool.close = AsyncMock()

        with patch("arq.connections.create_pool", new_callable=AsyncMock, return_value=mock_pool):
            await client.post(
                f"/api/v1/tertiary/studies/{study_id}/protocol/validate",
                headers=_bearer(user.id),
            )

        # Second validation should fail.
        mock_pool2 = MagicMock()
        mock_pool2.close = AsyncMock()
        with patch("arq.connections.create_pool", new_callable=AsyncMock, return_value=mock_pool2):
            resp = await client.post(
                f"/api/v1/tertiary/studies/{study_id}/protocol/validate",
                headers=_bearer(user.id),
            )
        assert resp.status_code == 409
