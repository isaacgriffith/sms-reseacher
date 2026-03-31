"""Unit tests for Research Protocol Definition ORM models (feature 010).

Tests verify table names, column types, unique constraints, enum values, cascade
behaviour, and relationship navigation for all 9 new protocol models.

All tests use an in-memory SQLite async session — no PostgreSQL connection required.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db.base import Base
from db.models.protocols import (
    EdgeConditionOperator,
    NodeAssignee,
    NodeAssigneeType,
    NodeDataType,
    ProtocolEdge,
    ProtocolNode,
    ProtocolNodeInput,
    ProtocolNodeOutput,
    ProtocolTaskType,
    QualityGate,
    QualityGateType,
    ResearchProtocol,
    StudyProtocolAssignment,
    TaskExecutionState,
    TaskNodeStatus,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def session():
    """Yield an in-memory SQLite async session with all protocol tables created."""
    import db.models  # noqa: F401 — registers all FK targets on Base.metadata
    import db.models.agents  # noqa: F401
    import db.models.protocols  # noqa: F401
    import db.models.study  # noqa: F401
    import db.models.users  # noqa: F401

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
    await engine.dispose()


# ---------------------------------------------------------------------------
# Enum value tests
# ---------------------------------------------------------------------------


class TestEnums:
    """Smoke-tests that enum members have the expected string values."""

    def test_protocol_task_type_values(self) -> None:
        """Verify ProtocolTaskType enum members map to their expected string values."""
        assert ProtocolTaskType.DEFINE_PICO.value == "DefinePICO"
        assert ProtocolTaskType.GENERATE_REPORT.value == "GenerateReport"

    def test_quality_gate_type_values(self) -> None:
        """Verify QualityGateType enum members map to their expected string values."""
        assert QualityGateType.METRIC_THRESHOLD.value == "metric_threshold"
        assert QualityGateType.COMPLETION_CHECK.value == "completion_check"
        assert QualityGateType.HUMAN_SIGN_OFF.value == "human_sign_off"

    def test_edge_condition_operator_values(self) -> None:
        """Verify EdgeConditionOperator enum members map to their expected string values."""
        assert EdgeConditionOperator.GT.value == "gt"
        assert EdgeConditionOperator.NEQ.value == "neq"

    def test_task_node_status_values(self) -> None:
        """Verify TaskNodeStatus enum members map to their expected string values."""
        assert TaskNodeStatus.PENDING.value == "pending"
        assert TaskNodeStatus.GATE_FAILED.value == "gate_failed"

    def test_node_assignee_type_values(self) -> None:
        """Verify NodeAssigneeType enum members map to their expected string values."""
        assert NodeAssigneeType.HUMAN_ROLE.value == "human_role"
        assert NodeAssigneeType.AI_AGENT.value == "ai_agent"

    def test_node_data_type_values(self) -> None:
        """Verify NodeDataType enum members map to their expected string values."""
        assert NodeDataType.CANDIDATE_PAPER_LIST.value == "candidate_paper_list"
        assert NodeDataType.REPORT.value == "report"


# ---------------------------------------------------------------------------
# Table name tests
# ---------------------------------------------------------------------------


class TestTableNames:
    """Verify ``__tablename__`` values are correct."""

    def test_research_protocol_tablename(self) -> None:
        """Verify ResearchProtocol uses the 'research_protocol' table name."""
        assert ResearchProtocol.__tablename__ == "research_protocol"

    def test_protocol_node_tablename(self) -> None:
        """Verify ProtocolNode uses the 'protocol_node' table name."""
        assert ProtocolNode.__tablename__ == "protocol_node"

    def test_protocol_node_input_tablename(self) -> None:
        """Verify ProtocolNodeInput uses the 'protocol_node_input' table name."""
        assert ProtocolNodeInput.__tablename__ == "protocol_node_input"

    def test_protocol_node_output_tablename(self) -> None:
        """Verify ProtocolNodeOutput uses the 'protocol_node_output' table name."""
        assert ProtocolNodeOutput.__tablename__ == "protocol_node_output"

    def test_quality_gate_tablename(self) -> None:
        """Verify QualityGate uses the 'quality_gate' table name."""
        assert QualityGate.__tablename__ == "quality_gate"

    def test_node_assignee_tablename(self) -> None:
        """Verify NodeAssignee uses the 'node_assignee' table name."""
        assert NodeAssignee.__tablename__ == "node_assignee"

    def test_protocol_edge_tablename(self) -> None:
        """Verify ProtocolEdge uses the 'protocol_edge' table name."""
        assert ProtocolEdge.__tablename__ == "protocol_edge"

    def test_study_protocol_assignment_tablename(self) -> None:
        """Verify StudyProtocolAssignment uses the 'study_protocol_assignment' table name."""
        assert StudyProtocolAssignment.__tablename__ == "study_protocol_assignment"

    def test_task_execution_state_tablename(self) -> None:
        """Verify TaskExecutionState uses the 'task_execution_state' table name."""
        assert TaskExecutionState.__tablename__ == "task_execution_state"


# ---------------------------------------------------------------------------
# ORM CRUD tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestResearchProtocol:
    """CRUD tests for :class:`ResearchProtocol`."""

    async def test_create_and_retrieve(self, session) -> None:
        """Verify a ResearchProtocol row can be inserted and its fields read back."""
        protocol = ResearchProtocol(
            name="Test Protocol",
            description="A test protocol.",
            study_type="SMS",
            is_default_template=False,
        )
        session.add(protocol)
        await session.flush()
        assert protocol.id is not None
        assert protocol.name == "Test Protocol"
        assert protocol.study_type == "SMS"
        assert protocol.is_default_template is False

    async def test_version_id_defaults_to_one(self, session) -> None:
        """Verify that version_id is set to 1 by the Python-side default on creation."""
        protocol = ResearchProtocol(name="V Protocol", study_type="SLR")
        session.add(protocol)
        await session.flush()
        # version_id default=1 is honoured by Python-side default
        assert protocol.version_id == 1

    async def test_repr(self) -> None:
        """Verify the __repr__ of ResearchProtocol includes the class name and study type."""
        protocol = ResearchProtocol(name="R", study_type="SMS")
        r = repr(protocol)
        assert "ResearchProtocol" in r
        assert "SMS" in r


@pytest.mark.asyncio
class TestProtocolNode:
    """CRUD tests for :class:`ProtocolNode`."""

    async def _make_protocol(self, session) -> ResearchProtocol:
        """Insert a minimal ResearchProtocol and return it after flushing."""
        p = ResearchProtocol(name="P", study_type="SMS")
        session.add(p)
        await session.flush()
        return p

    async def test_create_node(self, session) -> None:
        """Verify a ProtocolNode row can be inserted with correct task_type."""
        p = await self._make_protocol(session)
        node = ProtocolNode(
            protocol_id=p.id,
            task_id="define_pico",
            task_type=ProtocolTaskType.DEFINE_PICO,
            label="Define PICO",
            is_required=True,
        )
        session.add(node)
        await session.flush()
        assert node.id is not None
        assert node.task_type == ProtocolTaskType.DEFINE_PICO

    async def test_duplicate_task_id_raises(self, session) -> None:
        """Verify that two nodes with the same task_id in one protocol raise IntegrityError."""
        from sqlalchemy.exc import IntegrityError

        p = await self._make_protocol(session)
        session.add(ProtocolNode(
            protocol_id=p.id, task_id="n1",
            task_type=ProtocolTaskType.DEFINE_PICO, label="N1"
        ))
        session.add(ProtocolNode(
            protocol_id=p.id, task_id="n1",
            task_type=ProtocolTaskType.DEFINE_PICO, label="N1dup"
        ))
        with pytest.raises(IntegrityError):
            await session.flush()

    async def test_cascade_delete_removes_node(self, session) -> None:
        """Verify that deleting a protocol cascades to remove its child nodes."""
        from sqlalchemy import select

        p = await self._make_protocol(session)
        node = ProtocolNode(
            protocol_id=p.id, task_id="n1",
            task_type=ProtocolTaskType.DEFINE_PICO, label="N1"
        )
        session.add(node)
        await session.flush()
        await session.delete(p)
        await session.flush()
        remaining = (await session.execute(select(ProtocolNode))).scalars().all()
        assert len(remaining) == 0


@pytest.mark.asyncio
class TestProtocolNodeInputOutput:
    """Tests for :class:`ProtocolNodeInput` and :class:`ProtocolNodeOutput`."""

    async def _make_node(self, session) -> tuple[ResearchProtocol, ProtocolNode]:
        """Insert a minimal protocol and node, returning both after flushing."""
        p = ResearchProtocol(name="P", study_type="SMS")
        session.add(p)
        await session.flush()
        n = ProtocolNode(
            protocol_id=p.id, task_id="n1",
            task_type=ProtocolTaskType.DEFINE_PICO, label="N1"
        )
        session.add(n)
        await session.flush()
        return p, n

    async def test_create_input(self, session) -> None:
        """Verify a ProtocolNodeInput row can be inserted and assigned an id."""
        _, node = await self._make_node(session)
        inp = ProtocolNodeInput(
            node_id=node.id, name="questions",
            data_type=NodeDataType.TEXT, is_required=True,
        )
        session.add(inp)
        await session.flush()
        assert inp.id is not None

    async def test_create_output(self, session) -> None:
        """Verify a ProtocolNodeOutput row can be inserted and assigned an id."""
        _, node = await self._make_node(session)
        out = ProtocolNodeOutput(
            node_id=node.id, name="pico",
            data_type=NodeDataType.PICO_STRUCT,
        )
        session.add(out)
        await session.flush()
        assert out.id is not None

    async def test_duplicate_input_name_raises(self, session) -> None:
        """Verify that two inputs with the same name on one node raise IntegrityError."""
        from sqlalchemy.exc import IntegrityError

        _, node = await self._make_node(session)
        session.add(ProtocolNodeInput(node_id=node.id, name="x", data_type=NodeDataType.TEXT))
        session.add(ProtocolNodeInput(node_id=node.id, name="x", data_type=NodeDataType.TEXT))
        with pytest.raises(IntegrityError):
            await session.flush()


@pytest.mark.asyncio
class TestQualityGate:
    """Tests for :class:`QualityGate`."""

    async def _make_node(self, session) -> ProtocolNode:
        """Insert a minimal protocol and node, returning the node after flushing."""
        p = ResearchProtocol(name="P", study_type="SMS")
        session.add(p)
        await session.flush()
        n = ProtocolNode(
            protocol_id=p.id, task_id="n1",
            task_type=ProtocolTaskType.DEFINE_PICO, label="N1"
        )
        session.add(n)
        await session.flush()
        return n

    async def test_create_completion_check_gate(self, session) -> None:
        """Verify a COMPLETION_CHECK QualityGate row is created with its config stored."""
        node = await self._make_node(session)
        gate = QualityGate(
            node_id=node.id,
            gate_type=QualityGateType.COMPLETION_CHECK,
            config={"description": "PICO complete."},
        )
        session.add(gate)
        await session.flush()
        assert gate.id is not None
        assert gate.config == {"description": "PICO complete."}

    async def test_metric_threshold_gate(self, session) -> None:
        """Verify a METRIC_THRESHOLD QualityGate row is created with the correct gate_type."""
        node = await self._make_node(session)
        gate = QualityGate(
            node_id=node.id,
            gate_type=QualityGateType.METRIC_THRESHOLD,
            config={"metric_name": "kappa", "operator": "gte", "threshold": 0.6},
        )
        session.add(gate)
        await session.flush()
        assert gate.gate_type == QualityGateType.METRIC_THRESHOLD


@pytest.mark.asyncio
class TestTaskExecutionState:
    """Tests for :class:`TaskExecutionState`."""

    async def test_default_status_is_pending(self, session) -> None:
        """Verify a new TaskExecutionState defaults to PENDING status."""
        from db.models import Study, StudyType

        study = Study(name="S1", study_type=StudyType.SMS)
        session.add(study)
        p = ResearchProtocol(name="P", study_type="SMS")
        session.add(p)
        await session.flush()
        node = ProtocolNode(
            protocol_id=p.id, task_id="n1",
            task_type=ProtocolTaskType.DEFINE_PICO, label="N1"
        )
        session.add(node)
        await session.flush()
        state = TaskExecutionState(study_id=study.id, node_id=node.id)
        session.add(state)
        await session.flush()
        assert state.status == TaskNodeStatus.PENDING

    async def test_unique_study_node_constraint(self, session) -> None:
        """Verify that two TaskExecutionState rows for the same study+node raise IntegrityError."""
        from sqlalchemy.exc import IntegrityError

        from db.models import Study, StudyType

        study = Study(name="S2", study_type=StudyType.SMS)
        session.add(study)
        p = ResearchProtocol(name="P2", study_type="SMS")
        session.add(p)
        await session.flush()
        node = ProtocolNode(
            protocol_id=p.id, task_id="n1",
            task_type=ProtocolTaskType.DEFINE_PICO, label="N1"
        )
        session.add(node)
        await session.flush()
        session.add(TaskExecutionState(study_id=study.id, node_id=node.id))
        session.add(TaskExecutionState(study_id=study.id, node_id=node.id))
        with pytest.raises(IntegrityError):
            await session.flush()


# ---------------------------------------------------------------------------
# Relationship navigation tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestRelationships:
    """Verify that ORM relationships navigate correctly."""

    async def test_protocol_nodes_relationship(self, session) -> None:
        """Verify that protocol.nodes loads the correct child nodes via selectinload."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        p = ResearchProtocol(name="R", study_type="SMS")
        session.add(p)
        await session.flush()
        n = ProtocolNode(
            protocol_id=p.id, task_id="n1",
            task_type=ProtocolTaskType.DEFINE_PICO, label="N1"
        )
        session.add(n)
        await session.commit()

        result = await session.execute(
            select(ResearchProtocol)
            .options(selectinload(ResearchProtocol.nodes))
            .where(ResearchProtocol.id == p.id)
        )
        loaded = result.scalar_one()
        assert len(loaded.nodes) == 1
        assert loaded.nodes[0].task_id == "n1"
