"""Service layer for Research Protocol Definition (feature 010).

Provides:

- Pydantic discriminated-union gate config models (T019):
  :class:`MetricThresholdConfig`, :class:`CompletionCheckConfig`,
  :class:`HumanSignOffConfig`, :class:`QualityGateConfig`.

- Study-type task type allowlist and validation (T020):
  :data:`VALID_TASK_TYPES_BY_STUDY_TYPE`, :func:`validate_task_type`.

- Graph validation helpers (T021):
  :func:`detect_cycle`, :func:`validate_graph`,
  :func:`validate_required_input_coverage`.

- Protocol query helpers (T025, T026):
  :func:`list_protocols`, :func:`get_protocol_detail`.

All pure helpers are stateless so they are easily unit-tested without a
database connection (see ``backend/tests/unit/test_protocol_service.py``).
"""

from __future__ import annotations

from typing import Annotated, Literal

import structlog
from db.models.protocols import (
    EdgeConditionOperator,
    NodeAssignee,
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
)
from fastapi import HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# T019 — Pydantic discriminated-union gate config models
# ---------------------------------------------------------------------------


class MetricThresholdConfig(BaseModel):
    """Gate passes when ``metric_name`` exceeds ``threshold`` by ``operator``.

    Used with :attr:`~db.models.protocols.QualityGateType.METRIC_THRESHOLD`.

    Example::

        MetricThresholdConfig(
            gate_type="metric_threshold",
            metric_name="kappa_coefficient",
            operator="gte",
            threshold=0.6,
        )
    """

    gate_type: Literal["metric_threshold"]
    metric_name: str = Field(..., min_length=1, max_length=100)
    operator: Literal["gt", "gte", "lt", "lte", "eq", "neq"]
    threshold: float


class CompletionCheckConfig(BaseModel):
    """Gate passes when the node's task has been completed.

    Used with :attr:`~db.models.protocols.QualityGateType.COMPLETION_CHECK`.

    Example::

        CompletionCheckConfig(
            gate_type="completion_check",
            description="Data extraction is complete for all included papers.",
        )
    """

    gate_type: Literal["completion_check"]
    description: str = Field(..., min_length=1, max_length=500)


class HumanSignOffConfig(BaseModel):
    """Gate passes after an authorised human signs off the node's output.

    Used with :attr:`~db.models.protocols.QualityGateType.HUMAN_SIGN_OFF`.

    Example::

        HumanSignOffConfig(
            gate_type="human_sign_off",
            required_role="study_admin",
            prompt="Please review and confirm the synthesis is complete.",
        )
    """

    gate_type: Literal["human_sign_off"]
    required_role: str = Field(..., min_length=1, max_length=100)
    prompt: str = Field(..., min_length=1, max_length=1000)


#: Discriminated union of all gate config types.
#: Use this to validate the ``config`` JSON column from :class:`~db.models.protocols.QualityGate`.
QualityGateConfig = Annotated[
    MetricThresholdConfig | CompletionCheckConfig | HumanSignOffConfig,
    Field(discriminator="gate_type"),
]


GateConfigUnion = MetricThresholdConfig | CompletionCheckConfig | HumanSignOffConfig


def parse_gate_config(raw: dict) -> GateConfigUnion:
    """Parse a raw gate config dict into the appropriate typed Pydantic model.

    Args:
        raw: The ``config`` dict from a :class:`~db.models.protocols.QualityGate` row.

    Returns:
        A typed gate config object.

    Raises:
        :class:`pydantic.ValidationError`: If ``raw`` does not match any gate type.

    """
    from pydantic import TypeAdapter

    adapter: TypeAdapter[GateConfigUnion] = TypeAdapter(QualityGateConfig)  # type: ignore[type-arg]
    return adapter.validate_python(raw)


# ---------------------------------------------------------------------------
# T020 — Study-type task type allowlist and validate_task_type()
# ---------------------------------------------------------------------------

