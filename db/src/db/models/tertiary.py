"""ORM models for feature 009: Tertiary Studies Workflow.

Feature 009 additions:
- :class:`TertiaryProtocolStatus` — protocol lifecycle states (draft, validated).
- :class:`SecondaryStudyType` — type labels for secondary studies under review.
- :class:`TertiaryStudyProtocol` — one protocol per Tertiary Study.
- :class:`SecondaryStudySeedImport` — import audit record per seed operation.
- :class:`TertiaryDataExtraction` — secondary-study-specific extraction fields.
"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
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
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from db.base import Base


class TertiaryProtocolStatus(str, enum.Enum):
    """Protocol lifecycle states for a Tertiary Study.

    Transitions::

        draft → validated
        validated → draft  (on rejection via protocol review)
    """

    DRAFT = "draft"
    VALIDATED = "validated"


class SecondaryStudyType(str, enum.Enum):
    """Type of a secondary study included in a Tertiary Study's corpus."""

    SLR = "SLR"
    SMS = "SMS"
    RAPID_REVIEW = "RAPID_REVIEW"
    UNKNOWN = "UNKNOWN"


class TertiaryStudyProtocol(Base):
    """Research protocol for a Tertiary Study.

    One record per Tertiary Study.  Uses SQLAlchemy optimistic locking via
    ``version_id_col`` to prevent concurrent edit conflicts (HTTP 409 on
    stale updates).
    """

    __tablename__ = "tertiary_study_protocol"
    __table_args__ = (UniqueConstraint("study_id", name="uq_tertiary_protocol_study"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Lifecycle
    status: Mapped[TertiaryProtocolStatus] = mapped_column(
        Enum(TertiaryProtocolStatus, name="tertiary_protocol_status_enum"),
        nullable=False,
        default=TertiaryProtocolStatus.DRAFT,
        server_default=TertiaryProtocolStatus.DRAFT.value,
    )

    # Protocol content fields
    background: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_questions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    secondary_study_types: Mapped[list | None] = mapped_column(JSON, nullable=True)
    inclusion_criteria: Mapped[list | None] = mapped_column(JSON, nullable=True)
    exclusion_criteria: Mapped[list | None] = mapped_column(JSON, nullable=True)
    recency_cutoff_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    search_strategy: Mapped[str | None] = mapped_column(Text, nullable=True)
    quality_threshold: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Uses the existing SynthesisApproach enum from the SLR workflow.
    # Stored as the string enum name; validated at the application layer.
    synthesis_approach: Mapped[str | None] = mapped_column(
        Enum(
            "meta_analysis",
            "descriptive",
            "qualitative",
            name="synthesis_approach_enum",
            create_constraint=False,
        ),
        nullable=True,
    )

    dissemination_strategy: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Audit / optimistic locking
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
        return f"<TertiaryStudyProtocol id={self.id} study_id={self.study_id} status={self.status}>"


class SecondaryStudySeedImport(Base):
    """Audit record for a single seed import operation.

    Tracks which source study's included papers were copied into a Tertiary
    Study's candidate corpus, how many records were added vs. skipped as
    duplicates, and who triggered the import.
    """

    __tablename__ = "secondary_study_seed_import"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target_study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_study_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    records_added: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    records_skipped: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    imported_by_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<SecondaryStudySeedImport id={self.id}"
            f" target={self.target_study_id} source={self.source_study_id}"
            f" added={self.records_added}>"
        )


class TertiaryDataExtraction(Base):
    """Secondary-study-specific extraction fields for an included secondary study.

    One record per included ``CandidatePaper`` in a Tertiary Study.  Covers
    the nine extraction fields that are unique to secondary literature
    (as opposed to empirical papers).  Uses optimistic locking.
    """

    __tablename__ = "tertiary_data_extraction"
    __table_args__ = (
        UniqueConstraint("candidate_paper_id", name="uq_tertiary_extraction_candidate_paper"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_paper_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("candidate_paper.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Secondary-study-specific extraction fields
    secondary_study_type: Mapped[SecondaryStudyType | None] = mapped_column(
        Enum(SecondaryStudyType, name="secondary_study_type_enum"),
        nullable=True,
    )
    research_questions_addressed: Mapped[list | None] = mapped_column(JSON, nullable=True)
    databases_searched: Mapped[list | None] = mapped_column(JSON, nullable=True)
    study_period_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    study_period_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    primary_study_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    synthesis_approach_used: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_findings: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_gaps: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewer_quality_rating: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Reuses the existing ExtractionStatus enum from the SMS workflow.
    extraction_status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "ai_complete",
            "validated",
            "human_reviewed",
            name="extraction_status_enum",
            create_constraint=False,
        ),
        nullable=False,
        default="pending",
        server_default="pending",
    )
    extracted_by_agent: Mapped[str | None] = mapped_column(String(256), nullable=True)
    validated_by_reviewer_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Audit / optimistic locking
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
            f"<TertiaryDataExtraction id={self.id}"
            f" candidate_paper_id={self.candidate_paper_id}"
            f" status={self.extraction_status}>"
        )
