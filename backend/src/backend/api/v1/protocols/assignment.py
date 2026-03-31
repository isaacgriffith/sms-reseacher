"""Study protocol assignment endpoints for Research Protocol Definition (feature 010).

Routes:
- GET /studies/{study_id}/protocol-assignment → 200 | 403 | 404
- PUT /studies/{study_id}/protocol-assignment → 200 | 400 | 403 | 404 | 409
- GET /studies/{study_id}/execution-state → 200 | 403 | 404
"""

from __future__ import annotations

from db.models.protocols import ProtocolNode, TaskExecutionState
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.v1.protocols.schemas import (
    AssignProtocolRequest,
    ExecutionStateResponse,
    ProtocolAssignmentResponse,
    ResetProtocolRequest,
    TaskStateItemResponse,
)
from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.database import get_db
from backend.services.protocol_executor import ProtocolAssignmentService
from backend.services.protocol_service import get_protocol_assignment

router = APIRouter(tags=["protocols"])


@router.get(
    "/studies/{study_id}/protocol-assignment",
    response_model=ProtocolAssignmentResponse,
)
async def get_study_protocol_assignment(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProtocolAssignmentResponse:
    """Return the protocol currently assigned to a study.

    Args:
        study_id: ID of the study.
        current_user: Authenticated user from JWT.
        db: Active async database session.

    Returns:
        :class:`~backend.api.v1.protocols.schemas.ProtocolAssignmentResponse`
        describing the assignment.

    Raises:
        HTTP 403: If the requester is not a study member.
        HTTP 404: If the study has no protocol assignment.

    """
    await require_study_member(study_id=study_id, current_user=current_user, db=db)

    assignment = await get_protocol_assignment(study_id, db)
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No protocol assignment found for this study.",
        )

    return ProtocolAssignmentResponse(
        study_id=assignment.study_id,
        protocol_id=assignment.protocol_id,
        protocol_name=assignment.protocol.name,
        is_default_template=assignment.protocol.is_default_template,
        assigned_at=assignment.assigned_at,
        assigned_by_user_id=assignment.assigned_by_user_id,
    )


@router.put(
    "/studies/{study_id}/protocol-assignment",
    response_model=ProtocolAssignmentResponse,
)
async def assign_study_protocol(
    study_id: int,
    body: AssignProtocolRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProtocolAssignmentResponse:
    """Assign a protocol to a study, resetting execution state.

    Args:
        study_id: ID of the study.
        body: Request body containing the protocol_id to assign.
        current_user: Authenticated user from JWT.
        db: Active async database session.

    Returns:
        :class:`~backend.api.v1.protocols.schemas.ProtocolAssignmentResponse`
        for the updated assignment.

    Raises:
        HTTP 400: If protocol study_type does not match study study_type.
        HTTP 403: If the requester is not the study LEAD.
        HTTP 404: If the study or protocol is not found.
        HTTP 409: If the study is currently executing tasks.

    """
    svc = ProtocolAssignmentService()
    assignment = await svc.assign_protocol(
        study_id=study_id,
        protocol_id=body.protocol_id,
        user_id=current_user.user_id,
        db=db,
    )
    return ProtocolAssignmentResponse(
        study_id=assignment.study_id,
        protocol_id=assignment.protocol_id,
        protocol_name=assignment.protocol.name,
        is_default_template=assignment.protocol.is_default_template,
        assigned_at=assignment.assigned_at,
        assigned_by_user_id=assignment.assigned_by_user_id,
    )


@router.delete(
    "/studies/{study_id}/protocol-assignment",
    response_model=ProtocolAssignmentResponse,
)
async def reset_study_protocol_assignment(
    study_id: int,
    body: ResetProtocolRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProtocolAssignmentResponse:
    """Reset a study's protocol to the default template for its study type.

    Requires ``{"confirm_reset": true}`` in the request body. Blocked while
    any task is ACTIVE. Only study LEAD may call this.

    Args:
        study_id: ID of the study.
        body: Confirmation payload — must have ``confirm_reset=True``.
        current_user: Authenticated user from JWT.
        db: Active async database session.

    Returns:
        :class:`~backend.api.v1.protocols.schemas.ProtocolAssignmentResponse`
        for the new assignment pointing to the default template.

    Raises:
        HTTP 400: If ``confirm_reset`` is not ``True``.
        HTTP 403: If the requester is not the study LEAD.
        HTTP 404: If the study is not found or no default template exists.
        HTTP 409: If any task is currently ACTIVE.

    """
    if not body.confirm_reset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="confirm_reset must be true to proceed.",
        )

    svc = ProtocolAssignmentService()
    assignment = await svc.reset_to_default(
        study_id=study_id,
        user_id=current_user.user_id,
        db=db,
    )
    return ProtocolAssignmentResponse(
        study_id=assignment.study_id,
        protocol_id=assignment.protocol_id,
        protocol_name=assignment.protocol.name,
        is_default_template=assignment.protocol.is_default_template,
        assigned_at=assignment.assigned_at,
        assigned_by_user_id=assignment.assigned_by_user_id,
    )


@router.get(
    "/studies/{study_id}/execution-state",
    response_model=ExecutionStateResponse,
)
async def get_study_execution_state(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExecutionStateResponse:
    """Return the full execution state for a study's assigned protocol.

    Args:
        study_id: ID of the study.
        current_user: Authenticated user from JWT.
        db: Active async database session.

    Returns:
        :class:`~backend.api.v1.protocols.schemas.ExecutionStateResponse`
        with all task execution states.

    Raises:
        HTTP 403: If the requester is not a study member.
        HTTP 404: If the study has no protocol assignment.

    """
    await require_study_member(study_id=study_id, current_user=current_user, db=db)

    assignment = await get_protocol_assignment(study_id, db)
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No protocol assignment found",
        )

    stmt = (
        select(TaskExecutionState, ProtocolNode)
        .join(ProtocolNode, TaskExecutionState.node_id == ProtocolNode.id)
        .where(TaskExecutionState.study_id == study_id)
    )
    rows = (await db.execute(stmt)).all()
    tasks = [
        TaskStateItemResponse(
            node_id=state.node_id,
            task_id=node.task_id,
            task_type=node.task_type.value,
            label=node.label,
            status=state.status.value,
            activated_at=state.activated_at,
            completed_at=state.completed_at,
            gate_failure_detail=state.gate_failure_detail,
        )
        for state, node in rows
    ]
    return ExecutionStateResponse(
        study_id=study_id,
        protocol_id=assignment.protocol_id,
        tasks=tasks,
    )