#: Maps each study type string to the set of :class:`~db.models.protocols.ProtocolTaskType`
#: values that are valid for that study type.
#:
#: This mirrors the constraints documented in ``data-model.md``
#: "Valid task type ↔ study type combinations" and enforced at save time
#: via :func:`validate_task_type`.
VALID_TASK_TYPES_BY_STUDY_TYPE: dict[str, frozenset[ProtocolTaskType]] = {
    "SMS": frozenset(
        {
            ProtocolTaskType.DEFINE_PICO,
            ProtocolTaskType.BUILD_SEARCH_STRING,
            ProtocolTaskType.EXECUTE_SEARCH,
            ProtocolTaskType.SCREEN_PAPERS,
            ProtocolTaskType.FULL_TEXT_REVIEW,
            ProtocolTaskType.SNOWBALL_SEARCH,
            ProtocolTaskType.EXTRACT_DATA,
            ProtocolTaskType.SYNTHESIZE_DATA,
            ProtocolTaskType.VALIDATE_RESULTS,
            ProtocolTaskType.GENERATE_REPORT,
            ProtocolTaskType.STAKEHOLDER_ENGAGEMENT,
        }
    ),
    "SLR": frozenset(
        {
            ProtocolTaskType.DEFINE_PROTOCOL,
            ProtocolTaskType.BUILD_SEARCH_STRING,
            ProtocolTaskType.EXECUTE_SEARCH,
            ProtocolTaskType.GREY_LITERATURE_SEARCH,
            ProtocolTaskType.SCREEN_PAPERS,
            ProtocolTaskType.FULL_TEXT_REVIEW,
            ProtocolTaskType.SNOWBALL_SEARCH,
            ProtocolTaskType.ASSESS_QUALITY,
            ProtocolTaskType.CHECK_INTER_RATER_RELIABILITY,
            ProtocolTaskType.EXTRACT_DATA,
            ProtocolTaskType.SYNTHESIZE_DATA,
            ProtocolTaskType.GENERATE_REPORT,
            ProtocolTaskType.STAKEHOLDER_ENGAGEMENT,
        }
    ),
    "Rapid": frozenset(
        {
            ProtocolTaskType.DEFINE_PICO,
            ProtocolTaskType.BUILD_SEARCH_STRING,
            ProtocolTaskType.EXECUTE_SEARCH,
            ProtocolTaskType.SCREEN_PAPERS,
            ProtocolTaskType.FULL_TEXT_REVIEW,
            ProtocolTaskType.APPRAISE_QUALITY,
            ProtocolTaskType.APPRAISE_QUALITY_ITEMS,
            ProtocolTaskType.IDENTIFY_THREATS_TO_VALIDITY,
            ProtocolTaskType.NARRATIVE_SYNTHESIS,
            ProtocolTaskType.PRODUCE_BRIEFING,
            ProtocolTaskType.STAKEHOLDER_ENGAGEMENT,
        }
    ),
    "Tertiary": frozenset(
        {
            ProtocolTaskType.DEFINE_SCOPE,
            ProtocolTaskType.BUILD_SEARCH_STRING,
            ProtocolTaskType.EXECUTE_SEARCH,
            ProtocolTaskType.SEARCH_SECONDARY_STUDIES,
            ProtocolTaskType.SCREEN_PAPERS,
            ProtocolTaskType.FULL_TEXT_REVIEW,
            ProtocolTaskType.ASSESS_QUALITY,
            ProtocolTaskType.IMPORT_SEED_STUDIES,
            ProtocolTaskType.EXTRACT_DATA,
            ProtocolTaskType.SYNTHESIZE_DATA,
            ProtocolTaskType.GENERATE_REPORT,
            ProtocolTaskType.STAKEHOLDER_ENGAGEMENT,
        }
    ),
}


def validate_task_type(study_type: str, task_type: ProtocolTaskType) -> None:
    """Raise :class:`ValueError` if ``task_type`` is invalid for ``study_type``.

    Args:
        study_type: One of ``SMS``, ``SLR``, ``Rapid``, ``Tertiary``.
        task_type: The task type to validate.

    Raises:
        :class:`ValueError`: If ``task_type`` is not in the allowlist for
            ``study_type``, or if ``study_type`` is unknown.

    Example::

        validate_task_type("SMS", ProtocolTaskType.DEFINE_PICO)       # ok
        validate_task_type("SMS", ProtocolTaskType.DEFINE_PROTOCOL)   # ValueError

    """
    allowed = VALID_TASK_TYPES_BY_STUDY_TYPE.get(study_type)
    if allowed is None:
        raise ValueError(f"Unknown study_type {study_type!r}")
    if task_type not in allowed:
        raise ValueError(
            f"Task type {task_type.value!r} is not valid for study type {study_type!r}."
            f" Allowed types: {sorted(t.value for t in allowed)}"
        )


