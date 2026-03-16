"""ORM models: User, ResearchGroup, GroupMembership."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class GroupRole(str, enum.Enum):
    """Membership role within a research group."""

    ADMIN = "admin"
    MEMBER = "member"


class ThemePreference(str, enum.Enum):
    """User's preferred colour scheme for the application UI."""

    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


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
        """Return a debug representation."""
        return f"<ResearchGroup id={self.id} name={self.name!r}>"


class User(Base):
    """An authenticated system user.

    Security fields added in feature 004-frontend-improvements:
    - ``theme_preference``: persisted display mode preference.
    - ``token_version``: incremented on password change to invalidate prior JWTs.
    - ``totp_*``: TOTP two-factor authentication state.
    - ``password_changed_at`` / ``updated_at``: audit timestamps.
    """

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # --- Display preference ---
    theme_preference: Mapped[ThemePreference] = mapped_column(
        Enum(ThemePreference, name="theme_preference_enum"),
        nullable=False,
        default=ThemePreference.SYSTEM,
        server_default=ThemePreference.SYSTEM.value,
    )

    # --- Session / JWT invalidation ---
    token_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    # --- TOTP two-factor authentication ---
    totp_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    totp_secret_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    totp_failed_attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    totp_locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # --- Audit timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    password_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # --- Relationships ---
    memberships: Mapped[list["GroupMembership"]] = relationship(
        "GroupMembership", back_populates="user", cascade="all, delete-orphan"
    )
    backup_codes: Mapped[list["BackupCode"]] = relationship(  # type: ignore[name-defined]
        "BackupCode", back_populates="user", cascade="all, delete-orphan"
    )
    security_audit_events: Mapped[list["SecurityAuditEvent"]] = relationship(  # type: ignore[name-defined]
        "SecurityAuditEvent", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return a debug representation."""
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
        """Return a debug representation."""
        return f"<GroupMembership group={self.group_id} user={self.user_id} role={self.role}>"
