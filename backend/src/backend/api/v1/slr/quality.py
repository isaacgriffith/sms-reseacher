"""SLR quality assessment endpoints (feature 007).

Routes:
- GET  /slr/studies/{study_id}/quality-checklist          → 200 | 404
- PUT  /slr/studies/{study_id}/quality-checklist          → 200
- GET  /slr/papers/{candidate_paper_id}/quality-scores    → 200
- PUT  /slr/papers/{candidate_paper_id}/quality-scores    → 200 | 409
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services import quality_assessment_service

router = APIRouter(tags=["slr-quality"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class ChecklistItemResponse(BaseModel):
    """Single quality checklist item in a response."""

    id: int
    order: int
    question: str
    scoring_method: str
    weight: float

    model_config = {"from_attributes": True}


class ChecklistResponse(BaseModel):
    """Full quality assessment checklist response body."""

    id: int
    study_id: int
    name: str
    description: str | None
    items: list[ChecklistItemResponse]

    model_config = {"from_attributes": True}


class ChecklistItemInput(BaseModel):
    """A single checklist item in a PUT request."""

    order: int
    question: str
    scoring_method: str
    weight: float = 1.0


class ChecklistUpsertRequest(BaseModel):
    """Request body for PUT /quality-checklist."""

    name: str
    description: str | None = None
    items: list[ChecklistItemInput]


class ScoreItemResponse(BaseModel):
    """A single score in a response."""

    checklist_item_id: int
    score_value: float
    notes: str | None

    model_config = {"from_attributes": True}


class ReviewerScoresResponse(BaseModel):
    """All scores from one reviewer for a paper, with aggregate."""

    reviewer_id: int
    items: list[ScoreItemResponse]
    aggregate_quality_score: float


class PaperScoresResponse(BaseModel):
    """All reviewer scores for a single candidate paper."""

    candidate_paper_id: int
    reviewer_scores: list[ReviewerScoresResponse]


class ScoreItemInput(BaseModel):
    """A single score in a PUT request."""

    checklist_item_id: int
    score_value: float
    notes: str | None = None


class SubmitScoresRequest(BaseModel):
    """Request body for PUT /quality-scores."""

    reviewer_id: int
    scores: list[ScoreItemInput]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/quality-checklist",
    response_model=ChecklistResponse,
    summary="Get quality assessment checklist for an SLR study",
)
async def get_quality_checklist(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChecklistResponse:
    """Return the quality assessment checklist for an SLR study.

    Args:
        study_id: The study whose checklist to retrieve.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        The :class:`ChecklistResponse` for the study's checklist.

    Raises:
        HTTPException: 404 if no checklist exists for this study.

    """
    checklist = await quality_assessment_service.get_checklist(study_id, db)
    if checklist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No quality assessment checklist found for this study.",
        )
    return ChecklistResponse.model_validate(checklist)


@router.put(
    "/studies/{study_id}/quality-checklist",
    response_model=ChecklistResponse,
    summary="Create or replace quality assessment checklist for an SLR study",
)
async def upsert_quality_checklist(
    study_id: int,
    body: ChecklistUpsertRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChecklistResponse:
    """Create or fully replace the quality assessment checklist for an SLR study.

    All existing items are deleted and replaced with the items provided in the
    request body.

    Args:
        study_id: The study to create or update the checklist for.
        body: Checklist name, description, and item definitions.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        The updated :class:`ChecklistResponse`.

    """
    data = body.model_dump()
    checklist = await quality_assessment_service.upsert_checklist(study_id, data, db)
    return ChecklistResponse.model_validate(checklist)


@router.get(
    "/papers/{candidate_paper_id}/quality-scores",
    response_model=PaperScoresResponse,
    summary="Get all quality assessment scores for a candidate paper",
)
async def get_quality_scores(
    candidate_paper_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaperScoresResponse:
    """Return all reviewer quality scores for a candidate paper.

    For each reviewer that has submitted scores, computes the weighted
    aggregate quality score using the study's checklist.

    Args:
        candidate_paper_id: The candidate paper whose scores to retrieve.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        :class:`PaperScoresResponse` with per-reviewer scores and aggregates.

    """
    scores_by_reviewer = await quality_assessment_service.get_scores(candidate_paper_id, db)

    reviewer_scores: list[ReviewerScoresResponse] = []
    for reviewer_id, score_list in scores_by_reviewer.items():
        # Determine the study_id via CandidatePaper to fetch the checklist
        from db.models.candidate import CandidatePaper
        from sqlalchemy import select

        cp_result = await db.execute(
            select(CandidatePaper.study_id).where(CandidatePaper.id == candidate_paper_id)
        )
        cp_row = cp_result.one_or_none()
        checklist_items = []
        if cp_row is not None:
            checklist = await quality_assessment_service.get_checklist(cp_row[0], db)
            if checklist is not None:
                checklist_items = checklist.items

        aggregate = quality_assessment_service.compute_aggregate_score(score_list, checklist_items)
        reviewer_scores.append(
            ReviewerScoresResponse(
                reviewer_id=reviewer_id,
                items=[ScoreItemResponse.model_validate(s) for s in score_list],
                aggregate_quality_score=aggregate,
            )
        )

    return PaperScoresResponse(
        candidate_paper_id=candidate_paper_id,
        reviewer_scores=reviewer_scores,
    )


@router.put(
    "/papers/{candidate_paper_id}/quality-scores",
    response_model=PaperScoresResponse,
    summary="Submit or update quality assessment scores for a candidate paper",
)
async def submit_quality_scores(
    candidate_paper_id: int,
    body: SubmitScoresRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaperScoresResponse:
    """Submit or update a reviewer's quality assessment scores for a paper.

    Upserts scores for the given reviewer and returns the full
    :class:`PaperScoresResponse` including any other reviewers' scores.

    Args:
        candidate_paper_id: The paper being scored.
        body: Reviewer ID and list of scored checklist items.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        :class:`PaperScoresResponse` with all reviewer scores and aggregates.

    Raises:
        HTTPException: 409 on optimistic lock conflict.

    """
    try:
        await quality_assessment_service.submit_scores(
            candidate_paper_id=candidate_paper_id,
            reviewer_id=body.reviewer_id,
            scores=[s.model_dump() for s in body.scores],
            db=db,
        )
    except Exception as exc:
        if "StaleDataError" in type(exc).__name__ or "conflict" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Score was modified concurrently. Please reload and retry.",
            ) from exc
        raise

    return await get_quality_scores(candidate_paper_id, current_user=current_user, db=db)