# ---------------------------------------------------------------------------
# T021 — Graph validation helpers
# ---------------------------------------------------------------------------


class ProtocolGraphError(ValueError):
    """Raised when a protocol graph fails structural validation.

    Subclasses :class:`ValueError` so it surfaces as a 422 in FastAPI
    exception handlers that catch ``ValueError``.
    """


def detect_cycle(
    node_ids: list[str],
    edges: list[tuple[str, str]],
) -> bool:
    """Return ``True`` if the directed graph contains a cycle.

    Uses iterative depth-first search with three-colour marking
    (white/grey/black) to detect back edges.

    Args:
        node_ids: List of node ``task_id`` strings (vertex set).
        edges: List of ``(source_task_id, target_task_id)`` tuples (edge set).

    Returns:
        ``True`` if at least one cycle is detected, ``False`` otherwise.

    Example::

        detect_cycle(["a", "b", "c"], [("a", "b"), ("b", "c")])  # False
        detect_cycle(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")])  # True

    """
    adjacency: dict[str, list[str]] = {nid: [] for nid in node_ids}
    for src, tgt in edges:
        adjacency.setdefault(src, []).append(tgt)

    WHITE, GREY, BLACK = 0, 1, 2
    colour: dict[str, int] = dict.fromkeys(node_ids, WHITE)

    def _dfs(start: str) -> bool:
        stack = [(start, False)]
        while stack:
            node, backtrack = stack.pop()
            if backtrack:
                colour[node] = BLACK
                continue
            if colour[node] == GREY:
                return True
            if colour[node] == BLACK:
                continue
            colour[node] = GREY
            stack.append((node, True))
            for neighbour in adjacency.get(node, []):
                if colour[neighbour] == GREY:
                    return True
                if colour[neighbour] == WHITE:
                    stack.append((neighbour, False))
        return False

    for nid in node_ids:
        if colour[nid] == WHITE and _dfs(nid):
            return True
    return False


def validate_graph(
    study_type: str,
    nodes: list[dict],
    edges: list[dict],
) -> None:
    """Validate a complete protocol graph for structural correctness.

    Performs the following checks in order:

    1. At least one node exists.
    2. All ``task_id`` values are unique.
    3. All node ``task_type`` values are valid for ``study_type``
       (via :func:`validate_task_type`).
    4. All edge ``source_node_id`` / ``target_node_id`` values reference
       existing nodes.
    5. No self-loops (source == target).
    6. No cycles (via :func:`detect_cycle`).

    Args:
        study_type: Study type string (e.g. ``"SMS"``).
        nodes: List of node dicts with at least ``task_id`` and ``task_type`` keys.
        edges: List of edge dicts with at least ``source_task_id`` and
            ``target_task_id`` keys.

    Raises:
        :class:`ProtocolGraphError`: On any structural violation.

    Example::

        validate_graph(
            "SMS",
            nodes=[{"task_id": "n1", "task_type": "DefinePICO"}],
            edges=[],
        )

    """
    if not nodes:
        raise ProtocolGraphError("A protocol must have at least one node.")

    task_ids = [n["task_id"] for n in nodes]
    if len(task_ids) != len(set(task_ids)):
        seen: set[str] = set()
        dupes = [t for t in task_ids if t in seen or seen.add(t)]  # type: ignore[func-returns-value]
        raise ProtocolGraphError(
            f"Protocol contains duplicate task_id values: {sorted(set(dupes))}"
        )

    task_id_set = set(task_ids)

    for node in nodes:
        try:
            task_type = ProtocolTaskType(node["task_type"])
        except ValueError as exc:
            raise ProtocolGraphError(
                f"Unknown task_type {node['task_type']!r} on node {node['task_id']!r}."
            ) from exc
        validate_task_type(study_type, task_type)

    edge_pairs: list[tuple[str, str]] = []
    for edge in edges:
        src = edge["source_task_id"]
        tgt = edge["target_task_id"]
        if src not in task_id_set:
            raise ProtocolGraphError(f"Edge references unknown source node {src!r}.")
        if tgt not in task_id_set:
            raise ProtocolGraphError(f"Edge references unknown target node {tgt!r}.")
        if src == tgt:
            raise ProtocolGraphError(f"Self-loop detected on node {src!r}.")
        edge_pairs.append((src, tgt))

    if detect_cycle(task_ids, edge_pairs):
        raise ProtocolGraphError(
            "Protocol graph contains a cycle. Protocols must be directed acyclic graphs (DAGs)."
        )


