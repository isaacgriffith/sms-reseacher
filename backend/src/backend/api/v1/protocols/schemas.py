"""Pydantic response schemas for Research Protocol Definition (feature 010).

Provides typed response models for all protocol library and assignment
endpoints.  All models use ``model_config = {"from_attributes": True}`` so
they can be constructed directly from SQLAlchemy ORM objects.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

# ---------------------------------------------------------------------------
# Node sub-schemas
# ---------------------------------------------------------------------------


class ProtocolNodeInputResponse(BaseModel):
    """Response schema for a single node input slot.

    Attributes:
        id: Primary key.
        name: Slot name (unique within a node).
        data_type: Typed data category.
        is_required: Whether an incoming edge must cover this input.

    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    data_type: str
    is_required: bool


class ProtocolNodeOutputResponse(BaseModel):
    """Response schema for a single node output slot.

    Attributes:
        id: Primary key.
        name: Slot name (unique within a node).
        data_type: Typed data category.

    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    data_type: str


class AssigneeResponse(BaseModel):
    """Response schema for a single node assignee.

    Attributes:
        id: Primary key.
        assignee_type: ``human_role`` or ``ai_agent``.
        role: Human role string (non-null when ``assignee_type`` is
            ``human_role``).
        agent_id: UUID of the AI agent (non-null when ``assignee_type`` is
            ``ai_agent``).

    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    assignee_type: str
    role: str | None
    agent_id: uuid.UUID | None


class QualityGateResponse(BaseModel):
    """Response schema for a single quality gate.

    Attributes:
        id: Primary key.
        gate_type: Evaluation strategy (``metric_threshold``, etc.).
        config: Type-specific gate parameters as a free-form dict.

    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    gate_type: str
    config: dict[str, Any]


# ---------------------------------------------------------------------------
# Node detail schema
# ---------------------------------------------------------------------------


class ProtocolNodeDetailResponse(BaseModel):
    """Full detail response for a single protocol node.

    Includes inputs, outputs, quality gates, and assignees.

    Attributes:
        id: Primary key.
        task_id: Researcher-defined unique key within the protocol.
        task_type: Task type string (e.g. ``DefinePICO``).
        label: Human-readable display name.
        description: Optional longer description.
        is_required: Whether this node must run.
        position_x: Optional D3 layout X coordinate.
        position_y: Optional D3 layout Y coordinate.
        inputs: List of typed input slots.
        outputs: List of typed output slots.
        assignees: List of human/AI assignees.
        quality_gates: List of quality gates attached to this node.

    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: str
    task_type: str
    label: str
    description: str | None
    is_required: bool
    position_x: float | None
    position_y: float | None
    inputs: list[ProtocolNodeInputResponse]
    outputs: list[ProtocolNodeOutputResponse]
    assignees: list[AssigneeResponse]
    quality_gates: list[QualityGateResponse]


# ---------------------------------------------------------------------------
# Edge schema
# ---------------------------------------------------------------------------


class EdgeConditionResponse(BaseModel):
    """Condition triple on a conditional protocol edge.

    Attributes:
        output_name: Name of the source output whose value is tested.
        operator: Comparison operator (``gt``, ``gte``, ``lt``, etc.).
        value: Numeric threshold value.

    """

    output_name: str
    operator: str
    value: float


class ProtocolEdgeResponse(BaseModel):
    """Response schema for a directed protocol edge.

    Source and target are expressed as ``task_id`` strings (not integer
    node PKs) so callers can work with the logical graph without joining.

    Attributes:
        id: Primary key.
        edge_id: Researcher-defined unique key within the protocol.
        source_task_id: ``task_id`` of the source node.
        source_output_name: Name of the source output slot.
        target_task_id: ``task_id`` of the target node.
        target_input_name: Name of the target input slot.
        condition: Optional condition triple; ``null`` for unconditional edges.

    """

    id: int
    edge_id: str
    source_task_id: str
    source_output_name: str
    target_task_id: str
    target_input_name: str
    condition: EdgeConditionResponse | None


# ---------------------------------------------------------------------------
# Protocol list and detail schemas
# ---------------------------------------------------------------------------


