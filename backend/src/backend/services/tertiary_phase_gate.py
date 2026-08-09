"""Phase-gate unlock logic for Tertiary Studies (feature 009, phase 4 corrected in 012).

Tertiary Studies have a five-phase progression:
  - Phase 1: Protocol (always accessible)
  - Phase 2: Search & Import — requires a validated ``TertiaryStudyProtocol``
  - Phase 3: Screening — requires ≥1 ``CandidatePaper`` linked to the study
  - Phase 4: Quality Assessment — requires at least one *accepted*
              ``CandidatePaper`` (phase 3's output)
  - Phase 5: Synthesis & Report — requires ≥2 ``TertiaryDataExtraction`` records
              a human has reviewed (``human_reviewed`` or ``validated``; see
              TFIX8 at the phase-5 query for why ``ai_complete`` is excluded)

Phase 4 previously required a ``QualityAssessmentScore`` to exist — but
Quality Assessment is the only UI that creates one, so phase 4 was
permanently unreachable. The gate now checks phase 3's output instead of its
own (012 — see docs/features/012-wire-up-unreachable-workflows.md). Phase 5
is unchanged: it already gates on phase 4's output (extractions).
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

    # Phase 4: at least one accepted CandidatePaper — screening's (phase 3's)
    # output. NOT a QualityAssessmentScore: that is what phase 4 itself
    # produces, and a gate that requires its own phase's output can never
    # open (012).
    has_accepted_papers = await _has_accepted_papers(study_id, db)
    if not has_accepted_papers:
        return unlocked
    unlocked.append(4)

    # Phase 5: at least two TertiaryDataExtraction records a human has reviewed,
    # joined through CandidatePaper to scope to this study.
    #
    # TFIX8. This asked for `== "validated"` alone, which nothing in the
    # platform ever writes: `TertiaryExtractionForm` saves `human_reviewed`,
    # and no other path sets the field. Phase 5 was therefore unreachable.
    #
    # The corpus decides which side was wrong, and it is the gate. Requiring a
    # second validation event would encode a rule `docs/methodology/` does not
    # state: `04-tertiary.md` presents its two-reviewer consensus protocol as
    # "the only fully specified multi-rater extraction protocol in the corpus"
    # — an exemplar — and the same chapter records a tertiary study where "One
    # person seeing every paper is a known bias, accepted deliberately", whose
    # remedy is to "Record the trade-off rather than pretending it does not
    # exist". `08-extraction-and-synthesis.md` asks for independent double
    # extraction "where feasible". Disclosure, not prohibition.
    #
    # The opposite fix — making the form save "validated" — was rejected as
    # worse than the defect: a status named "validated" asserts a consensus
    # event that never happened, which is apparent conformance, and under
    # Principle XI that outranks an unreachable phase.
    #
    # Deliberately NOT `!= "pending"`, which is how phase_gate.py gates SMS:
    # that admits `ai_complete` — an AI pre-fill no reviewer has read — and
    # `01-slr.md` §2.4 forbids exactly that, "extraction decoupled from
    # appraisal". The SMS gate has the same weakness; recorded as TFIX10.
    try:
        from db.models.candidate import CandidatePaper as _CP  # type: ignore[import]

        extraction_result = await db.execute(
            select(func.count())
            .select_from(TertiaryDataExtraction)
            .join(_CP, TertiaryDataExtraction.candidate_paper_id == _CP.id)
            .where(
                _CP.study_id == study_id,
                TertiaryDataExtraction.extraction_status.in_(("validated", "human_reviewed")),
            )
        )
        validated_count = extraction_result.scalar_one()
        if validated_count >= 2:
            unlocked.append(5)
    except ImportError, Exception:
        pass

    return unlocked


async def _has_accepted_papers(study_id: int, db: AsyncSession) -> bool:
    """Return True when at least one accepted CandidatePaper exists for the study.

    This is screening's (phase 3's) output, and the correct prerequisite for
    unlocking phase 4 (012 — see module docstring). Replaces the former
    ``_is_quality_complete`` helper, which is no longer needed here: it
    checked for a ``QualityAssessmentScore``, which is what phase 4 itself
    now produces rather than requires. An equivalent helper remains in
    ``slr_phase_gate.py`` (``_is_quality_complete``), still needed there to
    gate SLR's phase 5.

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
