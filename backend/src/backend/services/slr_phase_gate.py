"""Phase-gate unlock logic for SLR studies (feature 007, corrected in 012).

SLR studies have a different phase sequence from SMS studies:
  - Phase 1: Protocol editor (always accessible)
  - Phase 2: Database search — requires validated ReviewProtocol
  - Phase 3: Screening — requires at least one completed SearchExecution
  - Phase 4: Quality assessment — requires at least one *accepted*
             CandidatePaper (phase 3's output)
  - Phase 5: Synthesis — requires at least one QualityAssessmentScore
             (phase 4's output)

Each gate deliberately checks the *previous* phase's output, never its own.
Before 012, phase 4 required a QualityAssessmentScore and phase 5 required a
completed SynthesisResult — but Quality Assessment and Synthesis are the
*only* UIs that create those rows respectively, so both phases were
permanently unreachable. See docs/features/012-wire-up-unreachable-workflows.md.

Phases 1 and 3 delegate to :func:`phase_gate.get_unlocked_phases` for
shared SMS/SLR logic where applicable.
"""

from __future__ import annotations

from db.models.slr import ReviewProtocol, ReviewProtocolStatus
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

        # TFIX12: `.limit(1)` because this asks whether *any* completed search
        # exists, not whether exactly one does. Without it `scalar_one_or_none`
        # raises MultipleResultsFound, and a study that ran a full search and a
        # snowball has two — `search_exec.py` has no constraint scoping
        # executions to a study, so that is legal and ordinary.
        search_result = await db.execute(
            select(SearchExecution)
            .where(
                SearchExecution.study_id == study_id,
                SearchExecution.status == SearchExecutionStatus.COMPLETED,
            )
            .limit(1)
        )
        if search_result.scalar_one_or_none() is None:
            return unlocked
        unlocked.append(3)
    except ImportError:
        return unlocked

    # Phase 4: at least one accepted CandidatePaper — screening's (phase 3's)
    # output. NOT a QualityAssessmentScore: that is what phase 4 itself
    # produces, and a gate that requires its own phase's output can never
    # open (012).
    has_accepted_papers = await _has_accepted_papers(study_id, db)
    if not has_accepted_papers:
        return unlocked
    unlocked.append(4)

    # Phase 5: at least one QualityAssessmentScore — Quality Assessment's
    # (phase 4's) output. NOT a completed SynthesisResult: that is what
    # phase 5 itself produces (012). Reuses _is_quality_complete, which is
    # exactly "a QA score exists" — the same predicate that gated phase 4
    # before this fix, now correctly applied one phase later.
    quality_complete = await _is_quality_complete(study_id, db)
    if quality_complete:
        unlocked.append(5)

    return unlocked


async def _has_accepted_papers(study_id: int, db: AsyncSession) -> bool:
    """Return True when at least one accepted CandidatePaper exists for the study.

    This is screening's (phase 3's) output, and the correct prerequisite for
    unlocking phase 4 (012 — see module docstring).

    Args:
        study_id: The study to evaluate.
        db: Active async database session.

    Returns:
        ``True`` if an accepted candidate paper exists, ``False`` otherwise.

    """
    try:
        from db.models.candidate import (  # type: ignore[import]
            CandidatePaper,
            CandidatePaperStatus,
        )

        result = await db.execute(
            select(CandidatePaper)
            .where(
                CandidatePaper.study_id == study_id,
                CandidatePaper.current_status == CandidatePaperStatus.ACCEPTED,
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None
    except ImportError, Exception:
        return False


async def _is_quality_complete(study_id: int, db: AsyncSession) -> bool:
    """Return True when at least one QualityAssessmentScore exists for the study.

    Used as the prerequisite for phase 5 (012): Quality Assessment's
    (phase 4's) output. The name predates 012, when this same predicate
    (incorrectly) gated phase 4 itself.

    Args:
        study_id: The study to evaluate.
        db: Active async database session.

    Returns:
        ``True`` if a QA score exists, ``False`` otherwise.

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
