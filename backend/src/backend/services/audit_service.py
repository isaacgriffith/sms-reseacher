"""Security audit event service.

Provides a single entry point for writing immutable security audit records
(password changes, 2FA enable/disable, backup code regeneration) to the
database and structured log.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_logger
from db.models.security_audit import SecurityAuditEvent, SecurityEventType

logger = get_logger(__name__)


async def create_security_audit_event(
    db: AsyncSession,
    user_id: int,
    event_type: SecurityEventType,
    ip_address: str | None = None,
) -> SecurityAuditEvent:
    """Insert an immutable security audit record and emit a structured log line.

    Args:
        db: Active async database session.
        user_id: Primary key of the user whose account was affected.
        event_type: The :class:`SecurityEventType` classifying this event.
        ip_address: Optional IP address of the request originator (IPv4 or IPv6).

    Returns:
        The persisted :class:`SecurityAuditEvent` instance.
    """
    event = SecurityAuditEvent(
        user_id=user_id,
        event_type=event_type,
        ip_address=ip_address,
    )
    db.add(event)
    await db.flush()

    logger.info(
        "security_event",
        user_id=user_id,
        event_type=event_type.value,
        ip_address=ip_address,
    )
    return event
