"""AuditRecord model for immutable study-level mutation logging (FR-044, NFR-002)."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from db.base import Base


class AuditAction(str, enum.Enum):
    """Allowed mutation action types for audit records."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class AuditRecord(Base):
    """Immutable, append-only record of a study-level data mutation.

    Records every create/update/delete event on audited entities. This table
    is written by ``backend.services.audit`` and is never updated or deleted
    after insertion (NFR-002).

    Scope of audited entities: ``Study`` (metadata), ``PICOComponent``,
    ``SearchString``, ``InclusionCriterion``, ``ExclusionCriterion``,
    ``SeedPaper``, ``SeedAuthor``, ``CandidatePaper`` decisions and conflict
    resolutions, and ``StudyMember`` add/remove. ``DataExtraction`` field edits
    are explicitly excluded (tracked by ``ExtractionFieldAudit``).

    Indexes:
        - ``(study_id, created_at DESC)`` — study admin audit log queries
        - ``(entity_type, entity_id)`` — entity-specific history queries
    """

    __tablename__ = "audit_record"

    __table_args__ = (
        Index("ix_audit_record_study_created", "study_id", "created_at"),
        Index("ix_audit_record_entity", "entity_type", "entity_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        ForeignKey("study.id", ondelete="CASCADE"), nullable=False
    )
    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    actor_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction, name="audit_action_enum"), nullable=False
    )
    field_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    before_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<AuditRecord id={self.id} study={self.study_id}"
            f" entity={self.entity_type}#{self.entity_id} action={self.action}>"
        )
