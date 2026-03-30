"""Unit tests for backend.services.rr_phase_gate (feature 008).

Covers:
- get_rr_unlocked_phases: phase 1 always unlocked
- get_rr_unlocked_phases: phase 2 requires validated protocol
- get_rr_unlocked_phases: phase 3 requires completed SearchExecution
- get_rr_unlocked_phases: phase 4 skipped/peer-reviewed-only mode unlocks immediately
- get_rr_unlocked_phases: phase 4 full mode requires QualityAssessmentScore
- get_rr_unlocked_phases: phase 5 requires at least one complete synthesis section
- _is_quality_complete: returns True for SKIPPED and PEER_REVIEWED_ONLY modes
- _is_quality_complete: returns False for FULL mode with no scores
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Register all ORM models before creating tables
import db.models  # noqa: F401
import db.models.users  # noqa: F401
import db.models.study  # noqa: F401
import db.models.rapid_review  # noqa: F401

from db.base import Base
from db.models.rapid_review import (
    RapidReviewProtocol,
    RRNarrativeSynthesisSection,
    RRProtocolStatus,
    RRQualityAppraisalMode,
)

STUDY_ID = 77


@pytest_asyncio.fixture
async def db_session():
    """Provide a fresh in-memory SQLite session with all RR tables created.

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


class TestGetRrUnlockedPhasesPhase1:
    """Phase 1 is always unlocked."""

    @pytest.mark.asyncio
    async def test_phase_1_always_unlocked_no_data(self, db_session) -> None:
        """No protocol row → only phase 1 unlocked."""
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        result = await get_rr_unlocked_phases(STUDY_ID, db_session)
        assert result == [1]

    @pytest.mark.asyncio
    async def test_returns_list(self, db_session) -> None:
        """Return type is always a list."""
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        result = await get_rr_unlocked_phases(STUDY_ID, db_session)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_phase_1_always_in_result(self, db_session) -> None:
        """Phase 1 is always present regardless of other conditions."""
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        result = await get_rr_unlocked_phases(STUDY_ID, db_session)
        assert 1 in result


class TestGetRrUnlockedPhasesPhase2:
    """Phase 2 requires a validated RapidReviewProtocol."""

    @pytest.mark.asyncio
    async def test_phase_2_locked_when_protocol_draft(self, db_session) -> None:
        """Protocol in DRAFT state → phase 2 NOT unlocked."""
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        protocol = RapidReviewProtocol(
            study_id=STUDY_ID,
            status=RRProtocolStatus.DRAFT,
        )
        db_session.add(protocol)
        await db_session.commit()

        result = await get_rr_unlocked_phases(STUDY_ID, db_session)
        assert 2 not in result

    @pytest.mark.asyncio
    async def test_phase_2_unlocked_when_protocol_validated(self, db_session) -> None:
        """Protocol in VALIDATED state → phase 2 IS unlocked."""
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        protocol = RapidReviewProtocol(
            study_id=STUDY_ID,
            status=RRProtocolStatus.VALIDATED,
            quality_appraisal_mode=RRQualityAppraisalMode.SKIPPED,
        )
        db_session.add(protocol)
        await db_session.commit()

        result = await get_rr_unlocked_phases(STUDY_ID, db_session)
        assert 2 in result

    @pytest.mark.asyncio
    async def test_phase_2_includes_phase_1(self, db_session) -> None:
        """When phase 2 is unlocked, phase 1 is still included."""
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        protocol = RapidReviewProtocol(
            study_id=STUDY_ID,
            status=RRProtocolStatus.VALIDATED,
            quality_appraisal_mode=RRQualityAppraisalMode.SKIPPED,
        )
        db_session.add(protocol)
        await db_session.commit()

        result = await get_rr_unlocked_phases(STUDY_ID, db_session)
        assert 1 in result
        assert 2 in result

    @pytest.mark.asyncio
    async def test_phase_2_not_unlocked_without_protocol(self, db_session) -> None:
        """No protocol row → phase 2 not unlocked."""
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        result = await get_rr_unlocked_phases(STUDY_ID, db_session)
        assert 2 not in result