def validate_required_input_coverage(
    nodes: list[dict],
    edges: list[dict],
) -> None:
    """Raise :class:`ProtocolGraphError` if required inputs lack a covering edge.

    A node input is "covered" when at least one incoming edge targets it
    (matching ``target_task_id`` + ``target_input_name``).

    Args:
        nodes: List of node dicts with ``task_id`` and ``inputs`` keys.
            Each item in ``inputs`` must have ``name`` and ``is_required`` keys.
        edges: List of edge dicts with ``target_task_id`` and ``target_input_name``.

    Raises:
        :class:`ProtocolGraphError`: If any required input has no covering edge.

    """
    covered: set[tuple[str, str]] = {(e["target_task_id"], e["target_input_name"]) for e in edges}
    missing: list[str] = []
    for node in nodes:
        for inp in node.get("inputs", []):
            if inp.get("is_required", True):
                key = (node["task_id"], inp["name"])
                if key not in covered:
                    missing.append(f"{node['task_id']}.{inp['name']}")
    if missing:
        raise ProtocolGraphError(f"Required inputs have no covering edge: {sorted(missing)}")


# ---------------------------------------------------------------------------
# T025 — Protocol query: list_protocols
# ---------------------------------------------------------------------------


async def list_protocols(
    user_id: int,
    study_type_filter: str | None,
    db: AsyncSession,
) -> list[ResearchProtocol]:
    """Return protocols visible to *user_id*.

    Returns all default templates plus all custom protocols owned by
    *user_id*.  When *study_type_filter* is provided, only protocols with
    a matching ``study_type`` are included.

    Args:
        user_id: ID of the requesting user.
        study_type_filter: Optional ``study_type`` string to narrow results.
        db: Active async database session.

    Returns:
        A list of :class:`~db.models.protocols.ResearchProtocol` ORM objects.

    """
    log = logger.bind(user_id=user_id, study_type_filter=study_type_filter)

    stmt = select(ResearchProtocol).where(
        or_(
            ResearchProtocol.is_default_template.is_(True),
            ResearchProtocol.owner_user_id == user_id,
        )
    )
    if study_type_filter is not None:
        stmt = stmt.where(ResearchProtocol.study_type == study_type_filter)
    stmt = stmt.order_by(
        ResearchProtocol.is_default_template.desc(),
        ResearchProtocol.name,
    )

    result = await db.execute(stmt)
    protocols = list(result.scalars().all())
    log.debug("list_protocols.ok", count=len(protocols))
    return protocols


# ---------------------------------------------------------------------------
# T026 — Protocol query: get_protocol_detail
# ---------------------------------------------------------------------------


