"""ORM models: StudyMember, Reviewer — extensions to the Study table."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from db.base import Base


class StudyMemberRole(str, enum.Enum):
    """Role of a user within a study team."""

    LEAD = "lead"
    MEMBER = "member"


class ReviewerType(str, enum.Enum):
    """Whether a reviewer is a human or an AI agent."""

    HUMAN = "human"
    AI_AGENT = "ai_agent"


class StudyMember(Base):
    """Many-to-many join between Study and User with a team role."""

    __tablename__ = "study_member"
    __table_args__ = (UniqueConstraint("study_id", "user_id", name="uq_study_member"),)

    study_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("study.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[StudyMemberRole] = mapped_column(
        Enum(StudyMemberRole, name="study_member_role_enum"),
        nullable=False,
        default=StudyMemberRole.MEMBER,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<StudyMember study={self.study_id} user={self.user_id} role={self.role}>"


class Reviewer(Base):
    """A reviewer slot for a study — either a human user or a named AI agent."""

    __tablename__ = "reviewer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("study.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reviewer_type: Mapped[ReviewerType] = mapped_column(
        Enum(ReviewerType, name="reviewer_type_enum"), nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    agent_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    agent_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Feature 005: reference to the new Agent abstraction.
    # Nullable during the transition period while agent_name is still populated.
    # Will be made non-nullable (for ai_agent rows) once all rows are migrated.
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<Reviewer id={self.id} study={self.study_id}"
            f" type={self.reviewer_type} user={self.user_id} agent={self.agent_name!r}>"
        )