class TestGetRrUnlockedPhasesPhase3:
    """Phase 3 requires at least one completed SearchExecution."""

    @pytest.mark.asyncio
    async def test_phase_3_locked_when_no_search_execution(self, db_session) -> None:
        """Validated protocol but no SearchExecution → phase 3 NOT unlocked."""
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        protocol = RapidReviewProtocol(
            study_id=STUDY_ID,
            status=RRProtocolStatus.VALIDATED,
            quality_appraisal_mode=RRQualityAppraisalMode.SKIPPED,
        )
        db_session.add(protocol)
        await db_session.commit()

        result = await get_rr_unlocked_phases(STUDY_ID, db_session)
        assert 3 not in result

    @pytest.mark.asyncio
    async def test_phase_3_locked_when_import_error(self, db_session) -> None:
        """ImportError for search_exec model → phase 3 NOT unlocked, returns [1,2]."""
        from unittest.mock import patch as mock_patch
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        protocol = RapidReviewProtocol(
            study_id=STUDY_ID,
            status=RRProtocolStatus.VALIDATED,
            quality_appraisal_mode=RRQualityAppraisalMode.SKIPPED,
        )
        db_session.add(protocol)
        await db_session.commit()

        import builtins
        original_import = builtins.__import__

        def mock_import(name: str, *args, **kwargs):  # type: ignore[no-untyped-def]
            if "search_exec" in name:
                raise ImportError("mocked missing module")
            return original_import(name, *args, **kwargs)

        with mock_patch("builtins.__import__", side_effect=mock_import):
            result = await get_rr_unlocked_phases(STUDY_ID, db_session)

        assert 3 not in result
        assert 1 in result


class TestGetRrUnlockedPhasesPhase4:
    """Phase 4 quality appraisal gating."""

    def _make_session_with_protocol(
        self,
        mode: RRQualityAppraisalMode,
    ) -> AsyncMock:
        """Build a mocked async session that returns a validated protocol with given mode.

        Args:
            mode: The quality appraisal mode to set on the protocol.

        Returns:
            A configured :class:`~unittest.mock.AsyncMock` session.
        """
        mock_protocol = MagicMock()
        mock_protocol.status = RRProtocolStatus.VALIDATED
        mock_protocol.quality_appraisal_mode = mode

        protocol_fetch = MagicMock()
        protocol_fetch.scalar_one_or_none.return_value = mock_protocol

        search_fetch = MagicMock()
        search_fetch.scalar_one_or_none.return_value = MagicMock()  # search exists

        section_fetch = MagicMock()
        section_fetch.scalar_one_or_none.return_value = None  # no complete sections

        session = AsyncMock()
        session.execute.side_effect = [protocol_fetch, search_fetch, section_fetch]
        return session

    @pytest.mark.asyncio
    async def test_phase_4_unlocked_when_quality_skipped(self) -> None:
        """SKIPPED mode → phase 4 is immediately unlocked."""
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        session = self._make_session_with_protocol(RRQualityAppraisalMode.SKIPPED)

        result = await get_rr_unlocked_phases(STUDY_ID, session)
        assert 4 in result

    @pytest.mark.asyncio
    async def test_phase_4_unlocked_when_peer_reviewed_only(self) -> None:
        """PEER_REVIEWED_ONLY mode → phase 4 is immediately unlocked."""
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        session = self._make_session_with_protocol(RRQualityAppraisalMode.PEER_REVIEWED_ONLY)

        result = await get_rr_unlocked_phases(STUDY_ID, session)
        assert 4 in result

    @pytest.mark.asyncio
    async def test_phase_4_locked_when_full_mode_no_scores(self) -> None:
        """FULL mode with no QualityAssessmentScore → phase 4 NOT unlocked."""
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        mock_protocol = MagicMock()
        mock_protocol.status = RRProtocolStatus.VALIDATED
        mock_protocol.quality_appraisal_mode = RRQualityAppraisalMode.FULL

        protocol_fetch = MagicMock()
        protocol_fetch.scalar_one_or_none.return_value = mock_protocol

        search_fetch = MagicMock()
        search_fetch.scalar_one_or_none.return_value = MagicMock()  # search exists

        # FULL mode quality check → no scores found
        qa_score_fetch = MagicMock()
        qa_score_fetch.scalar_one_or_none.return_value = None

        session = AsyncMock()
        session.execute.side_effect = [protocol_fetch, search_fetch, qa_score_fetch]

        result = await get_rr_unlocked_phases(STUDY_ID, session)
        assert 4 not in result


