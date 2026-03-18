"""Candidate paper list and detail endpoints."""

from db.models import Paper
from db.models.audit import AuditAction
from db.models.candidate import CandidatePaper
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services import audit as audit_svc

router = APIRouter(tags=["papers"])
logger = get_logger(__name__)


class PaperResponse(BaseModel):
    """Paper metadata."""

    id: int
    title: str
    abstract: str | None
    doi: str | None
    authors: list | None
    year: int | None
    venue: str | None
    source_url: str | None


class CandidatePaperResponse(BaseModel):
    """Candidate paper with decision status."""

    id: int
    study_id: int
    paper_id: int
    phase_tag: str
    current_status: str
    duplicate_of_id: int | None
    conflict_flag: bool = False
    paper: PaperResponse


@router.get(
    "/studies/{study_id}/papers",
    response_model=list[CandidatePaperResponse],
    summary="List candidate papers for a study",
)
async def list_candidate_papers(
    study_id: int,
    paper_status: str | None = Query(None, alias="status"),
    phase_tag: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CandidatePaperResponse]:
    """Return paginated candidate papers, optionally filtered by status and phase."""
    await require_study_member(study_id, current_user, db)

    query = select(CandidatePaper).where(CandidatePaper.study_id == study_id)

    if paper_status:
        query = query.where(CandidatePaper.current_status == paper_status)
    if phase_tag:
        query = query.where(CandidatePaper.phase_tag == phase_tag)

    query = query.order_by(CandidatePaper.id).offset(offset).limit(limit)
    result = await db.execute(query)
    candidates = result.scalars().all()

    responses = []
    for cp in candidates:
        paper_result = await db.execute(select(Paper).where(Paper.id == cp.paper_id))
        paper = paper_result.scalar_one_or_none()
        if paper is None:
            continue
        responses.append(
            CandidatePaperResponse(
                id=cp.id,
                study_id=cp.study_id,
                paper_id=cp.paper_id,
                phase_tag=cp.phase_tag,
                current_status=cp.current_status.value,
                duplicate_of_id=cp.duplicate_of_id,
                conflict_flag=cp.conflict_flag,
                paper=PaperResponse(
                    id=paper.id,
                    title=paper.title,
                    abstract=paper.abstract,
                    doi=paper.doi,
                    authors=paper.authors,
                    year=paper.year,
                    venue=paper.venue,
                    source_url=paper.source_url,
                ),
            )
        )
    return responses


@router.get(
    "/studies/{study_id}/papers/{candidate_id}",
    response_model=CandidatePaperResponse,
    summary="Get a specific candidate paper",
)
async def get_candidate_paper(
    study_id: int,
    candidate_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CandidatePaperResponse:
    """Return a single candidate paper with its metadata."""
    await require_study_member(study_id, current_user, db)

    cp_result = await db.execute(
        select(CandidatePaper).where(
            CandidatePaper.id == candidate_id,
            CandidatePaper.study_id == study_id,
        )
    )
    cp = cp_result.scalar_one_or_none()
    if cp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate paper not found"
        )

    paper_result = await db.execute(select(Paper).where(Paper.id == cp.paper_id))
    paper = paper_result.scalar_one_or_none()
    if paper is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")

    return CandidatePaperResponse(
        id=cp.id,
        study_id=cp.study_id,
        paper_id=cp.paper_id,
        phase_tag=cp.phase_tag,
        current_status=cp.current_status.value,
        duplicate_of_id=cp.duplicate_of_id,
        conflict_flag=cp.conflict_flag,
        paper=PaperResponse(
            id=paper.id,
            title=paper.title,
            abstract=paper.abstract,
            doi=paper.doi,
            authors=paper.authors,
            year=paper.year,
            venue=paper.venue,
            source_url=paper.source_url,
        ),
    )


# ---------------------------------------------------------------------------
# Schemas for decisions
# ---------------------------------------------------------------------------


class DecisionRequest(BaseModel):
    """Body for POST /studies/{study_id}/papers/{candidate_id}/decisions."""

    reviewer_id: int
    decision: str  # "accepted", "rejected", "duplicate"
    reasons: list[dict] = []
    overrides_decision_id: int | None = None


