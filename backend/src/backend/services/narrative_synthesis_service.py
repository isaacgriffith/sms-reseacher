"""Service layer for Rapid Review narrative synthesis sections (feature 008).

Provides auto-creation of synthesis sections from protocol research questions,
section updates, and synthesis completion gating.
"""

from __future__ import annotations

import structlog
from db.models.rapid_review import RRNarrativeSynthesisSection, RRProtocolStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services import rr_protocol_service

logger = structlog.get_logger(__name__)


async def get_or_create_sections(
    study_id: int,
    db: AsyncSession,
) -> list[RRNarrativeSynthesisSection]:
    """Return narrative synthesis sections for a study, creating missing ones.

    One section is created per entry in the validated protocol's
    ``research_questions`` list.  Sections are keyed by ``rq_index`` so
    re-running this function on an already-populated study is safe.

    If the protocol is not yet validated or has no research questions, returns
    whatever sections already exist (may be empty).

    Args:
        study_id: The Rapid Review study to fetch/create sections for.
        db: Active async database session.

    Returns:
        List of :class:`RRNarrativeSynthesisSection` records ordered by
        ``rq_index``.

    """
    bound = logger.bind(study_id=study_id)

    protocol = await rr_protocol_service.get_or_create_protocol(study_id, db)
    if protocol.status != RRProtocolStatus.VALIDATED:
        bound.debug("get_or_create_sections: protocol not validated, returning existing")
        return await _fetch_sections(study_id, db)

    rqs: list[str] = protocol.research_questions or []

    existing_result = await db.execute(
        select(RRNarrativeSynthesisSection)
        .where(RRNarrativeSynthesisSection.study_id == study_id)
        .order_by(RRNarrativeSynthesisSection.rq_index)
    )
    existing: list[RRNarrativeSynthesisSection] = list(existing_result.scalars().all())
    existing_indices = {s.rq_index for s in existing}

    created = 0
    for idx in range(len(rqs)):
        if idx not in existing_indices:
            section = RRNarrativeSynthesisSection(
                study_id=study_id,
                rq_index=idx,
            )
            db.add(section)
            created += 1

    if created:
        await db.flush()
        bound.info("narrative_sections_created", count=created)

    return await _fetch_sections(study_id, db)


async def update_section(
    section_id: int,
    narrative_text: str | None,
    is_complete: bool | None,
    db: AsyncSession,
) -> RRNarrativeSynthesisSection | None:
    """Update narrative text and/or completion flag on a synthesis section.

    Only the fields provided (non-``None``) are updated.

    Args:
        section_id: Primary key of the section to update.
        narrative_text: New researcher-authored narrative, or ``None`` to leave
            unchanged.
        is_complete: New completion flag, or ``None`` to leave unchanged.
        db: Active async database session.

    Returns:
        The updated :class:`RRNarrativeSynthesisSection`, or ``None`` if not
        found.

    """
    result = await db.execute(
        select(RRNarrativeSynthesisSection).where(RRNarrativeSynthesisSection.id == section_id)
    )
    section = result.scalar_one_or_none()
    if section is None:
        return None

    if narrative_text is not None:
        section.narrative_text = narrative_text
    if is_complete is not None:
        section.is_complete = is_complete

    await db.flush()
    logger.info(
        "narrative_section_updated",
        section_id=section_id,
        is_complete=section.is_complete,
    )
    return section


async def is_synthesis_complete(study_id: int, db: AsyncSession) -> bool:
    """Return ``True`` if all synthesis sections are marked complete.

    An empty section list (no sections exist) is treated as incomplete.

    Args:
        study_id: The Rapid Review study to check.
        db: Active async database session.

    Returns:
        ``True`` if every section has ``is_complete = True`` and at least one
        section exists; ``False`` otherwise.

    """
    sections = await _fetch_sections(study_id, db)
    if not sections:
        return False
    return all(s.is_complete for s in sections)


async def _fetch_sections(
    study_id: int,
    db: AsyncSession,
) -> list[RRNarrativeSynthesisSection]:
    """Fetch all synthesis sections for a study ordered by rq_index.

    Args:
        study_id: The Rapid Review study to query.
        db: Active async database session.

    Returns:
        List of :class:`RRNarrativeSynthesisSection` records.

    """
    result = await db.execute(
        select(RRNarrativeSynthesisSection)
        .where(RRNarrativeSynthesisSection.study_id == study_id)
        .order_by(RRNarrativeSynthesisSection.rq_index)
    )
    return list(result.scalars().all())
