"""Integration tests for protocol assignment and execution endpoints (feature 010, T069).

Covers:
- PUT /studies/{study_id}/protocol-assignment by LEAD succeeds → 200
- PUT /studies/{study_id}/protocol-assignment by non-LEAD member → 403
- PUT /studies/{study_id}/protocol-assignment with type mismatch → 400
- GET /studies/{study_id}/execution-state → 200 with tasks list
- GET /studies/{study_id}/execution-state for non-member → 403
- POST /studies/{study_id}/execution-state/{task_id}/complete → 200
- POST /studies/{study_id}/execution-state/{task_id}/complete when not ACTIVE → 409
- POST /studies/{study_id}/execution-state/{task_id}/complete by non-admin → 403
"""

from __future__ import annotations

import pytest
from db.models.protocols import (
    NodeAssignee,
    NodeAssigneeType,
    ProtocolNode,
    ProtocolTaskType,
    ResearchProtocol,
    StudyProtocolAssignment,
    TaskExecutionState,
    TaskNodeStatus,
)
from db.models.study import StudyMember, StudyMemberRole
from db.models.users import GroupMembership, GroupRole, ResearchGroup
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token


def _bearer(user_id: int) -> dict[str, str]:
    """Return Bearer token header for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study_and_protocol(
    client,
    db_engine,
    lead_user,
    study_type: str = "SMS",
    protocol_study_type: str = "SMS",
) -> tuple[int, int]:
    """Create group + study + protocol; return (study_id, protocol_id).

    The lead_user becomes the study LEAD.
    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name=f"Exec Group {lead_user.id}")
        session.add(group)
        await session.flush()
        session.add(GroupMembership(group_id=group.id, user_id=lead_user.id, role=GroupRole.ADMIN))
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": f"Exec Study {lead_user.id}",
            "topic": "Test",
            "study_type": study_type,
            "research_objectives": [],
            "research_questions": [],
        },
        headers=_bearer(lead_user.id),
    )
    assert resp.status_code == 201, resp.text
    study_id = resp.json()["id"]

    async with maker() as session:
        protocol = ResearchProtocol(
            name=f"Test Protocol {lead_user.id} {protocol_study_type}",
            study_type=protocol_study_type,
            is_default_template=True,
        )
        session.add(protocol)
        await session.commit()
        await session.refresh(protocol)
        return study_id, protocol.id


async def _add_node_and_assign(
    db_engine,
    study_id: int,
    protocol_id: int,
    task_id: str = "task_1",
    *,
    with_human_assignee: bool = False,
) -> tuple[int, int]:
    """Add ProtocolNode + StudyProtocolAssignment + TaskExecutionState rows."""
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        node = ProtocolNode(
            protocol_id=protocol_id,
            task_id=task_id,
            task_type=ProtocolTaskType.DEFINE_PICO,
            label="Define PICO",
        )
        session.add(node)
        await session.flush()

        if with_human_assignee:
            session.add(
                NodeAssignee(
                    node_id=node.id,
                    assignee_type=NodeAssigneeType.HUMAN_ROLE,
                    role="researcher",
                )
            )

        assignment = StudyProtocolAssignment(
            study_id=study_id,
            protocol_id=protocol_id,
        )
        session.add(assignment)
        await session.flush()

        state = TaskExecutionState(
            study_id=study_id,
            node_id=node.id,
            status=TaskNodeStatus.ACTIVE,
        )
        session.add(state)
        await session.commit()
        await session.refresh(node)
        await session.refresh(state)
        return node.id, state.id


