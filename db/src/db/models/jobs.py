"""BackgroundJob model for tracking async ARQ jobs."""

import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class JobType(str, enum.Enum):
    """Types of background jobs."""

    FULL_SEARCH = "full_search"
    SNOWBALL_SEARCH = "snowball_search"
    BATCH_EXTRACTION = "batch_extraction"
    GENERATE_RESULTS = "generate_results"
    EXPORT = "export"
    QUALITY_EVAL = "quality_eval"
    VALIDITY_PREFILL = "validity_prefill"
    EXPERT_SEED = "expert_seed"
    TEST_SEARCH = "test_search"


class JobStatus(str, enum.Enum):
    """Background job lifecycle states."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BackgroundJob(Base):
    """Tracks an async ARQ background job with progress state."""

    __tablename__ = "background_job"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    study_id: Mapped[int] = mapped_column(
        ForeignKey("study.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_type: Mapped[JobType] = mapped_column(
        Enum(JobType, name="background_job_type_enum"), nullable=False
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="background_job_status_enum"),
        nullable=False,
        default=JobStatus.QUEUED,
        server_default=JobStatus.QUEUED.value,
    )
    progress_pct: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0"
    )
    progress_detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    queued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f"<BackgroundJob id={self.id!r} type={self.job_type} status={self.status}>"
