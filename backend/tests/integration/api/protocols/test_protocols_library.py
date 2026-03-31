"""Integration tests for protocol library endpoints (feature 010, T037, T056).

Covers:
- GET /protocols returns default templates for authenticated user.
- GET /protocols?study_type=SMS filters by study type.
- GET /protocols/{id} returns full graph for default template.
- GET /protocols/{id} returns 403 for another user's custom protocol.
- GET /protocols/{id} returns 404 for missing protocol.
- POST /protocols copies a default template (T056).
- PUT /protocols/{id} updates successfully and fails with stale version_id (T056).
- PUT /protocols/{id} returns 403 on default template (T056).
- DELETE /protocols/{id} deletes a custom protocol (T056).
- DELETE /protocols/{id} returns 409 when assigned to a study (T056).
"""

from __future__ import annotations

import pytest
from db.models.protocols import ResearchProtocol
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token


def _bearer(user_id: int) -> dict[str, str]:
    """Return Bearer token header for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _insert_default_protocol(db_engine, study_type: str = "SMS") -> int:
    """Insert a minimal default protocol and return its id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        p = ResearchProtocol(
            name=f"Default {study_type} Protocol",
            study_type=study_type,
            is_default_template=True,
        )
        session.add(p)
        await session.commit()
        await session.refresh(p)
        return p.id


async def _insert_custom_protocol(db_engine, owner_user_id: int, study_type: str = "SMS") -> int:
    """Insert a minimal custom protocol owned by *owner_user_id* and return its id."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        p = ResearchProtocol(
            name=f"Custom Protocol for user {owner_user_id}",
            study_type=study_type,
            is_default_template=False,
            owner_user_id=owner_user_id,
        )
        session.add(p)
        await session.commit()
        await session.refresh(p)
        return p.id


class TestGetProtocols:
    """GET /protocols endpoint tests."""

    @pytest.mark.asyncio
    async def test_returns_default_templates(self, client, db_engine, alice) -> None:
        """Unauthenticated default templates appear in the list for any researcher."""
        alice_user, _ = alice
        await _insert_default_protocol(db_engine, "SMS")

        resp = await client.get("/api/v1/protocols", headers=_bearer(alice_user.id))

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert any(p["is_default_template"] for p in data)

    @pytest.mark.asyncio
    async def test_returns_own_custom_protocol(self, client, db_engine, alice) -> None:
        """A researcher's own custom protocols appear in the list."""
        alice_user, _ = alice
        await _insert_custom_protocol(db_engine, alice_user.id, "SLR")

        resp = await client.get("/api/v1/protocols", headers=_bearer(alice_user.id))

        assert resp.status_code == 200
        data = resp.json()
        custom = [p for p in data if not p["is_default_template"]]
        assert any(p["owner_user_id"] == alice_user.id for p in custom)

    @pytest.mark.asyncio
    async def test_does_not_return_other_users_custom_protocol(
        self, client, db_engine, alice, bob
    ) -> None:
        """Bob's custom protocol does not appear when Alice queries the list."""
        alice_user, _ = alice
        bob_user, _ = bob
        await _insert_custom_protocol(db_engine, bob_user.id, "SMS")

        resp = await client.get("/api/v1/protocols", headers=_bearer(alice_user.id))

        assert resp.status_code == 200
        data = resp.json()
        custom = [p for p in data if not p["is_default_template"]]
        assert not any(p["owner_user_id"] == bob_user.id for p in custom)

    @pytest.mark.asyncio
    async def test_study_type_filter(self, client, db_engine, alice) -> None:
        """study_type query parameter filters the result list."""
        alice_user, _ = alice
        await _insert_default_protocol(db_engine, "SMS")
        await _insert_default_protocol(db_engine, "SLR")

        resp = await client.get("/api/v1/protocols?study_type=SMS", headers=_bearer(alice_user.id))

        assert resp.status_code == 200
        data = resp.json()
        assert all(p["study_type"] == "SMS" for p in data)

    @pytest.mark.asyncio
    async def test_requires_auth(self, client) -> None:
        """GET /protocols returns 401 without a valid JWT."""
        resp = await client.get("/api/v1/protocols")
        assert resp.status_code == 401


