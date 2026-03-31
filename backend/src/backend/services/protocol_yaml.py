"""YAML import/export utilities for Research Protocol Definition (feature 010).

Provides serialisation and deserialisation of protocol graphs to/from YAML
format for the dual-pane editor and download/upload workflow.

Schema version ``"1.0"`` is the only supported version (Decision 6, research.md).
"""

from __future__ import annotations

import structlog
import yaml
from db.models.protocols import ResearchProtocol
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.protocol_service import (
    create_protocol,
)

logger = structlog.get_logger(__name__)

SUPPORTED_SCHEMA_VERSIONS: frozenset[str] = frozenset({"1.0"})

# ---------------------------------------------------------------------------
# Pydantic models for the YAML schema
# ---------------------------------------------------------------------------


class YamlNodeInput(BaseModel):
    """A node input slot in the YAML schema."""

    name: str
    data_type: str
    is_required: bool = True


class YamlNodeOutput(BaseModel):
    """A node output slot in the YAML schema."""

    name: str
    data_type: str


class YamlAssignee(BaseModel):
    """A node assignee in the YAML schema."""

    type: str
    role: str | None = None
    agent_id: str | None = None


class YamlQualityGate(BaseModel):
    """A quality gate in the YAML schema."""

    gate_type: str
    config: dict = Field(default_factory=dict)


class YamlNode(BaseModel):
    """A protocol node in the YAML schema."""

    task_id: str
    task_type: str
    label: str
    description: str | None = None
    is_required: bool = True
    inputs: list[YamlNodeInput] = Field(default_factory=list)
    outputs: list[YamlNodeOutput] = Field(default_factory=list)
    assignees: list[YamlAssignee] = Field(default_factory=list)
    quality_gates: list[YamlQualityGate] = Field(default_factory=list)


class YamlEdgeCondition(BaseModel):
    """An optional condition triple on an edge."""

    output_name: str
    operator: str
    value: float


class YamlEdge(BaseModel):
    """A protocol edge in the YAML schema."""

    edge_id: str
    source_task_id: str
    source_output: str
    target_task_id: str
    target_input: str
    condition: YamlEdgeCondition | None = None


