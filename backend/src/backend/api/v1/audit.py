"""Study audit log endpoint (FR-044).

Exposes ``GET /studies/{study_id}/audit`` for paginated access to the immutable
``AuditRecord`` table. Access is restricted to study leads (study admins).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger
from backend.core.database import get_db
from db.models.audit import AuditRecord
from db.models.study import StudyMember, StudyMemberRole
from db.models.users import User

router = APIRouter(tags=["audit"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class AuditActorResponse(BaseModel):
    """Minimal actor representation embedded in audit items."""

    type: str  # "user" | "agent"
    id: int | None
    display_name: str


class AuditItemResponse(BaseModel):
    """Single audit log entry."""

    id: int
    actor: AuditActorResponse
    entity_type: str
    entity_id: int
    action: str
    field_name: str | None
    before_value: dict | None
    after_value: dict | None
    created_at: str


class AuditPageResponse(BaseModel):
    """Paginated audit log response."""

    items: list[AuditItemResponse]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _require_study_lead(
    study_id: int, current_user: CurrentUser, db: AsyncSession
) -> None:
    """Raise HTTP 403 if *current_user* is not a lead of *study_id*.

    Args:
        study_id: The study to check.
        current_user: The authenticated user making the request.
        db: Active async database session.

    Raises:
        HTTPException: 403 if the user is not the study lead.
    """
    result = await db.execute(
        select(StudyMember).where(
            StudyMember.study_id == study_id,
            StudyMember.user_id == current_user.user_id,
            StudyMember.role == StudyMemberRole.LEAD,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: only the study lead may view the audit log",
        )


async def _build_actor(record: AuditRecord, db: AsyncSession) -> AuditActorResponse:
    """Resolve the actor display name for an audit record.

    Args:
        record: The AuditRecord whose actor to resolve.
        db: Active async database session.

    Returns:
        An :class:`AuditActorResponse` with type, id, and display_name.
    """
    if record.actor_agent is not None:
        return AuditActorResponse(type="agent", id=None, display_name=record.actor_agent)

    user_result = await db.execute(
        select(User).where(User.id == record.actor_user_id)
    )
    user = user_result.scalar_one_or_none()
    display = user.display_name if user else f"user:{record.actor_user_id}"
    return AuditActorResponse(type="user", id=record.actor_user_id, display_name=display)


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/audit",
    response_model=AuditPageResponse,
    summary="Get the paginated study-level audit log",
)
async def get_audit_log(
    study_id: int,
    entity_type: str | None = Query(None, description="Filter by entity type"),
    actor_user_id: int | None = Query(None, description="Filter by actor user ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AuditPageResponse:
    """Return a paginated, optionally filtered audit log for a study.

    Only the study lead may access this endpoint (HTTP 403 for non-leads).

    Args:
        study_id: The study whose audit log to return.
        entity_type: Optional filter — only return records for this entity type
            (e.g. ``"PICOComponent"``, ``"SearchString"``).
        actor_user_id: Optional filter — only return records attributed to this
            user ID.
        page: 1-based page number (default: 1).
        page_size: Number of records per page (default: 50, max: 200).
        current_user: Injected from the validated JWT; must be a study lead.
        db: Injected async database session.

    Returns:
        :class:`AuditPageResponse` with items, total, page, page_size.

    Raises:
        HTTPException: 403 if the caller is not the study lead.
    """
    await _require_study_lead(study_id, current_user, db)

    query = select(AuditRecord).where(AuditRecord.study_id == study_id)
    count_query = select(func.count()).select_from(AuditRecord).where(
        AuditRecord.study_id == study_id
    )

    if entity_type is not None:
        query = query.where(AuditRecord.entity_type == entity_type)
        count_query = count_query.where(AuditRecord.entity_type == entity_type)
    if actor_user_id is not None:
        query = query.where(AuditRecord.actor_user_id == actor_user_id)
        count_query = count_query.where(AuditRecord.actor_user_id == actor_user_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(AuditRecord.created_at.desc()).offset(offset).limit(page_size)
    records_result = await db.execute(query)
    records = records_result.scalars().all()

    items = [
        AuditItemResponse(
            id=r.id,
            actor=await _build_actor(r, db),
            entity_type=r.entity_type,
            entity_id=r.entity_id,
            action=r.action.value,
            field_name=r.field_name,
            before_value=r.before_value,
            after_value=r.after_value,
            created_at=r.created_at.isoformat(),
        )
        for r in records
    ]
    return AuditPageResponse(items=items, total=total, page=page, page_size=page_size)
