"""ORM models: Study, Paper, StudyPaper."""

import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
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
    """

    PENDING = "pending"
    INCLUDED = "included"
    EXCLUDED = "excluded"


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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    study_papers: Mapped[list["StudyPaper"]] = relationship(
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    study_papers: Mapped[list["StudyPaper"]] = relationship(
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

    study: Mapped["Study"] = relationship("Study", back_populates="study_papers")
    paper: Mapped["Paper"] = relationship("Paper", back_populates="study_papers")

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<StudyPaper study_id={self.study_id} paper_id={self.paper_id}"
            f" status={self.inclusion_status}>"
        )
