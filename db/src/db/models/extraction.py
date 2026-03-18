"""DataExtraction and ExtractionFieldAudit models."""

import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class ResearchType(str, enum.Enum):
    """Research type classification per R1–R6 decision rules."""

    EVALUATION = "evaluation"
    SOLUTION_PROPOSAL = "solution_proposal"
    VALIDATION = "validation"
    PHILOSOPHICAL = "philosophical"
    OPINION = "opinion"
    PERSONAL_EXPERIENCE = "personal_experience"
    UNKNOWN = "unknown"


class ExtractionStatus(str, enum.Enum):
    """Lifecycle states of a DataExtraction record."""

    PENDING = "pending"
    AI_COMPLETE = "ai_complete"
    VALIDATED = "validated"
    HUMAN_REVIEWED = "human_reviewed"


class DataExtraction(Base):
    """Structured extraction for one accepted paper within a study.

    Uses SQLAlchemy optimistic locking via version_id_col to prevent
    concurrent edit conflicts (HTTP 409 on stale updates).
    """

    __tablename__ = "data_extraction"
    __table_args__ = (
        UniqueConstraint("candidate_paper_id", name="uq_data_extraction_candidate_paper"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_paper_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_paper.id", ondelete="CASCADE"), nullable=False, index=True
    )
    research_type: Mapped[ResearchType] = mapped_column(
        Enum(ResearchType, name="research_type_enum"),
        nullable=False,
        default=ResearchType.UNKNOWN,
        server_default=ResearchType.UNKNOWN.value,
    )
    venue_type: Mapped[str] = mapped_column(
        String(128), nullable=False, default="", server_default=""
    )
    venue_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    author_details: Mapped[list | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    open_codings: Mapped[list | None] = mapped_column(JSON, nullable=True)
    keywords: Mapped[list | None] = mapped_column(JSON, nullable=True)
    question_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    extraction_status: Mapped[ExtractionStatus] = mapped_column(
        Enum(ExtractionStatus, name="extraction_status_enum"),
        nullable=False,
        default=ExtractionStatus.PENDING,
        server_default=ExtractionStatus.PENDING.value,
    )
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    extracted_by_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    validated_by_reviewer_id: Mapped[int | None] = mapped_column(
        ForeignKey("reviewer.id", ondelete="SET NULL"), nullable=True
    )
    conflict_flag: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __mapper_args__ = {"version_id_col": version_id}

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<DataExtraction id={self.id} candidate_paper_id={self.candidate_paper_id}"
            f" status={self.extraction_status}>"
        )


class ExtractionFieldAudit(Base):
    """Preserves the original AI value when a human edits an extraction field.

    Enables "restore original AI value" workflows and fine-grained extraction
    diff views. Separate from the general AuditRecord table (see audit.py).
    """

    __tablename__ = "extraction_field_audit"

    id: Mapped[int] = mapped_column(primary_key=True)
    extraction_id: Mapped[int] = mapped_column(
        ForeignKey("data_extraction.id", ondelete="CASCADE"), nullable=False, index=True
    )
    field_name: Mapped[str] = mapped_column(String(128), nullable=False)
    original_value: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    changed_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<ExtractionFieldAudit id={self.id} extraction_id={self.extraction_id}"
            f" field={self.field_name!r}>"
        )
