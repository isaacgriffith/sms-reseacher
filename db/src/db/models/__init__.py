"""ORM models package: Study, Paper, StudyPaper and all submodels.

Feature 010 additions — re-exported here for single stable import path:
- :class:`~db.models.protocols.ProtocolTaskType`
- :class:`~db.models.protocols.QualityGateType`
- :class:`~db.models.protocols.EdgeConditionOperator`
- :class:`~db.models.protocols.TaskNodeStatus`
- :class:`~db.models.protocols.NodeAssigneeType`
- :class:`~db.models.protocols.NodeDataType`
- :class:`~db.models.protocols.ResearchProtocol`
- :class:`~db.models.protocols.ProtocolNode`
- :class:`~db.models.protocols.ProtocolNodeInput`
- :class:`~db.models.protocols.ProtocolNodeOutput`
- :class:`~db.models.protocols.QualityGate`
- :class:`~db.models.protocols.NodeAssignee`
- :class:`~db.models.protocols.ProtocolEdge`
- :class:`~db.models.protocols.StudyProtocolAssignment`
- :class:`~db.models.protocols.TaskExecutionState`

Feature 009 additions — re-exported here for single stable import path:
- :class:`~db.models.tertiary.TertiaryProtocolStatus`
- :class:`~db.models.tertiary.SecondaryStudyType`
- :class:`~db.models.tertiary.TertiaryStudyProtocol`
- :class:`~db.models.tertiary.SecondaryStudySeedImport`
- :class:`~db.models.tertiary.TertiaryDataExtraction`

Feature 008 additions — re-exported here for single stable import path:
- :class:`~db.models.rapid_review.RRProtocolStatus`
- :class:`~db.models.rapid_review.RRQualityAppraisalMode`
- :class:`~db.models.rapid_review.RRInvolvementType`
- :class:`~db.models.rapid_review.RRThreatType`
- :class:`~db.models.rapid_review.BriefingStatus`
- :class:`~db.models.rapid_review.RapidReviewProtocol`
- :class:`~db.models.rapid_review.PractitionerStakeholder`
- :class:`~db.models.rapid_review.RRThreatToValidity`
- :class:`~db.models.rapid_review.RRNarrativeSynthesisSection`
- :class:`~db.models.rapid_review.EvidenceBriefing`
- :class:`~db.models.rapid_review.EvidenceBriefingShareToken`

This package supersedes the top-level ``models.py`` file.  All core models
(Study, Paper, StudyPaper) are defined here so that ``from db.models import Study``
continues to work correctly when the ``models/`` package takes precedence over
``models.py`` in Python's import resolution.

Feature 004 additions — re-exported here for single stable import path:
- :class:`~db.models.backup_codes.BackupCode`
- :class:`~db.models.security_audit.SecurityAuditEvent`
- :class:`~db.models.users.ThemePreference`
- :class:`~db.models.security_audit.SecurityEventType`

Feature 005 additions — re-exported here for single stable import path:
- :class:`~db.models.agents.ProviderType`
- :class:`~db.models.agents.AgentTaskType`
- :class:`~db.models.agents.Provider`
- :class:`~db.models.agents.AvailableModel`
- :class:`~db.models.agents.Agent`

Feature 006 additions — re-exported here for single stable import path:
- :class:`~db.models.search_integrations.DatabaseIndex`
- :class:`~db.models.search_integrations.IntegrationType`
- :class:`~db.models.search_integrations.TestStatus`
- :class:`~db.models.search_integrations.FullTextSource`
- :class:`~db.models.search_integrations.StudyDatabaseSelection`
- :class:`~db.models.search_integrations.SearchIntegrationCredential`

Feature 007 additions — re-exported here for single stable import path:
- :class:`~db.models.slr.ReviewProtocolStatus`
- :class:`~db.models.slr.SynthesisApproach`
- :class:`~db.models.slr.ChecklistScoringMethod`
- :class:`~db.models.slr.AgreementRoundType`
- :class:`~db.models.slr.SynthesisStatus`
- :class:`~db.models.slr.GreyLiteratureType`
- :class:`~db.models.slr.ReviewProtocol`
- :class:`~db.models.slr.QualityAssessmentChecklist`
- :class:`~db.models.slr.QualityChecklistItem`
- :class:`~db.models.slr.QualityAssessmentScore`
- :class:`~db.models.slr.InterRaterAgreementRecord`
- :class:`~db.models.slr.SynthesisResult`
- :class:`~db.models.slr.GreyLiteratureSource`
"""

# Feature 004: new models and enums (imported first so Alembic autogenerate
# detects them when env.py imports this package).
import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from db.base import Base

