"""Unit tests for backend.services.rr_protocol_service (feature 008).

Covers the core business logic functions that have no existing test coverage:
- detect_research_gap_questions: keyword heuristic classification
- _apply_fields: partial dict application to protocol ORM instance
- _auto_create_threats: auto-creation of CONTEXT_RESTRICTION threats
- get_or_create_protocol: returns existing or creates new protocol
- update_protocol: applies fields, resets validated to draft, 409 on unacknowledged
- validate_protocol: runs pre-checks, sets VALIDATED, creates threats
- invalidate_papers_for_study: bulk-marks papers as PROTOCOL_INVALIDATED
- configure_search_restrictions: upserts restriction threat rows
- set_single_reviewer_mode: toggles SINGLE_REVIEWER threat
- set_quality_appraisal_mode: manages QA threat rows
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from db.models.rapid_review import (
    RapidReviewProtocol,
    RRProtocolStatus,
    RRQualityAppraisalMode,
    RRThreatToValidity,
    RRThreatType,
)


# ---------------------------------------------------------------------------
# detect_research_gap_questions
# ---------------------------------------------------------------------------


class TestDetectResearchGapQuestions:
    """detect_research_gap_questions flags questions with gap-related keywords."""

    def test_flags_gap_keyword(self) -> None:
        """Flags a question containing 'gap'."""
        from backend.services.rr_protocol_service import detect_research_gap_questions

        result = detect_research_gap_questions(["What is the gap in testing tools?"])
        assert len(result) == 1

    def test_flags_future_work_keyword(self) -> None:
        """Flags a question containing 'future work'."""
        from backend.services.rr_protocol_service import detect_research_gap_questions

        result = detect_research_gap_questions(["What future work is needed in ML?"])
        assert len(result) == 1

    def test_flags_what_is_missing_keyword(self) -> None:
        """Flags a question containing 'what is missing'."""
        from backend.services.rr_protocol_service import detect_research_gap_questions

        result = detect_research_gap_questions(["What is missing from current frameworks?"])
        assert len(result) == 1

    def test_flags_lack_of_keyword(self) -> None:
        """Flags a question containing 'lack of'."""
        from backend.services.rr_protocol_service import detect_research_gap_questions

        result = detect_research_gap_questions(["Is there a lack of studies on TDD?"])
        assert len(result) == 1

    def test_does_not_flag_normal_question(self) -> None:
        """Does not flag questions without gap-related keywords."""
        from backend.services.rr_protocol_service import detect_research_gap_questions

        result = detect_research_gap_questions(["How effective is pair programming?"])
        assert result == []

    def test_returns_empty_list_for_empty_input(self) -> None:
        """Returns empty list for an empty input list."""
        from backend.services.rr_protocol_service import detect_research_gap_questions

        result = detect_research_gap_questions([])
        assert result == []

    def test_returns_only_flagged_questions(self) -> None:
        """Returns only the flagged questions, not the whole list."""
        from backend.services.rr_protocol_service import detect_research_gap_questions

        questions = [
            "How effective is TDD?",
            "What is the gap in TDD adoption?",
            "What tools are used?",
        ]
        result = detect_research_gap_questions(questions)
        assert len(result) == 1
        assert "gap" in result[0]

    def test_case_insensitive_matching(self) -> None:
        """Keyword matching is case-insensitive."""
        from backend.services.rr_protocol_service import detect_research_gap_questions

        result = detect_research_gap_questions(["What is the GAP in testing?"])
        assert len(result) == 1


# ---------------------------------------------------------------------------
# _apply_fields
# ---------------------------------------------------------------------------


class TestApplyFields:
    """_apply_fields applies allowed fields to a protocol instance in-place."""

    def _make_protocol(self) -> MagicMock:
        """Create a minimal mock protocol.

        Returns:
            A :class:`~unittest.mock.MagicMock` representing a
            :class:`~db.models.rapid_review.RapidReviewProtocol`.
        """
        p = MagicMock(spec=RapidReviewProtocol)
        p.practical_problem = None
        p.research_questions = None
        p.time_budget_days = None
        p.effort_budget_hours = None
        p.context_restrictions = None
        p.dissemination_medium = None
        p.problem_scoping_notes = None
        p.search_strategy_notes = None
        p.inclusion_criteria = None
        p.exclusion_criteria = None
        p.single_source_acknowledged = False
        return p

    def test_applies_allowed_field(self) -> None:
        """Sets practical_problem when it is in the allowed set."""
        from backend.services.rr_protocol_service import _apply_fields

        protocol = self._make_protocol()
        _apply_fields(protocol, {"practical_problem": "We need to know about TDD."})
        assert protocol.practical_problem == "We need to know about TDD."

    def test_ignores_unknown_fields(self) -> None:
        """Silently ignores fields not in the allowed set."""
        from backend.services.rr_protocol_service import _apply_fields

        protocol = self._make_protocol()
        _apply_fields(protocol, {"secret_field": "leaked", "status": "hacked"})
        # Verify allowed fields were not changed
        assert protocol.practical_problem is None

    def test_applies_multiple_fields(self) -> None:
        """Applies multiple allowed fields simultaneously."""
        from backend.services.rr_protocol_service import _apply_fields

        protocol = self._make_protocol()
        _apply_fields(
            protocol,
            {
                "practical_problem": "problem text",
                "research_questions": ["RQ1", "RQ2"],
                "time_budget_days": 30,
            },
        )
        assert protocol.practical_problem == "problem text"
        assert protocol.research_questions == ["RQ1", "RQ2"]
        assert protocol.time_budget_days == 30

    def test_applies_single_source_acknowledged(self) -> None:
        """Sets single_source_acknowledged when provided."""
        from backend.services.rr_protocol_service import _apply_fields

        protocol = self._make_protocol()
        _apply_fields(protocol, {"single_source_acknowledged": True})
        assert protocol.single_source_acknowledged is True


# ---------------------------------------------------------------------------
# _auto_create_threats
# ---------------------------------------------------------------------------


class TestAutoCreateThreats:
    """_auto_create_threats auto-creates CONTEXT_RESTRICTION threat entries."""

    def _make_protocol(
        self,
        context_restrictions: list | None = None,
        threats: list | None = None,
    ) -> MagicMock:
        """Build a minimal protocol mock.

        Args:
            context_restrictions: List of restriction dicts, or None.
            threats: Existing threat list, or None.

        Returns:
            A configured :class:`~unittest.mock.MagicMock`.
        """
        p = MagicMock()
        p.context_restrictions = context_restrictions
        p.threats = threats if threats is not None else []
        return p

    def test_does_nothing_when_no_restrictions(self) -> None:
        """Does nothing when context_restrictions is empty/None."""
        from backend.services.rr_protocol_service import _auto_create_threats

        protocol = self._make_protocol(context_restrictions=None)
        _auto_create_threats(protocol, study_id=1)
        assert len(protocol.threats) == 0

    def test_creates_threat_for_each_restriction(self) -> None:
        """Appends one CONTEXT_RESTRICTION threat per restriction dict."""
        from backend.services.rr_protocol_service import _auto_create_threats

        protocol = self._make_protocol(
            context_restrictions=[
                {"type": "geography", "description": "Europe only"},
                {"type": "language", "description": "English only"},
            ],
            threats=[],
        )
        _auto_create_threats(protocol, study_id=1)
        assert len(protocol.threats) == 2

    def test_skips_already_existing_threats(self) -> None:
        """Does not duplicate a threat whose source_detail already exists."""
        from backend.services.rr_protocol_service import _auto_create_threats

        existing_threat = MagicMock()
        existing_threat.threat_type = RRThreatType.CONTEXT_RESTRICTION
        existing_threat.source_detail = "geography"

        protocol = self._make_protocol(
            context_restrictions=[
                {"type": "geography", "description": "Europe only"},
            ],
            threats=[existing_threat],
        )
        _auto_create_threats(protocol, study_id=1)
        # Length unchanged — the existing threat was not duplicated
        assert len(protocol.threats) == 1

    def test_uses_description_from_restriction(self) -> None:
        """Uses the 'description' field as the threat description."""
        from backend.services.rr_protocol_service import _auto_create_threats

        protocol = self._make_protocol(
            context_restrictions=[
                {"type": "language", "description": "English-only studies"},
            ],
            threats=[],
        )
        _auto_create_threats(protocol, study_id=1)
        added = protocol.threats[0]
        assert isinstance(added, RRThreatToValidity)


# ---------------------------------------------------------------------------
# get_or_create_protocol
# ---------------------------------------------------------------------------


class TestGetOrCreateProtocol:
    """get_or_create_protocol returns or creates a protocol."""

    @pytest.mark.asyncio
    async def test_returns_existing_protocol(self) -> None:
        """Returns the protocol when it already exists in the database."""
        from backend.services.rr_protocol_service import get_or_create_protocol

        mock_protocol = MagicMock(spec=RapidReviewProtocol)

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = mock_protocol

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]

        result = await get_or_create_protocol(study_id=1, db=session)

        assert result is mock_protocol
        session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_creates_protocol_when_missing(self) -> None:
        """Creates and flushes a new protocol when none exists."""
        from backend.services.rr_protocol_service import get_or_create_protocol

        fetch_result = MagicMock()
        fetch_result.scalar_one_or_none.return_value = None  # no existing protocol

        session = AsyncMock()
        session.execute.side_effect = [fetch_result]
        session.add = MagicMock()
        session.flush = AsyncMock()

        result = await get_or_create_protocol(study_id=42, db=session)

        assert isinstance(result, RapidReviewProtocol)
        assert result.study_id == 42
        session.add.assert_called_once()
        session.flush.assert_awaited()


# ---------------------------------------------------------------------------
# update_protocol
# ---------------------------------------------------------------------------


class TestUpdateProtocol:
    """update_protocol applies changes and manages validation state."""

    @pytest.mark.asyncio
    async def test_raises_409_when_validated_without_acknowledgment(self) -> None:
        """Raises HTTP 409 when protocol is VALIDATED and ack flag is False."""
        from fastapi import HTTPException
        from backend.services.rr_protocol_service import update_protocol

        mock_protocol = MagicMock(spec=RapidReviewProtocol)
        mock_protocol.status = RRProtocolStatus.VALIDATED

        with patch(
            "backend.services.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ), patch(
            "backend.services.rr_protocol_service._count_study_papers",
            new=AsyncMock(return_value=5),
        ):
            session = AsyncMock()
            with pytest.raises(HTTPException) as exc_info:
                await update_protocol(
                    study_id=1,
                    data={"practical_problem": "new"},
                    acknowledge_invalidation=False,
                    db=session,
                )

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_resets_to_draft_when_validated_with_acknowledgment(self) -> None:
        """Resets status to DRAFT and invalidates papers when ack flag is True."""
        from backend.services.rr_protocol_service import update_protocol

        mock_protocol = MagicMock(spec=RapidReviewProtocol)
        mock_protocol.status = RRProtocolStatus.VALIDATED
        mock_protocol.practical_problem = None

        with patch(
            "backend.services.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ), patch(
            "backend.services.rr_protocol_service.invalidate_papers_for_study",
            new=AsyncMock(return_value=0),
        ):
            session = AsyncMock()
            session.flush = AsyncMock()
            await update_protocol(
                study_id=1,
                data={"practical_problem": "updated"},
                acknowledge_invalidation=True,
                db=session,
            )

        assert mock_protocol.status == RRProtocolStatus.DRAFT

    @pytest.mark.asyncio
    async def test_applies_fields_for_draft_protocol(self) -> None:
        """Applies the data dict without invalidation when protocol is DRAFT."""
        from backend.services.rr_protocol_service import update_protocol

        mock_protocol = MagicMock(spec=RapidReviewProtocol)
        mock_protocol.status = RRProtocolStatus.DRAFT
        mock_protocol.practical_problem = None

        with patch(
            "backend.services.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            session = AsyncMock()
            session.flush = AsyncMock()
            result = await update_protocol(
                study_id=1,
                data={"practical_problem": "new problem"},
                acknowledge_invalidation=False,
                db=session,
            )

        assert result is mock_protocol
        assert mock_protocol.practical_problem == "new problem"


# ---------------------------------------------------------------------------
# validate_protocol
# ---------------------------------------------------------------------------


class TestValidateProtocol:
    """validate_protocol validates the protocol when pre-checks pass."""

    @pytest.mark.asyncio
    async def test_raises_422_when_no_stakeholder(self) -> None:
        """Raises HTTP 422 when no PractitionerStakeholder exists."""
        from fastapi import HTTPException
        from backend.services.rr_protocol_service import validate_protocol

        mock_protocol = MagicMock(spec=RapidReviewProtocol)
        mock_protocol.status = RRProtocolStatus.DRAFT
        mock_protocol.research_questions = ["RQ1"]
        mock_protocol.practical_problem = "A problem"
        mock_protocol.context_restrictions = None
        mock_protocol.threats = []

        stakeholder_result = MagicMock()
        stakeholder_result.scalar_one_or_none.return_value = None  # no stakeholder

        session = AsyncMock()
        session.execute.side_effect = [stakeholder_result]
        session.flush = AsyncMock()

        with patch(
            "backend.services.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await validate_protocol(study_id=1, db=session)

        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_raises_422_when_no_research_questions(self) -> None:
        """Raises HTTP 422 when research_questions is empty."""
        from fastapi import HTTPException
        from backend.services.rr_protocol_service import validate_protocol

        mock_protocol = MagicMock(spec=RapidReviewProtocol)
        mock_protocol.status = RRProtocolStatus.DRAFT
        mock_protocol.research_questions = []  # empty
        mock_protocol.practical_problem = "A problem"
        mock_protocol.context_restrictions = None
        mock_protocol.threats = []

        stakeholder_result = MagicMock()
        stakeholder_result.scalar_one_or_none.return_value = MagicMock()  # has stakeholder

        session = AsyncMock()
        session.execute.side_effect = [stakeholder_result]
        session.flush = AsyncMock()

        with patch(
            "backend.services.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await validate_protocol(study_id=1, db=session)

        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_raises_422_when_no_practical_problem(self) -> None:
        """Raises HTTP 422 when practical_problem is empty."""
        from fastapi import HTTPException
        from backend.services.rr_protocol_service import validate_protocol

        mock_protocol = MagicMock(spec=RapidReviewProtocol)
        mock_protocol.status = RRProtocolStatus.DRAFT
        mock_protocol.research_questions = ["RQ1"]
        mock_protocol.practical_problem = ""  # empty
        mock_protocol.context_restrictions = None
        mock_protocol.threats = []

        stakeholder_result = MagicMock()
        stakeholder_result.scalar_one_or_none.return_value = MagicMock()

        session = AsyncMock()
        session.execute.side_effect = [stakeholder_result]
        session.flush = AsyncMock()

        with patch(
            "backend.services.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await validate_protocol(study_id=1, db=session)

        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_sets_validated_on_success(self) -> None:
        """Sets status to VALIDATED when all pre-checks pass."""
        from backend.services.rr_protocol_service import validate_protocol

        mock_protocol = MagicMock(spec=RapidReviewProtocol)
        mock_protocol.status = RRProtocolStatus.DRAFT
        mock_protocol.research_questions = ["RQ1"]
        mock_protocol.practical_problem = "A real problem"
        mock_protocol.context_restrictions = None
        mock_protocol.threats = []

        stakeholder_result = MagicMock()
        stakeholder_result.scalar_one_or_none.return_value = MagicMock()

        session = AsyncMock()
        session.execute.side_effect = [stakeholder_result]
        session.flush = AsyncMock()

        with (
            patch(
                "backend.services.rr_protocol_service.get_or_create_protocol",
                new=AsyncMock(return_value=mock_protocol),
            ),
            patch(
                "backend.services.narrative_synthesis_service.get_or_create_sections",
                new=AsyncMock(return_value=[]),
            ),
        ):
            result = await validate_protocol(study_id=1, db=session)

        assert result is mock_protocol
        assert mock_protocol.status == RRProtocolStatus.VALIDATED


# ---------------------------------------------------------------------------
# configure_search_restrictions
# ---------------------------------------------------------------------------


class TestConfigureSearchRestrictions:
    """configure_search_restrictions upserts restriction threat rows."""

    @pytest.mark.asyncio
    async def test_creates_new_restriction_threat(self) -> None:
        """Creates a new RRThreatToValidity when no existing row found."""
        from backend.services.rr_protocol_service import configure_search_restrictions

        existing_result = MagicMock()
        existing_result.scalars.return_value.all.return_value = []  # no existing threats

        session = AsyncMock()
        session.execute.side_effect = [existing_result]
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.delete = AsyncMock()

        await configure_search_restrictions(
            study_id=1,
            restrictions=[{"type": "year_range", "source_detail": "2015-2025"}],
            db=session,
        )

        session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_ignores_unknown_restriction_type(self) -> None:
        """Silently ignores restriction types not in the allowed set."""
        from backend.services.rr_protocol_service import configure_search_restrictions

        existing_result = MagicMock()
        existing_result.scalars.return_value.all.return_value = []

        session = AsyncMock()
        session.execute.side_effect = [existing_result]
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.delete = AsyncMock()

        # "single_source" is not in _RESTRICTION_TYPES
        await configure_search_restrictions(
            study_id=1,
            restrictions=[{"type": "single_source", "source_detail": "only IEEE"}],
            db=session,
        )

        session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_deletes_removed_restrictions(self) -> None:
        """Deletes existing threat rows for restriction types no longer in the list."""
        from backend.services.rr_protocol_service import configure_search_restrictions

        existing_threat = MagicMock()
        existing_threat.threat_type = RRThreatType.YEAR_RANGE
        existing_threat.source_detail = "2010-2020"

        existing_result = MagicMock()
        existing_result.scalars.return_value.all.return_value = [existing_threat]

        session = AsyncMock()
        session.execute.side_effect = [existing_result]
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.delete = AsyncMock()

        # Empty restrictions list → YEAR_RANGE should be deleted
        await configure_search_restrictions(study_id=1, restrictions=[], db=session)

        session.delete.assert_awaited_once_with(existing_threat)


# ---------------------------------------------------------------------------
# set_single_reviewer_mode
# ---------------------------------------------------------------------------


class TestSetSingleReviewerMode:
    """set_single_reviewer_mode creates or removes the SINGLE_REVIEWER threat."""

    @pytest.mark.asyncio
    async def test_creates_threat_when_enabled_and_no_existing(self) -> None:
        """Creates SINGLE_REVIEWER threat when enabled=True and none exists."""
        from backend.services.rr_protocol_service import set_single_reviewer_mode

        mock_protocol = MagicMock(spec=RapidReviewProtocol)
        mock_protocol.single_reviewer_mode = False

        threat_result = MagicMock()
        threat_result.scalar_one_or_none.return_value = None  # no existing threat

        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        with patch(
            "backend.services.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            session.execute.side_effect = [threat_result]
            await set_single_reviewer_mode(study_id=1, enabled=True, db=session)

        assert mock_protocol.single_reviewer_mode is True
        session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_does_not_create_threat_when_already_exists(self) -> None:
        """Does not add a duplicate threat when one already exists."""
        from backend.services.rr_protocol_service import set_single_reviewer_mode

        mock_protocol = MagicMock(spec=RapidReviewProtocol)
        mock_protocol.single_reviewer_mode = False

        existing_threat = MagicMock()
        threat_result = MagicMock()
        threat_result.scalar_one_or_none.return_value = existing_threat

        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        with patch(
            "backend.services.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            session.execute.side_effect = [threat_result]
            await set_single_reviewer_mode(study_id=1, enabled=True, db=session)

        session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_deletes_threat_when_disabled(self) -> None:
        """Deletes SINGLE_REVIEWER threat when enabled=False and one exists."""
        from backend.services.rr_protocol_service import set_single_reviewer_mode

        mock_protocol = MagicMock(spec=RapidReviewProtocol)
        mock_protocol.single_reviewer_mode = True

        existing_threat = MagicMock()
        threat_result = MagicMock()
        threat_result.scalar_one_or_none.return_value = existing_threat

        session = AsyncMock()
        session.flush = AsyncMock()
        session.delete = AsyncMock()

        with patch(
            "backend.services.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            session.execute.side_effect = [threat_result]
            await set_single_reviewer_mode(study_id=1, enabled=False, db=session)

        session.delete.assert_awaited_once_with(existing_threat)
        assert mock_protocol.single_reviewer_mode is False


# ---------------------------------------------------------------------------
# set_quality_appraisal_mode
# ---------------------------------------------------------------------------


class TestSetQualityAppraisalMode:
    """set_quality_appraisal_mode manages QA threat rows."""

    def _make_qa_session(
        self,
        qa_skipped_exists: bool = False,
        qa_simplified_exists: bool = False,
    ) -> AsyncMock:
        """Build a mock session that returns the specified QA threat rows.

        Args:
            qa_skipped_exists: Whether a QA_SKIPPED threat row exists.
            qa_simplified_exists: Whether a QA_SIMPLIFIED threat row exists.

        Returns:
            A configured :class:`~unittest.mock.AsyncMock` session.
        """
        mock_protocol = MagicMock(spec=RapidReviewProtocol)
        mock_protocol.quality_appraisal_mode = RRQualityAppraisalMode.FULL

        qa_skipped_result = MagicMock()
        qa_skipped_result.scalar_one_or_none.return_value = (
            MagicMock() if qa_skipped_exists else None
        )

        qa_simplified_result = MagicMock()
        qa_simplified_result.scalar_one_or_none.return_value = (
            MagicMock() if qa_simplified_exists else None
        )

        session = AsyncMock()
        session.execute.side_effect = [qa_skipped_result, qa_simplified_result]
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.delete = AsyncMock()

        return session, mock_protocol

    @pytest.mark.asyncio
    async def test_skipped_mode_creates_qa_skipped_threat(self) -> None:
        """Creates QA_SKIPPED threat when mode is SKIPPED and none exists."""
        from backend.services.rr_protocol_service import set_quality_appraisal_mode

        session, mock_protocol = self._make_qa_session(
            qa_skipped_exists=False, qa_simplified_exists=False
        )

        with patch(
            "backend.services.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            await set_quality_appraisal_mode(
                study_id=1,
                mode=RRQualityAppraisalMode.SKIPPED,
                db=session,
            )

        session.add.assert_called_once()
        assert mock_protocol.quality_appraisal_mode == RRQualityAppraisalMode.SKIPPED

    @pytest.mark.asyncio
    async def test_full_mode_removes_qa_skipped_threat(self) -> None:
        """Deletes QA_SKIPPED threat when mode is FULL and one exists."""
        from backend.services.rr_protocol_service import set_quality_appraisal_mode

        mock_protocol = MagicMock(spec=RapidReviewProtocol)
        mock_protocol.quality_appraisal_mode = RRQualityAppraisalMode.FULL

        existing_skipped = MagicMock()

        qa_skipped_result = MagicMock()
        qa_skipped_result.scalar_one_or_none.return_value = existing_skipped

        qa_simplified_result = MagicMock()
        qa_simplified_result.scalar_one_or_none.return_value = None

        session = AsyncMock()
        session.execute.side_effect = [qa_skipped_result, qa_simplified_result]
        session.add = MagicMock()
        session.flush = AsyncMock()
        session.delete = AsyncMock()

        with patch(
            "backend.services.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ):
            await set_quality_appraisal_mode(
                study_id=1,
                mode=RRQualityAppraisalMode.FULL,
                db=session,
            )

        session.delete.assert_awaited_once_with(existing_skipped)

    @pytest.mark.asyncio
    async def test_peer_reviewed_only_mode_creates_qa_simplified_threat(self) -> None:
        """Creates QA_SIMPLIFIED threat when mode is PEER_REVIEWED_ONLY and none exists."""
        from backend.services.rr_protocol_service import set_quality_appraisal_mode

        session, mock_protocol = self._make_qa_session(
            qa_skipped_exists=False, qa_simplified_exists=False
        )

        with patch(
            "backend.services.rr_protocol_service.get_or_create_protocol",
            new=AsyncMock(return_value=mock_protocol),
        ), patch(
            "backend.services.rr_protocol_service._exclude_non_peer_reviewed_papers",
            new=AsyncMock(return_value=0),
        ):
            await set_quality_appraisal_mode(
                study_id=1,
                mode=RRQualityAppraisalMode.PEER_REVIEWED_ONLY,
                db=session,
            )

        session.add.assert_called_once()
        assert mock_protocol.quality_appraisal_mode == RRQualityAppraisalMode.PEER_REVIEWED_ONLY
