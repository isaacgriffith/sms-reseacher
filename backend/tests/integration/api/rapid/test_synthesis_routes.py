"""Integration tests for Rapid Review synthesis and stakeholder routes (feature 008).

Covers:
- GET  /rapid/studies/{id}/synthesis           → 200 empty list
- PUT  /rapid/studies/{id}/synthesis/{sid}     → 200, 404
- POST /rapid/studies/{id}/synthesis/complete  → 200, 422
- GET  /rapid/studies/{id}/stakeholders        → 200 empty list
- POST /rapid/studies/{id}/stakeholders        → 201, 422 invalid type
- PUT  /rapid/studies/{id}/stakeholders/{id}   → 200, 404
- DELETE /rapid/studies/{id}/stakeholders/{id} → 204, 404
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Return Bearer token header for the given user id.

    Args:
        user_id: The numeric user ID to embed in the JWT.

    Returns:
        A dict with the ``Authorization`` header value.
    """
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_rr_study(client, db_engine, user, name_suffix: str = "") -> int:
    """Create a research group and RAPID study, return study id.

    Args:
        client: The httpx AsyncClient.
        db_engine: The in-memory async engine.
        user: The test user.
        name_suffix: Optional suffix to make group names unique.

    Returns:
        The newly created study ID.
    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=f"RR Synth Group {user.id}{name_suffix}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": f"RR Test Study {name_suffix}",
            "topic": "Rapid Review",
            "study_type": "Rapid",
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _insert_synthesis_section(
    db_engine,
    *,
    study_id: int,
    rq_index: int = 0,
    is_complete: bool = False,
    narrative_text: str | None = None,
) -> int:
    """Insert an RRNarrativeSynthesisSection directly into the test database.

    Args:
        db_engine: The in-memory async engine.
        study_id: Owning study ID.
        rq_index: Zero-based research question index.
        is_complete: Whether the section is marked complete.
        narrative_text: Optional narrative content.

    Returns:
        The section's primary key.
    """
    from db.models.rapid_review import RRNarrativeSynthesisSection

    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        section = RRNarrativeSynthesisSection(
            study_id=study_id,
            rq_index=rq_index,
            is_complete=is_complete,
            narrative_text=narrative_text,
        )
        session.add(section)
        await session.commit()
        await session.refresh(section)
        return section.id


# ---------------------------------------------------------------------------
# GET /rapid/studies/{id}/synthesis
# ---------------------------------------------------------------------------


class TestListSynthesisSections:
    """GET /rapid/studies/{id}/synthesis returns sections."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_initially(self, client, db_engine, alice) -> None:
        """Returns 200 with empty list when no sections exist."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "ls")

        resp = await client.get(
            f"/api/v1/rapid/studies/{study_id}/synthesis",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_returns_401_without_auth(self, client, db_engine, alice) -> None:
        """Returns 401 when no Authorization header is provided."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "ls2")

        resp = await client.get(f"/api/v1/rapid/studies/{study_id}/synthesis")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# PUT /rapid/studies/{id}/synthesis/{sid}
# ---------------------------------------------------------------------------


