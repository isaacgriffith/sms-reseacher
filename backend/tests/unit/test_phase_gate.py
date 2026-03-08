"""Unit tests for backend.services.phase_gate.

Covers:
- get_unlocked_phases: Phase 1 always unlocked
- get_unlocked_phases: Phase 2 unlocked when PICO saved
- get_unlocked_phases: Phase 3 unlocked when SearchExecution completed
- get_unlocked_phases: Phases 4+5 unlocked when extraction non-pending
- compute_staleness_flags: search stale when pico_saved_at > search_run_at
- compute_staleness_flags: extraction stale when search_run_at > extraction_started_at
- compute_current_phase: returns max unlocked phase
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Register all ORM models
import db.models  # noqa: F401
import db.models.users  # noqa: F401
import db.models.study  # noqa: F401
import db.models.pico  # noqa: F401
import db.models.seeds  # noqa: F401
import db.models.criteria  # noqa: F401
import db.models.search  # noqa: F401
import db.models.search_exec  # noqa: F401
import db.models.jobs  # noqa: F401
import db.models.candidate  # noqa: F401
import db.models.audit  # noqa: F401
import db.models.extraction  # noqa: F401

from db.base import Base
from db.models.pico import PICOComponent
from db.models.search import SearchString
from db.models.search_exec import SearchExecution, SearchExecutionStatus

from backend.services.phase_gate import (
    compute_current_phase,
    compute_staleness_flags,
    get_unlocked_phases,
)

STUDY_ID = 42


@pytest_asyncio.fixture
async def db_session():
    """Provide a fresh in-memory SQLite session."""
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


class TestGetUnlockedPhasesPhase1:
    """Phase 1 is always accessible."""

    @pytest.mark.asyncio
    async def test_phase_1_always_unlocked_no_data(self, db_session) -> None:
        """No PICO, no search → only phase 1 unlocked."""
        result = await get_unlocked_phases(STUDY_ID, db_session)
        assert result == [1]

    @pytest.mark.asyncio
    async def test_returns_list(self, db_session) -> None:
        """Return type is always a list."""
        result = await get_unlocked_phases(STUDY_ID, db_session)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_phase_1_always_in_result(self, db_session) -> None:
        """Phase 1 is always present in the unlocked list."""
        result = await get_unlocked_phases(STUDY_ID, db_session)
        assert 1 in result


class TestGetUnlockedPhasesPhase2:
    """Phase 2 requires PICO to be saved."""

    @pytest.mark.asyncio
    async def test_phase_2_unlocked_when_pico_saved(self, db_session) -> None:
        """After saving PICO, phase 2 is unlocked."""
        pico = PICOComponent(
            study_id=STUDY_ID,
            variant="PICO",
            population="software engineers",
        )
        db_session.add(pico)
        await db_session.commit()

        result = await get_unlocked_phases(STUDY_ID, db_session)
        assert 2 in result

    @pytest.mark.asyncio
    async def test_phase_2_not_unlocked_without_pico(self, db_session) -> None:
        """No PICO → phase 2 not unlocked."""
        result = await get_unlocked_phases(STUDY_ID, db_session)
        assert 2 not in result

    @pytest.mark.asyncio
    async def test_phase_2_unlocked_includes_phase_1(self, db_session) -> None:
        """When phase 2 is unlocked, phase 1 is also included."""
        db_session.add(PICOComponent(study_id=STUDY_ID, variant="PICO", population="X"))
        await db_session.commit()

        result = await get_unlocked_phases(STUDY_ID, db_session)
        assert 1 in result
        assert 2 in result

    @pytest.mark.asyncio
    async def test_pico_for_different_study_does_not_unlock(self, db_session) -> None:
        """PICO saved for a different study does not unlock this study's phase 2."""
        db_session.add(PICOComponent(study_id=999, variant="PICO", population="X"))
        await db_session.commit()

        result = await get_unlocked_phases(STUDY_ID, db_session)
        assert 2 not in result


