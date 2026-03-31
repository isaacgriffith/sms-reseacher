"""Integration tests for the study protocol assignment endpoint (feature 010, T038).

Covers:
- GET /studies/{study_id}/protocol-assignment returns 200 for a study member.
- GET /studies/{study_id}/protocol-assignment returns 403 for a non-member.
- GET /studies/{study_id}/protocol-assignment returns 404 when no assignment exists.
"""

from __future__ import annotations

import pytest
from db.models.protocols import ResearchProtocol, StudyProtocolAssignment
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
        """GET /studies/{id}/protocol-assignment returns 404 when no assignment exists."""
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