class TestGetRrUnlockedPhasesPhase5:
    """Phase 5 requires at least one complete synthesis section."""

    @pytest.mark.asyncio
    async def test_phase_5_unlocked_when_section_complete(self, db_session) -> None:
        """Complete synthesis section → phase 5 IS unlocked."""
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        protocol = RapidReviewProtocol(
            study_id=STUDY_ID,
            status=RRProtocolStatus.VALIDATED,
            quality_appraisal_mode=RRQualityAppraisalMode.SKIPPED,
        )
        db_session.add(protocol)
        await db_session.flush()

        section = RRNarrativeSynthesisSection(
            study_id=STUDY_ID,
            rq_index=0,
            is_complete=True,
        )
        db_session.add(section)
        await db_session.commit()

        # Need a search execution to pass phase 3 gate
        # Since search_exec may raise ImportError in SQLite test env, we mock it
        from unittest.mock import patch as mock_patch

        mock_search_exec = MagicMock()
        mock_completed_status = MagicMock()
        mock_search_exec.study_id = STUDY_ID
        mock_search_exec.status = mock_completed_status

        with mock_patch(
            "backend.services.rr_phase_gate.get_rr_unlocked_phases",
            wraps=None,
        ):
            # We test indirectly: patch the import of SearchExecution to succeed
            # with a mocked result
            import importlib
            import sys

            # Build a mock search_exec module
            mock_se_module = MagicMock()
            mock_se_class = MagicMock()
            mock_se_status = MagicMock()
            mock_se_status.COMPLETED = "COMPLETED"
            mock_se_class.study_id = STUDY_ID
            mock_se_module.SearchExecution = mock_se_class
            mock_se_module.SearchExecutionStatus = mock_se_status

            pass  # just use the mock session approach instead

        # Use mock session to control all DB calls
        mock_protocol = MagicMock()
        mock_protocol.status = RRProtocolStatus.VALIDATED
        mock_protocol.quality_appraisal_mode = RRQualityAppraisalMode.SKIPPED

        protocol_fetch = MagicMock()
        protocol_fetch.scalar_one_or_none.return_value = mock_protocol

        search_fetch = MagicMock()
        search_fetch.scalar_one_or_none.return_value = MagicMock()  # search completed

        section_fetch = MagicMock()
        section_fetch.scalar_one_or_none.return_value = MagicMock()  # complete section

        session = AsyncMock()
        session.execute.side_effect = [protocol_fetch, search_fetch, section_fetch]

        result = await get_rr_unlocked_phases(STUDY_ID, session)
        assert 5 in result

    @pytest.mark.asyncio
    async def test_phase_5_locked_when_no_complete_sections(self) -> None:
        """No complete synthesis sections → phase 5 NOT unlocked."""
        from backend.services.rr_phase_gate import get_rr_unlocked_phases

        mock_protocol = MagicMock()
        mock_protocol.status = RRProtocolStatus.VALIDATED
        mock_protocol.quality_appraisal_mode = RRQualityAppraisalMode.SKIPPED

        protocol_fetch = MagicMock()
        protocol_fetch.scalar_one_or_none.return_value = mock_protocol

        search_fetch = MagicMock()
        search_fetch.scalar_one_or_none.return_value = MagicMock()  # search completed

        section_fetch = MagicMock()
        section_fetch.scalar_one_or_none.return_value = None  # NO complete section

        session = AsyncMock()
        session.execute.side_effect = [protocol_fetch, search_fetch, section_fetch]

        result = await get_rr_unlocked_phases(STUDY_ID, session)
        assert 5 not in result


class TestIsQualityComplete:
    """_is_quality_complete helper returns correct booleans."""

    @pytest.mark.asyncio
    async def test_returns_true_for_skipped_mode(self) -> None:
        """SKIPPED mode satisfies the quality phase gate immediately."""
        from backend.services.rr_phase_gate import _is_quality_complete

        mock_protocol = MagicMock()
        mock_protocol.quality_appraisal_mode = RRQualityAppraisalMode.SKIPPED

        session = AsyncMock()
        result = await _is_quality_complete(STUDY_ID, mock_protocol, session)

        assert result is True

    @pytest.mark.asyncio
    async def test_returns_true_for_peer_reviewed_only_mode(self) -> None:
        """PEER_REVIEWED_ONLY mode satisfies the quality phase gate immediately."""
        from backend.services.rr_phase_gate import _is_quality_complete

        mock_protocol = MagicMock()
        mock_protocol.quality_appraisal_mode = RRQualityAppraisalMode.PEER_REVIEWED_ONLY

        session = AsyncMock()
        result = await _is_quality_complete(STUDY_ID, mock_protocol, session)

        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_for_full_mode_no_scores(self) -> None:
        """FULL mode with no QualityAssessmentScore rows returns False."""
        from backend.services.rr_phase_gate import _is_quality_complete

        mock_protocol = MagicMock()
        mock_protocol.quality_appraisal_mode = RRQualityAppraisalMode.FULL

        qa_result = MagicMock()
        qa_result.scalar_one_or_none.return_value = None

        session = AsyncMock()
        session.execute.side_effect = [qa_result]

        result = await _is_quality_complete(STUDY_ID, mock_protocol, session)

        assert result is False

    @pytest.mark.asyncio
    async def test_returns_true_for_full_mode_with_scores(self) -> None:
        """FULL mode with at least one QualityAssessmentScore returns True."""
        from backend.services.rr_phase_gate import _is_quality_complete

        mock_protocol = MagicMock()
        mock_protocol.quality_appraisal_mode = RRQualityAppraisalMode.FULL

        qa_result = MagicMock()
        qa_result.scalar_one_or_none.return_value = MagicMock()  # score exists

        session = AsyncMock()
        session.execute.side_effect = [qa_result]

        result = await _is_quality_complete(STUDY_ID, mock_protocol, session)

        assert result is True
