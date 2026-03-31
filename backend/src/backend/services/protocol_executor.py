"""Protocol execution engine for Research Protocol Definition (feature 010).

Handles advancing task execution state through protocol graphs, evaluating
quality gate conditions, and updating node statuses.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog
from db.models import Study
from db.models.protocols import (
    ProtocolEdge,
    ProtocolNode,
    QualityGate,
    QualityGateType,
    ResearchProtocol,
    StudyProtocolAssignment,
    TaskExecutionState,
    TaskNodeStatus,
)
from db.models.study import StudyMember, StudyMemberRole
from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# T072 — Remediation messages per metric name
# ---------------------------------------------------------------------------

REMEDIATION_MESSAGES: dict[str, str] = {
    "kappa_coefficient": (
        "Conduct a reconciliation round between reviewers and re-screen disputed papers."
    ),
    "accepted_paper_count": (
        "Review exclusion criteria or broaden the search string to capture more relevant papers."
    ),
    "test_set_recall": ("Expand the search string with additional synonyms and re-run the search."),
    "coverage_recall": ("Add missed papers as seed papers for a snowball round."),
}


# ---------------------------------------------------------------------------
# T071 — Gate result dataclass
# ---------------------------------------------------------------------------


@dataclass
class GateResult:
    """Result of evaluating one or more quality gates on a task node.

    Attributes:
        passed: ``True`` when all gates pass; ``False`` on the first failure.
        detail: Gate failure detail dict (populated on failure, ``None`` on pass).

    """

    passed: bool
    detail: dict | None = field(default=None)


# ---------------------------------------------------------------------------
# T073 — Metric readers (async, ≤ 20 lines each)
# ---------------------------------------------------------------------------


async def _read_kappa(study_id: int, db: AsyncSession) -> float | None:
    """Return most recent kappa_value from InterRaterAgreementRecord, or None."""
    from db.models.slr import InterRaterAgreementRecord

    result = await db.execute(
        select(InterRaterAgreementRecord.kappa_value)
        .where(InterRaterAgreementRecord.study_id == study_id)
        .order_by(InterRaterAgreementRecord.id.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _read_accepted_paper_count(study_id: int, db: AsyncSession) -> float | None:
    """Return count of accepted CandidatePaper rows for the study."""
    from db.models.candidate import CandidatePaper, CandidatePaperStatus

    result = await db.execute(
        select(func.count())
        .select_from(CandidatePaper)
        .where(
            CandidatePaper.study_id == study_id,
            CandidatePaper.current_status == CandidatePaperStatus.ACCEPTED,
        )
    )
    count = result.scalar_one()
    return float(count)


async def _read_test_set_recall(study_id: int, db: AsyncSession) -> float | None:
    """Return most recent test_set_recall from SearchStringIteration, or None."""
    from db.models.search import SearchString, SearchStringIteration

    result = await db.execute(
        select(SearchStringIteration.test_set_recall)
        .join(SearchString, SearchStringIteration.search_string_id == SearchString.id)
        .where(SearchString.study_id == study_id)
        .order_by(SearchStringIteration.id.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _read_coverage_recall(study_id: int, db: AsyncSession) -> float | None:
    """Return None — coverage recall is not tracked in the current system."""
    return None


#: Dispatch dict mapping metric_name → async reader function.
_METRIC_READERS: dict[str, Callable] = {
    "kappa_coefficient": _read_kappa,
    "accepted_paper_count": _read_accepted_paper_count,
    "test_set_recall": _read_test_set_recall,
    "coverage_recall": _read_coverage_recall,
}


# ---------------------------------------------------------------------------
# T071 — Gate evaluator strategies
# ---------------------------------------------------------------------------


async def _eval_metric_threshold(gate: QualityGate, study_id: int, db: AsyncSession) -> GateResult:
    """Evaluate a metric_threshold gate.

    Reads the named metric and compares it against the threshold using the
    configured operator.  If the metric is unavailable, the gate fails.

    Args:
        gate: The :class:`~db.models.protocols.QualityGate` to evaluate.
        study_id: Study whose data is read.
        db: Active async database session.

    Returns:
        :class:`GateResult` with ``passed=True`` if the metric satisfies the threshold.

    """
    cfg = gate.config or {}
    metric_name: str = cfg.get("metric_name", "")
    threshold: float = float(cfg.get("threshold", 0.0))
    operator: str = cfg.get("operator", "gte")

    reader = _METRIC_READERS.get(metric_name)
    measured: float | None = await reader(study_id, db) if reader else None

    _OPS: dict[str, Callable[[float, float], bool]] = {
        "gt": lambda m, t: m > t,
        "gte": lambda m, t: m >= t,
        "lt": lambda m, t: m < t,
        "lte": lambda m, t: m <= t,
        "eq": lambda m, t: m == t,
        "neq": lambda m, t: m != t,
    }
    op_fn = _OPS.get(operator, lambda m, t: m >= t)

    if measured is None or not op_fn(measured, threshold):
        return GateResult(
            passed=False,
            detail={
                "gate_type": "metric_threshold",
                "metric_name": metric_name,
                "measured_value": measured,
                "threshold": threshold,
                "operator": operator,
                "remediation": REMEDIATION_MESSAGES.get(metric_name, ""),
            },
        )
    return GateResult(passed=True)


async def _eval_completion_check(gate: QualityGate, study_id: int, db: AsyncSession) -> GateResult:
    """Evaluate a completion_check gate.

    Completion check gates always pass — the act of the researcher marking the
    task complete is the completion check.

    Args:
        gate: The quality gate (unused, present for signature uniformity).
        study_id: Study ID (unused).
        db: Database session (unused).

    Returns:
        :class:`GateResult` with ``passed=True``.

    """
    return GateResult(passed=True)


async def _eval_human_sign_off(gate: QualityGate, study_id: int, db: AsyncSession) -> GateResult:
    """Evaluate a human_sign_off gate.

    Human sign-off gates always fail until the study admin explicitly calls
    the ``/approve`` endpoint.

    Args:
        gate: The quality gate with ``required_role`` and ``prompt`` in config.
        study_id: Study ID (unused).
        db: Database session (unused).

    Returns:
        :class:`GateResult` with ``passed=False`` and the sign-off detail.

    """
    cfg = gate.config or {}
    return GateResult(
        passed=False,
        detail={
            "gate_type": "human_sign_off",
            "required_role": cfg.get("required_role", "study_admin"),
            "prompt": cfg.get("prompt", ""),
        },
    )


#: Dispatch dict mapping QualityGateType → async evaluator function.
_GATE_EVALUATORS: dict[QualityGateType, Callable] = {
    QualityGateType.METRIC_THRESHOLD: _eval_metric_threshold,
    QualityGateType.COMPLETION_CHECK: _eval_completion_check,
    QualityGateType.HUMAN_SIGN_OFF: _eval_human_sign_off,
}


async def evaluate_all_gates(node_id: int, study_id: int, db: AsyncSession) -> GateResult:
    """Evaluate every quality gate on a node in definition order.

    Returns the first failure encountered, or a passing result if all pass.

    Args:
        node_id: PK of the protocol node whose gates are evaluated.
        study_id: Study ID passed to metric readers.
        db: Active async database session.

    Returns:
        :class:`GateResult` — first failure or an all-pass result.

    """
    gates_result = await db.execute(select(QualityGate).where(QualityGate.node_id == node_id))
    gates = gates_result.scalars().all()
    for gate in gates:
        evaluator = _GATE_EVALUATORS.get(gate.gate_type)
        if evaluator is None:
            continue
        result = await evaluator(gate, study_id, db)
        if not result.passed:
            return result
    return GateResult(passed=True)


async def _load_study_and_check_admin(study_id: int, user_id: int, db: AsyncSession) -> Study:
    """Load study and verify user is LEAD.

    Args:
        study_id: ID of the study to load.
        user_id: ID of the user to check.
        db: Active async database session.

    Returns:
        The :class:`~db.models.Study` ORM object.

    Raises:
        :class:`fastapi.HTTPException`: 404 if study not found; 403 if user is not LEAD.

    """
    study_result = await db.execute(select(Study).where(Study.id == study_id))
    study = study_result.scalar_one_or_none()
    if study is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found.")

    lead_result = await db.execute(
        select(StudyMember).where(
            StudyMember.study_id == study_id,
            StudyMember.user_id == user_id,
            StudyMember.role == StudyMemberRole.LEAD,
        )
    )
    if lead_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Study admin required.")

    return study


async def _load_all_task_items(study_id: int, db: AsyncSession) -> list[dict]:
    """Load all TaskExecutionState rows for a study, joining ProtocolNode for task metadata.

    Args:
        study_id: ID of the study.
        db: Active async database session.

    Returns:
        List of dicts with node_id, task_id, task_type, label, status,
        activated_at, completed_at, and gate_failure_detail.

    """
    stmt = (
        select(TaskExecutionState, ProtocolNode)
        .join(ProtocolNode, TaskExecutionState.node_id == ProtocolNode.id)
        .where(TaskExecutionState.study_id == study_id)
    )
    rows = (await db.execute(stmt)).all()
    return [
        {
            "node_id": state.node_id,
            "task_id": node.task_id,
            "task_type": node.task_type.value,
            "label": node.label,
            "status": state.status.value,
            "activated_at": state.activated_at,
            "completed_at": state.completed_at,
            "gate_failure_detail": state.gate_failure_detail,
        }
        for state, node in rows
    ]


class ProtocolAssignmentService:
    """Service for assigning a research protocol to a study (T058)."""

    async def assign_protocol(
        self,
        study_id: int,
        protocol_id: int,
        user_id: int,
        db: AsyncSession,
    ) -> StudyProtocolAssignment:
        """Assign a protocol to a study.

        Args:
            study_id: ID of the study to assign to.
            protocol_id: ID of the protocol to assign.
            user_id: ID of the requesting user.
            db: Active async database session.

        Returns:
            The updated :class:`~db.models.protocols.StudyProtocolAssignment` with
            ``protocol`` selectinloaded.

        Raises:
            :class:`fastapi.HTTPException`:
                - 400 if protocol study_type does not match study study_type.
                - 403 if user is not LEAD or protocol is owned by another user.
                - 404 if study or protocol is not found.
                - 409 if there are active TaskExecutionState rows for the study.

        """
        log = logger.bind(study_id=study_id, protocol_id=protocol_id, user_id=user_id)

        study = await _load_study_and_check_admin(study_id, user_id, db)

        protocol_result = await db.execute(
            select(ResearchProtocol).where(ResearchProtocol.id == protocol_id)
        )
        protocol = protocol_result.scalar_one_or_none()
        if protocol is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocol not found.")

        if not protocol.is_default_template and protocol.owner_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this protocol.",
            )

        if protocol.study_type != study.study_type.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Protocol study_type does not match study study_type.",
            )

        active_result = await db.execute(
            select(TaskExecutionState).where(
                TaskExecutionState.study_id == study_id,
                TaskExecutionState.status == TaskNodeStatus.ACTIVE,
            )
        )
        if active_result.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="study_executing")

        nodes_result = await db.execute(
            select(ProtocolNode).where(ProtocolNode.protocol_id == protocol_id)
        )
        nodes = nodes_result.scalars().all()

        existing_result = await db.execute(
            select(StudyProtocolAssignment).where(StudyProtocolAssignment.study_id == study_id)
        )
        assignment = existing_result.scalar_one_or_none()
        if assignment is None:
            assignment = StudyProtocolAssignment(
                study_id=study_id,
                protocol_id=protocol_id,
                assigned_at=datetime.now(UTC),
                assigned_by_user_id=user_id,
            )
            db.add(assignment)
        else:
            assignment.protocol_id = protocol_id
            assignment.assigned_at = datetime.now(UTC)
            assignment.assigned_by_user_id = user_id

        await db.execute(delete(TaskExecutionState).where(TaskExecutionState.study_id == study_id))

        for node in nodes:
            db.add(
                TaskExecutionState(
                    study_id=study_id,
                    node_id=node.id,
                    status=TaskNodeStatus.PENDING,
                )
            )

        await db.flush()

        executor = ProtocolExecutorService()
        await executor.activate_eligible_tasks(study_id, db)

        stmt = (
            select(StudyProtocolAssignment)
            .where(StudyProtocolAssignment.study_id == study_id)
            .options(selectinload(StudyProtocolAssignment.protocol))
        )
        result = await db.execute(stmt)
        refreshed = result.scalar_one()

        await db.commit()
        log.info("assign_protocol.ok")
        return refreshed

    async def reset_to_default(
        self,
        study_id: int,
        user_id: int,
        db: AsyncSession,
    ) -> StudyProtocolAssignment:
        """Reset a study's protocol to the default template for its study type.

        Verifies the requester is LEAD, blocks if any task is ACTIVE, then
        finds the default template for the study's study_type, updates the
        assignment, deletes old execution states, and seeds new PENDING states
        with start nodes activated.

        Args:
            study_id: ID of the study to reset.
            user_id: ID of the requesting user (must be LEAD).
            db: Active async database session.

        Returns:
            The updated :class:`~db.models.protocols.StudyProtocolAssignment`
            with ``protocol`` selectinloaded.

        Raises:
            :class:`fastapi.HTTPException`:
                - 403 if user is not LEAD.
                - 404 if study not found or no default template exists.
                - 409 if any TaskExecutionState has status ACTIVE.

        """
        log = logger.bind(study_id=study_id, user_id=user_id)

        study = await _load_study_and_check_admin(study_id, user_id, db)

        active_result = await db.execute(
            select(TaskExecutionState).where(
                TaskExecutionState.study_id == study_id,
                TaskExecutionState.status == TaskNodeStatus.ACTIVE,
            )
        )
        if active_result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot reset while study is executing.",
            )

        default_result = await db.execute(
            select(ResearchProtocol).where(
                ResearchProtocol.is_default_template.is_(True),
                ResearchProtocol.study_type == study.study_type.value,
            )
        )
        default_protocol = default_result.scalars().first()
        if default_protocol is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No default template found for this study type.",
            )

        nodes_result = await db.execute(
            select(ProtocolNode).where(ProtocolNode.protocol_id == default_protocol.id)
        )
        nodes = nodes_result.scalars().all()

        existing_result = await db.execute(
            select(StudyProtocolAssignment).where(StudyProtocolAssignment.study_id == study_id)
        )
        assignment = existing_result.scalar_one_or_none()
        if assignment is None:
            assignment = StudyProtocolAssignment(
                study_id=study_id,
                protocol_id=default_protocol.id,
                assigned_at=datetime.now(UTC),
                assigned_by_user_id=user_id,
            )
            db.add(assignment)
        else:
            assignment.protocol_id = default_protocol.id
            assignment.assigned_at = datetime.now(UTC)
            assignment.assigned_by_user_id = user_id

        await db.execute(delete(TaskExecutionState).where(TaskExecutionState.study_id == study_id))

        for node in nodes:
            db.add(
                TaskExecutionState(
                    study_id=study_id,
                    node_id=node.id,
                    status=TaskNodeStatus.PENDING,
                )
            )

        await db.flush()

        executor = ProtocolExecutorService()
        await executor.activate_eligible_tasks(study_id, db)

        stmt = (
            select(StudyProtocolAssignment)
            .where(StudyProtocolAssignment.study_id == study_id)
            .options(selectinload(StudyProtocolAssignment.protocol))
        )
        result = await db.execute(stmt)
        refreshed = result.scalar_one()

        await db.commit()
        log.info("reset_to_default.ok", default_protocol_id=default_protocol.id)
        return refreshed


class ProtocolExecutorService:
    """Service for advancing task execution state through a protocol graph."""

    async def activate_eligible_tasks(self, study_id: int, db: AsyncSession) -> list[str]:
        """Activate PENDING tasks whose all predecessors are COMPLETE.

        Args:
            study_id: ID of the study.
            db: Active async database session.

        Returns:
            List of newly activated task_id strings.

        """
        assignment_result = await db.execute(
            select(StudyProtocolAssignment).where(StudyProtocolAssignment.study_id == study_id)
        )
        assignment = assignment_result.scalar_one_or_none()
        if assignment is None:
            return []

        protocol_id = assignment.protocol_id

        edges_result = await db.execute(
            select(ProtocolEdge).where(ProtocolEdge.protocol_id == protocol_id)
        )
        edges = edges_result.scalars().all()

        predecessors: dict[int, list[int]] = {}
        for edge in edges:
            predecessors.setdefault(edge.target_node_id, []).append(edge.source_node_id)

        states_result = await db.execute(
            select(TaskExecutionState).where(TaskExecutionState.study_id == study_id)
        )
        states = states_result.scalars().all()
        status_map: dict[int, TaskNodeStatus] = {s.node_id: s.status for s in states}

        newly_activated_node_ids: list[int] = []
        for state in states:
            if state.status != TaskNodeStatus.PENDING:
                continue
            preds = predecessors.get(state.node_id, [])
            if all(status_map.get(p) == TaskNodeStatus.COMPLETE for p in preds):
                state.status = TaskNodeStatus.ACTIVE
                state.activated_at = datetime.now(UTC)
                newly_activated_node_ids.append(state.node_id)

        await db.flush()

        if not newly_activated_node_ids:
            return []

        nodes_result = await db.execute(
            select(ProtocolNode).where(ProtocolNode.id.in_(newly_activated_node_ids))
        )
        nodes = nodes_result.scalars().all()
        return [n.task_id for n in nodes]

    async def complete_task(self, study_id: int, task_id_str: str, db: AsyncSession) -> dict:
        """Mark a task ACTIVE→COMPLETE and activate eligible downstream tasks.

        Args:
            study_id: ID of the study.
            task_id_str: The researcher-defined ``task_id`` string key for the node.
            db: Active async database session.

        Returns:
            Dict with keys: completed_task_id, gate_result, gate_failure_detail,
            newly_activated_task_ids, all_tasks.

        Raises:
            :class:`fastapi.HTTPException`:
                - 404 if the task is not found in the study's protocol.
                - 409 if the task is not in ACTIVE status.

        """
        log = logger.bind(study_id=study_id, task_id=task_id_str)

        stmt = (
            select(TaskExecutionState, ProtocolNode)
            .join(ProtocolNode, TaskExecutionState.node_id == ProtocolNode.id)
            .where(
                TaskExecutionState.study_id == study_id,
                ProtocolNode.task_id == task_id_str,
            )
        )
        row = (await db.execute(stmt)).one_or_none()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="task not found in study's protocol",
            )

        state, _node = row
        if state.status != TaskNodeStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="task is not in active status",
            )

        state.status = TaskNodeStatus.COMPLETE
        state.completed_at = datetime.now(UTC)
        await db.flush()

        gate_result_obj = await evaluate_all_gates(state.node_id, study_id, db)
        if not gate_result_obj.passed:
            state.status = TaskNodeStatus.GATE_FAILED
            state.completed_at = None
            state.gate_failure_detail = gate_result_obj.detail
            await db.commit()
            all_tasks = await _load_all_task_items(study_id, db)
            log.info("complete_task.gate_failed")
            return {
                "completed_task_id": task_id_str,
                "gate_result": "failed",
                "gate_failure_detail": gate_result_obj.detail,
                "newly_activated_task_ids": [],
                "all_tasks": all_tasks,
            }

        newly_activated = await self.activate_eligible_tasks(study_id, db)

        await db.commit()

        all_tasks = await _load_all_task_items(study_id, db)

        log.info("complete_task.ok")
        return {
            "completed_task_id": task_id_str,
            "gate_result": "passed",
            "gate_failure_detail": None,
            "newly_activated_task_ids": newly_activated,
            "all_tasks": all_tasks,
        }

    async def approve_task(self, study_id: int, task_id_str: str, db: AsyncSession) -> dict:
        """Clear a human_sign_off gate failure and mark the task COMPLETE.

        Called by the study admin after reviewing a task that failed a
        ``human_sign_off`` quality gate.

        Args:
            study_id: ID of the study.
            task_id_str: Researcher-defined ``task_id`` string of the node to approve.
            db: Active async database session.

        Returns:
            Same dict shape as :meth:`complete_task`.

        Raises:
            :class:`fastapi.HTTPException`:
                - 404 if the task is not found.
                - 409 if the task is not ``GATE_FAILED`` or the failure detail is
                  not a ``human_sign_off`` gate.

        """
        log = logger.bind(study_id=study_id, task_id=task_id_str)

        stmt = (
            select(TaskExecutionState, ProtocolNode)
            .join(ProtocolNode, TaskExecutionState.node_id == ProtocolNode.id)
            .where(
                TaskExecutionState.study_id == study_id,
                ProtocolNode.task_id == task_id_str,
            )
        )
        row = (await db.execute(stmt)).one_or_none()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="task not found in study's protocol",
            )

        state, _node = row
        if state.status != TaskNodeStatus.GATE_FAILED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="task is not in gate_failed status",
            )

        detail = state.gate_failure_detail or {}
        if detail.get("gate_type") != "human_sign_off":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="task has no pending human_sign_off gate",
            )

        state.status = TaskNodeStatus.COMPLETE
        state.completed_at = datetime.now(UTC)
        state.gate_failure_detail = None
        await db.flush()

        newly_activated = await self.activate_eligible_tasks(study_id, db)
        await db.commit()

        all_tasks = await _load_all_task_items(study_id, db)
        log.info("approve_task.ok")
        return {
            "completed_task_id": task_id_str,
            "gate_result": "passed",
            "gate_failure_detail": None,
            "newly_activated_task_ids": newly_activated,
            "all_tasks": all_tasks,
        }
