"""Phase-gate unlock logic for systematic mapping studies.

Determines which study phases are accessible based on completion of prior phases.
Phase unlock rules (enforced at service layer, not DB):
  - Phase 1: always accessible
  - Phase 2: pico_components non-empty
  - Phase 3: at least one SearchExecution with status=completed
  - Phase 4 & 5: at least one DataExtraction with status != pending
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.pico import PICOComponent


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
    pico_result = await db.execute(
        select(PICOComponent).where(PICOComponent.study_id == study_id)
    )
    pico = pico_result.scalar_one_or_none()
    if pico is not None:
        unlocked.append(2)
    else:
        return unlocked

    # Phase 3: at least one completed SearchExecution
    # Import here to avoid circular imports at module level
    try:
        from db.models.search_exec import SearchExecution, SearchExecutionStatus  # type: ignore[import]

        search_result = await db.execute(
            select(SearchExecution).where(
                SearchExecution.study_id == study_id,
                SearchExecution.status == SearchExecutionStatus.COMPLETED,
            )
        )
        if search_result.scalar_one_or_none() is not None:
            unlocked.append(3)
        else:
            return unlocked
    except ImportError:
        return unlocked

    # Phases 4 & 5: at least one non-pending DataExtraction
    try:
        from db.models.extraction import DataExtraction, ExtractionStatus  # type: ignore[import]

        extraction_result = await db.execute(
            select(DataExtraction)
            .join(DataExtraction.candidate_paper)
            .where(
                DataExtraction.extraction_status != ExtractionStatus.PENDING,
            )
        )
        if extraction_result.scalar_one_or_none() is not None:
            unlocked.extend([4, 5])
    except ImportError:
        pass

    return unlocked


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
