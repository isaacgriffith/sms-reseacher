"""Quality assessment service for SLR workflow (feature 007).

Provides checklist CRUD, score submission with upsert logic, and aggregate
score computation for quality assessment of accepted candidate papers.

Business rules:
- One checklist per study; items are replaced wholesale on upsert.
- Scores are upserted per (candidate_paper_id, reviewer_id, checklist_item_id).
- After score submission, if all reviewers have scored all accepted papers,
  Cohen's Kappa is computed and stored (only when exactly 2 reviewers exist).
- Kappa computation failures do not block score submission.
"""

from __future__ import annotations

import structlog
from db.models.candidate import CandidatePaper, CandidatePaperStatus
from db.models.slr import (
    AgreementRoundType,
    QualityAssessmentChecklist,
    QualityAssessmentScore,
    QualityChecklistItem,
)
from db.models.study import Reviewer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services import inter_rater_service

logger = structlog.get_logger(__name__)


async def get_checklist(
    study_id: int,
    db: AsyncSession,
) -> QualityAssessmentChecklist | None:
    """Fetch the quality assessment checklist for a study.

    Args:
        study_id: The study whose checklist to retrieve.
        db: Active async database session.

    Returns:
        The :class:`QualityAssessmentChecklist` for the study, or ``None`` if
        no checklist has been created yet.

    """
    result = await db.execute(
        select(QualityAssessmentChecklist).where(QualityAssessmentChecklist.study_id == study_id)
    )
    checklist = result.scalar_one_or_none()
    if checklist is not None:
        # Eagerly load items so callers don't need a live session
        await db.refresh(checklist, attribute_names=["items"])
    return checklist


async def upsert_checklist(
    study_id: int,
    data: dict,
    db: AsyncSession,
) -> QualityAssessmentChecklist:
    """Create or fully replace the quality assessment checklist for a study.

    Replaces all existing items via cascade delete + insert on every call so
    the checklist definition is always consistent with ``data``.

    Args:
        study_id: The study to create or update the checklist for.
        data: Dict with keys ``name``, ``description`` (optional), and
            ``items`` (list of dicts with ``order``, ``question``,
            ``scoring_method``, ``weight``).
        db: Active async database session.

    Returns:
        The persisted :class:`QualityAssessmentChecklist` with all items.

    """
    bound = logger.bind(study_id=study_id)

    result = await db.execute(
        select(QualityAssessmentChecklist).where(QualityAssessmentChecklist.study_id == study_id)
    )
    checklist = result.scalar_one_or_none()

    if checklist is None:
        checklist = QualityAssessmentChecklist(
            study_id=study_id,
            name=data["name"],
            description=data.get("description"),
        )
        db.add(checklist)
        await db.flush()
        bound.info("upsert_checklist: created", checklist_id=checklist.id)
    else:
        checklist.name = data["name"]
        checklist.description = data.get("description")
        # Delete existing items — cascade="all, delete-orphan" on the
        # relationship handles the DB-level DELETE when we clear the list.
        await db.refresh(checklist, attribute_names=["items"])
        checklist.items.clear()
        await db.flush()
        bound.info("upsert_checklist: replaced items", checklist_id=checklist.id)

    items_data = data.get("items", [])
    for item_data in items_data:
        item = QualityChecklistItem(
            checklist_id=checklist.id,
            order=item_data["order"],
            question=item_data["question"],
            scoring_method=item_data["scoring_method"],
            weight=item_data.get("weight", 1.0),
        )
        db.add(item)

    await db.commit()
    await db.refresh(checklist, attribute_names=["items"])
    return checklist


async def get_scores(
    candidate_paper_id: int,
    db: AsyncSession,
) -> dict[int, list[QualityAssessmentScore]]:
    """Fetch all quality assessment scores for a candidate paper.

    Args:
        candidate_paper_id: The candidate paper whose scores to retrieve.
        db: Active async database session.

    Returns:
        A dict mapping ``reviewer_id`` → list of
        :class:`QualityAssessmentScore` rows.

    """
    result = await db.execute(
        select(QualityAssessmentScore).where(
            QualityAssessmentScore.candidate_paper_id == candidate_paper_id
        )
    )
    rows = list(result.scalars().all())
    scores_by_reviewer: dict[int, list[QualityAssessmentScore]] = {}
    for score in rows:
        scores_by_reviewer.setdefault(score.reviewer_id, []).append(score)
    return scores_by_reviewer