class ProtocolListItemResponse(BaseModel):
    """Lightweight response schema for protocol list items.

    Attributes:
        id: Primary key.
        name: Protocol name.
        study_type: ``SMS``, ``SLR``, ``Rapid``, or ``Tertiary``.
        is_default_template: ``True`` for platform-supplied default protocols.
        owner_user_id: Owner's user ID; ``null`` for default templates.
        version_id: Optimistic-lock version counter.
        created_at: Creation timestamp.
        updated_at: Last-update timestamp.

    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    study_type: str
    is_default_template: bool
    owner_user_id: int | None
    version_id: int
    created_at: datetime
    updated_at: datetime


class ProtocolDetailResponse(BaseModel):
    """Full detail response for a research protocol.

    Includes all nodes (with inputs, outputs, gates, assignees) and edges.

    Attributes:
        id: Primary key.
        name: Protocol name.
        study_type: ``SMS``, ``SLR``, ``Rapid``, or ``Tertiary``.
        is_default_template: ``True`` for platform-supplied default protocols.
        owner_user_id: Owner's user ID; ``null`` for default templates.
        version_id: Optimistic-lock version counter.
        description: Optional longer description.
        nodes: All task nodes, each with full detail.
        edges: All directed edges with ``task_id``-based references.
        created_at: Creation timestamp.
        updated_at: Last-update timestamp.

    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    study_type: str
    is_default_template: bool
    owner_user_id: int | None
    version_id: int
    description: str | None
    nodes: list[ProtocolNodeDetailResponse]
    edges: list[ProtocolEdgeResponse]
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# T043 — Request schemas for create / update / copy
# ---------------------------------------------------------------------------


class ProtocolNodeInputRequest(BaseModel):
    """Request schema for a node input slot.

    Attributes:
        name: Slot name (unique within a node).
        data_type: Typed data category string.
        is_required: Whether an incoming edge must cover this input.

    """

    name: str
    data_type: str
    is_required: bool = True


class ProtocolNodeOutputRequest(BaseModel):
    """Request schema for a node output slot.

    Attributes:
        name: Slot name (unique within a node).
        data_type: Typed data category string.

    """

    name: str
    data_type: str


class QualityGateRequest(BaseModel):
    """Request schema for a quality gate.

    Attributes:
        gate_type: Evaluation strategy (``metric_threshold``, etc.).
        config: Type-specific gate parameters.

    """

    gate_type: str
    config: dict


class NodeAssigneeRequest(BaseModel):
    """Request schema for a node assignee.

    Attributes:
        assignee_type: ``human_role`` or ``ai_agent``.
        role: Human role string (for ``human_role`` type).
        agent_id: UUID string of the AI agent (for ``ai_agent`` type).

    """

    assignee_type: str
    role: str | None = None
    agent_id: str | None = None


class EdgeConditionRequest(BaseModel):
    """Request schema for an edge condition triple.

    Attributes:
        output_name: Name of the source output whose value is tested.
        operator: Comparison operator (``gt``, ``gte``, ``lt``, etc.).
        value: Numeric threshold value.

    """

    output_name: str
    operator: str
    value: float


class ProtocolEdgeRequest(BaseModel):
    """Request schema for a directed protocol edge.

    Attributes:
        edge_id: Researcher-defined unique key within the protocol.
        source_task_id: ``task_id`` of the source node.
        source_output_name: Name of the source output slot.
        target_task_id: ``task_id`` of the target node.
        target_input_name: Name of the target input slot.
        condition: Optional condition triple; ``null`` for unconditional edges.

    """

    edge_id: str
    source_task_id: str
    source_output_name: str
    target_task_id: str
    target_input_name: str
    condition: EdgeConditionRequest | None = None


class ProtocolNodeRequest(BaseModel):
    """Request schema for a protocol task node.

    Attributes:
        task_id: Researcher-defined key, unique within the protocol.
        task_type: Task type string (e.g. ``DefinePICO``).
        label: Human-readable display name.
        description: Optional longer description.
        is_required: Whether this node must run.
        position_x: Optional D3 layout X coordinate.
        position_y: Optional D3 layout Y coordinate.
        inputs: Typed input slots.
        outputs: Typed output slots.
        quality_gates: Quality gates attached to this node.
        assignees: Human/AI assignees.

    """

    task_id: str
    task_type: str
    label: str
    description: str | None = None
    is_required: bool = True
    position_x: float | None = None
    position_y: float | None = None
    inputs: list[ProtocolNodeInputRequest] = []
    outputs: list[ProtocolNodeOutputRequest] = []
    quality_gates: list[QualityGateRequest] = []
    assignees: list[NodeAssigneeRequest] = []


