"""ORM models for feature 007: SLR workflow.

Feature 007 additions:
- :class:`ReviewProtocolStatus` — protocol lifecycle states.
- :class:`SynthesisApproach` — synthesis method choices.
- :class:`ChecklistScoringMethod` — item scoring types.
- :class:`AgreementRoundType` — screening round labels.
- :class:`SynthesisStatus` — synthesis job states.
- :class:`GreyLiteratureType` — non-database source types.
- :class:`ReviewProtocol` — one protocol per SLR study.
- :class:`QualityAssessmentChecklist` — study-scoped QA checklist.
- :class:`QualityChecklistItem` — individual scored checklist items.
- :class:`QualityAssessmentScore` — one score per (reviewer, paper, item).
- :class:`InterRaterAgreementRecord` — Cohen's Kappa calculation record.
- :class:`SynthesisResult` — one synthesis run for a study.
- :class:`GreyLiteratureSource` — non-database literature entries.
"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from db.base import Base


class ReviewProtocolStatus(str, enum.Enum):
    """Protocol lifecycle states.

    Transitions::

        draft → under_review → draft (rejected) | validated (approved)
    """

    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    VALIDATED = "validated"


class SynthesisApproach(str, enum.Enum):
    """Synthesis method for a review or synthesis run."""

    META_ANALYSIS = "meta_analysis"
    DESCRIPTIVE = "descriptive"
    QUALITATIVE = "qualitative"
    NARRATIVE = "narrative"
    THEMATIC = "thematic"


class ChecklistScoringMethod(str, enum.Enum):
    """Scoring input type for a quality checklist item."""

    BINARY = "binary"
    SCALE_1_3 = "scale_1_3"
    SCALE_1_5 = "scale_1_5"


class AgreementRoundType(str, enum.Enum):
    """Screening round for which inter-rater agreement is computed."""

    TITLE_ABSTRACT = "title_abstract"
    INTRO_CONCLUSIONS = "intro_conclusions"
    FULL_TEXT = "full_text"
    QUALITY_ASSESSMENT = "quality_assessment"


class SynthesisStatus(str, enum.Enum):
    """ARQ synthesis job execution states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class GreyLiteratureType(str, enum.Enum):
    """Type of non-database grey literature source."""

    TECHNICAL_REPORT = "technical_report"
    DISSERTATION = "dissertation"
    REJECTED_PUBLICATION = "rejected_publication"
    WORK_IN_PROGRESS = "work_in_progress"


class ReviewProtocol(Base):
    """One SLR protocol per study.

    A study cannot advance past the protocol phase until ``status`` is
    ``validated``.  Uses optimistic locking (``version_id``) to prevent
    lost-update conflicts during concurrent edits.
    """

    __tablename__ = "review_protocol"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    status: Mapped[ReviewProtocolStatus] = mapped_column(
        Enum(ReviewProtocolStatus, name="review_protocol_status_enum"),
        nullable=False,
        default=ReviewProtocolStatus.DRAFT,
        server_default=ReviewProtocolStatus.DRAFT.value,
    )
    background: Mapped[str | None] = mapped_column(Text, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_questions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    pico_population: Mapped[str | None] = mapped_column(Text, nullable=True)
    pico_intervention: Mapped[str | None] = mapped_column(Text, nullable=True)
    pico_comparison: Mapped[str | None] = mapped_column(Text, nullable=True)
    pico_outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    pico_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    search_strategy: Mapped[str | None] = mapped_column(Text, nullable=True)
    inclusion_criteria: Mapped[list | None] = mapped_column(JSON, nullable=True)
    exclusion_criteria: Mapped[list | None] = mapped_column(JSON, nullable=True)
    data_extraction_strategy: Mapped[str | None] = mapped_column(Text, nullable=True)
    synthesis_approach: Mapped[SynthesisApproach | None] = mapped_column(
        Enum(SynthesisApproach, name="synthesis_approach_enum"),
        nullable=True,
    )
    dissemination_strategy: Mapped[str | None] = mapped_column(Text, nullable=True)
    timetable: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_report: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="AI reviewer JSON feedback"
    )
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __mapper_args__ = {"version_id_col": version_id}

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<ReviewProtocol id={self.id} study_id={self.study_id} status={self.status}>"


class QualityAssessmentChecklist(Base):
    """Named, study-scoped checklist of quality assessment items.

    One study may have exactly one checklist.  Items are defined via the
    :class:`QualityChecklistItem` relationship.
    """

    __tablename__ = "quality_assessment_checklist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    items: Mapped[list[QualityChecklistItem]] = relationship(
        "QualityChecklistItem",
        back_populates="checklist",
        cascade="all, delete-orphan",
        order_by="QualityChecklistItem.order",
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<QualityAssessmentChecklist id={self.id} study_id={self.study_id} name={self.name!r}>"
        )


