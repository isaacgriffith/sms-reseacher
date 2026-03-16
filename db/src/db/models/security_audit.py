"""ORM model: SecurityAuditEvent — immutable record of security-sensitive actions."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class SecurityEventType(str, enum.Enum):
    """Classifies account-level security events for the audit log."""

    PASSWORD_CHANGED = "password_changed"
    TOTP_ENABLED = "totp_enabled"
    TOTP_DISABLED = "totp_disabled"
    BACKUP_CODES_REGENERATED = "backup_codes_regenerated"
    TOTP_LOCKED = "totp_locked"


class SecurityAuditEvent(Base):
    """Immutable audit record for a security-sensitive account action.

    Records are inserted on password change, 2FA enable/disable, backup-code
    regeneration, and TOTP lockout.  They are never updated or deleted
    (except via CASCADE when the owning user is deleted).
    """

    __tablename__ = "security_audit_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[SecurityEventType] = mapped_column(
        Enum(SecurityEventType, name="security_event_type_enum"), nullable=False
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="security_audit_events")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f"<SecurityAuditEvent id={self.id} user_id={self.user_id}"
            f" type={self.event_type.value}>"
        )
