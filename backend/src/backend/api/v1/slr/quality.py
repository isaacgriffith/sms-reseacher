"""SLR quality assessment endpoints (feature 007).

Routes:
- GET  /slr/studies/{study_id}/quality-checklist          → 200 | 403 | 404
- PUT  /slr/studies/{study_id}/quality-checklist          → 200 | 403
- GET  /slr/papers/{candidate_paper_id}/quality-scores    → 200 | 403 | 404
- PUT  /slr/papers/{candidate_paper_id}/quality-scores    → 200 | 403 | 404 | 409
"""

from __future__ import annotations

from db.models.candidate import CandidatePaper
from db.models.study import Reviewer, ReviewerType
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# `resolve_session_reviewer` is reused rather than re-implemented here: TFIX4
# already solved "resolve the caller's own human Reviewer row for a study,
# creating it on demand" for screening decisions, and that is exactly what
# submitting a quality score needs (TFIX5, part 1). It stays defined in
# papers.py rather than moving to a shared module — the move buys nothing
# while there are two callers, and papers.py is where the contract is
# documented.
#
# It lost its leading underscore when this import was added: an underscore
# claims module-private, and a symbol imported across modules is not. TREF10
# renamed `_ensure_*` to `ensure_*` in `scripts/seed_helpers.py` for the same
# reason and in the same feature.
from backend.api.v1.papers import resolve_session_reviewer
from backend.core.auth import CurrentUser, get_current_user, require_study_member
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
    viewer_reviewer_id: int | None = None


class ScoreItemInput(BaseModel):
    """A single score in a PUT request."""

    checklist_item_id: int
    score_value: float
    notes: str | None = None


class SubmitScoresRequest(BaseModel):
    """Request body for PUT /quality-scores.

    No longer carries ``reviewer_id``: who is scoring is a property of who
    is asking (the session-authenticated caller), not a value the client
    supplies — see ``resolve_session_reviewer``. A client that still sends
    ``reviewer_id`` (e.g. an old frontend build) is not rejected; pydantic's
    default "ignore extra fields" behaviour just drops it, and the field is
    resolved from the session regardless of what the caller sent.
    """

    scores: list[ScoreItemInput]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _resolve_study_for_paper(candidate_paper_id: int, db: AsyncSession) -> int:
    """Return the study_id owning *candidate_paper_id*, or raise 404.

    The paper-keyed quality routes only ever receive a candidate_paper_id,
    but a membership check (and checklist lookup) needs the owning study_id
    — this resolves it once so both can share the result.

    Args:
        candidate_paper_id: The candidate paper to look up.
        db: Active async session.

    Returns:
        The owning study's id.

    Raises:
        HTTPException: 404 if no such candidate paper exists.

    """
    result = await db.execute(
        select(CandidatePaper.study_id).where(CandidatePaper.id == candidate_paper_id)
    )
    study_id = result.scalar_one_or_none()
    if study_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate paper not found.",
        )
    return study_id


async def _lookup_viewer_reviewer_id(
    study_id: int, current_user: CurrentUser, db: AsyncSession
) -> int | None:
    """Look up, but never create, the caller's own human Reviewer id.

    Unlike ``resolve_session_reviewer``, this backs a GET: a read must not
    have the side effect of creating a Reviewer row, so a caller who has
    never scored anything simply gets ``None`` back.

    Args:
        study_id: The study to look the reviewer up in.
        current_user: The authenticated caller.
        db: Active async session.

    Returns:
        The caller's Reviewer id, or ``None`` if no such row exists.

    """
    result = await db.execute(
        select(Reviewer.id).where(
            Reviewer.study_id == study_id,
            Reviewer.user_id == current_user.user_id,
            Reviewer.reviewer_type == ReviewerType.HUMAN,
        )
    )
    return result.scalar_one_or_none()


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
        HTTPException: 403 if the caller is not a member of the study; 404
            if no checklist exists for this study.

    """
    await require_study_member(study_id, current_user, db)
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

    Raises:
        HTTPException: 403 if the caller is not a member of the study.

    """
    await require_study_member(study_id, current_user, db)
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
        :class:`PaperScoresResponse` with per-reviewer scores, aggregates,
        and the caller's own ``viewer_reviewer_id`` (``None`` if the caller
        has never scored this study).

    Raises:
        HTTPException: 403 if the caller is not a member of the paper's
            study; 404 if no such candidate paper exists.

    """
    study_id = await _resolve_study_for_paper(candidate_paper_id, db)
    await require_study_member(study_id, current_user, db)

    scores_by_reviewer = await quality_assessment_service.get_scores(candidate_paper_id, db)

    checklist = await quality_assessment_service.get_checklist(study_id, db)
    checklist_items = checklist.items if checklist is not None else []

    reviewer_scores: list[ReviewerScoresResponse] = []
    for reviewer_id, score_list in scores_by_reviewer.items():
        aggregate = quality_assessment_service.compute_aggregate_score(score_list, checklist_items)
        reviewer_scores.append(
            ReviewerScoresResponse(
                reviewer_id=reviewer_id,
                items=[ScoreItemResponse.model_validate(s) for s in score_list],
                aggregate_quality_score=aggregate,
            )
        )

    viewer_reviewer_id = await _lookup_viewer_reviewer_id(study_id, current_user, db)

    return PaperScoresResponse(
        candidate_paper_id=candidate_paper_id,
        reviewer_scores=reviewer_scores,
        viewer_reviewer_id=viewer_reviewer_id,
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

    The scoring reviewer is resolved from the caller's own session (creating
    a Reviewer row on demand if this is their first score in the study) —
    any ``reviewer_id`` the client sends is ignored, so a caller cannot
    attribute scores to a different reviewer than themselves.

    Args:
        candidate_paper_id: The paper being scored.
        body: List of scored checklist items.
        current_user: JWT-authenticated user.
        db: Async database session.

    Returns:
        :class:`PaperScoresResponse` with all reviewer scores and aggregates.

    Raises:
        HTTPException: 403 if the caller is not a member of the paper's
            study; 404 if no such candidate paper exists; 409 on optimistic
            lock conflict.

    """
    study_id = await _resolve_study_for_paper(candidate_paper_id, db)
    await require_study_member(study_id, current_user, db)
    reviewer = await resolve_session_reviewer(study_id, current_user, db)

    try:
        await quality_assessment_service.submit_scores(
            candidate_paper_id=candidate_paper_id,
            reviewer_id=reviewer.id,
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
