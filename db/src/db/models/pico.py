"""ORM model: PICOComponent."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from db.base import Base


class PICOVariant(str, enum.Enum):
    """Supported PICO framework variants."""

    PICO = "PICO"
    PICOS = "PICOS"
    PICOT = "PICOT"
    SPIDER = "SPIDER"
    PCC = "PCC"


class PICOComponent(Base):
    """Stores the PICO/C components for a study (one row per study, upsert semantics)."""

    __tablename__ = "pico_component"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("study.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    variant: Mapped[PICOVariant] = mapped_column(
        Enum(PICOVariant, name="pico_variant_enum"), nullable=False
    )
    population: Mapped[str | None] = mapped_column(Text, nullable=True)
    intervention: Mapped[str | None] = mapped_column(Text, nullable=True)
    comparison: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_fields: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Variant-specific fields (S, T, Spider components)"
    )
    ai_suggestions: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="Last AI refinement suggestions per component"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<PICOComponent id={self.id} study={self.study_id} variant={self.variant}>"
