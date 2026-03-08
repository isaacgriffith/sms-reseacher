"""Study CRUD endpoints and the new-study wizard."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services import audit as audit_svc
from backend.services.phase_gate import compute_staleness_flags, get_unlocked_phases
from db.models.audit import AuditAction
from db.models import Study, StudyStatus, StudyType  # package __init__ exports these
from db.models.study import Reviewer, ReviewerType, StudyMember, StudyMemberRole
from db.models.users import GroupMembership, ResearchGroup

router = APIRouter(tags=["studies"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ReviewerConfig(BaseModel):
    """Reviewer specification in the wizard payload."""

    type: str  # "human" | "ai_agent"
    user_id: int | None = None
    agent_name: str | None = None
    agent_config: dict | None = None


class CreateStudyRequest(BaseModel):
    """Wizard payload for POST /groups/{group_id}/studies."""

    name: str
    topic: str
    study_type: str
    motivation: str | None = None
    research_objectives: list[str] = []
    research_questions: list[str] = []
    member_ids: list[int] = []
    reviewers: list[ReviewerConfig] = []
    snowball_threshold: int = 5


class PatchStudyRequest(BaseModel):
    """Partial update for PATCH /studies/{study_id}."""

    name: str | None = None
    topic: str | None = None
    motivation: str | None = None
    research_objectives: list[str] | None = None
    research_questions: list[str] | None = None
    snowball_threshold: int | None = None


class StudySummary(BaseModel):
    """Study list item."""

    id: int
    name: str
    topic: str | None
    study_type: str
    status: str
    current_phase: int
    created_at: str


class StudyDetail(BaseModel):
    """Full study detail with unlocked phases."""

    id: int
    name: str
    topic: str | None
    study_type: str
    status: str
    current_phase: int
    motivation: str | None
    research_objectives: list[str]
    research_questions: list[str]
    snowball_threshold: int
    unlocked_phases: list[int]
    stale_phases: dict[str, bool]
    created_at: str
    updated_at: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _study_metadata(study: Study) -> dict[str, Any]:
    """Extract research_objectives and research_questions from study metadata JSON."""
    meta: dict = {}
    if study.metadata_ and isinstance(study.metadata_, dict):
        meta = study.metadata_
    return meta


async def _require_study_access(
    study_id: int, current_user: CurrentUser, db: AsyncSession
) -> Study:
    """Return the study if the current user is a member, else raise 404."""
    result = await db.execute(
        select(Study)
        .join(StudyMember, StudyMember.study_id == Study.id)
        .where(Study.id == study_id, StudyMember.user_id == current_user.user_id)
    )
    study = result.scalar_one_or_none()
    if study is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    return study


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/groups/{group_id}/studies",
    response_model=list[StudySummary],
    summary="List studies in a research group",
)
async def list_studies(
    group_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[StudySummary]:
    """List all studies in a group. Caller must be a group member.

    Args:
        group_id: The research group to list studies for.
        current_user: Injected from the validated JWT.
        db: Injected async database session.

    Returns:
        A list of :class:`StudySummary` objects.

    Raises:
        HTTPException: 404 if group doesn't exist or user isn't a member.
    """
    membership = await db.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == current_user.user_id,
        )
    )
    if membership.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    result = await db.execute(
        select(Study)
        .join(StudyMember, StudyMember.study_id == Study.id)
        .where(Study.research_group_id == group_id, StudyMember.user_id == current_user.user_id)
        .order_by(Study.created_at.desc())
    )
    studies = result.scalars().all()
    return [
        StudySummary(
            id=s.id,
            name=s.name,
            topic=s.topic,
            study_type=s.study_type.value,
            status=s.status.value,
            current_phase=s.current_phase,
            created_at=s.created_at.isoformat(),
        )
        for s in studies
    ]


@router.post(
    "/groups/{group_id}/studies",
    response_model=StudyDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create a study via the wizard",
)
async def create_study(
    group_id: int,
    body: CreateStudyRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StudyDetail:
    """Create a new study with wizard payload. Caller becomes the study lead.

    Args:
        group_id: The group that will own this study.
        body: Wizard payload with name, type, PICO config, members, reviewers.
        current_user: Injected from the validated JWT.
        db: Injected async database session.

    Returns:
        Full :class:`StudyDetail` for the created study.

    Raises:
        HTTPException: 404 if the group isn't found or user isn't a member.
    """
    membership = await db.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == current_user.user_id,
        )
    )
    if membership.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    # Validate study type
    try:
        study_type = StudyType(body.study_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid study_type: {body.study_type}",
        )

    study = Study(
        name=body.name,
        topic=body.topic,
        study_type=study_type,
        status=StudyStatus.ACTIVE,
        motivation=body.motivation,
        research_group_id=group_id,
        snowball_threshold=body.snowball_threshold,
        current_phase=1,
        metadata_={
            "research_objectives": body.research_objectives,
            "research_questions": body.research_questions,
        },
    )
    db.add(study)
    await db.flush()

    # Add the creator as lead
    all_member_ids = {current_user.user_id} | set(body.member_ids)
    for uid in all_member_ids:
        role = StudyMemberRole.LEAD if uid == current_user.user_id else StudyMemberRole.MEMBER
        db.add(StudyMember(study_id=study.id, user_id=uid, role=role))

    # Add reviewers
    for rev in body.reviewers:
        rv_type = ReviewerType.HUMAN if rev.type == "human" else ReviewerType.AI_AGENT
        db.add(
            Reviewer(
                study_id=study.id,
                reviewer_type=rv_type,
                user_id=rev.user_id,
                agent_name=rev.agent_name,
                agent_config=rev.agent_config,
            )
        )

    await db.commit()
    logger.info("study_created", study_id=study.id, group_id=group_id)

    meta = _study_metadata(study)
    return StudyDetail(
        id=study.id,
        name=study.name,
        topic=study.topic,
        study_type=study.study_type.value,
        status=study.status.value,
        current_phase=study.current_phase,
        motivation=study.motivation,
        research_objectives=meta.get("research_objectives", []),
        research_questions=meta.get("research_questions", []),
        snowball_threshold=study.snowball_threshold,
        unlocked_phases=[1],
        stale_phases=compute_staleness_flags(study),
        created_at=study.created_at.isoformat(),
        updated_at=study.updated_at.isoformat(),
    )


@router.get(
    "/studies/{study_id}",
    response_model=StudyDetail,
    summary="Get full study detail",
)
async def get_study(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StudyDetail:
    """Return full study detail including unlocked phases.

    Args:
        study_id: The study to retrieve.
        current_user: Injected from the validated JWT; must be a study member.
        db: Injected async database session.

    Returns:
        :class:`StudyDetail` with all metadata and ``unlocked_phases``.
    """
    study = await _require_study_access(study_id, current_user, db)
    unlocked = await get_unlocked_phases(study_id, db)
    meta = _study_metadata(study)

    return StudyDetail(
        id=study.id,
        name=study.name,
        topic=study.topic,
        study_type=study.study_type.value,
        status=study.status.value,
        current_phase=study.current_phase,
        motivation=study.motivation,
        research_objectives=meta.get("research_objectives", []),
        research_questions=meta.get("research_questions", []),
        snowball_threshold=study.snowball_threshold,
        unlocked_phases=unlocked,
        stale_phases=compute_staleness_flags(study),
        created_at=study.created_at.isoformat(),
        updated_at=study.updated_at.isoformat(),
    )


@router.patch(
    "/studies/{study_id}",
    response_model=StudyDetail,
    summary="Update study metadata",
)
async def patch_study(
    study_id: int,
    body: PatchStudyRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StudyDetail:
    """Partially update a study's metadata.

    Args:
        study_id: The study to update.
        body: Fields to update (all optional).
        current_user: Injected from the validated JWT; must be a study member.
        db: Injected async database session.

    Returns:
        Updated :class:`StudyDetail`.
    """
    study = await _require_study_access(study_id, current_user, db)
    meta = _study_metadata(study)

    if body.name is not None:
        study.name = body.name
    if body.topic is not None:
        study.topic = body.topic
    if body.motivation is not None:
        study.motivation = body.motivation
    if body.snowball_threshold is not None:
        study.snowball_threshold = body.snowball_threshold
    if body.research_objectives is not None:
        meta["research_objectives"] = body.research_objectives
    if body.research_questions is not None:
        meta["research_questions"] = body.research_questions
    if body.research_objectives is not None or body.research_questions is not None:
        study.metadata_ = meta

    await db.flush()
    await audit_svc.record(
        db,
        study_id=study_id,
        actor_user_id=current_user.user_id,
        actor_agent=None,
        entity_type="Study",
        entity_id=study_id,
        action=AuditAction.UPDATE,
        after_value=body.model_dump(exclude_none=True),
    )
    await db.commit()

    unlocked = await get_unlocked_phases(study_id, db)
    return StudyDetail(
        id=study.id,
        name=study.name,
        topic=study.topic,
        study_type=study.study_type.value,
        status=study.status.value,
        current_phase=study.current_phase,
        motivation=study.motivation,
        research_objectives=meta.get("research_objectives", []),
        research_questions=meta.get("research_questions", []),
        snowball_threshold=study.snowball_threshold,
        unlocked_phases=unlocked,
        stale_phases=compute_staleness_flags(study),
        created_at=study.created_at.isoformat(),
        updated_at=study.updated_at.isoformat(),
    )


@router.post(
    "/studies/{study_id}/archive",
    response_model=dict,
    summary="Archive a study",
)
async def archive_study(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Set the study status to archived.

    Args:
        study_id: The study to archive.
        current_user: Injected from the validated JWT; must be a study member.
        db: Injected async database session.

    Returns:
        ``{"status": "archived"}``
    """
    study = await _require_study_access(study_id, current_user, db)
    study.status = StudyStatus.ARCHIVED
    await db.commit()
    logger.info("study_archived", study_id=study_id)
    return {"status": "archived"}


@router.delete(
    "/studies/{study_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Permanently delete a study",
)
async def delete_study(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Permanently delete a study. Caller must be the study lead.

    Args:
        study_id: The study to delete.
        current_user: Injected from the validated JWT; must be a lead.
        db: Injected async database session.

    Raises:
        HTTPException: 403 if caller is not the study lead.
    """
    # Must be a lead
    lead_result = await db.execute(
        select(StudyMember).where(
            StudyMember.study_id == study_id,
            StudyMember.user_id == current_user.user_id,
            StudyMember.role == StudyMemberRole.LEAD,
        )
    )
    if lead_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only the study lead can delete a study"
        )

    result = await db.execute(select(Study).where(Study.id == study_id))
    study = result.scalar_one_or_none()
    if study is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")

    await db.delete(study)
    await db.commit()
    logger.info("study_deleted", study_id=study_id)