class TestAssignProtocol:
    """PUT /studies/{study_id}/protocol-assignment endpoint tests."""

    @pytest.mark.asyncio
    async def test_assign_protocol_success(self, client, db_engine, alice) -> None:
        """PUT by LEAD returns 200 with assignment data."""
        alice_user, _ = alice
        study_id, protocol_id = await _setup_study_and_protocol(client, db_engine, alice_user)

        resp = await client.put(
            f"/api/v1/studies/{study_id}/protocol-assignment",
            json={"protocol_id": protocol_id},
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["study_id"] == study_id
        assert data["protocol_id"] == protocol_id

    @pytest.mark.asyncio
    async def test_assign_protocol_403_non_admin(self, client, db_engine, alice, bob) -> None:
        """PUT by non-LEAD study member returns 403."""
        alice_user, _ = alice
        bob_user, _ = bob
        study_id, protocol_id = await _setup_study_and_protocol(client, db_engine, alice_user)

        # Add bob as a MEMBER (not LEAD)
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            session.add(
                StudyMember(
                    study_id=study_id,
                    user_id=bob_user.id,
                    role=StudyMemberRole.MEMBER,
                )
            )
            await session.commit()

        resp = await client.put(
            f"/api/v1/studies/{study_id}/protocol-assignment",
            json={"protocol_id": protocol_id},
            headers=_bearer(bob_user.id),
        )

        assert resp.status_code == 403, resp.text

    @pytest.mark.asyncio
    async def test_assign_protocol_400_type_mismatch(self, client, db_engine, alice) -> None:
        """PUT with protocol whose study_type != study.study_type returns 400."""
        alice_user, _ = alice
        study_id, _ = await _setup_study_and_protocol(
            client, db_engine, alice_user, study_type="SMS", protocol_study_type="SMS"
        )
        # Create an SLR protocol directly in DB (no study creation to avoid unique group name)
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            slr_protocol = ResearchProtocol(
                name="SLR Protocol for mismatch test",
                study_type="SLR",
                is_default_template=True,
            )
            session.add(slr_protocol)
            await session.commit()
            await session.refresh(slr_protocol)
            slr_protocol_id = slr_protocol.id

        resp = await client.put(
            f"/api/v1/studies/{study_id}/protocol-assignment",
            json={"protocol_id": slr_protocol_id},
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 400, resp.text


class TestGetExecutionState:
    """GET /studies/{study_id}/execution-state endpoint tests."""

    @pytest.mark.asyncio
    async def test_get_execution_state_success(self, client, db_engine, alice) -> None:
        """GET returns 200 with task list after assignment."""
        alice_user, _ = alice
        study_id, protocol_id = await _setup_study_and_protocol(client, db_engine, alice_user)
        await _add_node_and_assign(db_engine, study_id, protocol_id)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/execution-state",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["study_id"] == study_id
        assert isinstance(data["tasks"], list)
        assert len(data["tasks"]) >= 1

    @pytest.mark.asyncio
    async def test_get_execution_state_403_non_member(self, client, db_engine, alice, bob) -> None:
        """GET by non-member returns 403."""
        alice_user, _ = alice
        bob_user, _ = bob
        study_id, protocol_id = await _setup_study_and_protocol(client, db_engine, alice_user)
        await _add_node_and_assign(db_engine, study_id, protocol_id)

        resp = await client.get(
            f"/api/v1/studies/{study_id}/execution-state",
            headers=_bearer(bob_user.id),
        )

        assert resp.status_code == 403, resp.text


class TestCompleteTask:
    """POST /studies/{study_id}/execution-state/{task_id}/complete endpoint tests."""

    @pytest.mark.asyncio
    async def test_complete_task_success(self, client, db_engine, alice) -> None:
        """POST by LEAD completes an ACTIVE task and returns 200."""
        alice_user, _ = alice
        study_id, protocol_id = await _setup_study_and_protocol(client, db_engine, alice_user)
        await _add_node_and_assign(db_engine, study_id, protocol_id, task_id="task_1")

        resp = await client.post(
            f"/api/v1/studies/{study_id}/execution-state/task_1/complete",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["completed_task_id"] == "task_1"
        assert data["gate_result"] == "passed"

    @pytest.mark.asyncio
    async def test_complete_task_409_not_active(self, client, db_engine, alice) -> None:
        """POST on a PENDING (not ACTIVE) task returns 409."""
        alice_user, _ = alice
        study_id, protocol_id = await _setup_study_and_protocol(client, db_engine, alice_user)

        # Create a node and assignment with PENDING status
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            node = ProtocolNode(
                protocol_id=protocol_id,
                task_id="pending_task",
                task_type=ProtocolTaskType.DEFINE_PICO,
                label="Pending Task",
            )
            session.add(node)
            await session.flush()

            session.add(StudyProtocolAssignment(study_id=study_id, protocol_id=protocol_id))
            session.add(
                TaskExecutionState(
                    study_id=study_id,
                    node_id=node.id,
                    status=TaskNodeStatus.PENDING,
                )
            )
            await session.commit()

        resp = await client.post(
            f"/api/v1/studies/{study_id}/execution-state/pending_task/complete",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 409, resp.text

    @pytest.mark.asyncio
    async def test_complete_task_403_non_admin(self, client, db_engine, alice, bob) -> None:
        """POST by member without human assignee returns 403."""
        alice_user, _ = alice
        bob_user, _ = bob
        study_id, protocol_id = await _setup_study_and_protocol(client, db_engine, alice_user)
        await _add_node_and_assign(
            db_engine, study_id, protocol_id, task_id="task_no_assign", with_human_assignee=False
        )

        # Add bob as a MEMBER
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            session.add(
                StudyMember(
                    study_id=study_id,
                    user_id=bob_user.id,
                    role=StudyMemberRole.MEMBER,
                )
            )
            await session.commit()

        resp = await client.post(
            f"/api/v1/studies/{study_id}/execution-state/task_no_assign/complete",
            headers=_bearer(bob_user.id),
        )

        assert resp.status_code == 403, resp.text


# ---------------------------------------------------------------------------
# Tests: gate failure + approve (T079)
# ---------------------------------------------------------------------------


async def _add_metric_gate_node_and_assign(
    db_engine, study_id: int, protocol_id: int, task_id: str = "gate_task"
) -> None:
    """Add a node with a metric_threshold gate and an ACTIVE TaskExecutionState."""
    from db.models.protocols import QualityGate, QualityGateType

    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        node = ProtocolNode(
            protocol_id=protocol_id,
            task_id=task_id,
            task_type=ProtocolTaskType.SCREEN_PAPERS,
            label=task_id,
        )
        session.add(node)
        await session.flush()
        session.add(
            QualityGate(
                node_id=node.id,
                gate_type=QualityGateType.METRIC_THRESHOLD,
                config={"metric_name": "kappa_coefficient", "operator": "gte", "threshold": 0.6},
            )
        )
        existing = await session.execute(
            StudyProtocolAssignment.__table__.select().where(
                StudyProtocolAssignment.__table__.c.study_id == study_id
            )
        )
        if existing.first() is None:
            session.add(StudyProtocolAssignment(study_id=study_id, protocol_id=protocol_id))
        session.add(TaskExecutionState(study_id=study_id, node_id=node.id, status=TaskNodeStatus.ACTIVE))
        await session.commit()
        return node.id


async def _add_human_gate_node_and_assign(
    db_engine, study_id: int, protocol_id: int, task_id: str = "human_task"
) -> None:
    """Add a node with a human_sign_off gate and a GATE_FAILED TaskExecutionState."""
    from db.models.protocols import QualityGate, QualityGateType

    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        node = ProtocolNode(
            protocol_id=protocol_id,
            task_id=task_id,
            task_type=ProtocolTaskType.SCREEN_PAPERS,
            label=task_id,
        )
        session.add(node)
        await session.flush()
        session.add(
            QualityGate(
                node_id=node.id,
                gate_type=QualityGateType.HUMAN_SIGN_OFF,
                config={"required_role": "study_admin", "prompt": "Confirm"},
            )
        )
        existing = await session.execute(
            StudyProtocolAssignment.__table__.select().where(
                StudyProtocolAssignment.__table__.c.study_id == study_id
            )
        )
        if existing.first() is None:
            session.add(StudyProtocolAssignment(study_id=study_id, protocol_id=protocol_id))
        session.add(
            TaskExecutionState(
                study_id=study_id,
                node_id=node.id,
                status=TaskNodeStatus.GATE_FAILED,
                gate_failure_detail={"gate_type": "human_sign_off", "prompt": "Confirm"},
            )
        )
        await session.commit()


class TestGateFailureAndApprove:
    """Integration tests for gate failure + approve endpoints (T079)."""

    @pytest.mark.asyncio
    async def test_complete_task_with_failing_kappa_gate(
        self, client, db_engine, alice
    ) -> None:
        """complete_task with failing kappa gate returns 200 with gate_result=failed."""
        from unittest.mock import AsyncMock, patch

        alice_user, _ = alice
        study_id, protocol_id = await _setup_study_and_protocol(client, db_engine, alice_user)
        await _add_metric_gate_node_and_assign(db_engine, study_id, protocol_id, "kappa_task")

        with patch.dict(
            "backend.services.protocol_executor._METRIC_READERS",
            {"kappa_coefficient": AsyncMock(return_value=0.42)},
        ):
            resp = await client.post(
                f"/api/v1/studies/{study_id}/execution-state/kappa_task/complete",
                headers=_bearer(alice_user.id),
            )

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["gate_result"] == "failed"
        assert data["gate_failure_detail"]["metric_name"] == "kappa_coefficient"
        assert data["gate_failure_detail"]["measured_value"] == 0.42

    @pytest.mark.asyncio
    async def test_complete_task_gate_failed_status_in_db(
        self, client, db_engine, alice
    ) -> None:
        """Task status is GATE_FAILED in DB after failing gate."""
        from unittest.mock import AsyncMock, patch
        from sqlalchemy import select as sa_select

        alice_user, _ = alice
        study_id, protocol_id = await _setup_study_and_protocol(client, db_engine, alice_user)
        await _add_metric_gate_node_and_assign(db_engine, study_id, protocol_id, "kappa_task2")

        with patch.dict(
            "backend.services.protocol_executor._METRIC_READERS",
            {"kappa_coefficient": AsyncMock(return_value=0.10)},
        ):
            await client.post(
                f"/api/v1/studies/{study_id}/execution-state/kappa_task2/complete",
                headers=_bearer(alice_user.id),
            )

        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            node_result = await session.execute(
                sa_select(ProtocolNode).where(ProtocolNode.task_id == "kappa_task2")
            )
            node = node_result.scalar_one()
            state_result = await session.execute(
                sa_select(TaskExecutionState).where(
                    TaskExecutionState.study_id == study_id,
                    TaskExecutionState.node_id == node.id,
                )
            )
            state = state_result.scalar_one()
            assert state.status == TaskNodeStatus.GATE_FAILED

    @pytest.mark.asyncio
    async def test_approve_by_admin_succeeds(self, client, db_engine, alice) -> None:
        """approve by study LEAD succeeds → 200 with gate_result=passed."""
        alice_user, _ = alice
        study_id, protocol_id = await _setup_study_and_protocol(client, db_engine, alice_user)
        await _add_human_gate_node_and_assign(db_engine, study_id, protocol_id, "human_approve")

        resp = await client.post(
            f"/api/v1/studies/{study_id}/execution-state/human_approve/approve",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["gate_result"] == "passed"

    @pytest.mark.asyncio
    async def test_approve_by_non_admin_returns_403(
        self, client, db_engine, alice, bob
    ) -> None:
        """approve by non-LEAD returns 403."""
        alice_user, _ = alice
        bob_user, _ = bob
        study_id, protocol_id = await _setup_study_and_protocol(client, db_engine, alice_user)
        await _add_human_gate_node_and_assign(db_engine, study_id, protocol_id, "human_403")

        resp = await client.post(
            f"/api/v1/studies/{study_id}/execution-state/human_403/approve",
            headers=_bearer(bob_user.id),
        )

        assert resp.status_code == 403, resp.text

    @pytest.mark.asyncio
    async def test_approve_non_gate_failed_task_returns_409(
        self, client, db_engine, alice
    ) -> None:
        """approve on a task that is not GATE_FAILED returns 409."""
        alice_user, _ = alice
        study_id, protocol_id = await _setup_study_and_protocol(client, db_engine, alice_user)
        await _add_node_and_assign(db_engine, study_id, protocol_id, task_id="active_task_approve")

        # task is ACTIVE, not GATE_FAILED
        resp = await client.post(
            f"/api/v1/studies/{study_id}/execution-state/active_task_approve/approve",
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 409, resp.text


class TestResetProtocolAssignment:
    """DELETE /studies/{study_id}/protocol-assignment (T092)."""

    @pytest.mark.asyncio
    async def test_reset_by_lead_returns_new_default_assignment(
        self, client, db_engine, alice
    ) -> None:
        """LEAD calling DELETE with confirm_reset=True resets to default template."""
        alice_user, _ = alice
        # _setup_study_and_protocol creates a default template and assigns it
        study_id, _ = await _setup_study_and_protocol(client, db_engine, alice_user)

        resp = await client.request("DELETE",             f"/api/v1/studies/{study_id}/protocol-assignment",
            json={"confirm_reset": True},
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["study_id"] == study_id
        assert data["is_default_template"] is True

    @pytest.mark.asyncio
    async def test_reset_without_confirm_returns_400(
        self, client, db_engine, alice
    ) -> None:
        """Sending confirm_reset=False (or omitting it) returns 400."""
        alice_user, _ = alice
        study_id, _ = await _setup_study_and_protocol(client, db_engine, alice_user)

        resp = await client.request("DELETE",             f"/api/v1/studies/{study_id}/protocol-assignment",
            json={"confirm_reset": False},
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 400, resp.text

    @pytest.mark.asyncio
    async def test_reset_by_non_lead_returns_403(
        self, client, db_engine, alice, bob
    ) -> None:
        """Non-LEAD member calling DELETE returns 403."""
        alice_user, _ = alice
        bob_user, _ = bob
        study_id, _ = await _setup_study_and_protocol(client, db_engine, alice_user)

        resp = await client.request("DELETE",             f"/api/v1/studies/{study_id}/protocol-assignment",
            json={"confirm_reset": True},
            headers=_bearer(bob_user.id),
        )

        assert resp.status_code == 403, resp.text

    @pytest.mark.asyncio
    async def test_reset_while_active_task_returns_409(
        self, client, db_engine, alice
    ) -> None:
        """DELETE returns 409 when any task is currently ACTIVE."""
        alice_user, _ = alice
        study_id, protocol_id = await _setup_study_and_protocol(client, db_engine, alice_user)
        # _add_node_and_assign creates a node in ACTIVE status
        await _add_node_and_assign(db_engine, study_id, protocol_id, task_id="active_for_reset")

        resp = await client.request("DELETE",             f"/api/v1/studies/{study_id}/protocol-assignment",
            json={"confirm_reset": True},
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 409, resp.text

    @pytest.mark.asyncio
    async def test_reset_clears_old_execution_states(
        self, client, db_engine, alice
    ) -> None:
        """After reset, old completed tasks from a custom protocol are gone."""
        alice_user, _ = alice
        # _setup creates a default template with no nodes.
        study_id, default_protocol_id = await _setup_study_and_protocol(
            client, db_engine, alice_user
        )

        # Create a separate *custom* protocol with a COMPLETED task and assign it.
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            custom_protocol = ResearchProtocol(
                name="Custom Before Reset",
                study_type="SMS",
                is_default_template=False,
                owner_user_id=alice_user.id,
            )
            session.add(custom_protocol)
            await session.flush()

            node = ProtocolNode(
                protocol_id=custom_protocol.id,
                task_id="completed_before_reset",
                task_type=ProtocolTaskType.DEFINE_PICO,
                label="Old Completed Task",
            )
            session.add(node)
            await session.flush()

            # Replace the assignment to point to the custom protocol
            result = await session.execute(
                select(StudyProtocolAssignment).where(
                    StudyProtocolAssignment.study_id == study_id
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                existing.protocol_id = custom_protocol.id
            else:
                session.add(
                    StudyProtocolAssignment(
                        study_id=study_id, protocol_id=custom_protocol.id
                    )
                )

            # Clear existing task states from the default assignment
            await session.execute(
                delete(TaskExecutionState).where(
                    TaskExecutionState.study_id == study_id
                )
            )
            state = TaskExecutionState(
                study_id=study_id,
                node_id=node.id,
                status=TaskNodeStatus.COMPLETE,
            )
            session.add(state)
            await session.commit()

        resp = await client.request(
            "DELETE",
            f"/api/v1/studies/{study_id}/protocol-assignment",
            json={"confirm_reset": True},
            headers=_bearer(alice_user.id),
        )

        assert resp.status_code == 200, resp.text

        # Verify old COMPLETE state from custom protocol is gone
        exec_resp = await client.get(
            f"/api/v1/studies/{study_id}/execution-state",
            headers=_bearer(alice_user.id),
        )
        assert exec_resp.status_code == 200
        tasks = exec_resp.json()["tasks"]
        old_ids = {t["task_id"] for t in tasks}
        assert "completed_before_reset" not in old_ids
