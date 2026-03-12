"""SearchExecution and SearchMetrics models."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class SearchExecutionStatus(str, enum.Enum):
    """Search execution lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SearchExecution(Base):
    """One full execution of an active search string across all databases."""

    __tablename__ = "search_execution"

    id: Mapped[int] = mapped_column(primary_key=True)
    study_id: Mapped[int] = mapped_column(
        ForeignKey("study.id", ondelete="CASCADE"), nullable=False, index=True
    )
    search_string_id: Mapped[int] = mapped_column(
        ForeignKey("search_string.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[SearchExecutionStatus] = mapped_column(
        Enum(SearchExecutionStatus, name="search_execution_status_enum"),
        nullable=False,
        default=SearchExecutionStatus.PENDING,
        server_default=SearchExecutionStatus.PENDING.value,
    )
    phase_tag: Mapped[str] = mapped_column(
        String(64), nullable=False, default="initial-search", server_default="initial-search"
    )
    databases_queried: Mapped[list | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    job_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<SearchExecution id={self.id} study_id={self.study_id} status={self.status}>"


class SearchMetrics(Base):
    """Aggregate paper counts for one search execution."""

    __tablename__ = "search_metrics"
    __table_args__ = (UniqueConstraint("search_execution_id", name="uq_search_metrics_execution"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    search_execution_id: Mapped[int] = mapped_column(
        ForeignKey("search_execution.id", ondelete="CASCADE"), nullable=False
    )
    total_identified: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default="0")
    accepted: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default="0")
    rejected: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default="0")
    duplicates: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default="0")
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<SearchMetrics id={self.id} execution_id={self.search_execution_id}"
            f" total={self.total_identified}>"
        )
