"""Inter-rater agreement service for SLR workflow (feature 007).

Provides Cohen's Kappa computation between two reviewers for a screening
round, and retrieval of all agreement records for a study.

Business rules:
- Both reviewers must have a decision for every paper in the round before
  Kappa can be computed (raises HTTP 422 if incomplete).
- The latest ``PaperDecision`` per (reviewer, paper) pair is used.
- ``kappa_value`` is ``None`` when the score is undefined (zero-variance
  decisions); ``kappa_undefined_reason`` explains why.
- ``threshold_met`` is ``False`` when kappa is ``None``.
"""

from __future__ import annotations

import structlog
from db.models.candidate import CandidatePaper, PaperDecision
from db.models.slr import AgreementRoundType, InterRaterAgreementRecord
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_settings
from backend.services.statistics import safe_cohen_kappa

logger = structlog.get_logger(__name__)


async def get_records(
    study_id: int,
    db: AsyncSession,
) -> list[InterRaterAgreementRecord]:
    """Fetch all inter-rater agreement records for a study.

    Args:
        study_id: The study whose records to retrieve.
        db: Active async database session.

    Returns:
        All :class:`InterRaterAgreementRecord` rows ordered by
        creation time (oldest first).

    """
    result = await db.execute(
        select(InterRaterAgreementRecord)
        .where(InterRaterAgreementRecord.study_id == study_id)
        .order_by(InterRaterAgreementRecord.created_at)
    )
    return list(result.scalars().all())


async def compute_and_store_kappa(
    study_id: int,
    reviewer_a_id: int,
    reviewer_b_id: int,
    round_type: AgreementRoundType,
    phase: str,
    db: AsyncSession,
) -> InterRaterAgreementRecord:
    """Compute Cohen's Kappa and persist an :class:`InterRaterAgreementRecord`.

    Retrieves all ``CandidatePaper`` rows for the study tagged with
    ``round_type``, then aligns the latest decision from each reviewer.
    Raises HTTP 422 if either reviewer has not assessed all papers in the
    round.

    Args:
        study_id: The study the reviewers belong to.
        reviewer_a_id: FK to ``reviewer.id`` for the first reviewer.
        reviewer_b_id: FK to ``reviewer.id`` for the second reviewer.
        round_type: Screening round (maps to ``CandidatePaper.phase_tag``).
        phase: ``"pre_discussion"`` or ``"post_discussion"``.
        db: Active async database session.

    Returns:
        The persisted :class:`InterRaterAgreementRecord`.

    Raises:
        HTTPException: 422 if no papers exist for the round.
        HTTPException: 422 if either reviewer has incomplete assessments.

    """
    bound = logger.bind(
        study_id=study_id,
        round_type=round_type,
        phase=phase,
        reviewer_a_id=reviewer_a_id,
        reviewer_b_id=reviewer_b_id,
    )

    # Fetch all candidate paper IDs for this round
    papers_result = await db.execute(
        select(CandidatePaper.id).where(
            CandidatePaper.study_id == study_id,
            CandidatePaper.phase_tag == round_type.value,
        )
    )
    paper_ids: list[int] = [row[0] for row in papers_result.all()]

    if not paper_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"No papers found for round '{round_type.value}' in study {study_id}.",
        )

    # Get the latest decision per paper for each reviewer
    decisions_a = await _get_latest_decisions(paper_ids, reviewer_a_id, db)
    decisions_b = await _get_latest_decisions(paper_ids, reviewer_b_id, db)

    # Check completion: every paper must have a decision from both reviewers
    missing_a = [pid for pid in paper_ids if pid not in decisions_a]
    missing_b = [pid for pid in paper_ids if pid not in decisions_b]

    if missing_a or missing_b:
        missing_parts = []
        if missing_a:
            missing_parts.append(
                f"Reviewer {reviewer_a_id} is missing {len(missing_a)} decision(s)"
            )
        if missing_b:
            missing_parts.append(
                f"Reviewer {reviewer_b_id} is missing {len(missing_b)} decision(s)"
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "One or both reviewers have not completed their independent "
                f"assessments for the round. {'; '.join(missing_parts)}."
            ),
        )

    # Align decisions in paper_id order for reproducible kappa
    aligned_a = [decisions_a[pid] for pid in paper_ids]
    aligned_b = [decisions_b[pid] for pid in paper_ids]

    kappa = safe_cohen_kappa(aligned_a, aligned_b)
    kappa_undefined_reason: str | None = None
    if kappa is None:
        kappa_undefined_reason = (
            "Zero-variance decisions: at least one reviewer gave the same "
            "decision to every paper, making Kappa undefined."
        )

    settings = get_settings()
    threshold_met = kappa is not None and kappa >= settings.slr_kappa_threshold

    record = InterRaterAgreementRecord(
        study_id=study_id,
        reviewer_a_id=reviewer_a_id,
        reviewer_b_id=reviewer_b_id,
        round_type=round_type,
        phase=phase,
        kappa_value=kappa,
        kappa_undefined_reason=kappa_undefined_reason,
        n_papers=len(paper_ids),
        threshold_met=threshold_met,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    bound.info(
        "compute_and_store_kappa: stored",
        kappa=kappa,
        n_papers=len(paper_ids),
        threshold_met=threshold_met,
    )
    return record


async def _get_latest_decisions(
    paper_ids: list[int],
    reviewer_id: int,
    db: AsyncSession,
) -> dict[int, str]:
    """Return the latest decision value per paper for a reviewer.

    When a reviewer has overridden a decision, the latest (most recently
    created) row takes precedence.

    Args:
        paper_ids: Candidate paper IDs to query.
        reviewer_id: The reviewer whose decisions to fetch.
        db: Active async database session.

    Returns:
        Mapping of ``{candidate_paper_id: decision_string}``.

    """
    result = await db.execute(
        select(
            PaperDecision.candidate_paper_id,
            PaperDecision.decision,
            PaperDecision.created_at,
        )
        .where(
            PaperDecision.candidate_paper_id.in_(paper_ids),
            PaperDecision.reviewer_id == reviewer_id,
        )
        .order_by(PaperDecision.created_at)
    )
    decisions: dict[int, str] = {}
    for paper_id, decision, _ in result.all():
        # Later rows overwrite earlier ones (latest wins)
        decisions[paper_id] = decision.value if hasattr(decision, "value") else str(decision)
    return decisions
