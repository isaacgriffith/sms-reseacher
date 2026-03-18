"""DomainModel, ClassificationScheme, and QualityReport models for US6 results."""

import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, SmallInteger, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class ChartType(str, enum.Enum):
    """Classification chart categories used in systematic mapping study results."""

    VENUE = "venue"
    AUTHOR = "author"
    LOCALE = "locale"
    INSTITUTION = "institution"
    YEAR = "year"
    SUBTOPIC = "subtopic"
    RESEARCH_TYPE = "research_type"
    RESEARCH_METHOD = "research_method"


class DomainModel(Base):
    """Versioned domain model snapshot produced by DomainModelAgent for a study.

    Captures concepts and relationships extracted from open codings, keywords,
    and paper summaries. Each version is a full snapshot; prior versions are retained.
    """

    __tablename__ = "domain_model"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        ForeignKey("study.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default="1"
    )
    concepts: Mapped[list | None] = mapped_column(JSON, nullable=True)
    relationships: Mapped[list | None] = mapped_column(JSON, nullable=True)
    svg_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
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
        return f"<DomainModel id={self.id} study_id={self.study_id} version={self.version}>"


class ClassificationScheme(Base):
    """Versioned classification chart for one chart_type within a study.

    One row per (study, chart_type, version) triple. Stores the raw chart data
    alongside the rendered SVG so the frontend can re-render or export.
    """

    __tablename__ = "classification_scheme"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        ForeignKey("study.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chart_type: Mapped[ChartType] = mapped_column(
        Enum(ChartType, name="chart_type_enum"), nullable=False
    )
    version: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default="1"
    )
    chart_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    svg_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
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
            f"<ClassificationScheme id={self.id} study_id={self.study_id}"
            f" chart_type={self.chart_type} version={self.version}>"
        )


class QualityReport(Base):
    """Versioned quality assessment report for a study, scored against a 5-criterion rubric.

    Scoring ranges: need_for_review 0–2, search_strategy 0–2,
    search_evaluation 0–3, extraction_classification 0–3, study_validity 0–1.
    Total 0–11.
    """

    __tablename__ = "quality_report"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        ForeignKey("study.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default="1"
    )
    score_need_for_review: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0"
    )
    score_search_strategy: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0"
    )
    score_search_evaluation: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0"
    )
    score_extraction_classification: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0"
    )
    score_study_validity: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0"
    )
    total_score: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0"
    )
    rubric_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[list | None] = mapped_column(JSON, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
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
            f"<QualityReport id={self.id} study_id={self.study_id}"
            f" total_score={self.total_score} version={self.version}>"
        )
