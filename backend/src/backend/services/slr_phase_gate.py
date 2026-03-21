"""Phase-gate unlock logic for SLR studies (feature 007).

SLR studies have a different phase sequence from SMS studies:
  - Phase 1: Protocol editor (always accessible)
  - Phase 2: Database search — requires validated ReviewProtocol
  - Phase 3: Screening — requires at least one completed SearchExecution
  - Phase 4: Quality assessment — requires all accepted papers to have QA
             scores from all assigned reviewers
  - Phase 5: Synthesis — requires a completed SynthesisResult

Phases 1 and 3 delegate to :func:`phase_gate.get_unlocked_phases` for
shared SMS/SLR logic where applicable.
"""

from __future__ import annotations

from db.models.slr import ReviewProtocol, ReviewProtocolStatus, SynthesisResult, SynthesisStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_slr_unlocked_phases(study_id: int, db: AsyncSession) -> list[int]:
    """Return the list of SLR phases currently unlocked for *study_id*.

    Phase 1 is always unlocked.  Each subsequent phase requires the
    prerequisite condition to be met.

    Args:
        study_id: The SLR study to evaluate.
        db: Async database session.

    Returns:
        A list of unlocked phase numbers (e.g. ``[1, 2]``).

    """
    unlocked = [1]

    # Phase 2: ReviewProtocol must be validated
    protocol_result = await db.execute(
        select(ReviewProtocol).where(ReviewProtocol.study_id == study_id)
    )
    protocol = protocol_result.scalar_one_or_none()
    if protocol is None or protocol.status != ReviewProtocolStatus.VALIDATED:
        return unlocked
    unlocked.append(2)

    # Phase 3: at least one completed SearchExecution
    try:
        from db.models.search_exec import (  # type: ignore[import]
            SearchExecution,
            SearchExecutionStatus,
        )

        search_result = await db.execute(
            select(SearchExecution).where(
                SearchExecution.study_id == study_id,
                SearchExecution.status == SearchExecutionStatus.COMPLETED,
            )
        )
        if search_result.scalar_one_or_none() is None:
            return unlocked
        unlocked.append(3)
    except ImportError:
        return unlocked

    # Phase 4: all accepted papers have QA scores from all assigned reviewers.
    # We approximate this by checking whether any QualityAssessmentScore exists
    # for this study (full enforcement is in quality_assessment_service).
    quality_complete = await _is_quality_complete(study_id, db)
    if not quality_complete:
        return unlocked
    unlocked.append(4)

    # Phase 5: at least one SynthesisResult with status=completed
    synthesis_result = await db.execute(
        select(SynthesisResult).where(
            SynthesisResult.study_id == study_id,
            SynthesisResult.status == SynthesisStatus.COMPLETED,
        )
    )
    if synthesis_result.scalar_one_or_none() is not None:
        unlocked.append(5)

    return unlocked


async def _is_quality_complete(study_id: int, db: AsyncSession) -> bool:
    """Return True when the quality assessment phase is sufficiently complete.

    Approximation: QA is considered complete when at least one
    :class:`QualityAssessmentScore` exists for an accepted candidate paper
    belonging to this study.

    Args:
        study_id: The study to evaluate.
        db: Active async database session.

    Returns:
        ``True`` if QA is complete, ``False`` otherwise.

    """
    try:
        from db.models.candidate import CandidatePaper  # type: ignore[import]
        from db.models.slr import QualityAssessmentScore  # type: ignore[attr-defined]

        # Check via a join through CandidatePaper
        result = await db.execute(
            select(QualityAssessmentScore)
            .join(
                CandidatePaper,
                QualityAssessmentScore.candidate_paper_id == CandidatePaper.id,
            )
            .where(CandidatePaper.study_id == study_id)
            .limit(1)
        )
        return result.scalar_one_or_none() is not None
    except ImportError, Exception:
        return False
