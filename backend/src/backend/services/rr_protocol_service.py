"""Service layer for Rapid Review protocol lifecycle management (feature 008).

Provides CRUD operations for :class:`RapidReviewProtocol`, protocol
validation, threat auto-creation, and paper invalidation.

Business rules:
- A ``VALIDATED`` protocol that is edited resets to ``DRAFT`` and
  invalidates all collected papers (requires ``acknowledge_invalidation``).
- Validation requires: at least one :class:`PractitionerStakeholder`,
  non-empty ``research_questions``, non-empty ``practical_problem``.
- Threats to validity are auto-created by the service layer; the
  researcher cannot create them directly.
"""

from __future__ import annotations

from typing import Any

import structlog
from db.models import InclusionStatus, Paper, StudyPaper
from db.models.rapid_review import (
    PractitionerStakeholder,
    RapidReviewProtocol,
    RRProtocolStatus,
    RRQualityAppraisalMode,
    RRThreatToValidity,
    RRThreatType,
)
from fastapi import HTTPException, status
from sqlalchemy import func as sqlfunc
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

_RESEARCH_GAP_KEYWORDS: frozenset[str] = frozenset(
    ["gap", "future work", "what is missing", "lack of"]
)


async def get_or_create_protocol(
    study_id: int,
    db: AsyncSession,
) -> RapidReviewProtocol:
    """Return the protocol for a study, creating it if it does not exist.

    Args:
        study_id: The Rapid Review study whose protocol to retrieve or create.
        db: Active async database session.

    Returns:
        The :class:`RapidReviewProtocol` ORM instance.

    """
    result = await db.execute(
        select(RapidReviewProtocol).where(RapidReviewProtocol.study_id == study_id)
    )
    protocol = result.scalar_one_or_none()
    if protocol is None:
        protocol = RapidReviewProtocol(study_id=study_id)
        db.add(protocol)
        await db.flush()
    return protocol


async def update_protocol(
    study_id: int,
    data: dict[str, Any],
    acknowledge_invalidation: bool,
    db: AsyncSession,
) -> RapidReviewProtocol:
    """Update Rapid Review protocol fields.

    If the protocol is currently ``VALIDATED``, resets it to ``DRAFT`` and
    invalidates all collected papers.  Requires
    ``acknowledge_invalidation=True``; if omitted raises HTTP 409 with the
    count of at-risk papers.

    Args:
        study_id: The study to update the protocol for.
        data: Dict of protocol field values to apply (all optional).
        acknowledge_invalidation: Whether the caller has confirmed the cascade.
        db: Active async database session.

    Returns:
        The updated :class:`RapidReviewProtocol` instance.

    Raises:
        HTTPException: 409 if the protocol is ``VALIDATED`` and
            ``acknowledge_invalidation`` is ``False``.

    """
    bound = logger.bind(study_id=study_id)
    protocol = await get_or_create_protocol(study_id, db)

    if protocol.status == RRProtocolStatus.VALIDATED and not acknowledge_invalidation:
        paper_count = await _count_study_papers(study_id, db)
        bound.warning("protocol_invalidation_required", papers_at_risk=paper_count)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": (
                    "Protocol is validated. All collected papers will be "
                    "invalidated. Resend with ?acknowledge_invalidation=true "
                    "to confirm."
                ),
                "papers_at_risk": paper_count,
            },
        )

    if protocol.status == RRProtocolStatus.VALIDATED:
        protocol.status = RRProtocolStatus.DRAFT
        await invalidate_papers_for_study(study_id, db)
        bound.info("protocol_reset_to_draft_via_edit")

    _apply_fields(protocol, data)
    await db.flush()
    bound.info("protocol_updated")
    return protocol