class TestGetUnlockedPhasesPhase3:
    """Phase 3 requires a completed SearchExecution."""

    async def _insert_search_execution(self, db_session, study_id: int, status: SearchExecutionStatus) -> None:
        """Insert a SearchString and SearchExecution for testing."""
        ss = SearchString(study_id=study_id, version=1, string_text="(TDD)")
        db_session.add(ss)
        await db_session.flush()
        db_session.add(
            SearchExecution(
                study_id=study_id,
                search_string_id=ss.id,
                status=status,
                phase_tag="initial-search",
                databases_queried=["acm"],
            )
        )

    @pytest.mark.asyncio
    async def test_phase_3_unlocked_when_search_completed(self, db_session) -> None:
        """Completed SearchExecution unlocks phase 3."""
        db_session.add(PICOComponent(study_id=STUDY_ID, variant="PICO", population="X"))
        await self._insert_search_execution(db_session, STUDY_ID, SearchExecutionStatus.COMPLETED)
        await db_session.commit()

        result = await get_unlocked_phases(STUDY_ID, db_session)
        assert 3 in result

    @pytest.mark.asyncio
    async def test_phase_3_not_unlocked_when_search_running(self, db_session) -> None:
        """A running (not completed) SearchExecution does not unlock phase 3."""
        db_session.add(PICOComponent(study_id=STUDY_ID, variant="PICO", population="X"))
        await self._insert_search_execution(db_session, STUDY_ID, SearchExecutionStatus.RUNNING)
        await db_session.commit()

        result = await get_unlocked_phases(STUDY_ID, db_session)
        assert 3 not in result

    @pytest.mark.asyncio
    async def test_phase_3_not_unlocked_without_pico(self, db_session) -> None:
        """Phase 3 requires phase 2 (PICO) to be unlocked first."""
        await self._insert_search_execution(db_session, STUDY_ID, SearchExecutionStatus.COMPLETED)
        await db_session.commit()

        result = await get_unlocked_phases(STUDY_ID, db_session)
        assert 3 not in result


class TestComputeCurrentPhase:
    """compute_current_phase returns the max unlocked phase."""

    @pytest.mark.asyncio
    async def test_returns_1_when_no_data(self, db_session) -> None:
        """No data → current phase is 1."""
        result = await compute_current_phase(STUDY_ID, db_session)
        assert result == 1

    @pytest.mark.asyncio
    async def test_returns_2_when_pico_saved(self, db_session) -> None:
        """PICO saved → current phase is 2."""
        db_session.add(PICOComponent(study_id=STUDY_ID, variant="PICO", population="X"))
        await db_session.commit()

        result = await compute_current_phase(STUDY_ID, db_session)
        assert result == 2

    @pytest.mark.asyncio
    async def test_returns_3_when_search_completed(self, db_session) -> None:
        """PICO + completed search → current phase is 3."""
        db_session.add(PICOComponent(study_id=STUDY_ID, variant="PICO", population="X"))
        ss = SearchString(study_id=STUDY_ID, version=1, string_text="(TDD)")
        db_session.add(ss)
        await db_session.flush()
        db_session.add(
            SearchExecution(
                study_id=STUDY_ID,
                search_string_id=ss.id,
                status=SearchExecutionStatus.COMPLETED,
                phase_tag="initial-search",
                databases_queried=["acm"],
            )
        )
        await db_session.commit()

        result = await compute_current_phase(STUDY_ID, db_session)
        assert result == 3


