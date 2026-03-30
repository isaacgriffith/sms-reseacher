"""Unit tests for backend.services.narrative_synthesis_service (feature 008).

Covers:
- get_or_create_sections: creates sections when protocol validated with RQs
- get_or_create_sections: returns existing sections without creating duplicates
- get_or_create_sections: returns empty/existing when protocol not validated
- update_section: updates narrative_text and is_complete
- update_section: leaves fields unchanged when None is passed
- update_section: returns None for missing section
- is_synthesis_complete: True when all sections complete
- is_synthesis_complete: False when any section incomplete
- is_synthesis_complete: False when no sections exist
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Register all ORM models before creating tables
import db.models  # noqa: F401
import db.models.rapid_review  # noqa: F401

from db.base import Base
from db.models.rapid_review import (
    RapidReviewProtocol,
    RRNarrativeSynthesisSection,
    RRProtocolStatus,
    RRQualityAppraisalMode,
)

STUDY_ID = 55


@pytest_asyncio.fixture
async def db_session():
    """Provide a fresh in-memory SQLite session with all RR tables.

    Yields:
        An :class:`~sqlalchemy.ext.asyncio.AsyncSession` backed by SQLite.
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_protocol(status: RRProtocolStatus, rqs: list[str] | None = None) -> MagicMock:
    """Build a minimal RapidReviewProtocol mock.

    Args:
        status: Protocol lifecycle status.
        rqs: List of research question strings, or None.

    Returns:
        A :class:`~unittest.mock.MagicMock` standing in for a
        :class:`~db.models.rapid_review.RapidReviewProtocol`.
    """
    p = MagicMock()
    p.status = status
    p.research_questions = rqs
    p.practical_problem = "some problem"
    p.quality_appraisal_mode = RRQualityAppraisalMode.FULL
    return p


def _make_section(rq_index: int = 0, is_complete: bool = False) -> MagicMock:
    """Build a minimal RRNarrativeSynthesisSection mock.

    Args:
        rq_index: Zero-based research question index.
        is_complete: Whether the section is marked complete.

    Returns:
        A :class:`~unittest.mock.MagicMock` standing in for a
        :class:`~db.models.rapid_review.RRNarrativeSynthesisSection`.
    """
    s = MagicMock()
    s.id = rq_index + 1
    s.rq_index = rq_index
    s.is_complete = is_complete
    s.narrative_text = None
    return s


# ---------------------------------------------------------------------------
# get_or_create_sections
# ---------------------------------------------------------------------------