# Feature 005: provider/model/agent models.
from db.models.agents import Agent as Agent  # noqa: F401
from db.models.agents import AgentTaskType as AgentTaskType  # noqa: F401
from db.models.agents import AvailableModel as AvailableModel  # noqa: F401
from db.models.agents import Provider as Provider  # noqa: F401
from db.models.agents import ProviderType as ProviderType  # noqa: F401
from db.models.backup_codes import BackupCode as BackupCode  # noqa: F401

# Feature 010: Research Protocol Definition models and enums.
from db.models.protocols import EdgeConditionOperator as EdgeConditionOperator  # noqa: F401
from db.models.protocols import NodeAssignee as NodeAssignee  # noqa: F401
from db.models.protocols import NodeAssigneeType as NodeAssigneeType  # noqa: F401
from db.models.protocols import NodeDataType as NodeDataType  # noqa: F401
from db.models.protocols import ProtocolEdge as ProtocolEdge  # noqa: F401
from db.models.protocols import ProtocolNode as ProtocolNode  # noqa: F401
from db.models.protocols import ProtocolNodeInput as ProtocolNodeInput  # noqa: F401
from db.models.protocols import ProtocolNodeOutput as ProtocolNodeOutput  # noqa: F401
from db.models.protocols import ProtocolTaskType as ProtocolTaskType  # noqa: F401
from db.models.protocols import QualityGate as QualityGate  # noqa: F401
from db.models.protocols import QualityGateType as QualityGateType  # noqa: F401
from db.models.protocols import ResearchProtocol as ResearchProtocol  # noqa: F401
from db.models.protocols import StudyProtocolAssignment as StudyProtocolAssignment  # noqa: F401
from db.models.protocols import TaskExecutionState as TaskExecutionState  # noqa: F401
from db.models.protocols import TaskNodeStatus as TaskNodeStatus  # noqa: F401

# Feature 008: Rapid Review workflow models and enums.
from db.models.rapid_review import BriefingStatus as BriefingStatus  # noqa: F401
from db.models.rapid_review import EvidenceBriefing as EvidenceBriefing  # noqa: F401
from db.models.rapid_review import (  # noqa: F401
    EvidenceBriefingShareToken as EvidenceBriefingShareToken,
)
from db.models.rapid_review import (  # noqa: F401
    PractitionerStakeholder as PractitionerStakeholder,
)
from db.models.rapid_review import RapidReviewProtocol as RapidReviewProtocol  # noqa: F401
from db.models.rapid_review import (  # noqa: F401
    RRInvolvementType as RRInvolvementType,
)
from db.models.rapid_review import (  # noqa: F401
    RRNarrativeSynthesisSection as RRNarrativeSynthesisSection,
)
from db.models.rapid_review import RRProtocolStatus as RRProtocolStatus  # noqa: F401
from db.models.rapid_review import (  # noqa: F401
    RRQualityAppraisalMode as RRQualityAppraisalMode,
)
from db.models.rapid_review import RRThreatToValidity as RRThreatToValidity  # noqa: F401
from db.models.rapid_review import RRThreatType as RRThreatType  # noqa: F401

# Feature 006: database search integrations and full-text retrieval models.
from db.models.search_integrations import DatabaseIndex as DatabaseIndex  # noqa: F401
from db.models.search_integrations import FullTextSource as FullTextSource  # noqa: F401
from db.models.search_integrations import IntegrationType as IntegrationType  # noqa: F401
from db.models.search_integrations import (  # noqa: F401
    SearchIntegrationCredential as SearchIntegrationCredential,
)
from db.models.search_integrations import (  # noqa: F401
    StudyDatabaseSelection as StudyDatabaseSelection,
)
from db.models.search_integrations import TestStatus as TestStatus  # noqa: F401
from db.models.security_audit import SecurityAuditEvent as SecurityAuditEvent  # noqa: F401
from db.models.security_audit import SecurityEventType as SecurityEventType  # noqa: F401

# Feature 007: SLR workflow models.
from db.models.slr import AgreementRoundType as AgreementRoundType  # noqa: F401
from db.models.slr import ChecklistScoringMethod as ChecklistScoringMethod  # noqa: F401
from db.models.slr import GreyLiteratureSource as GreyLiteratureSource  # noqa: F401
from db.models.slr import GreyLiteratureType as GreyLiteratureType  # noqa: F401
from db.models.slr import InterRaterAgreementRecord as InterRaterAgreementRecord  # noqa: F401
from db.models.slr import QualityAssessmentChecklist as QualityAssessmentChecklist  # noqa: F401
from db.models.slr import QualityAssessmentScore as QualityAssessmentScore  # noqa: F401
from db.models.slr import QualityChecklistItem as QualityChecklistItem  # noqa: F401
from db.models.slr import ReviewProtocol as ReviewProtocol  # noqa: F401
from db.models.slr import ReviewProtocolStatus as ReviewProtocolStatus  # noqa: F401
from db.models.slr import SynthesisApproach as SynthesisApproach  # noqa: F401
from db.models.slr import SynthesisResult as SynthesisResult  # noqa: F401
from db.models.slr import SynthesisStatus as SynthesisStatus  # noqa: F401