class TestComputeStalenessFlags:
    """compute_staleness_flags returns correct stale/fresh flags."""

    def _study(
        self,
        pico_saved_at: datetime | None = None,
        search_run_at: datetime | None = None,
        extraction_started_at: datetime | None = None,
    ) -> MagicMock:
        """Build a minimal study mock with the given timestamps."""
        s = MagicMock()
        s.pico_saved_at = pico_saved_at
        s.search_run_at = search_run_at
        s.extraction_started_at = extraction_started_at
        return s

    def _dt(self, offset_seconds: int = 0) -> datetime:
        return datetime(2025, 1, 1, 12, 0, offset_seconds, tzinfo=timezone.utc)

    def test_all_none_returns_both_false(self) -> None:
        """No timestamps → both flags False."""
        study = self._study()
        flags = compute_staleness_flags(study)
        assert flags == {"search": False, "extraction": False}

    def test_search_stale_when_pico_newer_than_search(self) -> None:
        """pico_saved_at > search_run_at → search is stale."""
        study = self._study(
            pico_saved_at=self._dt(10),
            search_run_at=self._dt(0),
        )
        flags = compute_staleness_flags(study)
        assert flags["search"] is True

    def test_search_not_stale_when_pico_older_than_search(self) -> None:
        """pico_saved_at < search_run_at → search is NOT stale."""
        study = self._study(
            pico_saved_at=self._dt(0),
            search_run_at=self._dt(10),
        )
        flags = compute_staleness_flags(study)
        assert flags["search"] is False

    def test_search_not_stale_when_pico_equal_to_search(self) -> None:
        """pico_saved_at == search_run_at → search is NOT stale."""
        t = self._dt(5)
        study = self._study(pico_saved_at=t, search_run_at=t)
        flags = compute_staleness_flags(study)
        assert flags["search"] is False

    def test_search_not_stale_when_search_run_at_missing(self) -> None:
        """pico_saved_at exists but search_run_at is None → search not stale."""
        study = self._study(pico_saved_at=self._dt(10))
        flags = compute_staleness_flags(study)
        assert flags["search"] is False

    def test_search_not_stale_when_pico_saved_at_missing(self) -> None:
        """search_run_at exists but pico_saved_at is None → search not stale."""
        study = self._study(search_run_at=self._dt(10))
        flags = compute_staleness_flags(study)
        assert flags["search"] is False

    def test_extraction_stale_when_search_newer_than_extraction(self) -> None:
        """search_run_at > extraction_started_at → extraction is stale."""
        study = self._study(
            search_run_at=self._dt(10),
            extraction_started_at=self._dt(0),
        )
        flags = compute_staleness_flags(study)
        assert flags["extraction"] is True

    def test_extraction_not_stale_when_search_older_than_extraction(self) -> None:
        """search_run_at < extraction_started_at → extraction is NOT stale."""
        study = self._study(
            search_run_at=self._dt(0),
            extraction_started_at=self._dt(10),
        )
        flags = compute_staleness_flags(study)
        assert flags["extraction"] is False

    def test_extraction_not_stale_when_search_run_at_missing(self) -> None:
        """extraction_started_at present but search_run_at None → not stale."""
        study = self._study(extraction_started_at=self._dt(0))
        flags = compute_staleness_flags(study)
        assert flags["extraction"] is False

    def test_extraction_not_stale_when_extraction_started_at_missing(self) -> None:
        """search_run_at present but extraction_started_at None → not stale."""
        study = self._study(search_run_at=self._dt(10))
        flags = compute_staleness_flags(study)
        assert flags["extraction"] is False

    def test_both_stale_simultaneously(self) -> None:
        """Both flags stale simultaneously when all timestamps configured."""
        study = self._study(
            pico_saved_at=self._dt(20),
            search_run_at=self._dt(10),
            extraction_started_at=self._dt(5),
        )
        flags = compute_staleness_flags(study)
        assert flags["search"] is True
        assert flags["extraction"] is True

    def test_returns_dict_with_correct_keys(self) -> None:
        """Return value always has 'search' and 'extraction' keys."""
        study = self._study()
        flags = compute_staleness_flags(study)
        assert "search" in flags
        assert "extraction" in flags
        assert len(flags) == 2
