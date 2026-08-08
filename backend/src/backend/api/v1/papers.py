"""Candidate paper list and detail endpoints."""

from db.models import Paper
from db.models.audit import AuditAction
from db.models.candidate import (
    CandidatePaper,
    CandidatePaperStatus,
    PaperDecision,
    PaperDecisionType,
)
from db.models.study import Reviewer, ReviewerType
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
    # NEW, required (contracts/paper-decisions.md): the CandidatePaper.current_status
    # as the reviewer was shown it, not a duplicate of `decision` — this is the
    # *before*, `decision` is the *after*. Required rather than optional so no
    # client can silently regain the ability FR-025 removes (FR-027).
    observed_status: str
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
    result = await db.execute(
        select(CandidatePaper).where(
            CandidatePaper.id == candidate_id, CandidatePaper.study_id == study_id
        )
    )
    cp = result.scalar_one_or_none()
    if cp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate paper not found"
        )
    return cp


async def _require_reviewer_in_study(reviewer_id: int, study_id: int, db: AsyncSession) -> None:
    """Verify reviewer belongs to study, raise 422 if not."""
    result = await db.execute(
        select(Reviewer).where(Reviewer.id == reviewer_id, Reviewer.study_id == study_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Reviewer does not belong to this study",
        )


def _parse_decision_type(decision: str) -> PaperDecisionType:
    """Parse a decision string into a PaperDecisionType or raise 422.

    Args:
        decision: The raw ``decision`` value from the request body.

    Returns:
        The parsed PaperDecisionType.

    Raises:
        HTTPException: 422 when the value is not one of the three valid
            decisions (accepted, rejected, duplicate).

    """
    try:
        return PaperDecisionType(decision)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid decision value: {decision!r}",
        ) from exc


def _assert_observed_status(cp: CandidatePaper, observed_status: str) -> None:
    """Reject a decision submitted against a stale view of the candidate paper.

    Args:
        cp: The candidate paper being decided on.
        observed_status: The ``current_status`` value the reviewer was shown
            before deciding (``DecisionRequest.observed_status``).

    Raises:
        HTTPException: 409 with a ``stale_state`` detail dict carrying both
            ``observed_status`` and ``current_status`` when they differ, so the
            client can show what changed instead of merely refusing.

    """
    if cp.current_status.value != observed_status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "stale_state",
                "observed_status": observed_status,
                "current_status": cp.current_status.value,
            },
        )


async def _assert_no_unacknowledged_prior(
    candidate_id: int,
    reviewer_id: int,
    overrides_decision_id: int | None,
    db: AsyncSession,
) -> None:
    """Reject a new decision that silently supersedes the reviewer's own prior one.

    Args:
        candidate_id: The candidate paper's id.
        reviewer_id: The reviewer submitting the new decision.
        overrides_decision_id: The id of the decision being explicitly superseded,
            as supplied in the request body. When set, no prior decision blocks
            the write — the caller has already acknowledged it.
        db: Active async session.

    Raises:
        HTTPException: 409 with an ``unacknowledged_prior_decision`` detail dict
            carrying the reviewer's most recent existing decision, raised when
            such a decision exists and ``overrides_decision_id`` was not supplied.

    """
    if overrides_decision_id is not None:
        return

    result = await db.execute(
        select(PaperDecision)
        .where(
            PaperDecision.candidate_paper_id == candidate_id,
            PaperDecision.reviewer_id == reviewer_id,
        )
        .order_by(PaperDecision.created_at.desc())
    )
    prior = result.scalars().first()
    if prior is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "unacknowledged_prior_decision",
                "prior_decision": {
                    "id": prior.id,
                    "decision": prior.decision.value,
                    "reasons": prior.reasons,
                    "decided_at": prior.created_at.isoformat() if prior.created_at else None,
                },
            },
        )