class DecisionResponse(BaseModel):
    """Response for a paper decision."""

    id: int
    candidate_paper_id: int
    reviewer_id: int
    decision: str
    reasons: list | None
    is_override: bool
    overrides_decision_id: int | None
    decided_at: str | None = None


class ResolveConflictRequest(BaseModel):
    """Body for POST resolve-conflict."""

    reviewer_id: int
    decision: str
    reasons: list[dict] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _load_candidate(study_id: int, candidate_id: int, db: AsyncSession) -> CandidatePaper:
    """Load a CandidatePaper or raise 404."""
    from db.models.candidate import CandidatePaper as CP

    result = await db.execute(select(CP).where(CP.id == candidate_id, CP.study_id == study_id))
    cp = result.scalar_one_or_none()
    if cp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate paper not found"
        )
    return cp


async def _require_reviewer_in_study(reviewer_id: int, study_id: int, db: AsyncSession) -> None:
    """Verify reviewer belongs to study, raise 422 if not."""
    from db.models.study import Reviewer

    result = await db.execute(
        select(Reviewer).where(Reviewer.id == reviewer_id, Reviewer.study_id == study_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Reviewer does not belong to this study",
        )


def _detect_conflict(decisions: list) -> bool:
    """Return True when multiple human reviewers have disagreeing decisions."""
    from db.models.study import ReviewerType

    human_decisions = [d for d in decisions if d._reviewer_type == ReviewerType.HUMAN]
    if len(human_decisions) < 2:
        return False
    unique = {d.decision for d in human_decisions}
    return len(unique) > 1


# ---------------------------------------------------------------------------
# T076: POST decision
# ---------------------------------------------------------------------------


@router.post(
    "/studies/{study_id}/papers/{candidate_id}/decisions",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a decision for a candidate paper",
)
async def submit_decision(
    study_id: int,
    candidate_id: int,
    body: DecisionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DecisionResponse:
    """Create a PaperDecision, update CandidatePaper status, and flag conflicts.

    - Validates reviewer_id belongs to the study.
    - Sets is_override=True when overrides_decision_id is provided.
    - After saving, checks all human-reviewer decisions for disagreement;
      if found, sets conflict_flag=True on the CandidatePaper.
    - Updates CandidatePaper.current_status to the new decision.
    """
    await require_study_member(study_id, current_user, db)
    await _require_reviewer_in_study(body.reviewer_id, study_id, db)

    cp = await _load_candidate(study_id, candidate_id, db)

    from db.models.candidate import CandidatePaperStatus, PaperDecision, PaperDecisionType
    from db.models.study import Reviewer, ReviewerType

    try:
        decision_enum = PaperDecisionType(body.decision)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid decision value: {body.decision!r}",
        ) from exc

    is_override = body.overrides_decision_id is not None
    pd = PaperDecision(
        candidate_paper_id=candidate_id,
        reviewer_id=body.reviewer_id,
        decision=decision_enum,
        reasons=body.reasons or None,
        is_override=is_override,
        overrides_decision_id=body.overrides_decision_id,
    )
    db.add(pd)
    await db.flush()

    # Update candidate status
    cp.current_status = CandidatePaperStatus(body.decision)

    # Conflict detection: fetch all decisions + reviewer types for this candidate
    decisions_result = await db.execute(
        select(PaperDecision, Reviewer)
        .join(Reviewer, PaperDecision.reviewer_id == Reviewer.id)
        .where(PaperDecision.candidate_paper_id == candidate_id)
    )
    rows = decisions_result.all()
    human_decisions = [d for d, r in rows if r.reviewer_type == ReviewerType.HUMAN]
    if len(human_decisions) >= 2:
        unique_decisions = {d.decision for d in human_decisions}
        cp.conflict_flag = len(unique_decisions) > 1
    else:
        cp.conflict_flag = False

    await audit_svc.record(
        db,
        study_id=study_id,
        actor_user_id=current_user.user_id,
        actor_agent=None,
        entity_type="PaperDecision",
        entity_id=pd.id,
        action=AuditAction.CREATE,
        after_value={
            "candidate_paper_id": candidate_id,
            "decision": body.decision,
            "reviewer_id": body.reviewer_id,
        },
    )
    await db.commit()

    return DecisionResponse(
        id=pd.id,
        candidate_paper_id=pd.candidate_paper_id,
        reviewer_id=pd.reviewer_id,
        decision=pd.decision.value,
        reasons=pd.reasons,
        is_override=pd.is_override,
        overrides_decision_id=pd.overrides_decision_id,
        decided_at=pd.created_at.isoformat() if pd.created_at else None,
    )


# ---------------------------------------------------------------------------
# T077: POST resolve-conflict
# ---------------------------------------------------------------------------


@router.post(
    "/studies/{study_id}/papers/{candidate_id}/resolve-conflict",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Resolve a reviewer conflict with a binding decision",
)
async def resolve_conflict(
    study_id: int,
    candidate_id: int,
    body: ResolveConflictRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DecisionResponse:
    """Submit a binding resolution decision and clear the conflict flag.

    Creates a new PaperDecision marked as an override, sets
    CandidatePaper.current_status to the resolved decision, and
    clears conflict_flag.
    """
    await require_study_member(study_id, current_user, db)
    await _require_reviewer_in_study(body.reviewer_id, study_id, db)

    cp = await _load_candidate(study_id, candidate_id, db)

    if not cp.conflict_flag:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No active conflict to resolve on this paper",
        )

    from db.models.candidate import CandidatePaperStatus, PaperDecision, PaperDecisionType

    try:
        decision_enum = PaperDecisionType(body.decision)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid decision value: {body.decision!r}",
        ) from exc

    pd = PaperDecision(
        candidate_paper_id=candidate_id,
        reviewer_id=body.reviewer_id,
        decision=decision_enum,
        reasons=body.reasons or None,
        is_override=True,
    )
    db.add(pd)

    cp.current_status = CandidatePaperStatus(body.decision)
    cp.conflict_flag = False

    await db.flush()
    await audit_svc.record(
        db,
        study_id=study_id,
        actor_user_id=current_user.user_id,
        actor_agent=None,
        entity_type="PaperDecision",
        entity_id=pd.id,
        action=AuditAction.CREATE,
        after_value={
            "candidate_paper_id": candidate_id,
            "decision": body.decision,
            "is_override": True,
            "conflict_resolved": True,
        },
    )
    await db.commit()

    return DecisionResponse(
        id=pd.id,
        candidate_paper_id=pd.candidate_paper_id,
        reviewer_id=pd.reviewer_id,
        decision=pd.decision.value,
        reasons=pd.reasons,
        is_override=pd.is_override,
        overrides_decision_id=None,
        decided_at=pd.created_at.isoformat() if pd.created_at else None,
    )


# ---------------------------------------------------------------------------
# GET decisions history
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/papers/{candidate_id}/decisions",
    response_model=list[DecisionResponse],
    summary="List all decisions for a candidate paper",
)
async def list_decisions(
    study_id: int,
    candidate_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DecisionResponse]:
    """Return the full decision audit trail for a candidate paper."""
    await require_study_member(study_id, current_user, db)
    await _load_candidate(study_id, candidate_id, db)

    from db.models.candidate import PaperDecision

    result = await db.execute(
        select(PaperDecision)
        .where(PaperDecision.candidate_paper_id == candidate_id)
        .order_by(PaperDecision.created_at)
    )
    decisions = result.scalars().all()
    return [
        DecisionResponse(
            id=d.id,
            candidate_paper_id=d.candidate_paper_id,
            reviewer_id=d.reviewer_id,
            decision=d.decision.value,
            reasons=d.reasons,
            is_override=bool(d.is_override),
            overrides_decision_id=d.overrides_decision_id,
            decided_at=d.created_at.isoformat() if not d.created_at else None,
        )
        for d in decisions
    ]
