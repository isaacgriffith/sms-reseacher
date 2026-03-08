"""Unit tests for backend.services.dedup — two-stage deduplication logic.

Covers:
- DOI exact match → DedupResult(is_duplicate=True, is_definite=True)
- Fuzzy title similarity ≥ 0.90 + author overlap → probable duplicate
- Below-threshold title similarity → not a duplicate
- No DOI falls through to fuzzy stage only
- Author mismatch vetoes high-title-similarity
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Register all ORM table definitions
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

from db.base import Base
from db.models import Paper
from db.models.candidate import CandidatePaper, CandidatePaperStatus

from backend.services.dedup import DedupResult, check_duplicate

STUDY_ID = 1
FAKE_EXEC_ID = 999  # SQLite won't enforce FK by default


@pytest_asyncio.fixture
async def db_session():
    """Provide a fresh in-memory SQLite session for each test."""
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


async def _insert_candidate(
    session: AsyncSession,
    *,
    title: str,
    doi: str | None = None,
    authors: list | None = None,
) -> CandidatePaper:
    """Insert a Paper and CandidatePaper and return the CandidatePaper."""
    paper = Paper(title=title, doi=doi, authors=authors)
    session.add(paper)
    await session.flush()
    cp = CandidatePaper(
        study_id=STUDY_ID,
        paper_id=paper.id,
        search_execution_id=FAKE_EXEC_ID,
        phase_tag="initial-search",
        current_status=CandidatePaperStatus.PENDING,
    )
    session.add(cp)
    await session.flush()
    return cp


class TestDedupResultShape:
    """DedupResult exposes expected fields."""

    @pytest.mark.asyncio
    async def test_not_a_duplicate_when_no_candidates(self, db_session: AsyncSession) -> None:
        """No existing candidates → is_duplicate=False."""
        result = await check_duplicate(
            study_id=STUDY_ID,
            doi="10.1/test",
            title="Any Title",
            db=db_session,
        )
        assert isinstance(result, DedupResult)
        assert result.is_duplicate is False
        assert result.is_definite is False
        assert result.candidate_id is None


class TestDOIExactMatch:
    """Stage 1: exact DOI match → definite duplicate."""

    @pytest.mark.asyncio
    async def test_exact_doi_match_returns_definite_duplicate(self, db_session: AsyncSession) -> None:
        """Same DOI → is_duplicate=True, is_definite=True."""
        cp = await _insert_candidate(db_session, title="TDD Practices", doi="10.1234/jss.2022")
        await db_session.commit()

        result = await check_duplicate(
            study_id=STUDY_ID,
            doi="10.1234/jss.2022",
            title="TDD Practices",
            db=db_session,
        )
        assert result.is_duplicate is True
        assert result.is_definite is True
        assert result.candidate_id == cp.id

    @pytest.mark.asyncio
    async def test_doi_match_case_insensitive(self, db_session: AsyncSession) -> None:
        """DOI matching is case-insensitive."""
        cp = await _insert_candidate(db_session, title="Paper A", doi="10.1234/ABC")
        await db_session.commit()

        result = await check_duplicate(
            study_id=STUDY_ID,
            doi="10.1234/abc",
            title="Paper A",
            db=db_session,
        )
        assert result.is_duplicate is True
        assert result.is_definite is True
        assert result.candidate_id == cp.id

    @pytest.mark.asyncio
    async def test_different_doi_is_not_duplicate(self, db_session: AsyncSession) -> None:
        """Different DOI → falls through to fuzzy stage."""
        await _insert_candidate(db_session, title="Paper A", doi="10.1234/aaa")
        await db_session.commit()

        result = await check_duplicate(
            study_id=STUDY_ID,
            doi="10.1234/bbb",
            title="Totally Different Title xyz",
            db=db_session,
        )
        assert result.is_duplicate is False

    @pytest.mark.asyncio
    async def test_doi_match_ignored_for_different_study(self, db_session: AsyncSession) -> None:
        """DOI match in a different study does not trigger duplicate."""
        paper = Paper(title="Paper X", doi="10.1/shared")
        db_session.add(paper)
        await db_session.flush()
        cp = CandidatePaper(
            study_id=999,  # different study
            paper_id=paper.id,
            search_execution_id=FAKE_EXEC_ID,
            phase_tag="initial-search",
            current_status=CandidatePaperStatus.PENDING,
        )
        db_session.add(cp)
        await db_session.commit()

        result = await check_duplicate(
            study_id=STUDY_ID,
            doi="10.1/shared",
            title="Paper X",
            db=db_session,
        )
        assert result.is_duplicate is False


class TestFuzzyTitleMatch:
    """Stage 2: fuzzy title ≥ 0.90 + author overlap → probable duplicate."""

    @pytest.mark.asyncio
    async def test_high_similarity_with_author_overlap_is_duplicate(
        self, db_session: AsyncSession
    ) -> None:
        """Title similarity ≥ 0.90 + matching author → probable duplicate."""
        cp = await _insert_candidate(
            db_session,
            title="A Survey of Test-Driven Development Practices",
            doi=None,
            authors=[{"name": "Alice Smith"}, {"name": "Bob Jones"}],
        )
        await db_session.commit()

        result = await check_duplicate(
            study_id=STUDY_ID,
            doi=None,
            title="A Survey of Test-Driven Development Practices",
            authors=[{"name": "Alice Smith"}],
            db=db_session,
        )
        assert result.is_duplicate is True
        assert result.is_definite is False
        assert result.candidate_id == cp.id

    @pytest.mark.asyncio
    async def test_slightly_different_title_no_doi_is_not_duplicate(
        self, db_session: AsyncSession
    ) -> None:
        """Title similarity below 0.90 → not a duplicate."""
        await _insert_candidate(
            db_session,
            title="Machine Learning in Healthcare Applications",
            doi=None,
        )
        await db_session.commit()

        result = await check_duplicate(
            study_id=STUDY_ID,
            doi=None,
            title="Test-Driven Development for Embedded Systems",
            db=db_session,
        )
        assert result.is_duplicate is False

    @pytest.mark.asyncio
    async def test_high_title_similarity_but_no_author_overlap_is_not_duplicate(
        self, db_session: AsyncSession
    ) -> None:
        """Same title but completely different authors → author check vetoes duplicate."""
        await _insert_candidate(
            db_session,
            title="A Survey of Test-Driven Development Practices",
            doi=None,
            authors=[{"name": "Charlie Brown"}, {"name": "Diana Prince"}],
        )
        await db_session.commit()

        result = await check_duplicate(
            study_id=STUDY_ID,
            doi=None,
            title="A Survey of Test-Driven Development Practices",
            authors=[{"name": "Eve Wilson"}, {"name": "Frank Miller"}],
            db=db_session,
        )
        assert result.is_duplicate is False

    @pytest.mark.asyncio
    async def test_high_title_no_authors_provided_is_duplicate(
        self, db_session: AsyncSession
    ) -> None:
        """Same title, no author data provided → author check skipped → duplicate."""
        cp = await _insert_candidate(
            db_session,
            title="Systematic Mapping Studies: A Tutorial",
            doi=None,
            authors=[{"name": "Alice Smith"}],
        )
        await db_session.commit()

        result = await check_duplicate(
            study_id=STUDY_ID,
            doi=None,
            title="Systematic Mapping Studies: A Tutorial",
            authors=None,  # no author data provided
            db=db_session,
        )
        # When candidate has no author data, author check is skipped
        assert result.is_duplicate is True
        assert result.candidate_id == cp.id
