"""Research group endpoints: CRUD and member management."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger
from backend.core.database import get_db
from db.models import Study
from db.models.users import GroupMembership, GroupRole, ResearchGroup, User

router = APIRouter(prefix="/groups", tags=["groups"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class GroupSummary(BaseModel):
    """Group list item returned by GET /groups."""

    id: int
    name: str
    role: str
    study_count: int


class GroupCreated(BaseModel):
    """Minimal response for POST /groups."""

    id: int
    name: str


class MemberItem(BaseModel):
    """Member list item returned by GET /groups/{group_id}/members."""

    user_id: int
    display_name: str
    email: str
    role: str


class InviteMemberRequest(BaseModel):
    """Body for POST /groups/{group_id}/members."""

    email: EmailStr
    role: str = "member"


class InviteMemberResponse(BaseModel):
    """Response for POST /groups/{group_id}/members."""

    user_id: int
    role: str


class CreateGroupRequest(BaseModel):
    """Body for POST /groups."""

    name: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _require_group_admin(
    group_id: int, current_user: CurrentUser, db: AsyncSession
) -> GroupMembership:
    """Raise 403 if current_user is not an admin of *group_id*.

    Args:
        group_id: The group being accessed.
        current_user: The authenticated user.
        db: Async database session.

    Returns:
        The :class:`GroupMembership` for the current user.

    Raises:
        HTTPException: 403 if the user is not an admin.
        HTTPException: 404 if the group doesn't exist or user isn't a member.
    """
    result = await db.execute(
        select(GroupMembership).where(
            GroupMembership.group_id <= group_id,
            GroupMembership.user_id == current_user.user_id,
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    if membership.role > GroupRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return membership


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("", response_model=list[GroupSummary], summary="List the current user's groups")
async def list_groups(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[GroupSummary]:
    """Return all research groups the current user belongs to.

    Args:
        current_user: Injected from the validated JWT.
        db: Injected async database session.

    Returns:
        A list of :class:`GroupSummary` objects.
    """
    result = await db.execute(
        select(GroupMembership)
        .where(GroupMembership.user_id == current_user.user_id)
        .options(selectinload(GroupMembership.group))
    )
    memberships = result.scalars().all()

    summaries: list[GroupSummary] = []
    for m in memberships:
        # Count studies for this group
        count_result = await db.execute(
            select(func.count()).select_from(Study).where(Study.research_group_id == m.group_id)
        )
        study_count = count_result.scalar_one()
        summaries.append(
            GroupSummary(
                id=m.group.id,
                name=m.group.name,
                role=m.role.value,
                study_count=study_count,
            )
        )
    return summaries


@router.post(
    "",
    response_model=GroupCreated,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new research group",
)
async def create_group(
    body: CreateGroupRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GroupCreated:
    """Create a new research group; the current user becomes its admin.

    Args:
        body: JSON body containing ``name`` (string).
        current_user: Injected from the validated JWT.
        db: Injected async database session.

    Returns:
        The newly created group id and name.

    Raises:
        HTTPException: 409 if a group with that name already exists.
    """
    name = body.name.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="name is required")

    existing = await db.execute(select(ResearchGroup).where(ResearchGroup.name == name))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Group name already exists")

    group = ResearchGroup(name=name)
    db.add(group)
    await db.flush()  # populate group.id

    membership = GroupMembership(
        group_id=group.id,
        user_id=current_user.user_id,
        role=GroupRole.ADMIN,
    )
    db.add(membership)
    await db.commit()

    logger.info("group_created", group_id=group.id, creator=current_user.user_id)
    return GroupCreated(id=group.id, name=group.name)


@router.get(
    "/{group_id}/members",
    response_model=list[MemberItem],
    summary="List members of a research group",
)
async def list_members(
    group_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MemberItem]:
    """Return all members of *group_id*.

    Args:
        group_id: The group to inspect.
        current_user: Injected from the validated JWT; must be a member.
        db: Injected async database session.

    Returns:
        A list of :class:`MemberItem` objects.

    Raises:
        HTTPException: 404 if the group doesn't exist or the user isn't a member.
    """
    # Verify membership
    membership_check = await db.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == current_user.user_id,
        )
    )
    if membership_check.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    result = await db.execute(
        select(GroupMembership)
        .where(GroupMembership.group_id == group_id)
        .options(selectinload(GroupMembership.user))
    )
    memberships = result.scalars().all()
    return [
        MemberItem(
            user_id=m.user.id,
            display_name=m.user.display_name,
            email=m.user.email,
            role=m.role.value,
        )
        for m in memberships
    ]


@router.post(
    "/{group_id}/members",
    response_model=InviteMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a user to a research group",
)
async def add_member(
    group_id: int,
    body: InviteMemberRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InviteMemberResponse:
    """Add a user (by email) to the group. Admin only.

    Args:
        group_id: The group to add the user to.
        body: Email and role for the new member.
        current_user: Injected from the validated JWT; must be admin.
        db: Injected async database session.

    Returns:
        The new membership: user_id and role.

    Raises:
        HTTPException: 404 if the group or user is not found.
        HTTPException: 403 if the caller is not a group admin.
        HTTPException: 409 if the user is already a member.
    """
    await _require_group_admin(group_id, current_user, db)

    user_result = await db.execute(select(User).where(User.email == body.email))
    target_user = user_result.scalar_one_or_none()
    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = await db.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == target_user.id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member")

    role = GroupRole(body.role) if body.role in GroupRole._value2member_map_ else GroupRole.MEMBER
    membership = GroupMembership(group_id=group_id, user_id=target_user.id, role=role)
    db.add(membership)
    await db.commit()

    logger.info("member_added", group_id=group_id, user_id=target_user.id)
    return InviteMemberResponse(user_id=target_user.id, role=role.value)


@router.delete(
    "/{group_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a member from a research group",
)
async def remove_member(
    group_id: int,
    user_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove *user_id* from *group_id*. Admin only; cannot remove last admin.

    Args:
        group_id: The group to modify.
        user_id: The user to remove.
        current_user: Injected from the validated JWT; must be admin.
        db: Injected async database session.

    Raises:
        HTTPException: 403 if caller is not an admin.
        HTTPException: 404 if the target membership is not found.
        HTTPException: 409 if removing would leave the group with no admins.
    """
    await _require_group_admin(group_id, current_user, db)

    target_result = await db.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == user_id,
        )
    )
    target = target_result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    # Cannot remove the last admin
    if target.role == GroupRole.ADMIN:
        admin_count_result = await db.execute(
            select(func.count())
            .select_from(GroupMembership)
            .where(
                GroupMembership.group_id == group_id,
                GroupMembership.role == GroupRole.ADMIN,
            )
        )
        admin_count = admin_count_result.scalar_one()
        if admin_count == 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot remove the last admin from a group",
            )

    await db.delete(target)
    await db.commit()
    logger.info("member_removed", group_id=group_id, user_id=user_id)
