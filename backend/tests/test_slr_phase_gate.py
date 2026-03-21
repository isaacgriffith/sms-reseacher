"""Unit tests for backend.services.slr_phase_gate (feature 007).

Tests cover:
- Phase 1 always unlocked.
- Phase 2 locked until ReviewProtocol is validated.
- Phase 3 locked until a completed SearchExecution exists.
- Phases 4 and 5 locked when quality/synthesis are incomplete.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db.base import Base
import db.models  # noqa: F401
import db.models.users  # noqa: F401
import db.models.study  # noqa: F401
import db.models.slr  # noqa: F401


@pytest_asyncio.fixture
async def db_session():
    """Provide a per-test in-memory SQLite session with all tables."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        yield session

    await engine.dispose()


async def _insert_study(db: AsyncSession) -> int:
    """Insert a minimal Study and ResearchGroup, returning the study id."""
    from db.models.users import ResearchGroup
    from db.models import Study, StudyType, StudyStatus

    group = ResearchGroup(name="Phase Gate Group")
    db.add(group)
    await db.flush()

    study = Study(
        name="SLR Phase Gate Test",
        research_group_id=group.id,
        study_type=StudyType.SLR,
        status=StudyStatus.ACTIVE,
    )
    db.add(study)
    await db.commit()
    await db.refresh(study)
    return study.id


class TestPhase1AlwaysUnlocked:
    """Phase 1 is always accessible regardless of study state."""

    @pytest.mark.asyncio
    async def test_phase_1_unlocked_with_no_protocol(self, db_session) -> None:
        """Phase 1 is unlocked even when no protocol exists."""
        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 1 in unlocked


class TestPhase2ProtocolValidation:
    """Phase 2 requires a validated ReviewProtocol."""

    @pytest.mark.asyncio
    async def test_phase_2_locked_without_protocol(self, db_session) -> None:
        """Phase 2 is not in unlocked list when no protocol exists."""
        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 2 not in unlocked

    @pytest.mark.asyncio
    async def test_phase_2_locked_when_protocol_is_draft(self, db_session) -> None:
        """Phase 2 is locked when protocol exists but is still in draft."""
        from db.models.slr import ReviewProtocol, ReviewProtocolStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = ReviewProtocol(
            study_id=study_id, status=ReviewProtocolStatus.DRAFT
        )
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 2 not in unlocked

    @pytest.mark.asyncio
    async def test_phase_2_locked_when_protocol_under_review(self, db_session) -> None:
        """Phase 2 is locked when protocol is under_review."""
        from db.models.slr import ReviewProtocol, ReviewProtocolStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = ReviewProtocol(
            study_id=study_id, status=ReviewProtocolStatus.UNDER_REVIEW
        )
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 2 not in unlocked

    @pytest.mark.asyncio
    async def test_phase_2_unlocked_when_protocol_validated(self, db_session) -> None:
        """Phase 2 is unlocked when ReviewProtocol.status == validated."""
        from db.models.slr import ReviewProtocol, ReviewProtocolStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = ReviewProtocol(
            study_id=study_id,
            status=ReviewProtocolStatus.VALIDATED,
            review_report={"issues": [], "overall_assessment": "OK"},
        )
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 2 in unlocked

    @pytest.mark.asyncio
    async def test_phase_1_always_included(self, db_session) -> None:
        """Phase 1 is always in the result even when phase 2 unlocks."""
        from db.models.slr import ReviewProtocol, ReviewProtocolStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = ReviewProtocol(
            study_id=study_id,
            status=ReviewProtocolStatus.VALIDATED,
        )
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 1 in unlocked
        assert 2 in unlocked

    @pytest.mark.asyncio
    async def test_phase_3_not_included_without_search(self, db_session) -> None:
        """Phase 3 is not unlocked when no completed search execution exists."""
        from db.models.slr import ReviewProtocol, ReviewProtocolStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = ReviewProtocol(
            study_id=study_id,
            status=ReviewProtocolStatus.VALIDATED,
        )
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert 3 not in unlocked

    @pytest.mark.asyncio
    async def test_unlocked_phases_ordered(self, db_session) -> None:
        """Unlocked phases list is in ascending order."""
        from db.models.slr import ReviewProtocol, ReviewProtocolStatus

        from backend.services.slr_phase_gate import get_slr_unlocked_phases

        study_id = await _insert_study(db_session)
        protocol = ReviewProtocol(
            study_id=study_id,
            status=ReviewProtocolStatus.VALIDATED,
        )
        db_session.add(protocol)
        await db_session.commit()

        unlocked = await get_slr_unlocked_phases(study_id, db_session)
        assert unlocked == sorted(unlocked)
