"""Audit trail write service for study-level mutation logging (FR-044, NFR-002).

Provides a single ``record`` coroutine that appends an immutable ``AuditRecord``
row to the database and emits a structured log line via structlog.
"""

from db.models.audit import AuditAction, AuditRecord
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_logger

logger = get_logger(__name__)


async def record(
    session: AsyncSession,
    /,
    study_id: int,
    actor_user_id: int | None,
    actor_agent: str | None,
    entity_type: str,
    entity_id: int,
    action: AuditAction,
    field_name: str | None = None,
    before_value: dict | None = None,
    after_value: dict | None = None,
) -> AuditRecord:
    """Append an immutable audit record for a study-level data mutation.

    Exactly one of *actor_user_id* or *actor_agent* must be non-``None``; if
    both are ``None`` a ``ValueError`` is raised (NFR-002: every audit record
    must be attributable to a human or an AI agent).

    The record is flushed to the session but the transaction is **not**
    committed here — callers are responsible for committing.

    Args:
        session: Active async database session (not committed by this function).
        study_id: Primary key of the study being mutated.
        actor_user_id: User PK if the mutation was made by a human; ``None`` for
            agent-initiated mutations.
        actor_agent: Agent identifier string (e.g. ``"SearchStringBuilderAgent"``)
            if the mutation was made by an AI agent; ``None`` for human actors.
        entity_type: Short class name of the mutated entity (e.g.
            ``"PICOComponent"``, ``"SearchString"``).
        entity_id: Primary key of the mutated entity row.
        action: :class:`~db.models.audit.AuditAction` variant — CREATE, UPDATE,
            or DELETE.
        field_name: The specific column/field that changed (optional; omit for
            whole-entity CREATE or DELETE events).
        before_value: JSON-serialisable snapshot of the field value *before* the
            mutation (``None`` for CREATE events).
        after_value: JSON-serialisable snapshot of the field value *after* the
            mutation (``None`` for DELETE events).

    Returns:
        The newly created :class:`~db.models.audit.AuditRecord` instance (flushed
        to the session, primary key assigned).

    Raises:
        ValueError: If both *actor_user_id* and *actor_agent* are ``None``.

    """
    if actor_user_id is None and actor_agent is None:
        raise ValueError("audit.record: at least one of actor_user_id or actor_agent must be set")

    audit_row = AuditRecord(
        study_id=study_id,
        actor_user_id=actor_user_id,
        actor_agent=actor_agent,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        field_name=field_name,
        before_value=before_value,
        after_value=after_value,
    )
    session.add(audit_row)
    await session.flush()

    logger.info(
        "audit_record_written",
        study_id=study_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action.value,
        actor_user_id=actor_user_id,
        actor_agent=actor_agent,
    )
    return audit_row