async def get_protocol_detail(
    protocol_id: int,
    user_id: int,
    db: AsyncSession,
) -> ResearchProtocol:
    """Load a protocol with all nested detail.

    Loads the protocol together with all nodes (including inputs, outputs,
    quality gates, and assignees) and edges via ``selectinload``.

    Args:
        protocol_id: Primary key of the protocol.
        user_id: ID of the requesting user; used to authorise access.
        db: Active async database session.

    Returns:
        The fully-loaded :class:`~db.models.protocols.ResearchProtocol`.

    Raises:
        :class:`fastapi.HTTPException` 404: If no protocol with *protocol_id*
            exists.
        :class:`fastapi.HTTPException` 403: If the protocol is owned by
            another user and is not a default template.

    """
    log = logger.bind(protocol_id=protocol_id, user_id=user_id)

    stmt = (
        select(ResearchProtocol)
        .where(ResearchProtocol.id == protocol_id)
        .options(
            selectinload(ResearchProtocol.nodes).options(
                selectinload(ProtocolNode.inputs),
                selectinload(ProtocolNode.outputs),
                selectinload(ProtocolNode.quality_gates),
                selectinload(ProtocolNode.assignees),
            ),
            selectinload(ResearchProtocol.edges).options(
                selectinload(ProtocolEdge.source_node),
                selectinload(ProtocolEdge.target_node),
            ),
        )
    )
    result = await db.execute(stmt)
    protocol = result.scalar_one_or_none()
    if protocol is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocol not found.")

    if not protocol.is_default_template and protocol.owner_user_id != user_id:
        log.warning("get_protocol_detail.forbidden")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    log.debug("get_protocol_detail.ok", protocol_name=protocol.name)
    return protocol


# ---------------------------------------------------------------------------
# T026 — Helper: build edge responses with task_id strings
# ---------------------------------------------------------------------------


def build_edge_responses(
    protocol: ResearchProtocol,
) -> list[dict]:
    """Build edge dicts with ``source_task_id`` / ``target_task_id`` strings.

    The :class:`~db.models.protocols.ProtocolEdge` ORM model stores integer
    node PKs; this helper resolves them to ``task_id`` strings using the
    nodes already loaded on *protocol*.

    Args:
        protocol: A fully-loaded :class:`~db.models.protocols.ResearchProtocol`
            (``nodes`` and ``edges`` must already be in the session cache).

    Returns:
        A list of dicts suitable for constructing
        :class:`~backend.api.v1.protocols.schemas.ProtocolEdgeResponse` objects.

    """
    node_id_to_task_id: dict[int, str] = {n.id: n.task_id for n in protocol.nodes}
    edges = []
    for edge in protocol.edges:
        condition = None
        if edge.condition_output_name is not None:
            condition = {
                "output_name": edge.condition_output_name,
                "operator": edge.condition_operator.value
                if edge.condition_operator is not None
                else None,
                "value": edge.condition_value,
            }
        edges.append(
            {
                "id": edge.id,
                "edge_id": edge.edge_id,
                "source_task_id": node_id_to_task_id.get(edge.source_node_id, ""),
                "source_output_name": edge.source_output_name,
                "target_task_id": node_id_to_task_id.get(edge.target_node_id, ""),
                "target_input_name": edge.target_input_name,
                "condition": condition,
            }
        )
    return edges


# ---------------------------------------------------------------------------
# T039-T042 — Helpers used by copy/create/update
# ---------------------------------------------------------------------------


async def _check_duplicate_name(name: str, user_id: int, db: AsyncSession) -> None:
    """Raise HTTP 409 if *user_id* already owns a protocol named *name*.

    Args:
        name: Proposed protocol name.
        user_id: Owner ID to check against.
        db: Active async database session.

    Raises:
        :class:`fastapi.HTTPException` 409: If the name is taken.

    """
    stmt = select(ResearchProtocol).where(
        ResearchProtocol.owner_user_id == user_id,
        ResearchProtocol.name == name,
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You already have a protocol named {name!r}.",
        )