class ProtocolCopyRequest(BaseModel):
    """Request schema for copying an existing protocol.

    Attributes:
        name: Name for the new copy.
        description: Optional description.
        copy_from_protocol_id: PK of the source protocol to copy.

    """

    name: str
    description: str | None = None
    copy_from_protocol_id: int


class ProtocolCreateRequest(BaseModel):
    """Request schema for creating a new protocol from a full graph definition.

    Attributes:
        name: Protocol name (unique per researcher).
        description: Optional description.
        study_type: ``SMS``, ``SLR``, ``Rapid``, or ``Tertiary``.
        nodes: Task nodes.
        edges: Directed edges.

    """

    name: str
    description: str | None = None
    study_type: str
    nodes: list[ProtocolNodeRequest] = []
    edges: list[ProtocolEdgeRequest] = []


class ProtocolUpdateRequest(BaseModel):
    """Request schema for replacing a protocol's full graph (optimistic lock).

    Attributes:
        name: New protocol name.
        description: New description (``null`` to clear).
        version_id: Client's expected current version; rejected if stale.
        nodes: Replacement node list.
        edges: Replacement edge list.

    """

    name: str
    description: str | None = None
    version_id: int
    nodes: list[ProtocolNodeRequest] = []
    edges: list[ProtocolEdgeRequest] = []


# ---------------------------------------------------------------------------
# Assignment schema
# ---------------------------------------------------------------------------


class ProtocolAssignmentResponse(BaseModel):
    """Response schema for a study's protocol assignment.

    Attributes:
        study_id: ID of the study.
        protocol_id: ID of the assigned protocol.
        protocol_name: Display name of the assigned protocol.
        is_default_template: Whether the assigned protocol is a default template.
        assigned_at: When the assignment was created or last updated.
        assigned_by_user_id: ID of the user who made the assignment;
            ``null`` for migration-seeded assignments.

    """

    study_id: int
    protocol_id: int
    protocol_name: str
    is_default_template: bool
    assigned_at: datetime
    assigned_by_user_id: int | None


class AssignProtocolRequest(BaseModel):
    """Request body for PUT /studies/{study_id}/protocol-assignment.

    Attributes:
        protocol_id: ID of the protocol to assign.

    """

    protocol_id: int


class ResetProtocolRequest(BaseModel):
    """Request body for DELETE /studies/{study_id}/protocol-assignment.

    Requires explicit confirmation to prevent accidental resets.

    Attributes:
        confirm_reset: Must be ``True`` to proceed with the reset.

    """

    confirm_reset: bool = False


class TaskStateItemResponse(BaseModel):
    """Execution state of a single protocol task node.

    Attributes:
        node_id: Primary key of the protocol node.
        task_id: Researcher-defined task key.
        task_type: Task type string.
        label: Human-readable display name.
        status: Current execution status string.
        activated_at: When the task became ACTIVE; ``null`` if still PENDING.
        completed_at: When the task reached COMPLETE; ``null`` if not yet done.
        gate_failure_detail: Gate failure diagnostic payload; ``null`` unless
            status is ``gate_failed``.

    """

    node_id: int
    task_id: str
    task_type: str
    label: str
    status: str
    activated_at: datetime | None
    completed_at: datetime | None
    gate_failure_detail: dict[str, Any] | None


class ExecutionStateResponse(BaseModel):
    """Full execution state for a study's protocol.

    Attributes:
        study_id: ID of the study.
        protocol_id: ID of the assigned protocol.
        tasks: Execution state of every task node.

    """

    study_id: int
    protocol_id: int
    tasks: list[TaskStateItemResponse]


class CompleteTaskResponse(BaseModel):
    """Response from marking a task complete.

    Attributes:
        completed_task_id: The task_id string of the completed node.
        gate_result: ``"passed"`` or ``"failed"``.
        gate_failure_detail: Diagnostic payload when ``gate_result`` is
            ``"failed"``; ``null`` otherwise.
        newly_activated_task_ids: Task IDs that transitioned to ACTIVE as a
            result of this completion.
        all_tasks: Updated execution state of every task node.

    """

    completed_task_id: str
    gate_result: str
    gate_failure_detail: dict[str, Any] | None
    newly_activated_task_ids: list[str]
    all_tasks: list[TaskStateItemResponse]
