"""Integration tests for SLR protocol routes (feature 007, T029).

Covers:
- GET /slr/studies/{id}/protocol → 404 when no protocol exists.
- PUT /slr/studies/{id}/protocol → 200 creates protocol.
- PUT /slr/studies/{id}/protocol → 200 updates existing protocol.
- PUT /slr/studies/{id}/protocol → 409 when protocol is validated.
- POST /slr/studies/{id}/protocol/submit-for-review → 202 enqueues job.
- POST /slr/studies/{id}/protocol/submit-for-review → 422 on incomplete protocol.
- POST /slr/studies/{id}/protocol/validate → 200 sets validated status.
- POST /slr/studies/{id}/protocol/validate → 422 when no review_report.
- GET /slr/studies/{id}/phases → 200 with correct unlocked phases.
- Phase gate blocks phase 2 until protocol is validated.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.slr import ReviewProtocol, ReviewProtocolStatus
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Return Bearer token header for the given user id."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study(client, db_engine, user) -> int:
    """Create a research group, study, return study id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=f"SLR Group {user.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "SLR Protocol Test",
            "topic": "TDD",
            "study_type": "SLR",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


_COMPLETE_PROTOCOL = {
    "background": "Background of TDD review",
    "rationale": "No prior meta-analysis exists",
    "research_questions": ["RQ1: What is the effect of TDD on defect density?"],
    "pico_population": "Software development teams",
    "pico_intervention": "TDD",
    "pico_comparison": "Traditional development",
    "pico_outcome": "Defect density",
    "search_strategy": "(TDD OR 'test-driven') AND (quality OR defect)",
    "inclusion_criteria": ["Empirical studies"],
    "exclusion_criteria": ["Grey literature"],
    "data_extraction_strategy": "Extract effect sizes",
    "synthesis_approach": "meta_analysis",
    "dissemination_strategy": "Journal publication",
    "timetable": "Q1-Q4 2026",
}


class TestGetProtocol:
    """GET /slr/studies/{id}/protocol."""

    @pytest.mark.asyncio
    async def test_returns_404_when_no_protocol(self, client, alice, db_engine) -> None:
        """Returns 404 when no protocol has been created yet."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/protocol",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_protocol_after_creation(self, client, alice, db_engine) -> None:
        """Returns 200 with protocol after PUT creates it."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        await client.put(
            f"/api/v1/slr/studies/{study_id}/protocol",
            json={"background": "Test background"},
            headers=_bearer(user.id),
        )

        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/protocol",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["background"] == "Test background"
        assert resp.json()["study_id"] == study_id