async def _recompute_conflict_flag(candidate_id: int, db: AsyncSession) -> bool:
    """Recompute whether a candidate paper has an active reviewer disagreement.

    A correction (an override by the same reviewer) must stay distinguishable
    from a disagreement (differing outcomes across different reviewers). This
    loads every decision on the candidate, keeps human-reviewer decisions only,
    drops any decision superseded by a later override, reduces to one — the
    latest surviving — decision per reviewer, and flags a conflict only when
    two or more distinct reviewers remain with differing outcomes.

    Args:
        candidate_id: The candidate paper's id.
        db: Active async session.

    Returns:
        True when two or more human reviewers currently hold differing,
        non-superseded decisions on the candidate; False otherwise.

    """
    result = await db.execute(
        select(PaperDecision, Reviewer)
        .join(Reviewer, PaperDecision.reviewer_id == Reviewer.id)
        .where(PaperDecision.candidate_paper_id == candidate_id)
        # `id` breaks ties on `created_at`. Its server default is func.now(),
        # which SQLite resolves to whole seconds, so two decisions recorded in
        # the same second sort arbitrarily — and "the reviewer's latest
        # decision" would then depend on row order rather than on time.
        .order_by(PaperDecision.created_at, PaperDecision.id)
    )
    rows = result.all()
    human_decisions = [d for d, r in rows if r.reviewer_type == ReviewerType.HUMAN]

    superseded_ids = {
        d.overrides_decision_id for d in human_decisions if d.overrides_decision_id is not None
    }
    surviving = [d for d in human_decisions if d.id not in superseded_ids]

    # Rows are ordered by created_at ascending, so the last assignment per
    # reviewer_id in this loop is that reviewer's latest surviving decision.
    latest_by_reviewer: dict[int, PaperDecision] = {}
    for d in surviving:
        latest_by_reviewer[d.reviewer_id] = d

    remaining = list(latest_by_reviewer.values())
    return len(remaining) >= 2 and len({d.decision for d in remaining}) > 1


async def _finalize_decision(
    db: AsyncSession,
    pd: PaperDecision,
    *,
    study_id: int,
    current_user: CurrentUser,
    audit_after: dict,
) -> DecisionResponse:
    """Record the audit entry for a persisted PaperDecision and build its response.

    Shared by ``submit_decision`` and ``resolve_conflict`` — both create a
    PaperDecision, flush it, then need the same audit-record-then-commit-then-
    serialize sequence.

    Args:
        db: Active async session; the PaperDecision must already be flushed so
            ``pd.id`` and ``pd.created_at`` are populated.
        pd: The flushed PaperDecision to record and return.
        study_id: The owning study's id, for the audit record.
        current_user: The authenticated user recorded as the audit actor.
        audit_after: The ``after_value`` payload for the audit record.

    Returns:
        The DecisionResponse for the persisted decision.

    """
    await audit_svc.record(
        db,
        study_id=study_id,
        actor_user_id=current_user.user_id,
        actor_agent=None,
        entity_type="PaperDecision",
        entity_id=pd.id,
        action=AuditAction.CREATE,
        after_value=audit_after,
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

    Raises:
        HTTPException: 422 for an invalid reviewer/decision; 409 for a stale
            ``observed_status`` (FR-025/FR-027) or an unacknowledged prior
            decision by the same reviewer (FR-022).

    """
    await require_study_member(study_id, current_user, db)
    await _require_reviewer_in_study(body.reviewer_id, study_id, db)
    cp = await _load_candidate(study_id, candidate_id, db)

    decision_enum = _parse_decision_type(body.decision)
    _assert_observed_status(cp, body.observed_status)
    await _assert_no_unacknowledged_prior(
        candidate_id, body.reviewer_id, body.overrides_decision_id, db
    )

    pd = PaperDecision(
        candidate_paper_id=candidate_id,
        reviewer_id=body.reviewer_id,
        decision=decision_enum,
        reasons=body.reasons or None,
        is_override=body.overrides_decision_id is not None,
        overrides_decision_id=body.overrides_decision_id,
    )
    db.add(pd)
    await db.flush()

    cp.current_status = CandidatePaperStatus(body.decision)
    cp.conflict_flag = await _recompute_conflict_flag(candidate_id, db)

    return await _finalize_decision(
        db,
        pd,
        study_id=study_id,
        current_user=current_user,
        audit_after={
            "candidate_paper_id": candidate_id,
            "decision": body.decision,
            "reviewer_id": body.reviewer_id,
        },
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

    decision_enum = _parse_decision_type(body.decision)

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
    return await _finalize_decision(
        db,
        pd,
        study_id=study_id,
        current_user=current_user,
        audit_after={
            "candidate_paper_id": candidate_id,
            "decision": body.decision,
            "is_override": True,
            "conflict_resolved": True,
        },
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
            decided_at=d.created_at.isoformat() if d.created_at else None,
        )
        for d in decisions
    ]