class QualityChecklistItem(Base):
    """Individual scored item within a quality assessment checklist.

    ``weight`` defaults to 1.0 and is used when computing the weighted
    aggregate quality score for a paper.
    """

    __tablename__ = "quality_checklist_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    checklist_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quality_assessment_checklist.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    scoring_method: Mapped[ChecklistScoringMethod] = mapped_column(
        Enum(ChecklistScoringMethod, name="checklist_scoring_method_enum"),
        nullable=False,
    )
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0, server_default="1.0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    checklist: Mapped[QualityAssessmentChecklist] = relationship(
        "QualityAssessmentChecklist", back_populates="items"
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<QualityChecklistItem id={self.id} checklist_id={self.checklist_id}"
            f" order={self.order}>"
        )


class QualityAssessmentScore(Base):
    """One score row per (reviewer, candidate paper, checklist item) triple.

    Uses optimistic locking (``version_id``) to prevent concurrent overwrites
    when two reviewers submit scores simultaneously.

    The aggregate quality score for a paper per reviewer is computed at query
    time as the weighted average of ``score_value × item.weight`` across all
    items — it is NOT stored in this table.
    """

    __tablename__ = "quality_assessment_score"
    __table_args__ = (
        UniqueConstraint(
            "candidate_paper_id",
            "reviewer_id",
            "checklist_item_id",
            name="uq_quality_assessment_score",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_paper_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("candidate_paper.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reviewer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reviewer.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    checklist_item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quality_checklist_item.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score_value: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __mapper_args__ = {"version_id_col": version_id}

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<QualityAssessmentScore id={self.id}"
            f" candidate_paper_id={self.candidate_paper_id}"
            f" reviewer_id={self.reviewer_id}>"
        )


class InterRaterAgreementRecord(Base):
    """Stores one Cohen's Kappa calculation between two reviewers.

    Records both pre- and post-discussion Kappa values for a given screening
    round within a study.  ``kappa_value`` is ``None`` when the calculation is
    undefined (e.g., zero-variance decisions).
    """

    __tablename__ = "inter_rater_agreement_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reviewer_a_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reviewer.id", ondelete="CASCADE"),
        nullable=False,
    )
    reviewer_b_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reviewer.id", ondelete="CASCADE"),
        nullable=False,
    )
    round_type: Mapped[AgreementRoundType] = mapped_column(
        Enum(AgreementRoundType, name="agreement_round_type_enum"),
        nullable=False,
    )
    phase: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="pre_discussion or post_discussion"
    )
    kappa_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    kappa_undefined_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    n_papers: Mapped[int] = mapped_column(Integer, nullable=False)
    threshold_met: Mapped[bool] = mapped_column(Boolean, nullable=False)
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
            f"<InterRaterAgreementRecord id={self.id} study_id={self.study_id}"
            f" round={self.round_type} kappa={self.kappa_value}>"
        )


class SynthesisResult(Base):
    """One completed (or in-progress) synthesis run for a study.

    Uses optimistic locking (``version_id``) to prevent concurrent job
    updates from overwriting each other's results.
    """

    __tablename__ = "synthesis_result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    approach: Mapped[SynthesisApproach] = mapped_column(
        Enum(SynthesisApproach, name="synthesis_approach_enum"),
        nullable=False,
    )
    status: Mapped[SynthesisStatus] = mapped_column(
        Enum(SynthesisStatus, name="synthesis_status_enum"),
        nullable=False,
        default=SynthesisStatus.PENDING,
        server_default=SynthesisStatus.PENDING.value,
    )
    model_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="fixed or random (meta-analysis only)"
    )
    parameters: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Input configuration"
    )
    computed_statistics: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Pooled effect, SE, CI, Q, tau2, I2, Kappa, etc."
    )
    forest_plot_svg: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="SVG string for descriptive synthesis"
    )
    funnel_plot_svg: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="SVG string for meta-analysis"
    )
    qualitative_themes: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Theme-to-paper mapping for qualitative synthesis"
    )
    sensitivity_analysis: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Subset results"
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Error detail if status=failed"
    )
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __mapper_args__ = {"version_id_col": version_id}

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<SynthesisResult id={self.id} study_id={self.study_id}"
            f" approach={self.approach} status={self.status}>"
        )


class GreyLiteratureSource(Base):
    """Non-database literature entry tracked per study.

    Used to record technical reports, dissertations, rejected publications,
    and work-in-progress items that cannot be retrieved from standard
    academic databases.
    """

    __tablename__ = "grey_literature_source"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_type: Mapped[GreyLiteratureType] = mapped_column(
        Enum(GreyLiteratureType, name="grey_literature_type_enum"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    authors: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Why included / relevance"
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

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<GreyLiteratureSource id={self.id} study_id={self.study_id}"
            f" type={self.source_type} title={self.title[:40]!r}>"
        )
