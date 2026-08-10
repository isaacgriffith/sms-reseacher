"""Integration tests for /api/v1/studies/{study_id}/validity endpoints (T155).

Covers:
- GET /validity → returns six fields (may be null initially)
- PUT /validity → stores six validity fields, partial update supported
- POST /validity/generate → 202 Accepted, BackgroundJob created
- 401 when unauthenticated
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
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
        group = ResearchGroup(name="Validity Lab")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Validity Study",
            "topic": "Testing validity discussion",
            "study_type": "SMS",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


_ALL_DIMS = [
    "descriptive",
    "theoretical",
    "generalizability_internal",
    "generalizability_external",
    "interpretive",
    "repeatability",
]


@pytest.mark.asyncio
async def test_get_validity_empty(client, alice, db_engine) -> None:
    """GET /validity returns all six fields (null initially)."""
    user, _ = alice
    study_id = await _setup_study(client, db_engine, user)

    resp = await client.get(
        f"/api/v1/studies/{study_id}/validity",
        headers=_bearer(user.id),
    )

    assert resp.status_code == 200
    body = resp.json()
    for dim in _ALL_DIMS:
        assert dim in body


@pytest.mark.asyncio
async def test_put_validity_stores_six_fields(client, alice, db_engine) -> None:
    """PUT /validity stores all six dimensions and returns them."""
    user, _ = alice
    study_id = await _setup_study(client, db_engine, user)

    payload = {
        "descriptive": "Data extracted by two reviewers.",
        "theoretical": "Grounded in established frameworks.",
        "generalizability_internal": "All papers treated consistently.",
        "generalizability_external": "Four major databases searched.",
        "interpretive": "Validated by inter-rater agreement.",
        "repeatability": "Search strings and protocol documented.",
    }

    resp = await client.put(
        f"/api/v1/studies/{study_id}/validity",
        json=payload,
        headers=_bearer(user.id),
    )

    assert resp.status_code == 200
    body = resp.json()
    for dim, expected in payload.items():
        assert body[dim] == expected


@pytest.mark.asyncio
async def test_put_validity_partial_update(client, alice, db_engine) -> None:
    """PUT /validity with partial body only updates supplied fields."""
    user, _ = alice
    study_id = await _setup_study(client, db_engine, user)

    # Set all fields first
    await client.put(
        f"/api/v1/studies/{study_id}/validity",
        json={
            "descriptive": "Original descriptive text.",
            "theoretical": "Original theoretical text.",
            "generalizability_internal": "Original internal text.",
            "generalizability_external": "Original external text.",
            "interpretive": "Original interpretive text.",
            "repeatability": "Original repeatability text.",
        },
        headers=_bearer(user.id),
    )

    # Partial update — only descriptive
    resp = await client.put(
        f"/api/v1/studies/{study_id}/validity",
        json={"descriptive": "Updated descriptive text."},
        headers=_bearer(user.id),
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["descriptive"] == "Updated descriptive text."
    assert body["theoretical"] == "Original theoretical text."


@pytest.mark.asyncio
async def test_put_validity_then_get_returns_stored(client, alice, db_engine) -> None:
    """GET /validity after a PUT returns the stored values."""
    user, _ = alice
    study_id = await _setup_study(client, db_engine, user)

    payload = {"repeatability": "Protocol documented for repeatability."}
    await client.put(
        f"/api/v1/studies/{study_id}/validity",
        json=payload,
        headers=_bearer(user.id),
    )

    resp = await client.get(
        f"/api/v1/studies/{study_id}/validity",
        headers=_bearer(user.id),
    )

    assert resp.status_code == 200
    assert resp.json()["repeatability"] == "Protocol documented for repeatability."


@pytest.mark.asyncio
async def test_post_validity_generate_202(client, alice, db_engine) -> None:
    """POST /validity/generate returns 202 Accepted and a job_id."""
    user, _ = alice
    study_id = await _setup_study(client, db_engine, user)

    with patch("arq.connections.create_pool") as mock_pool:
        mock_redis = AsyncMock()
        mock_redis.enqueue_job.return_value = AsyncMock(job_id="vp-job-001")
        mock_redis.close = AsyncMock()
        mock_pool.return_value = mock_redis

        resp = await client.post(
            f"/api/v1/studies/{study_id}/validity/generate",
            headers=_bearer(user.id),
        )

    assert resp.status_code == 202
    body = resp.json()
    assert "job_id" in body
    assert body["study_id"] == study_id


@pytest.mark.asyncio
async def test_validity_401_unauthenticated(client, alice, db_engine) -> None:
    """GET /validity returns 401 when no token is provided."""
    user, _ = alice
    study_id = await _setup_study(client, db_engine, user)

    resp = await client.get(f"/api/v1/studies/{study_id}/validity")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Threats to validity (TFIX11)
# ---------------------------------------------------------------------------


async def _add_human_reviewers(db_engine, study_id: int, count: int) -> None:
    """Attach *count* human reviewer rows to *study_id*."""
    from db.models.study import Reviewer, ReviewerType

    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        for _ in range(count):
            session.add(Reviewer(study_id=study_id, reviewer_type=ReviewerType.HUMAN))
        await session.commit()


class TestValidityThreats:
    """The single-reviewer disclosure, end to end through the API."""

    @pytest.mark.asyncio
    async def test_lone_reviewer_sees_three_threats(self, client, alice, db_engine) -> None:
        """GET derives on read, so the disclosure needs no explicit trigger."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_human_reviewers(db_engine, study_id, 1)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/validity/threats", headers=_bearer(user.id)
        )

        assert resp.status_code == 200
        threats = resp.json()["threats"]
        assert {t["threat_id"] for t in threats} == {"tv7", "tv13_4", "tv16"}

    @pytest.mark.asyncio
    async def test_threats_carry_their_reporting_category(self, client, alice, db_engine) -> None:
        """Each threat names the Petersen & Gencel heading it reports under."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_human_reviewers(db_engine, study_id, 1)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/validity/threats", headers=_bearer(user.id)
        )

        by_id = {t["threat_id"]: t for t in resp.json()["threats"]}
        assert by_id["tv7"]["validity_category"] == "theoretical"
        assert by_id["tv13_4"]["validity_category"] == "descriptive"
        assert by_id["tv16"]["validity_category"] == "interpretive"

    @pytest.mark.asyncio
    async def test_threats_start_unaddressed(self, client, alice, db_engine) -> None:
        """Nothing is pre-filled — step 4 is the researcher's to complete."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_human_reviewers(db_engine, study_id, 1)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/validity/threats", headers=_bearer(user.id)
        )

        assert all(t["is_addressed"] is False for t in resp.json()["threats"])

    @pytest.mark.asyncio
    async def test_two_reviewers_see_no_threats(self, client, alice, db_engine) -> None:
        """The disclosure is derived, so it disappears when it stops applying."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_human_reviewers(db_engine, study_id, 2)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/validity/threats", headers=_bearer(user.id)
        )

        assert resp.json()["threats"] == []

    @pytest.mark.asyncio
    async def test_repeated_gets_do_not_duplicate(self, client, alice, db_engine) -> None:
        """Derivation on read must be idempotent or every refresh adds rows."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_human_reviewers(db_engine, study_id, 1)

        for _ in range(3):
            resp = await client.get(
                f"/api/v1/studies/{study_id}/validity/threats", headers=_bearer(user.id)
            )

        assert len(resp.json()["threats"]) == 3

    @pytest.mark.asyncio
    async def test_acknowledging_marks_it_addressed(self, client, alice, db_engine) -> None:
        """Acknowledgement is a first-class step-4 outcome, not a lesser one."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_human_reviewers(db_engine, study_id, 1)
        await client.get(f"/api/v1/studies/{study_id}/validity/threats", headers=_bearer(user.id))

        resp = await client.patch(
            f"/api/v1/studies/{study_id}/validity/threats/tv7",
            json={"acknowledgement": "Sole author; the bias is accepted and reported."},
            headers=_bearer(user.id),
        )

        assert resp.status_code == 200
        assert resp.json()["is_addressed"] is True

    @pytest.mark.asyncio
    async def test_mitigating_marks_it_addressed(self, client, alice, db_engine) -> None:
        """Supervisor cross-check is the mitigation the corpus names."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_human_reviewers(db_engine, study_id, 1)
        await client.get(f"/api/v1/studies/{study_id}/validity/threats", headers=_bearer(user.id))

        resp = await client.patch(
            f"/api/v1/studies/{study_id}/validity/threats/tv13_4",
            json={"mitigation": "Supervisor cross-checked a random sample of 30 extractions."},
            headers=_bearer(user.id),
        )

        assert resp.status_code == 200
        assert resp.json()["is_addressed"] is True

    @pytest.mark.asyncio
    async def test_patching_an_underived_threat_404s(self, client, alice, db_engine) -> None:
        """A threat that does not apply cannot be addressed."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)
        await _add_human_reviewers(db_engine, study_id, 2)

        resp = await client.patch(
            f"/api/v1/studies/{study_id}/validity/threats/tv7",
            json={"acknowledgement": "Accepted"},
            headers=_bearer(user.id),
        )

        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_unknown_threat_id_422s(self, client, alice, db_engine) -> None:
        """The path parameter is validated against the catalogue enum."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.patch(
            f"/api/v1/studies/{study_id}/validity/threats/tv99",
            json={"acknowledgement": "Accepted"},
            headers=_bearer(user.id),
        )

        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_threats_401_unauthenticated(self, client, alice, db_engine) -> None:
        """Threat disclosure is study data, not public."""
        user, _ = alice
        study_id = await _setup_study(client, db_engine, user)

        resp = await client.get(f"/api/v1/studies/{study_id}/validity/threats")

        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_non_member_forbidden(self, client, alice, bob, db_engine) -> None:
        """Membership is required, matching the other validity endpoints."""
        owner, _ = alice
        outsider, _ = bob
        study_id = await _setup_study(client, db_engine, owner)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/validity/threats", headers=_bearer(outsider.id)
        )

        assert resp.status_code == 403
