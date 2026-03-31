"""Unit tests for backend.services.protocol_service write operations (feature 010, T057).

Covers:
- copy_protocol: deep copy of nodes/edges verified via mock DB
- update_protocol: optimistic lock check (409 on stale version_id)
- delete_protocol: blocked when assigned to a study (409)
- validate_graph: comprehensive cases including cycle, task type violations
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_session():
    """Return a minimal async session mock."""
    session = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    return session


def _make_protocol(
    *,
    id: int = 1,
    name: str = "Test Protocol",
    study_type: str = "SMS",
    is_default_template: bool = False,
    owner_user_id: int | None = 42,
    version_id: int = 1,
):
    """Return a minimal mock ResearchProtocol."""
    p = MagicMock()
    p.id = id
    p.name = name
    p.study_type = study_type
    p.is_default_template = is_default_template
    p.owner_user_id = owner_user_id
    p.version_id = version_id
    p.nodes = []
    p.edges = []
    p.study_assignments = []
    return p


# ---------------------------------------------------------------------------
# validate_graph comprehensive tests (T057 addition)
# ---------------------------------------------------------------------------


class TestValidateGraphComprehensive:
    """Additional validate_graph edge cases for T057."""

    def test_valid_sms_two_node_dag(self) -> None:
        """A valid two-node SMS DAG passes validation without error."""
        from backend.services.protocol_service import validate_graph

        nodes = [
            {"task_id": "a", "task_type": "DefinePICO"},
            {"task_id": "b", "task_type": "BuildSearchString"},
        ]
        edges = [{"source_task_id": "a", "target_task_id": "b"}]
        validate_graph("SMS", nodes, edges)  # no exception

    def test_complex_cycle_raises(self) -> None:
        """A four-node graph with a cycle in a sub-path raises ProtocolGraphError."""
        from backend.services.protocol_service import ProtocolGraphError, validate_graph

        nodes = [
            {"task_id": "a", "task_type": "DefinePICO"},
            {"task_id": "b", "task_type": "BuildSearchString"},
            {"task_id": "c", "task_type": "ExecuteSearch"},
            {"task_id": "d", "task_type": "ScreenPapers"},
        ]
        edges = [
            {"source_task_id": "a", "target_task_id": "b"},
            {"source_task_id": "b", "target_task_id": "c"},
            {"source_task_id": "c", "target_task_id": "d"},
            {"source_task_id": "d", "target_task_id": "b"},  # cycle: b→c→d→b
        ]
        with pytest.raises(ProtocolGraphError, match="cycle"):
            validate_graph("SMS", nodes, edges)

    def test_slr_specific_task_type_allowed(self) -> None:
        """DefineProtocol is valid for SLR but not SMS."""
        from backend.services.protocol_service import ProtocolGraphError, validate_graph

        nodes_slr = [{"task_id": "p", "task_type": "DefineProtocol"}]
        validate_graph("SLR", nodes_slr, [])  # no exception

        with pytest.raises((ProtocolGraphError, ValueError)):
            validate_graph("SMS", nodes_slr, [])

    def test_unknown_task_type_raises(self) -> None:
        """An unrecognised task_type string raises ProtocolGraphError."""
        from backend.services.protocol_service import ProtocolGraphError, validate_graph

        with pytest.raises(ProtocolGraphError, match="Unknown task_type"):
            validate_graph("SMS", [{"task_id": "n1", "task_type": "GhostTask"}], [])

    def test_ambiguous_duplicate_task_ids_raises(self) -> None:
        """Two nodes with the same task_id raise ProtocolGraphError."""
        from backend.services.protocol_service import ProtocolGraphError, validate_graph

        nodes = [
            {"task_id": "dup", "task_type": "DefinePICO"},
            {"task_id": "dup", "task_type": "BuildSearchString"},
        ]
        with pytest.raises(ProtocolGraphError, match="duplicate task_id"):
            validate_graph("SMS", nodes, [])


# ---------------------------------------------------------------------------
# copy_protocol — T057
# ---------------------------------------------------------------------------


class TestCopyProtocol:
    """Tests for copy_protocol deep-copy behaviour (T057)."""

    @pytest.mark.asyncio
    async def test_copy_protocol_calls_get_detail_and_commits(self) -> None:
        """copy_protocol calls get_protocol_detail for auth and commits the copy."""
        from backend.services.protocol_service import copy_protocol

        source = _make_protocol(id=10, is_default_template=True, owner_user_id=None, study_type="SMS")
        new_copy = _make_protocol(id=20, name="My Copy", owner_user_id=42, study_type="SMS")

        db = _make_mock_session()

        with (
            patch("backend.services.protocol_service.get_protocol_detail", new=AsyncMock(side_effect=[source, new_copy])),
            patch("backend.services.protocol_service._check_duplicate_name", new=AsyncMock()),
        ):
            result = await copy_protocol(
                source_id=10,
                user_id=42,
                new_name="My Copy",
                description=None,
                db=db,
            )

        db.commit.assert_called_once()
        assert result.name == "My Copy"

    @pytest.mark.asyncio
    async def test_copy_protocol_copies_nodes(self) -> None:
        """copy_protocol adds ORM objects for each source node."""
        from backend.services.protocol_service import copy_protocol

        node = MagicMock()
        node.id = 1
        node.task_id = "n1"
        node.task_type = MagicMock(value="DefinePICO")
        node.label = "Step 1"
        node.description = None
        node.is_required = True
        node.position_x = 0.0
        node.position_y = 0.0
        node.inputs = []
        node.outputs = []
        node.quality_gates = []
        node.assignees = []

        source = _make_protocol(id=10, is_default_template=True, owner_user_id=None)
        source.nodes = [node]
        source.edges = []

        new_copy = _make_protocol(id=20, name="Copy", owner_user_id=42)

        db = _make_mock_session()

        with (
            patch("backend.services.protocol_service.get_protocol_detail", new=AsyncMock(side_effect=[source, new_copy])),
            patch("backend.services.protocol_service._check_duplicate_name", new=AsyncMock()),
        ):
            await copy_protocol(source_id=10, user_id=42, new_name="Copy", description=None, db=db)

        # session.add was called at least for the new protocol and the node copy
        assert db.add.call_count >= 2


# ---------------------------------------------------------------------------
# update_protocol — T057
# ---------------------------------------------------------------------------


class TestUpdateProtocolUnit:
    """Tests for update_protocol optimistic lock behaviour (T057)."""

    @pytest.mark.asyncio
    async def test_update_raises_409_on_stale_version(self) -> None:
        """update_protocol raises HTTP 409 when version_id does not match."""
        from backend.services.protocol_service import update_protocol

        protocol = _make_protocol(id=5, owner_user_id=42, version_id=3, is_default_template=False)

        db = _make_mock_session()

        with patch("backend.services.protocol_service.get_protocol_detail", new=AsyncMock(return_value=protocol)):
            with pytest.raises(HTTPException) as exc_info:
                await update_protocol(
                    protocol_id=5,
                    version_id=1,  # stale — current is 3
                    name="New Name",
                    description=None,
                    nodes_payload=[],
                    edges_payload=[],
                    user_id=42,
                    db=db,
                )

        assert exc_info.value.status_code == 409
        assert exc_info.value.detail["current_version_id"] == 3

    @pytest.mark.asyncio
    async def test_update_raises_403_on_default_template(self) -> None:
        """update_protocol raises HTTP 403 for a default template."""
        from backend.services.protocol_service import update_protocol

        protocol = _make_protocol(id=5, is_default_template=True, owner_user_id=None)

        db = _make_mock_session()

        with patch("backend.services.protocol_service.get_protocol_detail", new=AsyncMock(return_value=protocol)):
            with pytest.raises(HTTPException) as exc_info:
                await update_protocol(
                    protocol_id=5,
                    version_id=1,
                    name="Modified",
                    description=None,
                    nodes_payload=[],
                    edges_payload=[],
                    user_id=42,
                    db=db,
                )

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_update_raises_403_when_not_owner(self) -> None:
        """update_protocol raises HTTP 403 when requester is not the owner."""
        from backend.services.protocol_service import update_protocol

        protocol = _make_protocol(id=5, is_default_template=False, owner_user_id=99, version_id=1)

        db = _make_mock_session()

        with patch("backend.services.protocol_service.get_protocol_detail", new=AsyncMock(return_value=protocol)):
            with pytest.raises(HTTPException) as exc_info:
                await update_protocol(
                    protocol_id=5,
                    version_id=1,
                    name="Stolen Update",
                    description=None,
                    nodes_payload=[],
                    edges_payload=[],
                    user_id=42,  # not the owner (99)
                    db=db,
                )

        assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# delete_protocol — T057
# ---------------------------------------------------------------------------


class TestDeleteProtocolUnit:
    """Tests for delete_protocol business logic (T057)."""

    @pytest.mark.asyncio
    async def test_delete_raises_409_when_assigned(self) -> None:
        """delete_protocol raises HTTP 409 when protocol is assigned to a study."""
        from backend.services.protocol_service import delete_protocol

        protocol = _make_protocol(id=7, is_default_template=False, owner_user_id=42)
        assignment = MagicMock()
        assignment.study_id = 100
        protocol.study_assignments = [assignment]

        db = _make_mock_session()

        scalar_result = MagicMock()
        scalar_result.scalar_one_or_none = MagicMock(return_value=protocol)
        db.execute = AsyncMock(return_value=scalar_result)

        with pytest.raises(HTTPException) as exc_info:
            await delete_protocol(protocol_id=7, user_id=42, db=db)

        assert exc_info.value.status_code == 409
        assert 100 in exc_info.value.detail["blocking_study_ids"]

    @pytest.mark.asyncio
    async def test_delete_raises_403_on_default_template(self) -> None:
        """delete_protocol raises HTTP 403 for a default template."""
        from backend.services.protocol_service import delete_protocol

        protocol = _make_protocol(id=8, is_default_template=True, owner_user_id=None)

        db = _make_mock_session()

        scalar_result = MagicMock()
        scalar_result.scalar_one_or_none = MagicMock(return_value=protocol)
        db.execute = AsyncMock(return_value=scalar_result)

        with pytest.raises(HTTPException) as exc_info:
            await delete_protocol(protocol_id=8, user_id=42, db=db)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_raises_403_when_not_owner(self) -> None:
        """delete_protocol raises HTTP 403 when requester is not the owner."""
        from backend.services.protocol_service import delete_protocol

        protocol = _make_protocol(id=9, is_default_template=False, owner_user_id=99)

        db = _make_mock_session()

        scalar_result = MagicMock()
        scalar_result.scalar_one_or_none = MagicMock(return_value=protocol)
        db.execute = AsyncMock(return_value=scalar_result)

        with pytest.raises(HTTPException) as exc_info:
            await delete_protocol(protocol_id=9, user_id=42, db=db)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_raises_404_when_not_found(self) -> None:
        """delete_protocol raises HTTP 404 when protocol does not exist."""
        from backend.services.protocol_service import delete_protocol

        db = _make_mock_session()

        scalar_result = MagicMock()
        scalar_result.scalar_one_or_none = MagicMock(return_value=None)
        db.execute = AsyncMock(return_value=scalar_result)

        with pytest.raises(HTTPException) as exc_info:
            await delete_protocol(protocol_id=999, user_id=42, db=db)

        assert exc_info.value.status_code == 404
