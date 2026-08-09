"""Phase-gate unlock logic for systematic mapping studies.

Determines which study phases are accessible based on completion of prior phases.
Phase unlock rules (enforced at service layer, not DB):
  - Phase 1: always accessible
  - Phase 2: pico_components non-empty
  - Phase 3: at least one SearchExecution with status=completed
  - Phase 4 & 5: at least one DataExtraction with status ``validated`` or
    ``human_reviewed``, on a CandidatePaper belonging to *this* study.
    Deliberately not "status != pending", which admits the ``ai_complete``
    pre-fill no reviewer has read — see TFIX10 at the query below.

Staleness rules (FR-008a):
  - Phase 2 data is stale if PICO was re-saved after the last search ran.
  - Phase 3 data is stale if a new search ran after extraction started.
"""

from typing import TYPE_CHECKING

from db.models.pico import PICOComponent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from db.models import Study


async def get_unlocked_phases(study_id: int, db: AsyncSession) -> list[int]:
    """Return the list of phases currently unlocked for *study_id*.

    Phase 1 is always unlocked. Each subsequent phase requires the
    prerequisite condition to be met.

    Args:
        study_id: The study to evaluate.
        db: Async database session.

    Returns:
        A list of unlocked phase numbers (e.g. ``[1, 2]``).

    """
    unlocked = [1]

    # Phase 2: PICO saved
    pico_result = await db.execute(select(PICOComponent).where(PICOComponent.study_id == study_id))
    pico = pico_result.scalar_one_or_none()
    if pico is not None:
        unlocked.append(2)
    else:
        return unlocked

    # Phase 3: at least one completed SearchExecution
    # Import here to avoid circular imports at module level
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
        if search_result.scalar_one_or_none() is not None:
            unlocked.append(3)
        else:
            return unlocked
    except ImportError:
        return unlocked

    # Phases 4 & 5: at least one *human-appraised* DataExtraction *belonging to
    # this study*. DataExtraction carries no study_id of its own — it hangs off
    # a CandidatePaper — so the scope has to come from the join. Without it the
    # query reads the whole table, and one extraction anywhere in the database
    # unlocks reporting for every mapping study that has reached phase 3
    # (TFIX1).
    #
    # TFIX10: this predicate was `!= PENDING`, which admits `ai_complete` — the
    # status `extraction_job` writes unattended. A batch extraction run was
    # therefore sufficient on its own to open reporting, so a mapping study
    # could reach phases 4 and 5 on wholly unreviewed model output.
    # `01-slr.md` 2.4 calls results extracted without checking whether a study
    # used an invalid metric obtainable "very quickly but will be wrong", and
    # is explicit that what it forbids is "extraction decoupled from
    # appraisal" rather than automation as such. Gating on "not pending" was
    # exactly that decoupling. Matches `tertiary_phase_gate.py`, which TFIX8
    # narrowed the same way.
    #
    # `validated` is included though nothing in `backend/src` assigns it: a
    # status ranked above `human_reviewed` must not be *less* able to unlock a
    # phase than the one below it. Its dead-terminal-state problem is a
    # separate defect, recorded as such rather than papered over here.
    try:
        from db.models.candidate import CandidatePaper  # type: ignore[import]
        from db.models.extraction import DataExtraction, ExtractionStatus  # type: ignore[import]

        extraction_result = await db.execute(
            select(DataExtraction.id)
            .join(CandidatePaper, DataExtraction.candidate_paper_id == CandidatePaper.id)
            .where(
                CandidatePaper.study_id == study_id,
                DataExtraction.extraction_status.in_(
                    [ExtractionStatus.VALIDATED, ExtractionStatus.HUMAN_REVIEWED]
                ),
            )
            .limit(1)
        )
        if extraction_result.scalar_one_or_none() is not None:
            unlocked.extend([4, 5])
    except ImportError:
        pass

    return unlocked


def compute_staleness_flags(study: Study) -> dict[str, bool]:
    """Return a mapping of phase labels to staleness booleans.

    A downstream phase is stale when an upstream edit post-dates its last
    execution timestamp (FR-008a invalidation rules).

    Rules:
    - ``"search"`` (phase 3 input) is stale when PICO was re-saved after the
      last search ran: ``pico_saved_at > search_run_at``.
    - ``"extraction"`` (phase 4/5 input) is stale when a new search ran after
      extraction started: ``search_run_at > extraction_started_at``.

    Args:
        study: The :class:`Study` ORM object with phase timestamp fields.

    Returns:
        Dict with keys ``"search"`` and ``"extraction"`` mapping to ``bool``.

    """
    search_stale = bool(
        study.pico_saved_at is not None
        and study.search_run_at is not None
        and study.pico_saved_at > study.search_run_at
    )
    extraction_stale = bool(
        study.search_run_at is not None
        and study.extraction_started_at is not None
        and study.search_run_at > study.extraction_started_at
    )
    return {"search": search_stale, "extraction": extraction_stale}


async def compute_current_phase(study_id: int, db: AsyncSession) -> int:
    """Return the highest unlocked phase for *study_id*.

    Args:
        study_id: The study to evaluate.
        db: Async database session.

    Returns:
        The current phase number (1–5).

    """
    unlocked = await get_unlocked_phases(study_id, db)
    return max(unlocked)