async def validate_protocol(
    study_id: int,
    db: AsyncSession,
) -> RapidReviewProtocol:
    """Attempt to validate the Rapid Review protocol.

    Pre-validation checks (all must pass):

    1. At least one :class:`PractitionerStakeholder` exists for this study.
    2. ``research_questions`` is non-empty.
    3. ``practical_problem`` is non-empty.

    On success the protocol status is set to ``VALIDATED`` and
    :func:`_auto_create_threats` is called to record any context-restriction
    threats.

    Args:
        study_id: The study whose protocol to validate.
        db: Active async database session.

    Returns:
        The updated :class:`RapidReviewProtocol` with ``status=VALIDATED``.

    Raises:
        HTTPException: 422 if any pre-validation check fails.

    """
    bound = logger.bind(study_id=study_id)
    protocol = await get_or_create_protocol(study_id, db)

    errors: list[str] = []

    stakeholder_result = await db.execute(
        select(PractitionerStakeholder).where(PractitionerStakeholder.study_id == study_id).limit(1)
    )
    if stakeholder_result.scalar_one_or_none() is None:
        errors.append("At least one practitioner stakeholder must be defined before validation.")

    if not protocol.research_questions:
        errors.append("Research questions must not be empty.")

    if not protocol.practical_problem:
        errors.append("Practical problem must not be empty.")

    if errors:
        bound.warning("protocol_validation_failed", errors=errors)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"detail": "Protocol validation failed", "errors": errors},
        )

    protocol.status = RRProtocolStatus.VALIDATED
    _auto_create_threats(protocol, study_id)
    await db.flush()
    bound.info("protocol_validated")

    # Auto-create narrative synthesis sections for each research question.
    from backend.services import narrative_synthesis_service

    await narrative_synthesis_service.get_or_create_sections(study_id, db)

    return protocol


def detect_research_gap_questions(questions: list[str]) -> list[str]:
    """Return the subset of questions that appear to be research-gap style.

    Uses a keyword heuristic: any question containing "gap", "future work",
    "what is missing", or "lack of" is flagged as potentially unsuitable for
    a practitioner-focused Rapid Review.

    Args:
        questions: List of research question strings to check.

    Returns:
        List of flagged question strings (may be empty).

    """
    return [q for q in questions if any(kw in q.lower() for kw in _RESEARCH_GAP_KEYWORDS)]


async def invalidate_papers_for_study(study_id: int, db: AsyncSession) -> int:
    """Bulk-mark all collected papers for a study as ``PROTOCOL_INVALIDATED``.

    Updates :attr:`StudyPaper.inclusion_status` for every paper linked to
    the study.

    Args:
        study_id: The Rapid Review study whose papers to invalidate.
        db: Active async database session.

    Returns:
        Number of ``StudyPaper`` rows updated.

    """
    cursor = await db.execute(
        update(StudyPaper)
        .where(StudyPaper.study_id == study_id)
        .values(inclusion_status=InclusionStatus.PROTOCOL_INVALIDATED)
        .execution_options(synchronize_session="fetch")
    )
    count: int = cursor.rowcount  # type: ignore[attr-defined]
    logger.info("papers_invalidated", study_id=study_id, count=count)
    return count


async def configure_search_restrictions(
    study_id: int,
    restrictions: list[dict[str, str]],
    db: AsyncSession,
) -> None:
    """Idempotently upsert :class:`RRThreatToValidity` rows for search restrictions.

    Handles the four configurable restriction types: ``YEAR_RANGE``,
    ``LANGUAGE``, ``GEOGRAPHY``, ``STUDY_DESIGN``.  Restrictions no longer
    present in *restrictions* are deleted; existing ones are updated
    in-place; new ones are created.

    Args:
        study_id: The Rapid Review study to configure.
        restrictions: List of ``{"type": str, "source_detail": str}`` dicts.
            Unknown or non-restriction types are silently ignored.
        db: Active async database session.

    """
    _RESTRICTION_TYPES: frozenset[RRThreatType] = frozenset(
        {
            RRThreatType.YEAR_RANGE,
            RRThreatType.LANGUAGE,
            RRThreatType.GEOGRAPHY,
            RRThreatType.STUDY_DESIGN,
        }
    )

    existing_result = await db.execute(
        select(RRThreatToValidity).where(
            RRThreatToValidity.study_id == study_id,
            RRThreatToValidity.threat_type.in_(list(_RESTRICTION_TYPES)),
        )
    )
    existing_map: dict[RRThreatType, RRThreatToValidity] = {
        t.threat_type: t for t in existing_result.scalars().all()
    }

    desired: dict[RRThreatType, str] = {}
    for item in restrictions:
        try:
            t_type = RRThreatType(item.get("type", ""))
        except ValueError:
            continue
        if t_type not in _RESTRICTION_TYPES:
            continue
        desired[t_type] = item.get("source_detail", "")

    for t_type, threat in existing_map.items():
        if t_type not in desired:
            await db.delete(threat)

    for t_type, source_detail in desired.items():
        label = t_type.value.replace("_", " ").title()
        description = f"{label}: {source_detail}" if source_detail else label
        if t_type in existing_map:
            existing_map[t_type].source_detail = source_detail
            existing_map[t_type].description = description
        else:
            db.add(
                RRThreatToValidity(
                    study_id=study_id,
                    threat_type=t_type,
                    description=description,
                    source_detail=source_detail or None,
                )
            )

    await db.flush()
    logger.info("search_restrictions_configured", study_id=study_id, count=len(desired))


