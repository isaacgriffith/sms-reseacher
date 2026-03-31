"""Protocol execution state endpoints for Research Protocol Definition (feature 010).

Routes:
- POST /studies/{study_id}/execution-state/{task_id}/complete → 200 | 403 | 404 | 409
- POST /studies/{study_id}/execution-state/{task_id}/approve  → 200 | 403 | 404 | 409
"""

from __future__ import annotations

from db.models.protocols import (
    NodeAssignee,
    NodeAssigneeType,
    ProtocolNode,
    TaskExecutionState,
)
from db.models.study import StudyMember, StudyMemberRole
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.protocols.schemas import CompleteTaskResponse, TaskStateItemResponse
from backend.core.auth import CurrentUser, get_current_user
from backend.core.database import get_db
from backend.services.protocol_executor import ProtocolExecutorService

router = APIRouter(tags=["protocols"])


@router.post(
    "/studies/{study_id}/execution-state/{task_id}/complete",
    response_model=CompleteTaskResponse,
)
async def complete_task_endpoint(
    study_id: int,
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompleteTaskResponse:
    """Mark a task complete. Only study LEAD or human-role task assignees may call this.

    Args:
        study_id: ID of the study.
        task_id: Researcher-defined ``task_id`` string of the node to complete.
        current_user: Authenticated user from JWT.
        db: Active async database session.

    Returns:
        :class:`~backend.api.v1.protocols.schemas.CompleteTaskResponse`
        with updated execution state.

    Raises:
        HTTP 403: If the requester is not authorised to complete the task.
        HTTP 404: If the task is not found in the study's protocol.
        HTTP 409: If the task is not currently in ACTIVE status.

    """
    lead_result = await db.execute(
        select(StudyMember).where(
            StudyMember.study_id == study_id,
            StudyMember.user_id == current_user.user_id,
            StudyMember.role == StudyMemberRole.LEAD,
        )
    )
    is_lead = lead_result.scalar_one_or_none() is not None

    if not is_lead:
        member_result = await db.execute(
            select(StudyMember).where(
                StudyMember.study_id == study_id,
                StudyMember.user_id == current_user.user_id,
            )
        )
        member = member_result.scalar_one_or_none()

        node_stmt = (
            select(ProtocolNode)
            .join(TaskExecutionState, TaskExecutionState.node_id == ProtocolNode.id)
            .where(
                TaskExecutionState.study_id == study_id,
                ProtocolNode.task_id == task_id,
            )
        )
        node = (await db.execute(node_stmt)).scalar_one_or_none()

        has_human_assignee = False
        if node is not None:
            assignee_result = await db.execute(
                select(NodeAssignee).where(
                    NodeAssignee.node_id == node.id,
                    NodeAssignee.assignee_type == NodeAssigneeType.HUMAN_ROLE,
                )
            )
            has_human_assignee = assignee_result.scalar_one_or_none() is not None

        if member is None or not has_human_assignee:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    executor = ProtocolExecutorService()
    result = await executor.complete_task(study_id, task_id, db)

    return CompleteTaskResponse(
        completed_task_id=result["completed_task_id"],
        gate_result=result["gate_result"],
        gate_failure_detail=result["gate_failure_detail"],
        newly_activated_task_ids=result["newly_activated_task_ids"],
        all_tasks=[TaskStateItemResponse(**t) for t in result["all_tasks"]],
    )


@router.post(
    "/studies/{study_id}/execution-state/{task_id}/approve",
    response_model=CompleteTaskResponse,
)
async def approve_task_endpoint(
    study_id: int,
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompleteTaskResponse:
    """Approve a human_sign_off gate failure. Only study LEAD may call this.

    Args:
        study_id: ID of the study.
        task_id: Researcher-defined ``task_id`` string of the node to approve.
        current_user: Authenticated user from JWT.
        db: Active async database session.

    Returns:
        :class:`~backend.api.v1.protocols.schemas.CompleteTaskResponse`
        with updated execution state after approval.

    Raises:
        HTTP 403: If the requester is not the study LEAD.
        HTTP 404: If the task is not found in the study's protocol.
        HTTP 409: If the task is not in ``gate_failed`` status or has no
            pending ``human_sign_off`` gate.

    """
    lead_result = await db.execute(
        select(StudyMember).where(
            StudyMember.study_id == study_id,
            StudyMember.user_id == current_user.user_id,
            StudyMember.role == StudyMemberRole.LEAD,
        )
    )
    if lead_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Study admin required.")

    executor = ProtocolExecutorService()
    result = await executor.approve_task(study_id, task_id, db)

    return CompleteTaskResponse(
        completed_task_id=result["completed_task_id"],
        gate_result=result["gate_result"],
        gate_failure_detail=result["gate_failure_detail"],
        newly_activated_task_ids=result["newly_activated_task_ids"],
        all_tasks=[TaskStateItemResponse(**t) for t in result["all_tasks"]],
    )
