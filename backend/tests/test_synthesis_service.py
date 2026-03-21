"""Unit tests for backend.services.synthesis_service (feature 007, T069).

Tests cover:
- start_synthesis creates a PENDING SynthesisResult record.
- list_results returns records for a study.
- get_result returns None for a missing ID.
- ARQ enqueue is called with correct arguments.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from db.base import Base
import db.models  # noqa: F401
import db.models.users  # noqa: F401
import db.models.study  # noqa: F401
import db.models.slr  # noqa: F401
import db.models.candidate  # noqa: F401
import db.models.search  # noqa: F401
import db.models.search_exec  # noqa: F401
import db.models.pico  # noqa: F401
import db.models.seeds  # noqa: F401
import db.models.criteria  # noqa: F401


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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_study_counter = 0


async def _insert_study(db: AsyncSession) -> int:
    """Insert a minimal Study and ResearchGroup, returning the study id."""
    global _study_counter
    _study_counter += 1

    from db.models.users import ResearchGroup
    from db.models import Study, StudyType, StudyStatus

    group = ResearchGroup(name=f"Synthesis Test Group {_study_counter}")
    db.add(group)
    await db.flush()

    study = Study(
        name=f"Synthesis Test SLR {_study_counter}",
        research_group_id=group.id,
        study_type=StudyType.SLR,
        status=StudyStatus.ACTIVE,
    )
    db.add(study)
    await db.commit()
    await db.refresh(study)
    return study.id


def _make_arq_pool() -> AsyncMock:
    """Return a minimal mock ARQ pool."""
    pool = AsyncMock()
    pool.enqueue_job = AsyncMock()
    return pool


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestStartSynthesis:
    """start_synthesis creates a PENDING record and enqueues the job."""

    @pytest.mark.asyncio
    async def test_creates_pending_record(self, db_session) -> None:
        """start_synthesis returns a SynthesisResult with status=PENDING."""
        from backend.services.synthesis_service import start_synthesis
        from db.models.slr import SynthesisStatus

        study_id = await _insert_study(db_session)
        pool = _make_arq_pool()

        record = await start_synthesis(
            study_id=study_id,
            approach="meta_analysis",
            parameters={"papers": [], "model_type": "fixed"},
            db=db_session,
            arq_pool=pool,
        )

        assert record.id is not None
        assert record.study_id == study_id
        assert record.status == SynthesisStatus.PENDING
        assert record.approach.value == "meta_analysis"

    @pytest.mark.asyncio
    async def test_enqueues_arq_job(self, db_session) -> None:
        """start_synthesis calls arq_pool.enqueue_job with correct synthesis_id."""
        from backend.services.synthesis_service import start_synthesis

        study_id = await _insert_study(db_session)
        pool = _make_arq_pool()

        record = await start_synthesis(
            study_id=study_id,
            approach="descriptive",
            parameters={"papers": []},
            db=db_session,
            arq_pool=pool,
        )

        pool.enqueue_job.assert_called_once_with("run_synthesis", synthesis_id=record.id)

    @pytest.mark.asyncio
    async def test_model_type_extracted_from_parameters(self, db_session) -> None:
        """model_type field is set from parameters when present."""
        from backend.services.synthesis_service import start_synthesis

        study_id = await _insert_study(db_session)
        pool = _make_arq_pool()

        record = await start_synthesis(
            study_id=study_id,
            approach="meta_analysis",
            parameters={"model_type": "random", "papers": []},
            db=db_session,
            arq_pool=pool,
        )

        assert record.model_type == "random"


class TestListResults:
    """list_results returns records for a study."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_initially(self, db_session) -> None:
        """list_results returns [] when no records exist."""
        from backend.services.synthesis_service import list_results

        study_id = await _insert_study(db_session)
        records = await list_results(study_id, db_session)
        assert records == []

    @pytest.mark.asyncio
    async def test_returns_records_for_study(self, db_session) -> None:
        """list_results returns all records for the given study."""
        from backend.services.synthesis_service import list_results, start_synthesis

        study_id = await _insert_study(db_session)
        pool = _make_arq_pool()

        await start_synthesis(
            study_id=study_id,
            approach="qualitative",
            parameters={"themes": []},
            db=db_session,
            arq_pool=pool,
        )

        records = await list_results(study_id, db_session)
        assert len(records) == 1
        assert records[0].study_id == study_id

    @pytest.mark.asyncio
    async def test_does_not_return_records_for_other_study(self, db_session) -> None:
        """list_results does not return records from a different study."""
        from backend.services.synthesis_service import list_results, start_synthesis

        study_id = await _insert_study(db_session)
        other_study_id = await _insert_study(db_session)
        pool = _make_arq_pool()

        await start_synthesis(
            study_id=other_study_id,
            approach="qualitative",
            parameters={},
            db=db_session,
            arq_pool=pool,
        )

        records = await list_results(study_id, db_session)
        assert records == []


class TestGetResult:
    """get_result retrieves a single record by primary key."""

    @pytest.mark.asyncio
    async def test_returns_none_for_missing_id(self, db_session) -> None:
        """get_result returns None when no record with that id exists."""
        from backend.services.synthesis_service import get_result

        result = await get_result(99999, db_session)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_record_by_id(self, db_session) -> None:
        """get_result returns the correct record when it exists."""
        from backend.services.synthesis_service import get_result, start_synthesis

        study_id = await _insert_study(db_session)
        pool = _make_arq_pool()
        created = await start_synthesis(
            study_id=study_id,
            approach="qualitative",
            parameters={},
            db=db_session,
            arq_pool=pool,
        )

        found = await get_result(created.id, db_session)
        assert found is not None
        assert found.id == created.id
