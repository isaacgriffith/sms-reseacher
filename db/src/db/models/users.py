"""ORM models: User, ResearchGroup, GroupMembership."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class GroupRole(str, enum.Enum):
    """Membership role within a research group."""

    ADMIN = "admin"
    MEMBER = "member"


class ResearchGroup(Base):
    """A named research group that owns studies."""

    __tablename__ = "research_group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    memberships: Mapped[list["GroupMembership"]] = relationship(
        "GroupMembership", back_populates="group", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ResearchGroup id={self.id} name={self.name!r}>"


class User(Base):
    """An authenticated system user."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    memberships: Mapped[list["GroupMembership"]] = relationship(
        "GroupMembership", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class GroupMembership(Base):
    """Many-to-many join between User and ResearchGroup with a role."""

    __tablename__ = "group_membership"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_membership"),)

    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("research_group.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[GroupRole] = mapped_column(
        Enum(GroupRole, name="group_role_enum"), nullable=False, default=GroupRole.MEMBER
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    group: Mapped["ResearchGroup"] = relationship("ResearchGroup", back_populates="memberships")
    user: Mapped["User"] = relationship("User", back_populates="memberships")

    def __repr__(self) -> str:
        return f"<GroupMembership group={self.group_id} user={self.user_id} role={self.role}>"