class TestGetProtocolDetail:
    """GET /protocols/{id} endpoint tests."""

    @pytest.mark.asyncio
    async def test_returns_default_template(self, client, db_engine, alice) -> None:
        """GET /protocols/{id} returns 200 for a default template."""
        alice_user, _ = alice
        protocol_id = await _insert_default_protocol(db_engine, "SMS")

        resp = await client.get(f"/api/v1/protocols/{protocol_id}", headers=_bearer(alice_user.id))

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == protocol_id
        assert data["is_default_template"] is True
        assert "nodes" in data
        assert "edges" in data

    @pytest.mark.asyncio
    async def test_returns_own_custom_protocol(self, client, db_engine, alice) -> None:
        """GET /protocols/{id} returns 200 for the requesting user's own protocol."""
        alice_user, _ = alice
        protocol_id = await _insert_custom_protocol(db_engine, alice_user.id)

        resp = await client.get(f"/api/v1/protocols/{protocol_id}", headers=_bearer(alice_user.id))

        assert resp.status_code == 200
        data = resp.json()
        assert data["owner_user_id"] == alice_user.id

    @pytest.mark.asyncio
    async def test_403_on_other_users_custom_protocol(
        self, client, db_engine, alice, bob
    ) -> None:
        """GET /protocols/{id} returns 403 when the protocol belongs to another user."""
        alice_user, _ = alice
        bob_user, _ = bob
        protocol_id = await _insert_custom_protocol(db_engine, bob_user.id)

        resp = await client.get(f"/api/v1/protocols/{protocol_id}", headers=_bearer(alice_user.id))

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_404_on_missing_protocol(self, client, alice) -> None:
        """GET /protocols/{id} returns 404 for a non-existent protocol id."""
        alice_user, _ = alice

        resp = await client.get("/api/v1/protocols/999999", headers=_bearer(alice_user.id))

        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# T056 — POST /protocols (copy and create)
# ---------------------------------------------------------------------------