class ProtocolExportSchema(BaseModel):
    """Root model for the YAML export/import schema (Decision 6)."""

    protocol_schema_version: str = "1.0"
    name: str
    study_type: str
    description: str | None = None
    nodes: list[YamlNode] = Field(default_factory=list)
    edges: list[YamlEdge] = Field(default_factory=list)

    @field_validator("protocol_schema_version")
    @classmethod
    def _check_version(cls, v: str) -> str:
        if v not in SUPPORTED_SCHEMA_VERSIONS:
            raise ValueError(
                f"Unsupported protocol_schema_version {v!r}."
                f" Supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)}"
            )
        return v


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class ProtocolYamlService:
    """Handles YAML export and import of research protocol graphs."""

    def _node_to_dict(self, node: object) -> dict:  # type: ignore[return]
        """Serialise a ProtocolNode ORM object to a YAML-compatible dict."""
        return {
            "task_id": node.task_id,  # type: ignore[attr-defined]
            "task_type": node.task_type.value,  # type: ignore[attr-defined]
            "label": node.label,  # type: ignore[attr-defined]
            "description": node.description,  # type: ignore[attr-defined]
            "is_required": node.is_required,  # type: ignore[attr-defined]
            "inputs": [
                {
                    "name": inp.name,
                    "data_type": inp.data_type.value,
                    "is_required": inp.is_required,
                }
                for inp in node.inputs  # type: ignore[attr-defined]
            ],
            "outputs": [
                {"name": out.name, "data_type": out.data_type.value}
                for out in node.outputs  # type: ignore[attr-defined]
            ],
            "assignees": [
                {
                    "type": a.assignee_type.value,
                    "role": a.role,
                    "agent_id": str(a.agent_id) if a.agent_id else None,
                }
                for a in node.assignees  # type: ignore[attr-defined]
            ],
            "quality_gates": [
                {"gate_type": g.gate_type.value, "config": g.config}
                for g in node.quality_gates  # type: ignore[attr-defined]
            ],
        }

    def _edge_to_dict(self, edge: object, node_id_to_task_id: dict[int, str]) -> dict:  # type: ignore[return]
        """Serialise a ProtocolEdge ORM object to a YAML-compatible dict."""
        condition = None
        if edge.condition_output_name is not None:  # type: ignore[attr-defined]
            condition = {
                "output_name": edge.condition_output_name,  # type: ignore[attr-defined]
                "operator": edge.condition_operator.value,  # type: ignore[attr-defined]
                "value": edge.condition_value,  # type: ignore[attr-defined]
            }
        return {
            "edge_id": edge.edge_id,  # type: ignore[attr-defined]
            "source_task_id": node_id_to_task_id[edge.source_node_id],  # type: ignore[attr-defined]
            "source_output": edge.source_output_name,  # type: ignore[attr-defined]
            "target_task_id": node_id_to_task_id[edge.target_node_id],  # type: ignore[attr-defined]
            "target_input": edge.target_input_name,  # type: ignore[attr-defined]
            "condition": condition,
        }

    async def export(self, protocol: ResearchProtocol) -> str:
        """Serialise *protocol* to a YAML string.

        The protocol must already be loaded with all nested relationships
        (nodes, edges, inputs, outputs, quality_gates, assignees).

        Args:
            protocol: Fully-loaded :class:`~db.models.protocols.ResearchProtocol`.

        Returns:
            YAML string ready to serve as a file download.

        """
        node_id_to_task_id: dict[int, str] = {n.id: n.task_id for n in protocol.nodes}

        data: dict = {
            "protocol_schema_version": "1.0",
            "name": protocol.name,
            "study_type": protocol.study_type,
        }
        if protocol.description:
            data["description"] = protocol.description

        data["nodes"] = [self._node_to_dict(n) for n in protocol.nodes]
        data["edges"] = [self._edge_to_dict(e, node_id_to_task_id) for e in protocol.edges]

        logger.info("protocol_yaml.export", protocol_id=protocol.id, name=protocol.name)
        return yaml.dump(data, allow_unicode=True, sort_keys=False)

    def _schema_to_payloads(self, schema: ProtocolExportSchema) -> tuple[list[dict], list[dict]]:
        """Convert a validated export schema to nodes_payload and edges_payload dicts."""
        nodes_payload: list[dict] = []
        for n in schema.nodes:
            nodes_payload.append(
                {
                    "task_id": n.task_id,
                    "task_type": n.task_type,
                    "label": n.label,
                    "description": n.description,
                    "is_required": n.is_required,
                    "inputs": [
                        {"name": i.name, "data_type": i.data_type, "is_required": i.is_required}
                        for i in n.inputs
                    ],
                    "outputs": [{"name": o.name, "data_type": o.data_type} for o in n.outputs],
                    "quality_gates": [
                        {"gate_type": g.gate_type, "config": g.config} for g in n.quality_gates
                    ],
                    "assignees": [
                        {"assignee_type": a.type, "role": a.role, "agent_id": a.agent_id}
                        for a in n.assignees
                    ],
                }
            )

        edges_payload: list[dict] = []
        for e in schema.edges:
            ed: dict = {
                "edge_id": e.edge_id,
                "source_task_id": e.source_task_id,
                "source_output_name": e.source_output,
                "target_task_id": e.target_task_id,
                "target_input_name": e.target_input,
                "condition": None,
            }
            if e.condition is not None:
                ed["condition"] = {
                    "output_name": e.condition.output_name,
                    "operator": e.condition.operator,
                    "value": e.condition.value,
                }
            edges_payload.append(ed)

        return nodes_payload, edges_payload

    async def import_yaml(
        self,
        yaml_str: str,
        user_id: int,
        db: AsyncSession,
    ) -> ResearchProtocol:
        """Parse *yaml_str* and persist a new custom protocol owned by *user_id*.

        Args:
            yaml_str: Raw YAML content from an uploaded file.
            user_id: ID of the owning researcher.
            db: Active async database session.

        Returns:
            The newly created :class:`~db.models.protocols.ResearchProtocol`.

        Raises:
            :class:`fastapi.HTTPException` 400: On YAML parse error, unsupported
                schema version, cycle, unknown task type, or dangling input.

        """
        try:
            raw = yaml.safe_load(yaml_str)
        except yaml.YAMLError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"YAML parse error: {exc}",
            ) from exc

        if not isinstance(raw, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="YAML root must be a mapping.",
            )

        try:
            schema = ProtocolExportSchema.model_validate(raw)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        nodes_payload, edges_payload = self._schema_to_payloads(schema)

        logger.info("protocol_yaml.import", name=schema.name, study_type=schema.study_type)
        return await create_protocol(
            name=schema.name,
            study_type=schema.study_type,
            description=schema.description,
            nodes_payload=nodes_payload,
            edges_payload=edges_payload,
            user_id=user_id,
            db=db,
        )
