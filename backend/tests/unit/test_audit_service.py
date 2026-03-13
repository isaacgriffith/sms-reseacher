"""Unit tests for backend.services.audit.

Covers:
- AuditRecord row is created and flushed to the session
- ValueError raised when both actor_user_id and actor_agent are None
- structlog emits an audit_record_written event
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, call


# ---------------------------------------------------------------------------
# ValueError when both actor fields are None
# ---------------------------------------------------------------------------


def test_record_raises_when_both_actors_none():
    """record() raises ValueError if actor_user_id and actor_agent are both None."""
    from db.models.audit import AuditAction

    async def _run():
        session = AsyncMock()
        from backend.services.audit import record

        try:
            await record(
                session,
                study_id=1,
                actor_user_id=None,
                actor_agent=None,
                entity_type="Study",
                entity_id=1,
                action=AuditAction.UPDATE,
            )
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "actor" in str(exc).lower()

    asyncio.run(_run())


def test_record_raises_with_descriptive_message():
    """record() ValueError message mentions actor_user_id and actor_agent."""
    from db.models.audit import AuditAction

    async def _run():
        session = AsyncMock()
        from backend.services.audit import record

        try:
            await record(
                session,
                study_id=99,
                actor_user_id=None,
                actor_agent=None,
                entity_type="PICOComponent",
                entity_id=5,
                action=AuditAction.CREATE,
            )
        except ValueError as exc:
            assert "actor_user_id" in str(exc) or "actor_agent" in str(exc)
        else:
            assert False, "ValueError not raised"

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# AuditRecord row is added to session and flushed
# ---------------------------------------------------------------------------


def test_record_adds_row_to_session():
    """record() calls session.add() with an AuditRecord and then flush()."""
    from db.models.audit import AuditAction, AuditRecord

    async def _run():
        session = AsyncMock()
        from backend.services.audit import record

        result = await record(
            session,
            study_id=1,
            actor_user_id=42,
            actor_agent=None,
            entity_type="SearchString",
            entity_id=7,
            action=AuditAction.CREATE,
            after_value={"text": "TDD AND testing"},
        )
        session.add.assert_called_once()
        session.flush.assert_awaited_once()
        assert isinstance(result, AuditRecord)

    asyncio.run(_run())


def test_record_with_agent_actor():
    """record() accepts actor_agent instead of actor_user_id."""
    from db.models.audit import AuditAction, AuditRecord

    async def _run():
        session = AsyncMock()
        from backend.services.audit import record

        result = await record(
            session,
            study_id=3,
            actor_user_id=None,
            actor_agent="SearchStringBuilderAgent",
            entity_type="SearchString",
            entity_id=2,
            action=AuditAction.CREATE,
        )
        session.add.assert_called_once()
        assert isinstance(result, AuditRecord)
        assert result.actor_agent == "SearchStringBuilderAgent"
        assert result.actor_user_id is None

    asyncio.run(_run())


def test_record_sets_correct_fields():
    """record() populates all AuditRecord fields correctly."""
    from db.models.audit import AuditAction, AuditRecord

    async def _run():
        session = AsyncMock()
        from backend.services.audit import record

        result = await record(
            session,
            study_id=5,
            actor_user_id=10,
            actor_agent=None,
            entity_type="InclusionCriterion",
            entity_id=3,
            action=AuditAction.DELETE,
            field_name="description",
            before_value={"description": "old"},
            after_value=None,
        )
        assert result.study_id == 5
        assert result.actor_user_id == 10
        assert result.entity_type == "InclusionCriterion"
        assert result.entity_id == 3
        assert result.action == AuditAction.DELETE
        assert result.field_name == "description"
        assert result.before_value == {"description": "old"}
        assert result.after_value is None

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# structlog warning emitted
# ---------------------------------------------------------------------------


def test_record_emits_structlog_info():
    """record() emits a structured log event via structlog."""
    from db.models.audit import AuditAction

    async def _run():
        session = AsyncMock()
        mock_logger = MagicMock()

        with patch("backend.services.audit.logger", mock_logger):
            from backend.services.audit import record

            await record(
                session,
                study_id=2,
                actor_user_id=1,
                actor_agent=None,
                entity_type="Study",
                entity_id=2,
                action=AuditAction.UPDATE,
            )
            mock_logger.info.assert_called_once()
            call_kwargs = mock_logger.info.call_args
            assert "audit_record_written" in call_kwargs[0]

    asyncio.run(_run())