class TestGetOrCreateSections:
    """get_or_create_sections creates or returns synthesis sections."""

    @pytest.mark.asyncio
    async def test_creates_sections_when_protocol_validated_with_rqs(self) -> None:
        """Creates one section per RQ when protocol is validated."""
        from backend.services.narrative_synthesis_service import get_or_create_sections

        mock_protocol = _make_protocol(RRProtocolStatus.VALIDATED, rqs=["RQ1", "RQ2"])

        # existing sections query → empty
        existing_result = MagicMock()
        existing_result.scalars.return_value.all.return_value = []

        # after flush: fetch_sections query → two new sections
        fetch_result = MagicMock()
        s0 = _make_section(0)
        s1 = _make_section(1)
        fetch_result.scalars.return_value.all.return_value = [s0, s1]

        session = AsyncMock()
        session.execute.side_effect = [existing_result, fetch_result]
        session.add = MagicMock()  # sync mock so side_effect captures work
        session.flush = AsyncMock()

        added = []
        session.add.side_effect = lambda obj: added.append(obj)

        with patch(
            "backend.services.narrative_synthesis_service.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            result = await get_or_create_sections(study_id=STUDY_ID, db=session)

        assert len(added) == 2
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_returns_existing_without_creating_duplicates(self) -> None:
        """Does not add new sections when all RQ indices already exist."""
        from backend.services.narrative_synthesis_service import get_or_create_sections

        mock_protocol = _make_protocol(RRProtocolStatus.VALIDATED, rqs=["RQ1"])

        existing_s = _make_section(0)

        existing_result = MagicMock()
        existing_result.scalars.return_value.all.return_value = [existing_s]

        fetch_result = MagicMock()
        fetch_result.scalars.return_value.all.return_value = [existing_s]

        session = AsyncMock()
        session.execute.side_effect = [existing_result, fetch_result]
        session.flush = AsyncMock()

        added = []
        session.add.side_effect = lambda obj: added.append(obj)

        with patch(
            "backend.services.narrative_synthesis_service.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            result = await get_or_create_sections(study_id=STUDY_ID, db=session)

        assert len(added) == 0  # no new sections added
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_returns_empty_when_protocol_not_validated(self) -> None:
        """Returns whatever existing sections exist when protocol is DRAFT."""
        from backend.services.narrative_synthesis_service import get_or_create_sections

        mock_protocol = _make_protocol(RRProtocolStatus.DRAFT, rqs=["RQ1"])

        # Fetch sections directly (protocol not validated)
        fetch_result = MagicMock()
        fetch_result.scalars.return_value.all.return_value = []

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        with patch(
            "backend.services.narrative_synthesis_service.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            result = await get_or_create_sections(study_id=STUDY_ID, db=session)

        assert result == []

    @pytest.mark.asyncio
    async def test_returns_existing_when_protocol_not_validated(self) -> None:
        """Returns existing sections (not empty) when protocol is DRAFT."""
        from backend.services.narrative_synthesis_service import get_or_create_sections

        mock_protocol = _make_protocol(RRProtocolStatus.DRAFT)

        existing_s = _make_section(0)
        fetch_result = MagicMock()
        fetch_result.scalars.return_value.all.return_value = [existing_s]

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        with patch(
            "backend.services.narrative_synthesis_service.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            result = await get_or_create_sections(study_id=STUDY_ID, db=session)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_handles_empty_research_questions(self) -> None:
        """Validated protocol with no RQs creates no new sections."""
        from backend.services.narrative_synthesis_service import get_or_create_sections

        mock_protocol = _make_protocol(RRProtocolStatus.VALIDATED, rqs=[])

        existing_result = MagicMock()
        existing_result.scalars.return_value.all.return_value = []

        fetch_result = MagicMock()
        fetch_result.scalars.return_value.all.return_value = []

        session = AsyncMock()
        session.execute.side_effect = [existing_result, fetch_result]
        session.add = MagicMock()  # sync mock so side_effect captures work
        session.flush = AsyncMock()

        added = []
        session.add.side_effect = lambda obj: added.append(obj)

        with patch(
            "backend.services.narrative_synthesis_service.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            result = await get_or_create_sections(study_id=STUDY_ID, db=session)

        assert len(added) == 0
        assert result == []


# ---------------------------------------------------------------------------
# update_section
# ---------------------------------------------------------------------------


class TestUpdateSection:
    """update_section modifies narrative_text and/or is_complete."""

    @pytest.mark.asyncio
    async def test_updates_narrative_text(self) -> None:
        """Sets narrative_text when a new value is provided."""
        from backend.services.narrative_synthesis_service import update_section

        mock_section = _make_section(0)
        mock_section.narrative_text = None

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_section

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]
        session.flush = AsyncMock()

        result = await update_section(
            section_id=1,
            narrative_text="New finding text",
            is_complete=None,
            db=session,
        )

        assert result is mock_section
        assert mock_section.narrative_text == "New finding text"

    @pytest.mark.asyncio
    async def test_updates_is_complete(self) -> None:
        """Sets is_complete when a new value is provided."""
        from backend.services.narrative_synthesis_service import update_section

        mock_section = _make_section(0, is_complete=False)

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_section

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]
        session.flush = AsyncMock()

        result = await update_section(
            section_id=1,
            narrative_text=None,
            is_complete=True,
            db=session,
        )

        assert result is mock_section
        assert mock_section.is_complete is True

    @pytest.mark.asyncio
    async def test_leaves_fields_unchanged_when_none(self) -> None:
        """Does not overwrite fields when None is passed for both parameters."""
        from backend.services.narrative_synthesis_service import update_section

        mock_section = _make_section(0, is_complete=True)
        mock_section.narrative_text = "Original text"

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_section

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]
        session.flush = AsyncMock()

        result = await update_section(
            section_id=1,
            narrative_text=None,
            is_complete=None,
            db=session,
        )

        assert result is mock_section
        # Original values preserved
        assert mock_section.narrative_text == "Original text"
        assert mock_section.is_complete is True

    @pytest.mark.asyncio
    async def test_returns_none_for_missing_section(self) -> None:
        """Returns None when the section ID does not exist."""
        from backend.services.narrative_synthesis_service import update_section

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = None

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        result = await update_section(
            section_id=9999,
            narrative_text="text",
            is_complete=True,
            db=session,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_calls_flush_after_update(self) -> None:
        """db.flush() is called after updating the section."""
        from backend.services.narrative_synthesis_service import update_section

        mock_section = _make_section(0)

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_section

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]
        session.flush = AsyncMock()

        await update_section(
            section_id=1,
            narrative_text="text",
            is_complete=True,
            db=session,
        )

        session.flush.assert_awaited()


# ---------------------------------------------------------------------------
# is_synthesis_complete
# ---------------------------------------------------------------------------


class TestIsSynthesisComplete:
    """is_synthesis_complete returns correct boolean."""

    @pytest.mark.asyncio
    async def test_returns_true_when_all_sections_complete(self) -> None:
        """Returns True when every section has is_complete=True."""
        from backend.services.narrative_synthesis_service import is_synthesis_complete

        s0 = _make_section(0, is_complete=True)
        s1 = _make_section(1, is_complete=True)

        fetch_result = MagicMock()
        fetch_result.scalars.return_value.all.return_value = [s0, s1]

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        result = await is_synthesis_complete(study_id=STUDY_ID, db=session)

        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_any_section_incomplete(self) -> None:
        """Returns False when at least one section has is_complete=False."""
        from backend.services.narrative_synthesis_service import is_synthesis_complete

        s0 = _make_section(0, is_complete=True)
        s1 = _make_section(1, is_complete=False)

        fetch_result = MagicMock()
        fetch_result.scalars.return_value.all.return_value = [s0, s1]

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        result = await is_synthesis_complete(study_id=STUDY_ID, db=session)

        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_when_no_sections_exist(self) -> None:
        """Returns False when no synthesis sections exist for the study."""
        from backend.services.narrative_synthesis_service import is_synthesis_complete

        fetch_result = MagicMock()
        fetch_result.scalars.return_value.all.return_value = []

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        result = await is_synthesis_complete(study_id=STUDY_ID, db=session)

        assert result is False

    @pytest.mark.asyncio
    async def test_returns_true_for_single_complete_section(self) -> None:
        """Returns True when there is exactly one section and it is complete."""
        from backend.services.narrative_synthesis_service import is_synthesis_complete

        s0 = _make_section(0, is_complete=True)

        fetch_result = MagicMock()
        fetch_result.scalars.return_value.all.return_value = [s0]

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        result = await is_synthesis_complete(study_id=STUDY_ID, db=session)

        assert result is True