async def set_single_reviewer_mode(
    study_id: int,
    enabled: bool,
    db: AsyncSession,
) -> None:
    """Toggle single-reviewer mode and manage the ``SINGLE_REVIEWER`` threat.

    When *enabled* is ``True``, creates a ``SINGLE_REVIEWER``
    :class:`RRThreatToValidity` record if one does not already exist.
    When *enabled* is ``False``, removes the record if present.
    Also updates :attr:`RapidReviewProtocol.single_reviewer_mode`.

    Args:
        study_id: The Rapid Review study to update.
        enabled: Target state of single-reviewer mode.
        db: Active async database session.

    """
    protocol = await get_or_create_protocol(study_id, db)
    protocol.single_reviewer_mode = enabled

    existing_result = await db.execute(
        select(RRThreatToValidity).where(
            RRThreatToValidity.study_id == study_id,
            RRThreatToValidity.threat_type == RRThreatType.SINGLE_REVIEWER,
        )
    )
    threat = existing_result.scalar_one_or_none()

    if enabled and threat is None:
        db.add(
            RRThreatToValidity(
                study_id=study_id,
                threat_type=RRThreatType.SINGLE_REVIEWER,
                description=(
                    "Papers reviewed by a single reviewer without independent verification."
                ),
                source_detail=None,
            )
        )
    elif not enabled and threat is not None:
        await db.delete(threat)

    await db.flush()
    logger.info("single_reviewer_mode_set", study_id=study_id, enabled=enabled)


async def set_quality_appraisal_mode(
    study_id: int,
    mode: RRQualityAppraisalMode,
    db: AsyncSession,
) -> None:
    """Set the quality appraisal mode and manage associated threat entries.

    For ``SKIPPED`` mode, creates a ``QA_SKIPPED`` threat and removes any
    ``QA_SIMPLIFIED`` threat.  For ``PEER_REVIEWED_ONLY``, creates a
    ``QA_SIMPLIFIED`` threat, removes any ``QA_SKIPPED`` threat, and
    bulk-excludes papers whose :attr:`Paper.metadata_` flags them as
    non-peer-reviewed.  For ``FULL``, removes both QA threats.

    Args:
        study_id: The Rapid Review study to configure.
        mode: The target :class:`RRQualityAppraisalMode`.
        db: Active async database session.

    """
    bound = logger.bind(study_id=study_id, mode=mode.value)
    protocol = await get_or_create_protocol(study_id, db)
    protocol.quality_appraisal_mode = mode

    qa_skipped_result = await db.execute(
        select(RRThreatToValidity).where(
            RRThreatToValidity.study_id == study_id,
            RRThreatToValidity.threat_type == RRThreatType.QA_SKIPPED,
        )
    )
    qa_skipped = qa_skipped_result.scalar_one_or_none()

    qa_simplified_result = await db.execute(
        select(RRThreatToValidity).where(
            RRThreatToValidity.study_id == study_id,
            RRThreatToValidity.threat_type == RRThreatType.QA_SIMPLIFIED,
        )
    )
    qa_simplified = qa_simplified_result.scalar_one_or_none()

    if mode == RRQualityAppraisalMode.SKIPPED:
        if qa_skipped is None:
            db.add(
                RRThreatToValidity(
                    study_id=study_id,
                    threat_type=RRThreatType.QA_SKIPPED,
                    description="Quality appraisal was skipped entirely.",
                    source_detail=None,
                )
            )
        if qa_simplified is not None:
            await db.delete(qa_simplified)

    elif mode == RRQualityAppraisalMode.PEER_REVIEWED_ONLY:
        if qa_simplified is None:
            db.add(
                RRThreatToValidity(
                    study_id=study_id,
                    threat_type=RRThreatType.QA_SIMPLIFIED,
                    description=(
                        "Quality appraisal simplified to peer-reviewed venues only. "
                        "Non-peer-reviewed papers have been excluded."
                    ),
                    source_detail=None,
                )
            )
        if qa_skipped is not None:
            await db.delete(qa_skipped)
        await _exclude_non_peer_reviewed_papers(study_id, db)

    else:  # FULL
        if qa_skipped is not None:
            await db.delete(qa_skipped)
        if qa_simplified is not None:
            await db.delete(qa_simplified)

    await db.flush()
    bound.info("quality_appraisal_mode_set")


