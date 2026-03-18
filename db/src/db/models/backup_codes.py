"""ORM model: BackupCode — single-use 2FA recovery codes."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class BackupCode(Base):
    """A single-use backup code for TOTP 2FA account recovery.

    Codes are generated in batches of 10 on 2FA activation or regeneration.
    Each code is stored as a bcrypt hash; the plaintext is shown to the user
    once and never stored.  When a code is redeemed, ``used_at`` is set and
    the code is permanently invalidated.

    All codes for a user are deleted when 2FA is disabled or regenerated.
    """

    __tablename__ = "backup_code"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hashed_code: Mapped[str] = mapped_column(String(255), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship("User", back_populates="backup_codes")  # type: ignore[name-defined]  # noqa: F821

    def __repr__(self) -> str:
        """Return a debug representation."""
        used = "used" if self.used_at else "unused"
        return f"<BackupCode id={self.id} user_id={self.user_id} {used}>"
