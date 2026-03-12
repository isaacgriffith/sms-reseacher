"""Search string and iteration models."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class SearchString(Base):
    """A versioned Boolean search string for a study.

    Multiple versions may exist; only one is marked ``is_active`` at a time.
    """

    __tablename__ = "search_string"

    id: Mapped[int] = mapped_column(primary_key=True)
    study_id: Mapped[int] = mapped_column(ForeignKey("study.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    string_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    created_by_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)


class SearchStringIteration(Base):
    """One test-retest cycle for a search string.

    Records recall against the seed test set and human approval state.
    """

    __tablename__ = "search_string_iteration"

    id: Mapped[int] = mapped_column(primary_key=True)
    search_string_id: Mapped[int] = mapped_column(
        ForeignKey("search_string.id", ondelete="CASCADE"), nullable=False
    )
    iteration_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    result_set_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    test_set_recall: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ai_adequacy_judgment: Mapped[str | None] = mapped_column(Text, nullable=True)
    human_approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