def _build_nodes_from_payload(
    protocol_id: int,
    nodes_payload: list[dict],
) -> tuple[list[ProtocolNode], dict[str, ProtocolNode]]:
    """Build unsaved :class:`ProtocolNode` ORM objects from request payload dicts.

    Args:
        protocol_id: PK of the owning protocol (set on each node).
        nodes_payload: List of node dicts with task_id, task_type, label, etc.

    Returns:
        A tuple of (list of ProtocolNode objects, task_id → ProtocolNode mapping).

    """
    nodes: list[ProtocolNode] = []
    task_id_map: dict[str, ProtocolNode] = {}
    for nd in nodes_payload:
        node = ProtocolNode(
            protocol_id=protocol_id,
            task_id=nd["task_id"],
            task_type=ProtocolTaskType(nd["task_type"]),
            label=nd.get("label", nd["task_id"]),
            description=nd.get("description"),
            is_required=nd.get("is_required", True),
            position_x=nd.get("position_x"),
            position_y=nd.get("position_y"),
        )
        for inp in nd.get("inputs", []):
            node.inputs.append(
                ProtocolNodeInput(
                    name=inp["name"],
                    data_type=NodeDataType(inp["data_type"]),
                    is_required=inp.get("is_required", True),
                )
            )
        for out in nd.get("outputs", []):
            node.outputs.append(
                ProtocolNodeOutput(
                    name=out["name"],
                    data_type=NodeDataType(out["data_type"]),
                )
            )
        for gate in nd.get("quality_gates", []):
            node.quality_gates.append(
                QualityGate(
                    gate_type=QualityGateType(gate["gate_type"]),
                    config=gate["config"],
                )
            )
        for assignee in nd.get("assignees", []):
            import uuid as _uuid

            node.assignees.append(
                NodeAssignee(
                    assignee_type=assignee["assignee_type"],
                    role=assignee.get("role"),
                    agent_id=_uuid.UUID(assignee["agent_id"]) if assignee.get("agent_id") else None,
                )
            )
        nodes.append(node)
        task_id_map[nd["task_id"]] = node
    return nodes, task_id_map


def _build_edges_from_payload(
    protocol_id: int,
    edges_payload: list[dict],
    task_id_map: dict[str, ProtocolNode],
) -> list[ProtocolEdge]:
    """Build unsaved :class:`ProtocolEdge` ORM objects from request payload dicts.

    Args:
        protocol_id: PK of the owning protocol.
        edges_payload: List of edge dicts with source_task_id, target_task_id, etc.
        task_id_map: Mapping of task_id → :class:`ProtocolNode` (must have PKs).

    Returns:
        List of :class:`ProtocolEdge` objects ready to persist.

    """
    edges: list[ProtocolEdge] = []
    for ed in edges_payload:
        src_node = task_id_map[ed["source_task_id"]]
        tgt_node = task_id_map[ed["target_task_id"]]
        condition = ed.get("condition")
        edge = ProtocolEdge(
            protocol_id=protocol_id,
            edge_id=ed["edge_id"],
            source_node_id=src_node.id,
            source_output_name=ed["source_output_name"],
            target_node_id=tgt_node.id,
            target_input_name=ed["target_input_name"],
            condition_output_name=condition["output_name"] if condition else None,
            condition_operator=EdgeConditionOperator(condition["operator"]) if condition else None,
            condition_value=condition["value"] if condition else None,
        )
        edges.append(edge)
    return edges


# ---------------------------------------------------------------------------
# T039 — copy_protocol
# ---------------------------------------------------------------------------


