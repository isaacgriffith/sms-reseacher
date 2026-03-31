"""Integration tests for YAML export and import endpoints (feature 010, T086/T087).

Covers:
- GET /protocols/{id}/export returns valid YAML for a protocol the user owns.
- GET /protocols/{id}/export returns 404 for a missing protocol.
- GET /protocols/{id}/export returns 403 for another user's custom protocol.
- POST /protocols/import round-trips: exported YAML can be re-imported and creates a new protocol.
- POST /protocols/import returns 400 on malformed YAML.
- POST /protocols/import returns 400 on unsupported schema version.
- POST /protocols/import unauthenticated returns 401.
"""

from __future__ import annotations

import io

import pytest
import yaml
from db.models.protocols import (
    NodeDataType,
    ProtocolEdge,
    ProtocolNode,
    ProtocolNodeInput,
    ProtocolNodeOutput,
    ProtocolTaskType,
    QualityGate,
    QualityGateType,
    ResearchProtocol,
)
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token


def _bearer(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _insert_protocol_with_nodes(
    db_engine,
    owner_user_id: int | None,
    is_default_template: bool = False,
) -> int:
    """Insert a protocol with one search node and one review node (connected)."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        p = ResearchProtocol(
            name="YAML Test Protocol",
            study_type="SMS",
            is_default_template=is_default_template,
            owner_user_id=owner_user_id,
        )
        session.add(p)
        await session.flush()

        n1 = ProtocolNode(
            protocol_id=p.id,
            task_id="search",
            task_type=ProtocolTaskType.EXECUTE_SEARCH,
            label="Literature Search",
            is_required=True,
        )
        session.add(n1)
        await session.flush()

        out1 = ProtocolNodeOutput(
            node_id=n1.id,
            name="results",
            data_type=NodeDataType.CANDIDATE_PAPER_LIST,
        )
        session.add(out1)

        n2 = ProtocolNode(
            protocol_id=p.id,
            task_id="review",
            task_type=ProtocolTaskType.SCREEN_PAPERS,
            label="Screen Papers",
            is_required=True,
        )
        session.add(n2)
        await session.flush()

        inp2 = ProtocolNodeInput(
            node_id=n2.id,
            name="papers",
            data_type=NodeDataType.CANDIDATE_PAPER_LIST,
            is_required=True,
        )
        session.add(inp2)

        gate = QualityGate(
            node_id=n2.id,
            gate_type=QualityGateType.COMPLETION_CHECK,
            config={},
        )
        session.add(gate)

        edge = ProtocolEdge(
            protocol_id=p.id,
            edge_id="e1",
            source_node_id=n1.id,
            source_output_name="results",
            target_node_id=n2.id,
            target_input_name="papers",
        )
        session.add(edge)

        await session.commit()
        return p.id


class TestExportProtocol:
    """GET /protocols/{id}/export."""

    @pytest.mark.asyncio
    async def test_export_own_protocol_returns_yaml(self, client, db_engine, alice) -> None:
        """Export returns valid YAML with all expected top-level keys."""
        alice_user, _ = alice
        protocol_id = await _insert_protocol_with_nodes(db_engine, alice_user.id)

        resp = await client.get(
            f"/api/v1/protocols/{protocol_id}/export",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 200
        assert "yaml" in resp.headers.get("content-type", "").lower()
        doc = yaml.safe_load(resp.text)
        assert doc["protocol_schema_version"] == "1.0"
        assert doc["name"] == "YAML Test Protocol"
        assert doc["study_type"] == "SMS"
        assert isinstance(doc["nodes"], list)
        assert isinstance(doc["edges"], list)
        assert len(doc["nodes"]) == 2
        assert len(doc["edges"]) == 1

    @pytest.mark.asyncio
    async def test_export_default_template_returns_yaml(self, client, db_engine, alice) -> None:
        """Default templates can be exported by any authenticated user."""
        alice_user, _ = alice
        protocol_id = await _insert_protocol_with_nodes(
            db_engine, None, is_default_template=True
        )

        resp = await client.get(
            f"/api/v1/protocols/{protocol_id}/export",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_export_missing_returns_404(self, client, alice) -> None:
        """Exporting a non-existent protocol returns 404."""
        alice_user, _ = alice

        resp = await client.get(
            "/api/v1/protocols/999999/export",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_export_other_users_protocol_returns_403(
        self, client, db_engine, alice
    ) -> None:
        """Exporting another researcher's custom protocol returns 403."""
        alice_user, _ = alice
        other_owner_id = alice_user.id + 1
        protocol_id = await _insert_protocol_with_nodes(db_engine, other_owner_id)

        resp = await client.get(
            f"/api/v1/protocols/{protocol_id}/export",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 403


class TestImportProtocol:
    """POST /protocols/import."""

    def _make_upload(self, content: str) -> dict:
        """Build multipart upload dict for httpx AsyncClient."""
        return {"file": ("protocol.yaml", io.BytesIO(content.encode()), "application/x-yaml")}

    @pytest.mark.asyncio
    async def test_round_trip_import(self, client, db_engine, alice) -> None:
        """Exported YAML can be imported to create a new custom protocol."""
        alice_user, _ = alice
        protocol_id = await _insert_protocol_with_nodes(db_engine, alice_user.id)

        # export
        export_resp = await client.get(
            f"/api/v1/protocols/{protocol_id}/export",
            headers=_bearer(alice_user.id),
        )
        assert export_resp.status_code == 200
        doc = yaml.safe_load(export_resp.text)
        # rename to avoid 409 duplicate-name conflict
        doc["name"] = "YAML Test Protocol (imported)"
        yaml_str = yaml.dump(doc)

        # import
        import_resp = await client.post(
            "/api/v1/protocols/import",
            headers=_bearer(alice_user.id),
            files=self._make_upload(yaml_str),
        )

        assert import_resp.status_code == 201
        data = import_resp.json()
        assert data["name"] == "YAML Test Protocol (imported)"
        assert data["id"] != protocol_id  # new distinct protocol
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1

    @pytest.mark.asyncio
    async def test_import_malformed_yaml_returns_400(self, client, alice) -> None:
        """Malformed YAML content returns 400 Bad Request."""
        alice_user, _ = alice

        resp = await client.post(
            "/api/v1/protocols/import",
            headers=_bearer(alice_user.id),
            files=self._make_upload("{ this: is: : not valid yaml : ["),
        )

        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_import_unsupported_schema_version_returns_400(
        self, client, alice
    ) -> None:
        """YAML with an unsupported protocol_schema_version returns 400."""
        alice_user, _ = alice
        doc = {
            "protocol_schema_version": "9.9",
            "name": "Future Protocol",
            "study_type": "SMS",
            "nodes": [],
            "edges": [],
        }

        resp = await client.post(
            "/api/v1/protocols/import",
            headers=_bearer(alice_user.id),
            files=self._make_upload(yaml.dump(doc)),
        )

        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_import_unauthenticated_returns_401(self, client) -> None:
        """Import without a Bearer token returns 401."""
        doc = {
            "protocol_schema_version": "1.0",
            "name": "Test",
            "study_type": "SMS",
            "nodes": [],
            "edges": [],
        }

        resp = await client.post(
            "/api/v1/protocols/import",
            files=self._make_upload(yaml.dump(doc)),
        )

        assert resp.status_code == 401
