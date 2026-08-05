"""Integration tests for the study protocol assignment endpoint (feature 010, T038).

Covers:
- GET /studies/{study_id}/protocol-assignment returns 200 for a study member.
- GET /studies/{study_id}/protocol-assignment returns 403 for a non-member.
- GET /studies/{study_id}/protocol-assignment returns 404 when no assignment exists.
"""

from __future__ import annotations

import pytest
from db.models.protocols import (
    ProtocolNode,
    ProtocolTaskType,
    ResearchProtocol,
    StudyProtocolAssignment,
)
from db.models.users import GroupMembership, GroupRole, ResearchGroup
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token


def _bearer(user_id: int) -> dict[str, str]:
    """Return Bearer token header for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study_with_assignment(
    client, db_engine, user, study_type: str = "SMS"
) -> tuple[int, int]:
    """Create a group + study + default protocol assignment; return (study_id, protocol_id)."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=f"Group {user.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": f"Assignment Test Study {user.id}",
            "topic": "Test",
            "study_type": study_type,
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201, resp.text
    study_id = resp.json()["id"]

    # Insert a default protocol and manually assign it to the study
    async with maker() as session:
        protocol = ResearchProtocol(
            name=f"Default {study_type} Protocol",
            study_type=study_type,
            is_default_template=True,
        )
        session.add(protocol)
        await session.flush()
        assignment = StudyProtocolAssignment(
            study_id=study_id,
            protocol_id=protocol.id,
        )
        session.add(assignment)
        await session.commit()
        await session.refresh(protocol)
        return study_id, protocol.id


class TestGetStudyProtocolAssignment:
    """GET /studies/{study_id}/protocol-assignment endpoint tests."""

    @pytest.mark.asyncio
    async def test_returns_assignment_for_study_member(self, client, db_engine, alice) -> None:
        """GET /studies/{id}/protocol-assignment returns 200 for a study member."""
        alice_user, _ = alice
        study_id, protocol_id = await _setup_study_with_assignment(client, db_engine, alice_user)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/protocol-assignment",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["study_id"] == study_id
        assert data["protocol_id"] == protocol_id
        assert data["is_default_template"] is True

    @pytest.mark.asyncio
    async def test_403_for_non_member(self, client, db_engine, alice, bob) -> None:
        """GET /studies/{id}/protocol-assignment returns 403 for a non-member."""
        alice_user, _ = alice
        bob_user, _ = bob
        study_id, _ = await _setup_study_with_assignment(client, db_engine, alice_user)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/protocol-assignment",
            headers=_bearer(bob_user.id),
        )

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_404_when_no_assignment(self, client, db_engine, alice) -> None:
        """GET /studies/{id}/protocol-assignment returns 404 when no assignment exists.

        Study creation auto-assigns the default template for the study type, so
        this case only arises when no template has been seeded — which is true
        of the test database (built with ``create_all``, not the migrations
        that seed the four defaults).
        """
        alice_user, _ = alice

        # Create a study without an assignment
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            group = ResearchGroup(name=f"NoAssign Group {alice_user.id}")
            session.add(group)
            await session.flush()
            session.add(
                GroupMembership(group_id=group.id, user_id=alice_user.id, role=GroupRole.ADMIN)
            )
            await session.commit()
            group_id = group.id

        resp = await client.post(
            f"/api/v1/groups/{group_id}/studies",
            json={
                "name": "No Assignment Study",
                "topic": "Test",
                "study_type": "SMS",
                "research_objectives": [],
                "research_questions": [],
            },
            headers=_bearer(alice_user.id),
        )
        assert resp.status_code == 201, resp.text
        study_id = resp.json()["id"]

        resp = await client.get(
            f"/api/v1/studies/{study_id}/protocol-assignment",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 404


async def _seed_default_template(db_engine, study_type: str, node_count: int = 2) -> int:
    """Insert a default template for *study_type* with *node_count* nodes.

    Mirrors what migration ``0018_research_protocol_definition`` seeds, which the
    ``create_all``-built test database does not run.

    Args:
        db_engine: The test database engine fixture.
        study_type: Study type the template applies to, e.g. ``"SMS"``.
        node_count: How many task nodes to attach.

    Returns:
        The ``id`` of the inserted protocol.

    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        protocol = ResearchProtocol(
            name=f"Default {study_type} Protocol",
            study_type=study_type,
            is_default_template=True,
        )
        session.add(protocol)
        await session.flush()
        for i in range(node_count):
            session.add(
                ProtocolNode(
                    protocol_id=protocol.id,
                    task_id=f"task_{i}",
                    task_type=ProtocolTaskType.DEFINE_PICO,
                    label=f"Task {i}",
                )
            )
        await session.commit()
        return protocol.id


async def _create_group_and_study(client, db_engine, user, study_type: str) -> int:
    """Create a group the *user* administers plus a study of *study_type*.

    Args:
        client: The async HTTP test client.
        db_engine: The test database engine fixture.
        user: The user who creates and leads the study.
        study_type: Study type to create, e.g. ``"SLR"``.

    Returns:
        The ``id`` of the created study.

    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=f"AutoAssign Group {user.id} {study_type}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": f"AutoAssign {study_type} Study",
            "topic": "Test",
            "study_type": study_type,
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201, resp.text
    return int(resp.json()["id"])


class TestDefaultProtocolAutoAssignment:
    """Study creation assigns the default template for the study's type."""

    @pytest.mark.asyncio
    async def test_new_study_gets_default_template(self, client, db_engine, alice) -> None:
        """Creating a study assigns its type's default template without user action."""
        alice_user, _ = alice
        protocol_id = await _seed_default_template(db_engine, "SMS")

        study_id = await _create_group_and_study(client, db_engine, alice_user, "SMS")

        resp = await client.get(
            f"/api/v1/studies/{study_id}/protocol-assignment",
            headers=_bearer(alice_user.id),
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["protocol_id"] == protocol_id

    @pytest.mark.asyncio
    async def test_default_template_is_matched_by_study_type(
        self, client, db_engine, alice
    ) -> None:
        """An SLR study gets the SLR template, not another type's."""
        alice_user, _ = alice
        await _seed_default_template(db_engine, "SMS")
        slr_protocol_id = await _seed_default_template(db_engine, "SLR")

        study_id = await _create_group_and_study(client, db_engine, alice_user, "SLR")

        resp = await client.get(
            f"/api/v1/studies/{study_id}/protocol-assignment",
            headers=_bearer(alice_user.id),
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["protocol_id"] == slr_protocol_id

    @pytest.mark.asyncio
    async def test_execution_state_is_seeded_for_every_node(self, client, db_engine, alice) -> None:
        """Auto-assignment seeds one execution-state row per template node."""
        alice_user, _ = alice
        await _seed_default_template(db_engine, "SMS", node_count=3)

        study_id = await _create_group_and_study(client, db_engine, alice_user, "SMS")

        resp = await client.get(
            f"/api/v1/studies/{study_id}/execution-state",
            headers=_bearer(alice_user.id),
        )
        assert resp.status_code == 200, resp.text
        tasks = resp.json()["tasks"]
        assert len(tasks) == 3

    @pytest.mark.asyncio
    async def test_creation_succeeds_when_no_template_exists(
        self, client, db_engine, alice
    ) -> None:
        """A database with no seeded templates must still allow study creation."""
        alice_user, _ = alice

        study_id = await _create_group_and_study(client, db_engine, alice_user, "SMS")

        resp = await client.get(
            f"/api/v1/studies/{study_id}/protocol-assignment",
            headers=_bearer(alice_user.id),
        )
        assert resp.status_code == 404