# Feature 009: Tertiary Studies Workflow models.
from db.models.tertiary import SecondaryStudySeedImport as SecondaryStudySeedImport  # noqa: F401
from db.models.tertiary import SecondaryStudyType as SecondaryStudyType  # noqa: F401
from db.models.tertiary import TertiaryDataExtraction as TertiaryDataExtraction  # noqa: F401
from db.models.tertiary import TertiaryProtocolStatus as TertiaryProtocolStatus  # noqa: F401
from db.models.tertiary import TertiaryStudyProtocol as TertiaryStudyProtocol  # noqa: F401
from db.models.users import ThemePreference as ThemePreference  # noqa: F401


class StudyType(str, enum.Enum):
    """Allowed study types."""

    SMS = "SMS"
    SLR = "SLR"
    TERTIARY = "Tertiary"
    RAPID = "Rapid"


class StudyStatus(str, enum.Enum):
    """Study lifecycle states.

    Transitions::

        draft → active → completed
                      └→ archived
    """

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class InclusionStatus(str, enum.Enum):
    """Paper inclusion states within a study.

    Transitions::

        pending → included
                └→ excluded
                └→ protocol_invalidated  (Rapid Review only — 008)

    ``PROTOCOL_INVALIDATED`` is set on all collected papers when a validated
    Rapid Review protocol is edited.  Papers in this state must be re-screened
    after the protocol is re-validated.
    """

    PENDING = "pending"
    INCLUDED = "included"
    EXCLUDED = "excluded"
    PROTOCOL_INVALIDATED = "protocol_invalidated"


class Study(Base):
    """Represents a systematic research study (SMS, SLR, Tertiary, or Rapid)."""

    __tablename__ = "study"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    study_type: Mapped[StudyType] = mapped_column(
        Enum(StudyType, name="study_type_enum"), nullable=False
    )
    status: Mapped[StudyStatus] = mapped_column(
        Enum(StudyStatus, name="study_status_enum"),
        nullable=False,
        default=StudyStatus.DRAFT,
        server_default=StudyStatus.DRAFT.value,
    )
    # Phase 2 extensions
    topic: Mapped[str | None] = mapped_column(Text, nullable=True)
    motivation: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_phase: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default="1"
    )
    research_group_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("research_group.id", ondelete="SET NULL"), nullable=True, index=True
    )
    snowball_threshold: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=5, server_default="5"
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSON, nullable=True, comment="Flexible study metadata (objectives, questions)"
    )
    # Validity discussion (Phase 4) — six text dimensions, stored as a JSON object
    validity: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment=(
            "Validity discussion dimensions: descriptive, theoretical, "
            "generalizability_internal, generalizability_external, "
            "interpretive, repeatability"
        ),
    )
    # Phase-gate staleness timestamps — set by the endpoint that produces each phase's data
    pico_saved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    search_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    extraction_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    study_papers: Mapped[list[StudyPaper]] = relationship(
        "StudyPaper", back_populates="study", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<Study id={self.id} name={self.name!r} type={self.study_type}>"


class Paper(Base):
    """Represents a single academic paper."""

    __tablename__ = "paper"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSON, nullable=True, comment="Flexible bibliographic fields"
    )
    # Phase 2 extensions
    authors: Mapped[list | None] = mapped_column(JSON, nullable=True)
    year: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_text_available: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    # Feature 006: full-text retrieval and Markdown conversion
    full_text_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_text_source: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="FullTextSource enum value: unpaywall|direct|scihub|unavailable|pending",
    )
    full_text_converted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    study_papers: Mapped[list[StudyPaper]] = relationship(
        "StudyPaper", back_populates="paper", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<Paper id={self.id} doi={self.doi!r} title={self.title[:40]!r}>"


class StudyPaper(Base):
    """Join table linking a Study to a Paper with an inclusion decision."""

    __tablename__ = "study_paper"
    __table_args__ = (UniqueConstraint("study_id", "paper_id", name="uq_study_paper"),)

    study_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("study.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
    paper_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("paper.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
    inclusion_status: Mapped[InclusionStatus | None] = mapped_column(
        Enum(InclusionStatus, name="inclusion_status_enum"),
        nullable=True,
        default=InclusionStatus.PENDING,
    )

    study: Mapped[Study] = relationship("Study", back_populates="study_papers")
    paper: Mapped[Paper] = relationship("Paper", back_populates="study_papers")

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<StudyPaper study_id={self.study_id} paper_id={self.paper_id}"
            f" status={self.inclusion_status}>"
        )
