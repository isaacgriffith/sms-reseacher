"""Phase-gate unlock logic for Tertiary Studies (feature 009).

Tertiary Studies have a five-phase progression:
  - Phase 1: Protocol (always accessible)
  - Phase 2: Search & Import — requires a validated ``TertiaryStudyProtocol``
  - Phase 3: Screening — requires ≥1 ``CandidatePaper`` linked to the study
  - Phase 4: Quality Assessment — requires all accepted papers to have QA scores
              from all assigned reviewers (approximated)
  - Phase 5: Synthesis & Report — requires ≥2 ``TertiaryDataExtraction`` records
              with ``extraction_status == validated``
"""

from __future__ import annotations

from db.models.tertiary import TertiaryDataExtraction, TertiaryProtocolStatus, TertiaryStudyProtocol
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_tertiary_unlocked_phases(study_id: int, db: AsyncSession) -> list[int]:
    """Return the list of Tertiary Study phases currently unlocked for *study_id*.

    Phase 1 is always unlocked.  Each subsequent phase is gated on the
    prerequisite condition documented in data-model.md.

    Args:
        study_id: The Tertiary Study to evaluate.
        db: Async database session.

    Returns:
        A list of unlocked phase numbers (e.g. ``[1, 2, 3]``).

    """
    unlocked = [1]

    # Phase 2: TertiaryStudyProtocol must exist and be validated.
    protocol_result = await db.execute(
        select(TertiaryStudyProtocol).where(TertiaryStudyProtocol.study_id == study_id)
    )
    protocol = protocol_result.scalar_one_or_none()
    if protocol is None or protocol.status != TertiaryProtocolStatus.VALIDATED:
        return unlocked
    unlocked.append(2)

    # Phase 3: at least one CandidatePaper linked to this study.
    try:
        from db.models.candidate import CandidatePaper  # type: ignore[import]

        paper_result = await db.execute(
            select(func.count())
            .select_from(CandidatePaper)
            .where(CandidatePaper.study_id == study_id)
        )
        paper_count = paper_result.scalar_one()
        if paper_count == 0:
            return unlocked
        unlocked.append(3)
    except ImportError, Exception:
        return unlocked

    # Phase 4: all accepted papers have QA scores (approximated: at least one
    # QualityAssessmentScore exists for the study).
    quality_complete = await _is_quality_complete(study_id, db)
    if not quality_complete:
        return unlocked
    unlocked.append(4)

    # Phase 5: at least two TertiaryDataExtraction records with status=validated,
    # joined through CandidatePaper to scope to this study.
    try:
        from db.models.candidate import CandidatePaper as _CP  # type: ignore[import]

        extraction_result = await db.execute(
            select(func.count())
            .select_from(TertiaryDataExtraction)
            .join(_CP, TertiaryDataExtraction.candidate_paper_id == _CP.id)
            .where(
                _CP.study_id == study_id,
                TertiaryDataExtraction.extraction_status == "validated",
            )
        )
        validated_count = extraction_result.scalar_one()
        if validated_count >= 2:
            unlocked.append(5)
    except ImportError, Exception:
        pass

    return unlocked


async def _is_quality_complete(study_id: int, db: AsyncSession) -> bool:
    """Return True when the quality assessment phase is sufficiently complete.

    Approximation: QA is considered complete when at least one
    ``QualityAssessmentScore`` exists for an accepted candidate paper
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