async def submit_scores(
    candidate_paper_id: int,
    reviewer_id: int,
    scores: list[dict],
    db: AsyncSession,
) -> list[QualityAssessmentScore]:
    """Upsert quality assessment scores for one reviewer on one paper.

    For each ``(candidate_paper_id, reviewer_id, checklist_item_id)`` triple,
    updates the existing row or inserts a new one.

    After storing scores, triggers Cohen's Kappa computation if all reviewers
    have scored all accepted papers in the study (only when exactly 2 reviewers
    exist).  Kappa failures are silently logged and do not block the response.

    Args:
        candidate_paper_id: The paper being scored.
        reviewer_id: The reviewer submitting scores.
        scores: List of dicts with keys ``checklist_item_id``, ``score_value``,
            and optional ``notes``.
        db: Active async database session.

    Returns:
        The list of persisted :class:`QualityAssessmentScore` rows.

    """
    bound = logger.bind(candidate_paper_id=candidate_paper_id, reviewer_id=reviewer_id)

    # Fetch existing scores for this (paper, reviewer) pair
    existing_result = await db.execute(
        select(QualityAssessmentScore).where(
            QualityAssessmentScore.candidate_paper_id == candidate_paper_id,
            QualityAssessmentScore.reviewer_id == reviewer_id,
        )
    )
    existing_map: dict[int, QualityAssessmentScore] = {
        s.checklist_item_id: s for s in existing_result.scalars().all()
    }

    upserted: list[QualityAssessmentScore] = []
    for score_data in scores:
        item_id = score_data["checklist_item_id"]
        if item_id in existing_map:
            score = existing_map[item_id]
            score.score_value = score_data["score_value"]
            score.notes = score_data.get("notes")
        else:
            score = QualityAssessmentScore(
                candidate_paper_id=candidate_paper_id,
                reviewer_id=reviewer_id,
                checklist_item_id=item_id,
                score_value=score_data["score_value"],
                notes=score_data.get("notes"),
            )
            db.add(score)
        upserted.append(score)

    await db.commit()
    for score in upserted:
        await db.refresh(score)

    bound.info("submit_scores: stored", n_scores=len(upserted))

    # Trigger kappa if all reviewers have completed all accepted papers
    await _maybe_trigger_kappa(candidate_paper_id, db)

    return upserted


def compute_aggregate_score(
    scores: list[QualityAssessmentScore],
    checklist_items: list[QualityChecklistItem],
) -> float:
    """Compute the weighted average quality score for a single reviewer on one paper.

    Matches scores to checklist items by ``checklist_item_id`` / ``id`` and
    computes ``sum(score * weight) / sum(weight)`` for matched pairs.

    Args:
        scores: The reviewer's :class:`QualityAssessmentScore` rows.
        checklist_items: All :class:`QualityChecklistItem` rows for the checklist.

    Returns:
        Weighted average as a ``float``, or ``0.0`` when no items match.

    """
    item_weights: dict[int, float] = {item.id: item.weight for item in checklist_items}
    score_map: dict[int, float] = {s.checklist_item_id: s.score_value for s in scores}

    total_weight = 0.0
    weighted_sum = 0.0
    for item_id, weight in item_weights.items():
        if item_id in score_map:
            weighted_sum += score_map[item_id] * weight
            total_weight += weight

    if total_weight == 0.0:
        return 0.0
    return weighted_sum / total_weight


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _maybe_trigger_kappa(
    candidate_paper_id: int,
    db: AsyncSession,
) -> None:
    """Check completion and trigger Kappa computation if warranted.

    Only triggers when there are exactly 2 reviewers and both have submitted
    scores for all checklist items across all accepted candidate papers.

    Args:
        candidate_paper_id: The paper that was just scored (used to look up study).
        db: Active async database session.

    """
    # Get the study_id from the candidate paper
    cp_result = await db.execute(
        select(CandidatePaper.study_id).where(CandidatePaper.id == candidate_paper_id)
    )
    row = cp_result.one_or_none()
    if row is None:
        return
    study_id: int = row[0]

    # Get reviewers for this study
    rev_result = await db.execute(select(Reviewer.id).where(Reviewer.study_id == study_id))
    reviewer_ids = [r[0] for r in rev_result.all()]
    if len(reviewer_ids) != 2:
        return

    # Get all accepted candidate papers for this study
    accepted_result = await db.execute(
        select(CandidatePaper.id).where(
            CandidatePaper.study_id == study_id,
            CandidatePaper.current_status == CandidatePaperStatus.ACCEPTED,
        )
    )
    accepted_paper_ids = [r[0] for r in accepted_result.all()]
    if not accepted_paper_ids:
        return

    # Get the checklist to know how many items to expect per paper
    checklist_result = await db.execute(
        select(QualityAssessmentChecklist).where(QualityAssessmentChecklist.study_id == study_id)
    )
    checklist = checklist_result.scalar_one_or_none()
    if checklist is None:
        return
    await db.refresh(checklist, attribute_names=["items"])
    n_items = len(checklist.items)
    if n_items == 0:
        return

    # Check that both reviewers have all scores for all accepted papers
    for rev_id in reviewer_ids:
        score_count_result = await db.execute(
            select(QualityAssessmentScore).where(
                QualityAssessmentScore.reviewer_id == rev_id,
                QualityAssessmentScore.candidate_paper_id.in_(accepted_paper_ids),
            )
        )
        existing_scores = list(score_count_result.scalars().all())
        required = len(accepted_paper_ids) * n_items
        if len(existing_scores) < required:
            return  # This reviewer is not complete yet

    # Both reviewers have all scores — compute kappa
    rev_a, rev_b = reviewer_ids[0], reviewer_ids[1]
    bound = logger.bind(study_id=study_id, reviewer_a_id=rev_a, reviewer_b_id=rev_b)
    try:
        await inter_rater_service.compute_and_store_kappa(
            study_id=study_id,
            reviewer_a_id=rev_a,
            reviewer_b_id=rev_b,
            round_type=AgreementRoundType.QUALITY_ASSESSMENT,
            phase="post_discussion",
            db=db,
        )
        bound.info("_maybe_trigger_kappa: kappa stored")
    except Exception:
        bound.warning("_maybe_trigger_kappa: kappa computation failed", exc_info=True)