class TestCreateProtocol:
    """POST /protocols endpoint tests (T056)."""

    @pytest.mark.asyncio
    async def test_copy_default_template(self, client, db_engine, alice) -> None:
        """POST /protocols with copy_from_protocol_id returns 201 with deep copy."""
        alice_user, _ = alice
        source_id = await _insert_default_protocol(db_engine, "SMS")

        resp = await client.post(
            "/api/v1/protocols",
            json={"name": "My SMS Copy", "copy_from_protocol_id": source_id},
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "My SMS Copy"
        assert data["is_default_template"] is False
        assert data["owner_user_id"] == alice_user.id
        assert data["study_type"] == "SMS"

    @pytest.mark.asyncio
    async def test_copy_403_on_other_users_protocol(
        self, client, db_engine, alice, bob
    ) -> None:
        """POST /protocols returns 403 when copying another user's non-default protocol."""
        alice_user, _ = alice
        bob_user, _ = bob
        source_id = await _insert_custom_protocol(db_engine, bob_user.id, "SMS")

        resp = await client.post(
            "/api/v1/protocols",
            json={"name": "Stolen Copy", "copy_from_protocol_id": source_id},
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_copy_409_on_duplicate_name(self, client, db_engine, alice) -> None:
        """POST /protocols returns 409 if the user already owns a protocol with that name."""
        alice_user, _ = alice
        source_id = await _insert_default_protocol(db_engine, "SMS")
        await _insert_custom_protocol(db_engine, alice_user.id, "SMS")

        resp = await client.post(
            "/api/v1/protocols",
            json={"name": f"Custom Protocol for user {alice_user.id}", "copy_from_protocol_id": source_id},
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_create_full_graph(self, client, alice) -> None:
        """POST /protocols with a full graph definition returns 201."""
        alice_user, _ = alice

        payload = {
            "name": "My From-Scratch Protocol",
            "study_type": "SMS",
            "nodes": [
                {
                    "task_id": "n1",
                    "task_type": "DefinePICO",
                    "label": "Define PICO",
                    "inputs": [],
                    "outputs": [],
                    "quality_gates": [],
                    "assignees": [],
                }
            ],
            "edges": [],
        }
        resp = await client.post(
            "/api/v1/protocols",
            json=payload,
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "My From-Scratch Protocol"
        assert len(data["nodes"]) == 1

    @pytest.mark.asyncio
    async def test_create_400_on_cycle(self, client, alice) -> None:
        """POST /protocols returns 400 when the graph has a cycle."""
        alice_user, _ = alice

        payload = {
            "name": "Cyclic Protocol",
            "study_type": "SMS",
            "nodes": [
                {"task_id": "a", "task_type": "DefinePICO", "label": "A", "inputs": [], "outputs": [], "quality_gates": [], "assignees": []},
                {"task_id": "b", "task_type": "BuildSearchString", "label": "B", "inputs": [], "outputs": [], "quality_gates": [], "assignees": []},
            ],
            "edges": [
                {"edge_id": "e1", "source_task_id": "a", "source_output_name": "out", "target_task_id": "b", "target_input_name": "in"},
                {"edge_id": "e2", "source_task_id": "b", "source_output_name": "out", "target_task_id": "a", "target_input_name": "in"},
            ],
        }
        resp = await client.post(
            "/api/v1/protocols",
            json=payload,
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# T056 — PUT /protocols/{id}
# ---------------------------------------------------------------------------


class TestUpdateProtocol:
    """PUT /protocols/{id} endpoint tests (T056)."""

    @pytest.mark.asyncio
    async def test_update_success(self, client, db_engine, alice) -> None:
        """PUT /protocols/{id} returns 200 with updated name."""
        alice_user, _ = alice
        protocol_id = await _insert_custom_protocol(db_engine, alice_user.id)

        payload = {
            "name": "Updated Protocol Name",
            "version_id": 1,
            "nodes": [
                {"task_id": "n1", "task_type": "DefinePICO", "label": "Step 1", "inputs": [], "outputs": [], "quality_gates": [], "assignees": []},
            ],
            "edges": [],
        }
        resp = await client.put(
            f"/api/v1/protocols/{protocol_id}",
            json=payload,
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Updated Protocol Name"
        assert data["version_id"] == 2

    @pytest.mark.asyncio
    async def test_update_409_version_conflict(self, client, db_engine, alice) -> None:
        """PUT /protocols/{id} returns 409 when version_id is stale."""
        alice_user, _ = alice
        protocol_id = await _insert_custom_protocol(db_engine, alice_user.id)

        payload = {
            "name": "Conflict Protocol",
            "version_id": 999,
            "nodes": [
                {"task_id": "n1", "task_type": "DefinePICO", "label": "Step 1", "inputs": [], "outputs": [], "quality_gates": [], "assignees": []},
            ],
            "edges": [],
        }
        resp = await client.put(
            f"/api/v1/protocols/{protocol_id}",
            json=payload,
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 409
        data = resp.json()
        assert data["detail"]["current_version_id"] == 1

    @pytest.mark.asyncio
    async def test_update_403_on_default_template(self, client, db_engine, alice) -> None:
        """PUT /protocols/{id} returns 403 for a default template."""
        alice_user, _ = alice
        protocol_id = await _insert_default_protocol(db_engine, "SMS")

        payload = {
            "name": "Attempt to Modify Default",
            "version_id": 1,
            "nodes": [],
            "edges": [],
        }
        resp = await client.put(
            f"/api/v1/protocols/{protocol_id}",
            json=payload,
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_update_403_on_other_users_protocol(
        self, client, db_engine, alice, bob
    ) -> None:
        """PUT /protocols/{id} returns 403 when not the owner."""
        alice_user, _ = alice
        bob_user, _ = bob
        protocol_id = await _insert_custom_protocol(db_engine, bob_user.id)

        payload = {
            "name": "Stolen Update",
            "version_id": 1,
            "nodes": [],
            "edges": [],
        }
        resp = await client.put(
            f"/api/v1/protocols/{protocol_id}",
            json=payload,
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# T056 — DELETE /protocols/{id}
# ---------------------------------------------------------------------------


class TestDeleteProtocol:
    """DELETE /protocols/{id} endpoint tests (T056)."""

    @pytest.mark.asyncio
    async def test_delete_success(self, client, db_engine, alice) -> None:
        """DELETE /protocols/{id} returns 204 and the protocol is gone."""
        alice_user, _ = alice
        protocol_id = await _insert_custom_protocol(db_engine, alice_user.id)

        resp = await client.delete(
            f"/api/v1/protocols/{protocol_id}",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 204

        get_resp = await client.get(
            f"/api/v1/protocols/{protocol_id}",
            headers=_bearer(alice_user.id),
        )
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_403_on_default_template(self, client, db_engine, alice) -> None:
        """DELETE /protocols/{id} returns 403 for a default template."""
        alice_user, _ = alice
        protocol_id = await _insert_default_protocol(db_engine, "SLR")

        resp = await client.delete(
            f"/api/v1/protocols/{protocol_id}",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_403_on_other_users_protocol(
        self, client, db_engine, alice, bob
    ) -> None:
        """DELETE /protocols/{id} returns 403 when not the owner."""
        alice_user, _ = alice
        bob_user, _ = bob
        protocol_id = await _insert_custom_protocol(db_engine, bob_user.id)

        resp = await client.delete(
            f"/api/v1/protocols/{protocol_id}",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_409_when_assigned_to_study(
        self, client, db_engine, alice
    ) -> None:
        """DELETE /protocols/{id} returns 409 when the protocol is assigned to a study."""
        from db.models import Study
        from db.models.protocols import StudyProtocolAssignment
        from sqlalchemy.ext.asyncio import async_sessionmaker

        alice_user, _ = alice

        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            protocol = ResearchProtocol(
                name="Assigned Protocol",
                study_type="SMS",
                is_default_template=False,
                owner_user_id=alice_user.id,
            )
            session.add(protocol)
            await session.flush()

            from db.models import StudyType
            study = Study(
                name="Test Study",
                study_type=StudyType.SMS,
            )
            session.add(study)
            await session.flush()

            assignment = StudyProtocolAssignment(
                study_id=study.id,
                protocol_id=protocol.id,
            )
            session.add(assignment)
            await session.commit()
            protocol_id = protocol.id

        resp = await client.delete(
            f"/api/v1/protocols/{protocol_id}",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 409
        data = resp.json()
        assert "blocking_study_ids" in data["detail"]