async def _exclude_non_peer_reviewed_papers(study_id: int, db: AsyncSession) -> int:
    """Bulk-exclude papers whose metadata marks them as non-peer-reviewed.

    Updates :attr:`StudyPaper.inclusion_status` to ``EXCLUDED`` for papers
    linked to *study_id* whose :attr:`Paper.metadata_` contains
    ``{"is_peer_reviewed": false}``.  Papers with no ``is_peer_reviewed``
    key are left unchanged (benefit of the doubt).

    Args:
        study_id: The Rapid Review study to filter.
        db: Active async database session.

    Returns:
        Number of :class:`StudyPaper` rows updated.

    """
    paper_result = await db.execute(
        select(Paper.id).where(Paper.metadata_["is_peer_reviewed"].as_boolean().is_(False))
    )
    non_peer_reviewed_ids = [row[0] for row in paper_result.all()]

    if not non_peer_reviewed_ids:
        logger.info("no_non_peer_reviewed_papers_found", study_id=study_id)
        return 0

    cursor = await db.execute(
        update(StudyPaper)
        .where(
            StudyPaper.study_id == study_id,
            StudyPaper.paper_id.in_(non_peer_reviewed_ids),
        )
        .values(inclusion_status=InclusionStatus.EXCLUDED)
        .execution_options(synchronize_session="fetch")
    )
    count: int = cursor.rowcount  # type: ignore[attr-defined]
    logger.info(
        "non_peer_reviewed_papers_excluded",
        study_id=study_id,
        count=count,
    )
    return count


async def _count_study_papers(study_id: int, db: AsyncSession) -> int:
    """Return the number of :class:`StudyPaper` rows for a study.

    Args:
        study_id: The study to count papers for.
        db: Active async database session.

    Returns:
        Row count.

    """
    result = await db.execute(
        select(sqlfunc.count()).select_from(StudyPaper).where(StudyPaper.study_id == study_id)
    )
    return result.scalar_one()


def _apply_fields(protocol: RapidReviewProtocol, data: dict[str, Any]) -> None:
    """Apply a partial dict of fields to the protocol ORM instance in-place.

    Only allowed field names are applied; unknown keys are silently ignored.

    Args:
        protocol: The protocol to update.
        data: Dict of field name → new value pairs.

    """
    allowed: frozenset[str] = frozenset(
        {
            "practical_problem",
            "research_questions",
            "time_budget_days",
            "effort_budget_hours",
            "context_restrictions",
            "dissemination_medium",
            "problem_scoping_notes",
            "search_strategy_notes",
            "inclusion_criteria",
            "exclusion_criteria",
            "single_source_acknowledged",
        }
    )
    for key, value in data.items():
        if key in allowed:
            setattr(protocol, key, value)


def _auto_create_threats(protocol: RapidReviewProtocol, study_id: int) -> None:
    """Auto-create :class:`RRThreatToValidity` rows for active context restrictions.

    Called during protocol validation.  Creates a ``CONTEXT_RESTRICTION``
    threat entry for each restriction in
    :attr:`RapidReviewProtocol.context_restrictions` that is not already
    recorded.

    Args:
        protocol: The protocol being validated.
        study_id: The study ID for threat records.

    """
    if not protocol.context_restrictions:
        return

    existing_details = {
        t.source_detail
        for t in (protocol.threats or [])
        if t.threat_type == RRThreatType.CONTEXT_RESTRICTION
    }
    for restriction in protocol.context_restrictions:
        detail = restriction.get("type", "")
        if detail not in existing_details:
            desc = restriction.get("description", f"Context restriction: {detail}")
            protocol.threats.append(
                RRThreatToValidity(
                    study_id=study_id,
                    threat_type=RRThreatType.CONTEXT_RESTRICTION,
                    description=desc,
                    source_detail=detail,
                )
            )