async def copy_protocol(
    source_id: int,
    user_id: int,
    new_name: str,
    description: str | None,
    db: AsyncSession,
) -> ResearchProtocol:
    """Deep-copy a protocol and return the new copy owned by *user_id*.

    Copies all nodes (inputs, outputs, quality gates, assignees) and edges.
    The source must be a default template or owned by *user_id*.

    Args:
        source_id: PK of the source protocol to copy.
        user_id: ID of the user who will own the copy.
        new_name: Name for the new protocol.
        description: Optional description for the new protocol.
        db: Active async database session.

    Returns:
        The newly created :class:`~db.models.protocols.ResearchProtocol`.

    Raises:
        :class:`fastapi.HTTPException` 403: If source is another user's non-default protocol.
        :class:`fastapi.HTTPException` 404: If source protocol does not exist.
        :class:`fastapi.HTTPException` 409: If *user_id* already has a protocol named *new_name*.

    """
    log = logger.bind(source_id=source_id, user_id=user_id, new_name=new_name)
    source = await get_protocol_detail(source_id, user_id, db)
    await _check_duplicate_name(new_name, user_id, db)

    new_protocol = ResearchProtocol(
        name=new_name,
        description=description,
        study_type=source.study_type,
        is_default_template=False,
        owner_user_id=user_id,
        version_id=1,
    )
    db.add(new_protocol)
    await db.flush()

    old_to_new: dict[int, ProtocolNode] = {}
    for node in source.nodes:
        new_node = ProtocolNode(
            protocol_id=new_protocol.id,
            task_id=node.task_id,
            task_type=node.task_type,
            label=node.label,
            description=node.description,
            is_required=node.is_required,
            position_x=node.position_x,
            position_y=node.position_y,
        )
        for inp in node.inputs:
            new_node.inputs.append(
                ProtocolNodeInput(
                    name=inp.name,
                    data_type=inp.data_type,
                    is_required=inp.is_required,
                )
            )
        for out in node.outputs:
            new_node.outputs.append(ProtocolNodeOutput(name=out.name, data_type=out.data_type))
        for gate in node.quality_gates:
            new_node.quality_gates.append(QualityGate(gate_type=gate.gate_type, config=gate.config))
        for assignee in node.assignees:
            new_node.assignees.append(
                NodeAssignee(
                    assignee_type=assignee.assignee_type,
                    role=assignee.role,
                    agent_id=assignee.agent_id,
                )
            )
        db.add(new_node)
        old_to_new[node.id] = new_node

    await db.flush()

    for edge in source.edges:
        db.add(
            ProtocolEdge(
                protocol_id=new_protocol.id,
                edge_id=edge.edge_id,
                source_node_id=old_to_new[edge.source_node_id].id,
                source_output_name=edge.source_output_name,
                target_node_id=old_to_new[edge.target_node_id].id,
                target_input_name=edge.target_input_name,
                condition_output_name=edge.condition_output_name,
                condition_operator=edge.condition_operator,
                condition_value=edge.condition_value,
            )
        )

    await db.commit()
    log.info("copy_protocol.ok", new_id=new_protocol.id)
    return await get_protocol_detail(new_protocol.id, user_id, db)


# ---------------------------------------------------------------------------
# T040 — create_protocol
# ---------------------------------------------------------------------------


