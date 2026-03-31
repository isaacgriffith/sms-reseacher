"""ORM models for Research Protocol Definition (feature 010).

Feature 010 additions:

Enums:
- :class:`ProtocolTaskType` — all valid task types across all study types.
- :class:`QualityGateType` — gate evaluation strategy.
- :class:`EdgeConditionOperator` — numeric comparison operators for conditional edges.
- :class:`TaskNodeStatus` — runtime execution state for a protocol node.
- :class:`NodeAssigneeType` — human role vs AI agent assignee.
- :class:`NodeDataType` — typed data slot for node inputs and outputs.

ORM models:
- :class:`ResearchProtocol` — header record for a named protocol graph.
- :class:`ProtocolNode` — a task vertex in a protocol graph.
- :class:`ProtocolNodeInput` — named typed input slot on a node.
- :class:`ProtocolNodeOutput` — named typed output slot on a node.
- :class:`QualityGate` — quality gate condition attached to a node.
- :class:`NodeAssignee` — assignee (human or AI) on a node.
- :class:`ProtocolEdge` — directed information-flow edge between two nodes.
- :class:`StudyProtocolAssignment` — one-to-one mapping of study to protocol.
- :class:`TaskExecutionState` — runtime state of each node within a study execution.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from db.base import Base

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ProtocolTaskType(str, enum.Enum):
    """All valid task types across all supported study types.

    A companion mapping ``VALID_TASK_TYPES_BY_STUDY_TYPE`` in the service layer
    constrains which types are valid for each :class:`~db.models.StudyType`.

    PostgreSQL enum name: ``protocol_task_type_enum``
    """

    DEFINE_PICO = "DefinePICO"
    DEFINE_PROTOCOL = "DefineProtocol"
    DEFINE_SCOPE = "DefineScope"
    BUILD_SEARCH_STRING = "BuildSearchString"
    EXECUTE_SEARCH = "ExecuteSearch"
    GREY_LITERATURE_SEARCH = "GreyLiteratureSearch"
    SEARCH_SECONDARY_STUDIES = "SearchSecondaryStudies"
    SCREEN_PAPERS = "ScreenPapers"
    FULL_TEXT_REVIEW = "FullTextReview"
    SNOWBALL_SEARCH = "SnowballSearch"
    ASSESS_QUALITY = "AssessQuality"
    APPRAISE_QUALITY = "AppraiseQuality"
    CHECK_INTER_RATER_RELIABILITY = "CheckInterRaterReliability"
    IMPORT_SEED_STUDIES = "ImportSeedStudies"
    EXTRACT_DATA = "ExtractData"
    APPRAISE_QUALITY_ITEMS = "AppraiseQualityItems"
    IDENTIFY_THREATS_TO_VALIDITY = "IdentifyThreatsToValidity"
    NARRATIVE_SYNTHESIS = "NarrativeSynthesis"
    SYNTHESIZE_DATA = "SynthesizeData"
    PRODUCE_BRIEFING = "ProduceBriefing"
    VALIDATE_RESULTS = "ValidateResults"
    GENERATE_REPORT = "GenerateReport"
    STAKEHOLDER_ENGAGEMENT = "StakeholderEngagement"


class QualityGateType(str, enum.Enum):
    """Gate evaluation strategy for a quality gate attached to a protocol node.

    PostgreSQL enum name: ``quality_gate_type_enum``
    """

    METRIC_THRESHOLD = "metric_threshold"
    COMPLETION_CHECK = "completion_check"
    HUMAN_SIGN_OFF = "human_sign_off"


class EdgeConditionOperator(str, enum.Enum):
    """Numeric comparison operators for conditional protocol edges.

    PostgreSQL enum name: ``edge_condition_operator_enum``
    """

    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    EQ = "eq"
    NEQ = "neq"


class TaskNodeStatus(str, enum.Enum):
    """Runtime execution state for a protocol node within a study.

    Transitions::

        PENDING → ACTIVE → COMPLETE
                         ↘ GATE_FAILED → ACTIVE (after remediation)
        COMPLETE (via false conditional edge) → SKIPPED

    PostgreSQL enum name: ``task_node_status_enum``
    """

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"
    SKIPPED = "skipped"
    GATE_FAILED = "gate_failed"


class NodeAssigneeType(str, enum.Enum):
    """Whether a protocol node assignee is a human role or an AI agent.

    PostgreSQL enum name: ``node_assignee_type_enum``
    """

    HUMAN_ROLE = "human_role"
    AI_AGENT = "ai_agent"


class NodeDataType(str, enum.Enum):
    """Typed data slot for protocol node inputs and outputs.

    PostgreSQL enum name: ``node_data_type_enum``
    """

    TEXT = "text"
    PICO_STRUCT = "pico_struct"
    SEARCH_STRING = "search_string"
    CANDIDATE_PAPER_LIST = "candidate_paper_list"
    FULL_TEXT_CONTENT = "full_text_content"
    EXTRACTION_RECORD_LIST = "extraction_record_list"
    SYNTHESIS_RESULT = "synthesis_result"
    QUALITY_SCORE = "quality_score"
    PAPER_COUNT = "paper_count"
    BOOLEAN = "boolean"
    REPORT = "report"


# ---------------------------------------------------------------------------
# ORM models
# ---------------------------------------------------------------------------


class ResearchProtocol(Base):
    """Header record for a named research protocol graph.

    Default templates supplied by the platform have ``owner_user_id = NULL``
    and ``is_default_template = True``; they are immutable for all users.
    Researcher-created custom protocols use ``is_default_template = False``
    and carry the creator's ``owner_user_id``.

    Uses SQLAlchemy optimistic locking via ``version_id_col`` to prevent
    concurrent edit conflicts (HTTP 409 on stale PUT requests).
    """

    __tablename__ = "research_protocol"
    __table_args__ = (
        UniqueConstraint("name", "owner_user_id", name="uq_research_protocol_name_owner"),
        Index("ix_research_protocol_owner_study_type", "owner_user_id", "study_type"),
        Index("ix_research_protocol_default_study_type", "is_default_template", "study_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    study_type: Mapped[str] = mapped_column(
        Enum(
            "SMS",
            "SLR",
            "Tertiary",
            "Rapid",
            name="study_type_enum",
            create_constraint=False,
        ),
        nullable=False,
    )
    is_default_template: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    owner_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    nodes: Mapped[list[ProtocolNode]] = relationship(
        "ProtocolNode", back_populates="protocol", cascade="all, delete-orphan"
    )
    edges: Mapped[list[ProtocolEdge]] = relationship(
        "ProtocolEdge", back_populates="protocol", cascade="all, delete-orphan"
    )
    study_assignments: Mapped[list[StudyProtocolAssignment]] = relationship(
        "StudyProtocolAssignment", back_populates="protocol"
    )

    __mapper_args__ = {"version_id_col": version_id}

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<ResearchProtocol id={self.id} name={self.name!r}"
            f" study_type={self.study_type} default={self.is_default_template}>"
        )


class ProtocolNode(Base):
    """A task vertex in a research protocol graph.

    Each node has a researcher-defined ``task_id`` key that is unique within
    its protocol, a ``task_type`` (validated against the study type's allowlist),
    optional layout coordinates for the D3 visual editor, and collections of
    typed input/output slots, quality gates, and assignees.
    """

    __tablename__ = "protocol_node"
    __table_args__ = (UniqueConstraint("protocol_id", "task_id", name="uq_protocol_node_task_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    protocol_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("research_protocol.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[str] = mapped_column(String(100), nullable=False)
    task_type: Mapped[ProtocolTaskType] = mapped_column(
        Enum(ProtocolTaskType, name="protocol_task_type_enum"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    position_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    position_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    protocol: Mapped[ResearchProtocol] = relationship("ResearchProtocol", back_populates="nodes")
    inputs: Mapped[list[ProtocolNodeInput]] = relationship(
        "ProtocolNodeInput", back_populates="node", cascade="all, delete-orphan"
    )
    outputs: Mapped[list[ProtocolNodeOutput]] = relationship(
        "ProtocolNodeOutput", back_populates="node", cascade="all, delete-orphan"
    )
    quality_gates: Mapped[list[QualityGate]] = relationship(
        "QualityGate", back_populates="node", cascade="all, delete-orphan"
    )
    assignees: Mapped[list[NodeAssignee]] = relationship(
        "NodeAssignee", back_populates="node", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<ProtocolNode id={self.id} task_id={self.task_id!r}"
            f" type={self.task_type} protocol={self.protocol_id}>"
        )


class ProtocolNodeInput(Base):
    """Named typed input slot on a protocol node.

    Required inputs (``is_required = True``) must have an incoming edge
    before the protocol graph can be saved.
    """

    __tablename__ = "protocol_node_input"
    __table_args__ = (UniqueConstraint("node_id", "name", name="uq_protocol_node_input_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    node_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("protocol_node.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    data_type: Mapped[NodeDataType] = mapped_column(
        Enum(NodeDataType, name="node_data_type_enum"), nullable=False
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    node: Mapped[ProtocolNode] = relationship("ProtocolNode", back_populates="inputs")

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<ProtocolNodeInput id={self.id} name={self.name!r} type={self.data_type}>"


class ProtocolNodeOutput(Base):
    """Named typed output slot on a protocol node."""

    __tablename__ = "protocol_node_output"
    __table_args__ = (UniqueConstraint("node_id", "name", name="uq_protocol_node_output_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    node_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("protocol_node.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    data_type: Mapped[NodeDataType] = mapped_column(
        Enum(NodeDataType, name="node_data_type_enum"), nullable=False
    )

    node: Mapped[ProtocolNode] = relationship("ProtocolNode", back_populates="outputs")

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<ProtocolNodeOutput id={self.id} name={self.name!r} type={self.data_type}>"


class QualityGate(Base):
    """A quality gate condition attached to a protocol node.

    The ``config`` JSON column holds type-specific parameters validated by
    discriminated Pydantic models in the service layer (see research.md Decision 3):

    - ``metric_threshold``: ``{metric_name, operator, threshold}``
    - ``completion_check``: ``{description}``
    - ``human_sign_off``: ``{required_role, prompt}``
    """

    __tablename__ = "quality_gate"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    node_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("protocol_node.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    gate_type: Mapped[QualityGateType] = mapped_column(
        Enum(QualityGateType, name="quality_gate_type_enum"), nullable=False
    )
    config: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    node: Mapped[ProtocolNode] = relationship("ProtocolNode", back_populates="quality_gates")

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<QualityGate id={self.id} type={self.gate_type} node={self.node_id}>"


class NodeAssignee(Base):
    """An assignee (human role or AI agent) on a protocol node.

    Exactly one of ``role`` (when ``assignee_type = human_role``) or
    ``agent_id`` (when ``assignee_type = ai_agent``) must be non-null;
    this invariant is enforced at the service layer.
    """

    __tablename__ = "node_assignee"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    node_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("protocol_node.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignee_type: Mapped[NodeAssigneeType] = mapped_column(
        Enum(NodeAssigneeType, name="node_assignee_type_enum"), nullable=False
    )
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent.id", ondelete="SET NULL"),
        nullable=True,
    )

    node: Mapped[ProtocolNode] = relationship("ProtocolNode", back_populates="assignees")

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<NodeAssignee id={self.id} type={self.assignee_type}"
            f" role={self.role!r} agent={self.agent_id}>"
        )


class ProtocolEdge(Base):
    """A directed information-flow edge between two task nodes in a protocol.

    The optional condition triple (``condition_output_name``,
    ``condition_operator``, ``condition_value``) is either all set or all null.
    A null ``condition_output_name`` denotes an unconditional edge.

    Cycle detection is performed at the service layer on every save.
    """

    __tablename__ = "protocol_edge"
    __table_args__ = (UniqueConstraint("protocol_id", "edge_id", name="uq_protocol_edge_edge_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    protocol_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("research_protocol.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    edge_id: Mapped[str] = mapped_column(String(100), nullable=False)
    source_node_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("protocol_node.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_output_name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_node_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("protocol_node.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_input_name: Mapped[str] = mapped_column(String(100), nullable=False)
    condition_output_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    condition_operator: Mapped[EdgeConditionOperator | None] = mapped_column(
        Enum(EdgeConditionOperator, name="edge_condition_operator_enum"), nullable=True
    )
    condition_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    protocol: Mapped[ResearchProtocol] = relationship("ResearchProtocol", back_populates="edges")
    source_node: Mapped[ProtocolNode] = relationship("ProtocolNode", foreign_keys=[source_node_id])
    target_node: Mapped[ProtocolNode] = relationship("ProtocolNode", foreign_keys=[target_node_id])

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<ProtocolEdge id={self.id} edge_id={self.edge_id!r}"
            f" {self.source_node_id}→{self.target_node_id}>"
        )


class StudyProtocolAssignment(Base):
    """Associates a study with its assigned protocol (one study → one protocol).

    Created automatically for all new studies (pointing to the matching default
    template) and for existing studies by the ``0018`` Alembic migration.
    Reassignment is blocked while any ``TaskExecutionState.status = ACTIVE``.
    """

    __tablename__ = "study_protocol_assignment"
    __table_args__ = (UniqueConstraint("study_id", name="uq_study_protocol_assignment_study"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    protocol_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("research_protocol.id", ondelete="RESTRICT"),
        nullable=False,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    assigned_by_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )

    protocol: Mapped[ResearchProtocol] = relationship(
        "ResearchProtocol", back_populates="study_assignments"
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<StudyProtocolAssignment id={self.id}"
            f" study={self.study_id} protocol={self.protocol_id}>"
        )


class TaskExecutionState(Base):
    """Runtime state of a single protocol node within a specific study's execution.

    One row per (study, protocol_node) pair. Created for all nodes when a
    protocol is assigned to a study. The ``gate_failure_detail`` JSON column
    is populated when ``status = GATE_FAILED`` with diagnostic information
    including the gate id, measured value, threshold, and remediation guidance.
    """

    __tablename__ = "task_execution_state"
    __table_args__ = (
        UniqueConstraint("study_id", "node_id", name="uq_task_execution_state_study_node"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("protocol_node.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[TaskNodeStatus] = mapped_column(
        Enum(TaskNodeStatus, name="task_node_status_enum"),
        nullable=False,
        default=TaskNodeStatus.PENDING,
        server_default=TaskNodeStatus.PENDING.value,
    )
    gate_failure_detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<TaskExecutionState id={self.id}"
            f" study={self.study_id} node={self.node_id} status={self.status}>"
        )