class TestUpsertProtocol:
    """PUT /slr/studies/{id}/protocol."""

    @pytest.mark.asyncio
    async def test_creates_protocol(self, client, alice, db_engine) -> None:
        """PUT creates a new draft protocol."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.put(
            f"/api/v1/slr/studies/{study_id}/protocol",
            json={"background": "Initial background"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["background"] == "Initial background"
        assert body["status"] == "draft"

    @pytest.mark.asyncio
    async def test_updates_protocol(self, client, alice, db_engine) -> None:
        """PUT updates an existing draft protocol."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await client.put(
            f"/api/v1/slr/studies/{study_id}/protocol",
            json={"background": "Old background"},
            headers=_bearer(user.id),
        )
        resp = await client.put(
            f"/api/v1/slr/studies/{study_id}/protocol",
            json={"background": "New background"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["background"] == "New background"

    @pytest.mark.asyncio
    async def test_returns_409_on_validated_protocol(self, client, alice, db_engine) -> None:
        """PUT returns 409 when protocol is already validated."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        # Directly insert a validated protocol
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            protocol = ReviewProtocol(
                study_id=study_id,
                status=ReviewProtocolStatus.VALIDATED,
                review_report={"issues": [], "overall_assessment": "OK"},
            )
            session.add(protocol)
            await session.commit()

        resp = await client.put(
            f"/api/v1/slr/studies/{study_id}/protocol",
            json={"background": "Attempted edit"},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 409


class TestSubmitForReview:
    """POST /slr/studies/{id}/protocol/submit-for-review."""

    @pytest.mark.asyncio
    async def test_returns_202_and_enqueues_job(self, client, alice, db_engine) -> None:
        """Returns 202 and enqueues ARQ job when protocol is complete."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await client.put(
            f"/api/v1/slr/studies/{study_id}/protocol",
            json=_COMPLETE_PROTOCOL,
            headers=_bearer(user.id),
        )

        mock_job = MagicMock()
        mock_job.job_id = "test-job-id"
        mock_pool = MagicMock()
        mock_pool.enqueue_job = AsyncMock(return_value=mock_job)
        mock_pool.close = AsyncMock()

        with patch("arq.connections.create_pool", new_callable=AsyncMock, return_value=mock_pool):
            resp = await client.post(
                f"/api/v1/slr/studies/{study_id}/protocol/submit-for-review",
                headers=_bearer(user.id),
            )

        assert resp.status_code == 202
        body = resp.json()
        assert body["status"] == "under_review"
        assert "job_id" in body

    @pytest.mark.asyncio
    async def test_returns_422_on_incomplete_protocol(self, client, alice, db_engine) -> None:
        """Returns 422 when required fields are missing."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        # Only set background, missing all other required fields
        await client.put(
            f"/api/v1/slr/studies/{study_id}/protocol",
            json={"background": "Only background"},
            headers=_bearer(user.id),
        )

        mock_pool = MagicMock()
        mock_pool.close = AsyncMock()
        with patch("arq.connections.create_pool", new_callable=AsyncMock, return_value=mock_pool):
            resp = await client.post(
                f"/api/v1/slr/studies/{study_id}/protocol/submit-for-review",
                headers=_bearer(user.id),
            )

        assert resp.status_code == 422


class TestValidateProtocol:
    """POST /slr/studies/{id}/protocol/validate."""

    @pytest.mark.asyncio
    async def test_validates_protocol(self, client, alice, db_engine) -> None:
        """Returns 200 with status=validated when review_report exists."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        # Insert protocol with review_report set
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            protocol = ReviewProtocol(
                study_id=study_id,
                status=ReviewProtocolStatus.DRAFT,
                review_report={"issues": [], "overall_assessment": "Good protocol."},
            )
            session.add(protocol)
            await session.commit()

        resp = await client.post(
            f"/api/v1/slr/studies/{study_id}/protocol/validate",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "validated"

    @pytest.mark.asyncio
    async def test_returns_422_when_no_review_report(self, client, alice, db_engine) -> None:
        """Returns 422 when protocol has no review_report yet."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await client.put(
            f"/api/v1/slr/studies/{study_id}/protocol",
            json={"background": "Background"},
            headers=_bearer(user.id),
        )

        resp = await client.post(
            f"/api/v1/slr/studies/{study_id}/protocol/validate",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422


class TestGetPhases:
    """GET /slr/studies/{id}/phases."""

    @pytest.mark.asyncio
    async def test_phase_1_always_unlocked(self, client, alice, db_engine) -> None:
        """Phase 1 is always in unlocked_phases."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/phases",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert 1 in resp.json()["unlocked_phases"]

    @pytest.mark.asyncio
    async def test_phase_2_blocked_without_validated_protocol(
        self, client, alice, db_engine
    ) -> None:
        """Phase 2 is not unlocked when no validated protocol exists."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/phases",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert 2 not in resp.json()["unlocked_phases"]

    @pytest.mark.asyncio
    async def test_phase_2_unlocked_after_protocol_validated(
        self, client, alice, db_engine
    ) -> None:
        """Phase 2 is unlocked once the protocol is validated."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            protocol = ReviewProtocol(
                study_id=study_id,
                status=ReviewProtocolStatus.VALIDATED,
                review_report={"issues": [], "overall_assessment": "Good."},
            )
            session.add(protocol)
            await session.commit()

        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/phases",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert 2 in resp.json()["unlocked_phases"]
        assert resp.json()["protocol_status"] == "validated"

    @pytest.mark.asyncio
    async def test_protocol_status_none_when_no_protocol(
        self, client, alice, db_engine
    ) -> None:
        """protocol_status is None when no protocol exists."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        resp = await client.get(
            f"/api/v1/slr/studies/{study_id}/phases",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["protocol_status"] is None
