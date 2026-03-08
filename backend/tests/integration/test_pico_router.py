"""Integration tests for the /api/v1/pico router.

Covers GET /pico, PUT /pico, and 404 error paths.
"""

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
        group = ResearchGroup(name="PICO Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "PICO Study",
            "topic": "TDD",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    return resp.json()["id"]


_PICO_PAYLOAD = {
    "variant": "PICO",
    "population": "Software engineers",
    "intervention": "TDD",
    "comparison": "No TDD",
    "outcome": "Code quality",
}


class TestGetPico:
    """GET /studies/{study_id}/pico — retrieve current PICO record."""

    @pytest.mark.asyncio
    async def test_returns_404_when_no_pico(self, client, alice, db_engine):
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(f"/api/v1/studies/{study_id}/pico", headers=_bearer(user.id))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client):
        resp = await client.get("/api/v1/studies/1/pico")
        assert resp.status_code == 401


class TestUpsertPico:
    """PUT /studies/{study_id}/pico — create or replace PICO."""

    @pytest.mark.asyncio
    async def test_creates_pico_record(self, client, alice, db_engine):
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.put(
            f"/api/v1/studies/{study_id}/pico",
            json=_PICO_PAYLOAD,
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["variant"] == "PICO"
        assert body["population"] == "Software engineers"
        assert body["study_id"] == study_id

    @pytest.mark.asyncio
    async def test_subsequent_put_updates_record(self, client, alice, db_engine):
        """Second PUT replaces the PICO record."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await client.put(
            f"/api/v1/studies/{study_id}/pico",
            json=_PICO_PAYLOAD,
            headers=_bearer(user.id),
        )
        resp = await client.put(
            f"/api/v1/studies/{study_id}/pico",
            json={**_PICO_PAYLOAD, "population": "Updated population"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["population"] == "Updated population"

    @pytest.mark.asyncio
    async def test_invalid_variant_returns_422(self, client, alice, db_engine):
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.put(
            f"/api/v1/studies/{study_id}/pico",
            json={**_PICO_PAYLOAD, "variant": "BADVARIANT"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_pico_save_stamps_pico_saved_at(self, client, alice, db_engine):
        """Saving PICO sets pico_saved_at on the study (staleness tracking)."""
        from sqlalchemy import select

        from db.models import Study

        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await client.put(
            f"/api/v1/studies/{study_id}/pico",
            json=_PICO_PAYLOAD,
            headers=_bearer(user.id),
        )
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            result = await session.execute(select(Study).where(Study.id == study_id))
            study = result.scalar_one()
        assert study.pico_saved_at is not None

    @pytest.mark.asyncio
    async def test_pico_saved_unlocks_phase_2(self, client, alice, db_engine):
        """After saving PICO, GET /studies/{id} shows phase 2 unlocked."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await client.put(
            f"/api/v1/studies/{study_id}/pico",
            json=_PICO_PAYLOAD,
            headers=_bearer(user.id),
        )
        resp = await client.get(f"/api/v1/studies/{study_id}", headers=_bearer(user.id))
        assert 2 in resp.json()["unlocked_phases"]
