"""CandidatePaper and PaperDecision models."""

import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class CandidatePaperStatus(str, enum.Enum):
    """Lifecycle states of a candidate paper within a study."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"


class PaperDecisionType(str, enum.Enum):
    """Possible paper review decisions."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"


class CandidatePaper(Base):
    """Join entity: one row per (study, paper) pair discovered during any search phase.

    Uses SQLAlchemy optimistic locking via version_id_col.
    """

    __tablename__ = "candidate_paper"
    __table_args__ = (
        UniqueConstraint("study_id", "paper_id", name="uq_candidate_paper_study_paper"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    study_id: Mapped[int] = mapped_column(
        ForeignKey("study.id", ondelete="CASCADE"), nullable=False, index=True
    )
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("paper.id", ondelete="CASCADE"), nullable=False
    )
    search_execution_id: Mapped[int] = mapped_column(
        ForeignKey("search_execution.id", ondelete="CASCADE"), nullable=False
    )
    phase_tag: Mapped[str] = mapped_column(String(64), nullable=False)
    current_status: Mapped[CandidatePaperStatus] = mapped_column(
        Enum(CandidatePaperStatus, name="candidate_paper_status_enum"),
        nullable=False,
        default=CandidatePaperStatus.PENDING,
        server_default=CandidatePaperStatus.PENDING.value,
    )
    duplicate_of_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidate_paper.id", ondelete="SET NULL"), nullable=True
    )
    conflict_flag: Mapped[bool] = mapped_column(
        Integer, nullable=False, default=False, server_default="0"
    )
    # Feature 009: set when the paper was added via a tertiary seed import.
    source_seed_import_id: Mapped[int | None] = mapped_column(
        ForeignKey("secondary_study_seed_import.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
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
            f"<CandidatePaper id={self.id} study_id={self.study_id}"
            f" paper_id={self.paper_id} status={self.current_status}>"
        )


class PaperDecision(Base):
    """Audit log of every decision (AI or human) made on a CandidatePaper."""

    __tablename__ = "paper_decision"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_paper_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_paper.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reviewer_id: Mapped[int] = mapped_column(
        ForeignKey("reviewer.id", ondelete="CASCADE"), nullable=False
    )
    decision: Mapped[PaperDecisionType] = mapped_column(
        Enum(PaperDecisionType, name="paper_decision_type_enum"), nullable=False
    )
    reasons: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_override: Mapped[bool] = mapped_column(
        Integer, nullable=False, default=False, server_default="0"
    )
    overrides_decision_id: Mapped[int | None] = mapped_column(
        ForeignKey("paper_decision.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<PaperDecision id={self.id} candidate_paper_id={self.candidate_paper_id}"
            f" decision={self.decision}>"
        )
