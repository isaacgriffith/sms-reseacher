"""Phase-gate unlock logic for Rapid Review studies (feature 008).

Rapid Review studies use a five-phase workflow distinct from SMS and SLR:

- Phase 1: Protocol editor (always accessible).
- Phase 2: Search configuration — requires a validated ``RapidReviewProtocol``.
- Phase 3: Paper selection — requires at least one completed ``SearchExecution``.
- Phase 4: Quality appraisal — unlocked immediately when
  ``quality_appraisal_mode`` is ``SKIPPED`` or ``PEER_REVIEWED_ONLY``; otherwise
  requires at least one ``QualityAssessmentScore`` for the study.
- Phase 5: Narrative synthesis — requires at least one completed
  ``RRNarrativeSynthesisSection``.

This module is registered in the phase-gate dispatch dict in
``backend.api.v1.studies`` via ``StudyType.RAPID``.
"""

from __future__ import annotations

from db.models.rapid_review import (
    RapidReviewProtocol,
    RRNarrativeSynthesisSection,
    RRProtocolStatus,
    RRQualityAppraisalMode,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_rr_unlocked_phases(study_id: int, db: AsyncSession) -> list[int]:
    """Return the list of Rapid Review phases currently unlocked for *study_id*.

    Phase 1 is always unlocked.  Each subsequent phase requires the
    prerequisite condition defined in the phase-gate contract to be met.

    Args:
        study_id: The Rapid Review study to evaluate.
        db: Async database session.

    Returns:
        A list of unlocked phase numbers (e.g. ``[1, 2, 3]``).

    """
    unlocked = [1]

    # Phase 2: RapidReviewProtocol must be validated.
    protocol_result = await db.execute(
        select(RapidReviewProtocol).where(RapidReviewProtocol.study_id == study_id)
    )
    protocol = protocol_result.scalar_one_or_none()
    if protocol is None or protocol.status != RRProtocolStatus.VALIDATED:
        return unlocked
    unlocked.append(2)

    # Phase 3: at least one completed SearchExecution for this study.
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

    # Phase 4: quality appraisal.
    # Unlocked immediately when QA mode is SKIPPED or PEER_REVIEWED_ONLY.
    # For FULL mode: requires at least one QualityAssessmentScore for this study.
    quality_complete = await _is_quality_complete(study_id, protocol, db)
    if not quality_complete:
        return unlocked
    unlocked.append(4)

    # Phase 5: at least one RRNarrativeSynthesisSection with is_complete=True.
    section_result = await db.execute(
        select(RRNarrativeSynthesisSection).where(
            RRNarrativeSynthesisSection.study_id == study_id,
            RRNarrativeSynthesisSection.is_complete.is_(True),
        )
    )
    if section_result.scalar_one_or_none() is not None:
        unlocked.append(5)

    return unlocked


async def _is_quality_complete(
    study_id: int,
    protocol: RapidReviewProtocol,
    db: AsyncSession,
) -> bool:
    """Return True when the quality appraisal phase gate is satisfied.

    For ``SKIPPED`` and ``PEER_REVIEWED_ONLY`` modes the gate is satisfied
    immediately.  For ``FULL`` mode at least one
    :class:`~db.models.slr.QualityAssessmentScore` must exist for the study.

    Args:
        study_id: The Rapid Review study to evaluate.
        protocol: The study's ``RapidReviewProtocol`` record (already loaded).
        db: Active async database session.

    Returns:
        ``True`` if the quality phase gate is satisfied, ``False`` otherwise.

    """
    if protocol.quality_appraisal_mode in (
        RRQualityAppraisalMode.SKIPPED,
        RRQualityAppraisalMode.PEER_REVIEWED_ONLY,
    ):
        return True

    # FULL mode: check whether any QualityAssessmentScore exists for this study.
    try:
        from db.models.candidate import CandidatePaper  # type: ignore[import]
        from db.models.slr import QualityAssessmentScore  # type: ignore[attr-defined]

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
