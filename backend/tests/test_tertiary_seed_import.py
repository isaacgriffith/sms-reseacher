"""Unit tests for TertiaryExtractionService.import_seed_study (feature 009, T042).

Tests cover:
- Happy path: N included papers from source study are imported into target.
- Deduplication: re-importing the same source skips all previously imported papers.
- Edge case: source study with zero included papers raises ValueError.
- ensure_extraction_records: creates stubs for accepted papers without records.
- ensure_extraction_records: idempotent when called twice.
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
import db.models.candidate  # noqa: F401
import db.models.search  # noqa: F401
import db.models.search_exec  # noqa: F401
import db.models.tertiary  # noqa: F401


@pytest_asyncio.fixture
async def db_session():
    """Per-test in-memory SQLite session with all tables.

    Yields:
        An :class:`~sqlalchemy.ext.asyncio.AsyncSession` backed by SQLite
        in-memory storage.
    """
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


async def _insert_study(db: AsyncSession, name: str = "Test Study") -> int:
    """Insert a ResearchGroup and Study, return study id.

    Args:
        db: Active async database session.
        name: Study name.

    Returns:
        Integer study id.
    """
    from db.models.users import ResearchGroup
    from db.models import Study, StudyType, StudyStatus

    group = ResearchGroup(name=f"Group for {name}")
    db.add(group)
    await db.flush()

    study = Study(
        name=name,
        research_group_id=group.id,
        study_type=StudyType.SMS,
        status=StudyStatus.ACTIVE,
    )
    db.add(study)
    await db.commit()
    await db.refresh(study)
    return study.id


async def _insert_paper(db: AsyncSession, doi: str = "10.0000/paper.1") -> int:
    """Insert a Paper row and return its id.

    Args:
        db: Active async database session.
        doi: DOI for the paper.

    Returns:
        Integer paper id.
    """
    from db.models import Paper

    paper = Paper(title=f"Paper {doi}", doi=doi)
    db.add(paper)
    await db.flush()
    return paper.id


async def _insert_search_execution(db: AsyncSession, study_id: int) -> int:
    """Insert a minimal SearchString + SearchExecution, return execution id.

    Args:
        db: Active async database session.
        study_id: Study owning the search.

    Returns:
        Integer search execution id.
    """
    from db.models.search import SearchString
    from db.models.search_exec import SearchExecution, SearchExecutionStatus

    ss = SearchString(study_id=study_id, version=1, string_text="test query", is_active=True)
    db.add(ss)
    await db.flush()

    se = SearchExecution(
        study_id=study_id,
        search_string_id=ss.id,
        status=SearchExecutionStatus.COMPLETED,
    )
    db.add(se)
    await db.flush()
    return se.id


async def _add_accepted_papers(
    db: AsyncSession,
    study_id: int,
    n: int = 2,
) -> list[int]:
    """Add *n* accepted CandidatePaper rows to *study_id*, return paper ids.

    Args:
        db: Active async database session.
        study_id: Study to attach papers to.
        n: Number of papers to create.

    Returns:
        List of created CandidatePaper ids.
    """
    from db.models.candidate import CandidatePaper, CandidatePaperStatus

    se_id = await _insert_search_execution(db, study_id)
    cp_ids = []
    for i in range(n):
        paper_id = await _insert_paper(db, doi=f"10.0000/seed.{study_id}.{i}")
        cp = CandidatePaper(
            study_id=study_id,
            paper_id=paper_id,
            search_execution_id=se_id,
            phase_tag="phase2",
            current_status=CandidatePaperStatus.ACCEPTED,
        )
        db.add(cp)
        await db.flush()
        cp_ids.append(cp.id)

    await db.commit()
    return cp_ids


# ---------------------------------------------------------------------------
# Tests: import_seed_study
# ---------------------------------------------------------------------------


class TestImportSeedStudy:
    """TertiaryExtractionService.import_seed_study behaviour."""

    @pytest.mark.asyncio
    async def test_happy_path_imports_all_included_papers(self, db_session) -> None:
        """Records_added equals the number of accepted papers in the source study."""
        from backend.services.tertiary_extraction_service import TertiaryExtractionService

        source_id = await _insert_study(db_session, name="Source SLR")
        target_id = await _insert_study(db_session, name="Target Tertiary")
        await _add_accepted_papers(db_session, source_id, n=3)

        svc = TertiaryExtractionService()
        result = await svc.import_seed_study(
            target_study_id=target_id,
            source_study_id=source_id,
            user_id=None,
            db=db_session,
        )
        await db_session.commit()

        assert result.records_added == 3
        assert result.records_skipped == 0
        assert result.target_study_id == target_id
        assert result.source_study_id == source_id

    @pytest.mark.asyncio
    async def test_deduplication_skips_already_imported_papers(self, db_session) -> None:
        """Re-importing the same source skips all previously imported papers."""
        from backend.services.tertiary_extraction_service import TertiaryExtractionService

        source_id = await _insert_study(db_session, name="Source SLR Dup")
        target_id = await _insert_study(db_session, name="Target Tertiary Dup")
        await _add_accepted_papers(db_session, source_id, n=2)

        svc = TertiaryExtractionService()

        # First import — all papers added.
        first = await svc.import_seed_study(
            target_study_id=target_id,
            source_study_id=source_id,
            user_id=None,
            db=db_session,
        )
        await db_session.commit()
        assert first.records_added == 2

        # Second import — all papers skipped.
        second = await svc.import_seed_study(
            target_study_id=target_id,
            source_study_id=source_id,
            user_id=None,
            db=db_session,
        )
        await db_session.commit()

        assert second.records_added == 0
        assert second.records_skipped == 2

    @pytest.mark.asyncio
    async def test_raises_value_error_when_no_included_papers(self, db_session) -> None:
        """import_seed_study raises ValueError when source has zero included papers."""
        from backend.services.tertiary_extraction_service import TertiaryExtractionService

        source_id = await _insert_study(db_session, name="Empty Source")
        target_id = await _insert_study(db_session, name="Target Tertiary Empty")

        svc = TertiaryExtractionService()
        with pytest.raises(ValueError, match="no included"):
            await svc.import_seed_study(
                target_study_id=target_id,
                source_study_id=source_id,
                user_id=None,
                db=db_session,
            )


# ---------------------------------------------------------------------------
# Tests: ensure_extraction_records
# ---------------------------------------------------------------------------


class TestEnsureExtractionRecords:
    """TertiaryExtractionService.ensure_extraction_records behaviour."""

    @pytest.mark.asyncio
    async def test_creates_stubs_for_accepted_papers(self, db_session) -> None:
        """Creates TertiaryDataExtraction stubs for each accepted CandidatePaper."""
        from backend.services.tertiary_extraction_service import TertiaryExtractionService
        from db.models.tertiary import TertiaryDataExtraction
        from sqlalchemy import select

        study_id = await _insert_study(db_session, name="Extraction Stub Study")
        cp_ids = await _add_accepted_papers(db_session, study_id, n=2)

        svc = TertiaryExtractionService()
        created = await svc.ensure_extraction_records(study_id, db_session)
        await db_session.commit()

        assert created == 2

        result = await db_session.execute(
            select(TertiaryDataExtraction).where(
                TertiaryDataExtraction.candidate_paper_id.in_(cp_ids)
            )
        )
        records = list(result.scalars().all())
        assert len(records) == 2
        for r in records:
            assert r.extraction_status == "pending"

    @pytest.mark.asyncio
    async def test_idempotent_when_called_twice(self, db_session) -> None:
        """ensure_extraction_records returns 0 on second call (stubs already exist)."""
        from backend.services.tertiary_extraction_service import TertiaryExtractionService

        study_id = await _insert_study(db_session, name="Idempotent Study")
        await _add_accepted_papers(db_session, study_id, n=1)

        svc = TertiaryExtractionService()
        first = await svc.ensure_extraction_records(study_id, db_session)
        await db_session.commit()
        assert first == 1

        second = await svc.ensure_extraction_records(study_id, db_session)
        await db_session.commit()
        assert second == 0

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_accepted_papers(self, db_session) -> None:
        """ensure_extraction_records returns 0 when the study has no accepted papers."""
        from backend.services.tertiary_extraction_service import TertiaryExtractionService

        study_id = await _insert_study(db_session, name="Empty Extraction Study")
        svc = TertiaryExtractionService()
        created = await svc.ensure_extraction_records(study_id, db_session)
        assert created == 0
