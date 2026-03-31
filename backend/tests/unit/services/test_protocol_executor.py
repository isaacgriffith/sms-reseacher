"""Unit tests for ProtocolExecutorService and ProtocolAssignmentService (feature 010, T070).

Covers:
- activate_eligible_tasks: node with no incoming edges gets activated
- activate_eligible_tasks: downstream node activated after predecessor completes
- activate_eligible_tasks: node NOT activated if predecessor still PENDING
- assign_protocol: creates correct number of TaskExecutionState rows
- complete_task: transitions task to COMPLETE
- complete_task: raises 409 if task not ACTIVE
"""

from __future__ import annotations

import db.models  # noqa: F401
import db.models.protocols  # noqa: F401
import db.models.study  # noqa: F401
import db.models.users  # noqa: F401
import pytest
import pytest_asyncio
from db.base import Base
from db.models import Study
from db.models.protocols import (
    ProtocolEdge,
    ProtocolNode,
    ProtocolTaskType,
    ResearchProtocol,
    StudyProtocolAssignment,
    TaskExecutionState,
    TaskNodeStatus,
)
from db.models.study import StudyMember, StudyMemberRole
from db.models.users import ResearchGroup, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from backend.services.protocol_executor import (
    ProtocolAssignmentService,
    ProtocolExecutorService,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide an in-memory SQLite session with all protocol tables created."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        yield session
    await engine.dispose()


async def _create_user(session: AsyncSession, email: str) -> User:
    """Insert and return a User row."""
    from backend.core.auth import hash_password

    user = User(email=email, hashed_password=hash_password("pw"), display_name=email)
    session.add(user)
    await session.flush()
    return user


async def _create_study(session: AsyncSession, user: User, study_type: str = "SMS") -> Study:
    """Insert group + study + LEAD membership; return Study."""
    from db.models import StudyType

    group = ResearchGroup(name=f"Group {user.id}")
    session.add(group)
    await session.flush()

    study = Study(
        name=f"Study {user.id}",
        study_type=StudyType(study_type),
        research_group_id=group.id,
        snowball_threshold=3,
    )
    session.add(study)
    await session.flush()

    session.add(StudyMember(study_id=study.id, user_id=user.id, role=StudyMemberRole.LEAD))
    await session.flush()
    return study


async def _create_protocol(
    session: AsyncSession, study_type: str = "SMS", *, is_default: bool = True
) -> ResearchProtocol:
    """Insert and return a ResearchProtocol."""
    protocol = ResearchProtocol(
        name=f"Proto {study_type}",
        study_type=study_type,
        is_default_template=is_default,
    )
    session.add(protocol)
    await session.flush()
    return protocol


async def _create_node(session: AsyncSession, protocol_id: int, task_id: str) -> ProtocolNode:
    """Insert and return a ProtocolNode."""
    node = ProtocolNode(
        protocol_id=protocol_id,
        task_id=task_id,
        task_type=ProtocolTaskType.DEFINE_PICO,
        label=task_id,
    )
    session.add(node)
    await session.flush()
    return node


# ---------------------------------------------------------------------------
# Tests: activate_eligible_tasks
# ---------------------------------------------------------------------------


class TestActivateEligibleTasks:
    """Tests for ProtocolExecutorService.activate_eligible_tasks."""

    @pytest.mark.asyncio
    async def test_activate_no_predecessors(self, db_session: AsyncSession) -> None:
        """Node with no incoming edges is activated immediately."""
        user = await _create_user(db_session, "a@test.com")
        study = await _create_study(db_session, user)
        protocol = await _create_protocol(db_session)
        node = await _create_node(db_session, protocol.id, "task_a")

        db_session.add(StudyProtocolAssignment(study_id=study.id, protocol_id=protocol.id))
        state = TaskExecutionState(
            study_id=study.id, node_id=node.id, status=TaskNodeStatus.PENDING
        )
        db_session.add(state)
        await db_session.flush()

        svc = ProtocolExecutorService()
        activated = await svc.activate_eligible_tasks(study.id, db_session)

        assert "task_a" in activated
        result = (
            await db_session.execute(
                select(TaskExecutionState).where(TaskExecutionState.study_id == study.id)
            )
        ).scalar_one()
        assert result.status == TaskNodeStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_activate_with_complete_predecessor(self, db_session: AsyncSession) -> None:
        """Downstream node activated when its predecessor is COMPLETE."""
        user = await _create_user(db_session, "b@test.com")
        study = await _create_study(db_session, user)
        protocol = await _create_protocol(db_session)
        node_a = await _create_node(db_session, protocol.id, "task_a")
        node_b = await _create_node(db_session, protocol.id, "task_b")

        db_session.add(
            ProtocolEdge(
                protocol_id=protocol.id,
                edge_id="e1",
                source_node_id=node_a.id,
                source_output_name="out",
                target_node_id=node_b.id,
                target_input_name="in",
            )
        )
        db_session.add(StudyProtocolAssignment(study_id=study.id, protocol_id=protocol.id))
        db_session.add(
            TaskExecutionState(study_id=study.id, node_id=node_a.id, status=TaskNodeStatus.COMPLETE)
        )
        db_session.add(
            TaskExecutionState(study_id=study.id, node_id=node_b.id, status=TaskNodeStatus.PENDING)
        )
        await db_session.flush()

        svc = ProtocolExecutorService()
        activated = await svc.activate_eligible_tasks(study.id, db_session)

        assert "task_b" in activated

    @pytest.mark.asyncio
    async def test_no_activate_pending_predecessor(self, db_session: AsyncSession) -> None:
        """Downstream node is NOT activated when predecessor is still PENDING."""
        user = await _create_user(db_session, "c@test.com")
        study = await _create_study(db_session, user)
        protocol = await _create_protocol(db_session)
        node_a = await _create_node(db_session, protocol.id, "task_a")
        node_b = await _create_node(db_session, protocol.id, "task_b")

        db_session.add(
            ProtocolEdge(
                protocol_id=protocol.id,
                edge_id="e1",
                source_node_id=node_a.id,
                source_output_name="out",
                target_node_id=node_b.id,
                target_input_name="in",
            )
        )
        db_session.add(StudyProtocolAssignment(study_id=study.id, protocol_id=protocol.id))
        db_session.add(
            TaskExecutionState(study_id=study.id, node_id=node_a.id, status=TaskNodeStatus.PENDING)
        )
        db_session.add(
            TaskExecutionState(study_id=study.id, node_id=node_b.id, status=TaskNodeStatus.PENDING)
        )
        await db_session.flush()

        svc = ProtocolExecutorService()
        activated = await svc.activate_eligible_tasks(study.id, db_session)

        # task_a has no predecessors → activated. task_b has pending pred → not activated.
        assert "task_b" not in activated


# ---------------------------------------------------------------------------
# Tests: assign_protocol creates states
# ---------------------------------------------------------------------------


class TestAssignProtocol:
    """Tests for ProtocolAssignmentService.assign_protocol."""

    @pytest.mark.asyncio
    async def test_assign_protocol_creates_states(self, db_session: AsyncSession) -> None:
        """assign_protocol creates one TaskExecutionState per protocol node."""
        user = await _create_user(db_session, "d@test.com")
        study = await _create_study(db_session, user)
        protocol = await _create_protocol(db_session)
        await _create_node(db_session, protocol.id, "n1")
        await _create_node(db_session, protocol.id, "n2")
        await _create_node(db_session, protocol.id, "n3")
        await db_session.commit()

        svc = ProtocolAssignmentService()
        assignment = await svc.assign_protocol(study.id, protocol.id, user.id, db_session)

        assert assignment.protocol_id == protocol.id

        states = (
            (
                await db_session.execute(
                    select(TaskExecutionState).where(TaskExecutionState.study_id == study.id)
                )
            )
            .scalars()
            .all()
        )
        assert len(states) == 3


# ---------------------------------------------------------------------------
# Tests: complete_task
# ---------------------------------------------------------------------------


class TestCompleteTask:
    """Tests for ProtocolExecutorService.complete_task."""

    @pytest.mark.asyncio
    async def test_complete_task_transitions_to_complete(self, db_session: AsyncSession) -> None:
        """complete_task sets status to COMPLETE."""
        user = await _create_user(db_session, "e@test.com")
        study = await _create_study(db_session, user)
        protocol = await _create_protocol(db_session)
        node = await _create_node(db_session, protocol.id, "task_x")

        db_session.add(StudyProtocolAssignment(study_id=study.id, protocol_id=protocol.id))
        db_session.add(
            TaskExecutionState(study_id=study.id, node_id=node.id, status=TaskNodeStatus.ACTIVE)
        )
        await db_session.commit()

        svc = ProtocolExecutorService()
        result = await svc.complete_task(study.id, "task_x", db_session)

        assert result["completed_task_id"] == "task_x"
        assert result["gate_result"] == "passed"

        state = (
            await db_session.execute(
                select(TaskExecutionState).where(TaskExecutionState.study_id == study.id)
            )
        ).scalar_one()
        assert state.status == TaskNodeStatus.COMPLETE

    @pytest.mark.asyncio
    async def test_complete_task_409_if_not_active(self, db_session: AsyncSession) -> None:
        """complete_task raises 409 if task is not ACTIVE."""
        from fastapi import HTTPException

        user = await _create_user(db_session, "f@test.com")
        study = await _create_study(db_session, user)
        protocol = await _create_protocol(db_session)
        node = await _create_node(db_session, protocol.id, "task_y")

        db_session.add(StudyProtocolAssignment(study_id=study.id, protocol_id=protocol.id))
        db_session.add(
            TaskExecutionState(study_id=study.id, node_id=node.id, status=TaskNodeStatus.PENDING)
        )
        await db_session.commit()

        svc = ProtocolExecutorService()
        with pytest.raises(HTTPException) as exc_info:
            await svc.complete_task(study.id, "task_y", db_session)

        assert exc_info.value.status_code == 409


# ---------------------------------------------------------------------------
# Tests: gate evaluation (T078)
# ---------------------------------------------------------------------------


class TestGateEvaluation:
    """Unit tests for quality gate evaluation and REMEDIATION_MESSAGES."""

    def test_remediation_messages_covers_all_metric_names(self) -> None:
        """REMEDIATION_MESSAGES has entries for all documented metric names."""
        from backend.services.protocol_executor import REMEDIATION_MESSAGES

        expected = {"kappa_coefficient", "accepted_paper_count", "test_set_recall", "coverage_recall"}
        assert expected.issubset(set(REMEDIATION_MESSAGES.keys()))

    @pytest.mark.asyncio
    async def test_metric_threshold_gate_pass(self, db_session: AsyncSession) -> None:
        """metric_threshold gate passes when metric satisfies threshold."""
        from unittest.mock import AsyncMock, patch

        from backend.services.protocol_executor import _eval_metric_threshold
        from db.models.protocols import QualityGate, QualityGateType

        gate = QualityGate(
            gate_type=QualityGateType.METRIC_THRESHOLD,
            config={"metric_name": "kappa_coefficient", "operator": "gte", "threshold": 0.6},
        )
        mock_reader = AsyncMock(return_value=0.75)
        with patch.dict(
            "backend.services.protocol_executor._METRIC_READERS",
            {"kappa_coefficient": mock_reader},
        ):
            result = await _eval_metric_threshold(gate, 1, db_session)

        assert result.passed is True
        assert result.detail is None

    @pytest.mark.asyncio
    async def test_metric_threshold_gate_fail(self, db_session: AsyncSession) -> None:
        """metric_threshold gate fails when metric is below threshold."""
        from unittest.mock import AsyncMock, patch

        from backend.services.protocol_executor import REMEDIATION_MESSAGES, _eval_metric_threshold
        from db.models.protocols import QualityGate, QualityGateType

        gate = QualityGate(
            gate_type=QualityGateType.METRIC_THRESHOLD,
            config={"metric_name": "kappa_coefficient", "operator": "gte", "threshold": 0.6},
        )
        mock_reader = AsyncMock(return_value=0.42)
        with patch.dict(
            "backend.services.protocol_executor._METRIC_READERS",
            {"kappa_coefficient": mock_reader},
        ):
            result = await _eval_metric_threshold(gate, 1, db_session)

        assert result.passed is False
        assert result.detail is not None
        assert result.detail["measured_value"] == 0.42
        assert result.detail["threshold"] == 0.6
        assert result.detail["remediation"] == REMEDIATION_MESSAGES["kappa_coefficient"]

    @pytest.mark.asyncio
    async def test_completion_check_gate_always_passes(self, db_session: AsyncSession) -> None:
        """completion_check gate always returns passed=True."""
        from backend.services.protocol_executor import _eval_completion_check
        from db.models.protocols import QualityGate, QualityGateType

        gate = QualityGate(
            gate_type=QualityGateType.COMPLETION_CHECK,
            config={"description": "All papers reviewed"},
        )
        result = await _eval_completion_check(gate, 1, db_session)
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_human_sign_off_gate_always_fails(self, db_session: AsyncSession) -> None:
        """human_sign_off gate always returns passed=False until approved."""
        from backend.services.protocol_executor import _eval_human_sign_off
        from db.models.protocols import QualityGate, QualityGateType

        gate = QualityGate(
            gate_type=QualityGateType.HUMAN_SIGN_OFF,
            config={"required_role": "study_admin", "prompt": "Confirm"},
        )
        result = await _eval_human_sign_off(gate, 1, db_session)
        assert result.passed is False
        assert result.detail is not None
        assert result.detail["gate_type"] == "human_sign_off"

    @pytest.mark.asyncio
    async def test_complete_task_gate_failure_sets_gate_failed(
        self, db_session: AsyncSession
    ) -> None:
        """complete_task sets GATE_FAILED when a metric_threshold gate fails."""
        from unittest.mock import AsyncMock, patch

        from db.models.protocols import QualityGate, QualityGateType

        user = await _create_user(db_session, "g@test.com")
        study = await _create_study(db_session, user)
        protocol = await _create_protocol(db_session)
        node = await _create_node(db_session, protocol.id, "task_kappa")

        db_session.add(
            QualityGate(
                node_id=node.id,
                gate_type=QualityGateType.METRIC_THRESHOLD,
                config={"metric_name": "kappa_coefficient", "operator": "gte", "threshold": 0.6},
            )
        )
        db_session.add(StudyProtocolAssignment(study_id=study.id, protocol_id=protocol.id))
        db_session.add(
            TaskExecutionState(
                study_id=study.id, node_id=node.id, status=TaskNodeStatus.ACTIVE
            )
        )
        await db_session.commit()

        svc = ProtocolExecutorService()
        with patch(
            "backend.services.protocol_executor._read_kappa",
            new=AsyncMock(return_value=0.42),
        ):
            result = await svc.complete_task(study.id, "task_kappa", db_session)

        assert result["gate_result"] == "failed"
        assert result["gate_failure_detail"] is not None
        assert result["gate_failure_detail"]["metric_name"] == "kappa_coefficient"

        state = (
            await db_session.execute(
                select(TaskExecutionState).where(TaskExecutionState.study_id == study.id)
            )
        ).scalar_one()
        assert state.status == TaskNodeStatus.GATE_FAILED

    @pytest.mark.asyncio
    async def test_approve_task_clears_human_sign_off(self, db_session: AsyncSession) -> None:
        """approve_task clears GATE_FAILED and sets COMPLETE for human_sign_off gate."""
        user = await _create_user(db_session, "h@test.com")
        study = await _create_study(db_session, user)
        protocol = await _create_protocol(db_session)
        node = await _create_node(db_session, protocol.id, "task_sign")

        db_session.add(StudyProtocolAssignment(study_id=study.id, protocol_id=protocol.id))
        db_session.add(
            TaskExecutionState(
                study_id=study.id,
                node_id=node.id,
                status=TaskNodeStatus.GATE_FAILED,
                gate_failure_detail={"gate_type": "human_sign_off", "prompt": "Confirm"},
            )
        )
        await db_session.commit()

        svc = ProtocolExecutorService()
        result = await svc.approve_task(study.id, "task_sign", db_session)

        assert result["gate_result"] == "passed"

        state = (
            await db_session.execute(
                select(TaskExecutionState).where(TaskExecutionState.study_id == study.id)
            )
        ).scalar_one()
        assert state.status == TaskNodeStatus.COMPLETE
        assert state.gate_failure_detail is None