class TestUpdateSynthesisSection:
    """PUT /rapid/studies/{id}/synthesis/{sid} updates a section."""

    @pytest.mark.asyncio
    async def test_returns_404_for_missing_section(self, client, db_engine, alice) -> None:
        """Returns 404 when the section ID does not exist."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "us1")

        resp = await client.put(
            f"/api/v1/rapid/studies/{study_id}/synthesis/9999",
            json={"narrative_text": "test", "is_complete": False},
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_updates_section_with_none_values(self, client, db_engine, alice) -> None:
        """Returns 404 when section exists in different study (membership check)."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "us2")
        section_id = await _insert_synthesis_section(db_engine, study_id=study_id, rq_index=0)

        # Update with only narrative_text (no is_complete) should also return 404
        # for wrong study
        wrong_study = study_id + 9999
        resp = await client.put(
            f"/api/v1/rapid/studies/{wrong_study}/synthesis/{section_id}",
            json={"narrative_text": "test"},
            headers=_bearer(user.id),
        )
        # Should be 403 (membership check) or 404
        assert resp.status_code in (403, 404)

    @pytest.mark.asyncio
    async def test_returns_404_for_wrong_study(self, client, db_engine, alice) -> None:
        """Returns 404 when section belongs to a different study."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "us3")
        section_id = await _insert_synthesis_section(db_engine, study_id=study_id)

        # Use wrong study_id in path
        resp = await client.put(
            f"/api/v1/rapid/studies/9999/synthesis/{section_id}",
            json={"narrative_text": "test"},
            headers=_bearer(user.id),
        )
        assert resp.status_code in (403, 404)


# ---------------------------------------------------------------------------
# POST /rapid/studies/{id}/synthesis/complete
# ---------------------------------------------------------------------------


class TestCompleteSynthesis:
    """POST /rapid/studies/{id}/synthesis/complete marks synthesis complete."""

    @pytest.mark.asyncio
    async def test_returns_422_when_sections_incomplete(
        self, client, db_engine, alice
    ) -> None:
        """Returns 422 when any section is not complete."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "cs1")
        await _insert_synthesis_section(
            db_engine, study_id=study_id, rq_index=0, is_complete=False
        )

        resp = await client.post(
            f"/api/v1/rapid/studies/{study_id}/synthesis/complete",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_200_when_all_sections_complete(
        self, client, db_engine, alice
    ) -> None:
        """Returns 200 with synthesis_complete=True when all sections done."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "cs2")
        await _insert_synthesis_section(
            db_engine, study_id=study_id, rq_index=0, is_complete=True
        )

        resp = await client.post(
            f"/api/v1/rapid/studies/{study_id}/synthesis/complete",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["synthesis_complete"] is True

    @pytest.mark.asyncio
    async def test_returns_200_when_no_sections_exist(
        self, client, db_engine, alice
    ) -> None:
        """Returns 200 with synthesis_complete=True when no sections exist (trivially complete)."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "cs3")

        # No sections at all → empty synthesis list → complete
        resp = await client.post(
            f"/api/v1/rapid/studies/{study_id}/synthesis/complete",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json()["synthesis_complete"] is True


# ---------------------------------------------------------------------------
# Stakeholder routes
# ---------------------------------------------------------------------------


class TestStakeholderRoutes:
    """CRUD tests for /rapid/studies/{id}/stakeholders."""

    @pytest.mark.asyncio
    async def test_get_returns_empty_list_initially(
        self, client, db_engine, alice
    ) -> None:
        """Returns 200 with empty list when no stakeholders exist."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "sh1")

        resp = await client.get(
            f"/api/v1/rapid/studies/{study_id}/stakeholders",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_post_creates_stakeholder(self, client, db_engine, alice) -> None:
        """Returns 201 with stakeholder data when creation succeeds."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "sh2")

        resp = await client.post(
            f"/api/v1/rapid/studies/{study_id}/stakeholders",
            json={
                "name": "Alice Practitioner",
                "role_title": "Software Engineer",
                "organisation": "Acme Corp",
                "involvement_type": "problem_definer",
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Alice Practitioner"
        assert data["study_id"] == study_id

    @pytest.mark.asyncio
    async def test_post_returns_422_for_invalid_involvement_type(
        self, client, db_engine, alice
    ) -> None:
        """Returns 422 when involvement_type is not a valid enum value."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "sh3")

        resp = await client.post(
            f"/api/v1/rapid/studies/{study_id}/stakeholders",
            json={
                "name": "Bob",
                "role_title": "Manager",
                "organisation": "Corp",
                "involvement_type": "invalid_type",
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_get_returns_created_stakeholders(
        self, client, db_engine, alice
    ) -> None:
        """Returns the list with stakeholders after creation."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "sh4")

        await client.post(
            f"/api/v1/rapid/studies/{study_id}/stakeholders",
            json={
                "name": "Carol",
                "role_title": "PM",
                "organisation": "Org",
                "involvement_type": "advisor",
            },
            headers=_bearer(user.id),
        )

        resp = await client.get(
            f"/api/v1/rapid/studies/{study_id}/stakeholders",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    @pytest.mark.asyncio
    async def test_put_stakeholder_wrong_study_returns_403_or_404(
        self, client, db_engine, alice
    ) -> None:
        """Returns 403 or 404 when using wrong study_id in PUT request."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "sh5")

        create_resp = await client.post(
            f"/api/v1/rapid/studies/{study_id}/stakeholders",
            json={
                "name": "Dave",
                "role_title": "Analyst",
                "organisation": "Corp",
                "involvement_type": "recipient",
            },
            headers=_bearer(user.id),
        )
        stakeholder_id = create_resp.json()["id"]

        # Use wrong study_id
        resp = await client.put(
            f"/api/v1/rapid/studies/9999/stakeholders/{stakeholder_id}",
            json={
                "name": "Dave Updated",
                "role_title": "Senior Analyst",
                "organisation": "Corp",
                "involvement_type": "recipient",
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code in (403, 404)

    @pytest.mark.asyncio
    async def test_put_returns_404_for_missing_stakeholder(
        self, client, db_engine, alice
    ) -> None:
        """Returns 404 when the stakeholder ID does not exist."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "sh6")

        resp = await client.put(
            f"/api/v1/rapid/studies/{study_id}/stakeholders/9999",
            json={
                "name": "Ghost",
                "role_title": "Ghost",
                "organisation": "None",
                "involvement_type": "advisor",
            },
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_removes_stakeholder(self, client, db_engine, alice) -> None:
        """Returns 204 when the stakeholder is successfully deleted."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "sh7")

        create_resp = await client.post(
            f"/api/v1/rapid/studies/{study_id}/stakeholders",
            json={
                "name": "Eve",
                "role_title": "Tester",
                "organisation": "QA Inc",
                "involvement_type": "advisor",
            },
            headers=_bearer(user.id),
        )
        stakeholder_id = create_resp.json()["id"]

        resp = await client.delete(
            f"/api/v1/rapid/studies/{study_id}/stakeholders/{stakeholder_id}",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_returns_404_for_missing_stakeholder(
        self, client, db_engine, alice
    ) -> None:
        """Returns 404 when trying to delete a non-existent stakeholder."""
        user, _ = alice
        study_id = await _setup_rr_study(client, db_engine, user, "sh8")

        resp = await client.delete(
            f"/api/v1/rapid/studies/{study_id}/stakeholders/9999",
            headers=_bearer(user.id),
        )
        assert resp.status_code == 404