async def create_protocol(
    name: str,
    study_type: str,
    description: str | None,
    nodes_payload: list[dict],
    edges_payload: list[dict],
    user_id: int,
    db: AsyncSession,
) -> ResearchProtocol:
    """Create a new custom protocol from a full graph definition.

    Args:
        name: Protocol name (must be unique per user).
        study_type: ``SMS``, ``SLR``, ``Rapid``, or ``Tertiary``.
        description: Optional description.
        nodes_payload: List of node dicts conforming to the node request schema.
        edges_payload: List of edge dicts conforming to the edge request schema.
        user_id: ID of the owning researcher.
        db: Active async database session.

    Returns:
        The newly created :class:`~db.models.protocols.ResearchProtocol`.

    Raises:
        :class:`fastapi.HTTPException` 400: On graph validation failure.
        :class:`fastapi.HTTPException` 409: If *user_id* already has a protocol named *name*.

    """
    log = logger.bind(user_id=user_id, name=name, study_type=study_type)
    try:
        validate_graph(study_type, nodes_payload, edges_payload)
    except (ProtocolGraphError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await _check_duplicate_name(name, user_id, db)

    protocol = ResearchProtocol(
        name=name,
        description=description,
        study_type=study_type,
        is_default_template=False,
        owner_user_id=user_id,
        version_id=1,
    )
    db.add(protocol)
    await db.flush()

    nodes, task_id_map = _build_nodes_from_payload(protocol.id, nodes_payload)
    for node in nodes:
        db.add(node)
    await db.flush()

    for edge in _build_edges_from_payload(protocol.id, edges_payload, task_id_map):
        db.add(edge)

    await db.commit()
    log.info("create_protocol.ok", protocol_id=protocol.id)
    return await get_protocol_detail(protocol.id, user_id, db)


# ---------------------------------------------------------------------------
# T041 — update_protocol
# ---------------------------------------------------------------------------


async def update_protocol(
    protocol_id: int,
    version_id: int,
    name: str,
    description: str | None,
    nodes_payload: list[dict],
    edges_payload: list[dict],
    user_id: int,
    db: AsyncSession,
) -> ResearchProtocol:
    """Replace a protocol's full graph atomically.

    Validates the incoming graph, checks the optimistic lock, then replaces
    all nodes and edges in a single transaction.

    Args:
        protocol_id: PK of the protocol to update.
        version_id: Client's expected current version (optimistic lock).
        name: New protocol name.
        description: New description (``None`` to clear).
        nodes_payload: Replacement node list.
        edges_payload: Replacement edge list.
        user_id: ID of the requesting researcher.
        db: Active async database session.

    Returns:
        The updated :class:`~db.models.protocols.ResearchProtocol`.

    Raises:
        :class:`fastapi.HTTPException` 400: On graph validation failure.
        :class:`fastapi.HTTPException` 403: If not owner or is a default template.
        :class:`fastapi.HTTPException` 404: If protocol not found.
        :class:`fastapi.HTTPException` 409: On version_id mismatch.

    """
    log = logger.bind(protocol_id=protocol_id, user_id=user_id)
    protocol = await get_protocol_detail(protocol_id, user_id, db)

    if protocol.is_default_template:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify a default template.",
        )
    if protocol.owner_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if protocol.version_id != version_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "conflict", "current_version_id": protocol.version_id},
        )

    try:
        validate_graph(protocol.study_type, nodes_payload, edges_payload)
    except (ProtocolGraphError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    # Delete all existing nodes (cascade removes inputs/outputs/gates/assignees) and edges
    for edge in list(protocol.edges):
        await db.delete(edge)
    for node in list(protocol.nodes):
        await db.delete(node)
    await db.flush()

    # Update protocol header (triggers version_id increment via mapper_args)
    protocol.name = name
    protocol.description = description
    await db.flush()

    nodes, task_id_map = _build_nodes_from_payload(protocol.id, nodes_payload)
    for node in nodes:
        db.add(node)
    await db.flush()

    for edge in _build_edges_from_payload(protocol.id, edges_payload, task_id_map):
        db.add(edge)

    await db.commit()
    log.info("update_protocol.ok", new_version=protocol.version_id)
    return await get_protocol_detail(protocol.id, user_id, db)


# ---------------------------------------------------------------------------
# T042 — delete_protocol
# ---------------------------------------------------------------------------


async def delete_protocol(
    protocol_id: int,
    user_id: int,
    db: AsyncSession,
) -> None:
    """Delete a custom protocol.

    Args:
        protocol_id: PK of the protocol to delete.
        user_id: ID of the requesting researcher.
        db: Active async database session.

    Raises:
        :class:`fastapi.HTTPException` 403: If not owner or is a default template.
        :class:`fastapi.HTTPException` 404: If protocol not found.
        :class:`fastapi.HTTPException` 409: If protocol is assigned to one or more studies.

    """
    log = logger.bind(protocol_id=protocol_id, user_id=user_id)

    stmt = (
        select(ResearchProtocol)
        .where(ResearchProtocol.id == protocol_id)
        .options(selectinload(ResearchProtocol.study_assignments))
    )
    result = await db.execute(stmt)
    protocol = result.scalar_one_or_none()
    if protocol is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocol not found.")

    if protocol.is_default_template:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete a default template.",
        )
    if protocol.owner_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if protocol.study_assignments:
        blocking_ids = [a.study_id for a in protocol.study_assignments]
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": "Protocol is assigned to studies.",
                "blocking_study_ids": blocking_ids,
            },
        )

    await db.delete(protocol)
    await db.commit()
    log.info("delete_protocol.ok")


# ---------------------------------------------------------------------------
# T029 — Assignment query helper
# ---------------------------------------------------------------------------


async def get_protocol_assignment(
    study_id: int,
    db: AsyncSession,
) -> StudyProtocolAssignment | None:
    """Return the :class:`~db.models.protocols.StudyProtocolAssignment` for *study_id*.

    Args:
        study_id: ID of the study.
        db: Active async database session.

    Returns:
        The assignment ORM object, or ``None`` if no assignment exists.

    """
    stmt = (
        select(StudyProtocolAssignment)
        .where(StudyProtocolAssignment.study_id == study_id)
        .options(selectinload(StudyProtocolAssignment.protocol))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
