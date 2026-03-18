"""Admin endpoints for agent management (Feature 005).

Exposes:
- ``GET /admin/agent-task-types`` — list all valid AgentTaskType values.
- ``GET /admin/agents`` — list all agents.
- ``POST /admin/agents`` — create a new agent.
- ``GET /admin/agents/{id}`` — get a single agent.
- ``PATCH /admin/agents/{id}`` — update an agent.
- ``DELETE /admin/agents/{id}`` — soft-delete an agent.
- ``POST /admin/agents/generate-persona-svg`` — AI-generate a persona SVG image.
- ``POST /admin/agents/{id}/generate-system-message`` — AI-generate system message.
- ``POST /admin/agents/{id}/undo-system-message`` — restore previous system message.
"""

from __future__ import annotations

import datetime
import uuid

from db.models.agents import Agent, AvailableModel, Provider
from db.models.users import GroupMembership, GroupRole
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services.agent_service import (
    AgentCreate,
    AgentGeneratorNotConfiguredError,
    AgentHasDependentsError,
    AgentNotFoundError,
    AgentService,
    AgentUpdate,
    NoUndoBufferError,
    PersonaSvgGenerationError,
    StaleVersionError,
    TemplateValidationError,
)

router = APIRouter(tags=["admin-agents"])
logger = get_logger(__name__)
_service = AgentService()


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------


async def _require_admin(
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> None:
    """Require that the caller holds an admin role in at least one group.

    Args:
        current_user: Injected authenticated user.
        db: Injected async database session.

    Raises:
        HTTPException: 403 if the user is not an admin.

    """
    result = await db.execute(
        select(GroupMembership)
        .where(
            GroupMembership.user_id == current_user.user_id,
            GroupMembership.role <= GroupRole.ADMIN,
        )
        .limit(1)
    )
    if result.scalars().first() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: system admin role required",
        )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class AgentSummaryResponse(BaseModel):
    """Summary response schema for listing Agent records.

    Attributes:
        id: Agent UUID.
        task_type: AgentTaskType string value.
        role_name: Short functional role label.
        persona_name: Human-readable persona name.
        model_id: UUID of the assigned AvailableModel.
        provider_id: UUID of the assigned Provider.
        model_display_name: Display name of the assigned model.
        provider_display_name: Display name of the assigned provider.
        is_active: Whether the agent is active.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.

    """

    id: uuid.UUID
    task_type: str
    role_name: str
    persona_name: str
    model_id: uuid.UUID
    provider_id: uuid.UUID
    model_display_name: str
    provider_display_name: str
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class AgentFullResponse(BaseModel):
    """Full response schema for a single Agent record.

    Extends :class:`AgentSummaryResponse` with detailed fields.

    Attributes:
        id: Agent UUID.
        task_type: AgentTaskType string value.
        role_name: Short functional role label.
        persona_name: Human-readable persona name.
        model_id: UUID of the assigned AvailableModel.
        provider_id: UUID of the assigned Provider.
        model_display_name: Display name of the assigned model.
        provider_display_name: Display name of the assigned provider.
        is_active: Whether the agent is active.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        role_description: Full role description.
        persona_description: Narrative persona background.
        persona_svg: Optional raw SVG markup.
        system_message_template: Jinja2 template string.
        system_message_undo_buffer: Previous template string, if any.
        version_id: Optimistic-locking counter.

    """

    id: uuid.UUID
    task_type: str
    role_name: str
    persona_name: str
    model_id: uuid.UUID
    provider_id: uuid.UUID
    model_display_name: str
    provider_display_name: str
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    role_description: str
    persona_description: str
    persona_svg: str | None
    system_message_template: str
    system_message_undo_buffer: str | None
    version_id: int

    model_config = {"from_attributes": True}


class AgentCreateBody(BaseModel):
    """Request schema for creating a new Agent.

    Attributes:
        task_type: AgentTaskType string value.
        role_name: Short functional role label.
        role_description: Full role description.
        persona_name: Human-readable persona name.
        persona_description: Narrative persona background.
        system_message_template: Jinja2 template string.
        model_id: UUID of the AvailableModel to assign.
        provider_id: UUID of the Provider to assign.
        persona_svg: Optional raw SVG markup.

    """

    task_type: str
    role_name: str
    role_description: str
    persona_name: str
    persona_description: str
    system_message_template: str
    model_id: uuid.UUID
    provider_id: uuid.UUID
    persona_svg: str | None = None


class SystemMessageGenerateResult(BaseModel):
    """Response schema for system-message generation.

    Attributes:
        system_message_template: Newly generated Jinja2 template.
        previous_message_preserved: True if a previous template was moved to
            the undo buffer.

    """

    system_message_template: str
    previous_message_preserved: bool


class PersonaSvgGenerateBody(BaseModel):
    """Request schema for persona SVG generation.

    Attributes:
        persona_name: Human-readable persona name.
        persona_description: Narrative description of the persona.
        agent_id: Optional existing agent UUID for context.

    """

    persona_name: str
    persona_description: str
    agent_id: uuid.UUID | None = None


class PersonaSvgGenerateResult(BaseModel):
    """Response schema for persona SVG generation.

    Attributes:
        svg: Raw SVG markup string.

    """

    svg: str


class AgentUpdateBody(BaseModel):
    """Request schema for partially updating an Agent.

    All fields are optional — only supplied values are applied.

    Attributes:
        version_id: Optimistic-locking counter (required for conflict detection).
        task_type: New AgentTaskType string, or omitted to keep current.
        role_name: New role label, or omitted to keep current.
        role_description: New description, or omitted to keep current.
        persona_name: New persona name, or omitted to keep current.
        persona_description: New persona description, or omitted.
        persona_svg: New SVG markup string, or omitted.
        system_message_template: New Jinja2 template, or omitted.
        model_id: New model UUID, or omitted.
        provider_id: New provider UUID, or omitted.
        is_active: New activation status, or omitted.

    """

    version_id: int = 0
    task_type: str | None = None
    role_name: str | None = None
    role_description: str | None = None
    persona_name: str | None = None
    persona_description: str | None = None
    persona_svg: str | None = None
    system_message_template: str | None = None
    model_id: uuid.UUID | None = None
    provider_id: uuid.UUID | None = None
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _load_display_names(
    agent: Agent,
    db: AsyncSession,
) -> tuple[str, str]:
    """Load model and provider display names for an Agent.

    Args:
        agent: The Agent ORM instance.
        db: Active async database session.

    Returns:
        Tuple of (model_display_name, provider_display_name).

    """
    model_result = await db.execute(
        select(AvailableModel).where(AvailableModel.id == agent.model_id)
    )
    model = model_result.scalar_one_or_none()
    model_display_name = model.display_name if model else str(agent.model_id)

    provider_result = await db.execute(select(Provider).where(Provider.id == agent.provider_id))
    provider = provider_result.scalar_one_or_none()
    provider_display_name = provider.display_name if provider else str(agent.provider_id)

    return model_display_name, provider_display_name


def _agent_to_summary(
    agent: Agent,
    model_display_name: str,
    provider_display_name: str,
) -> AgentSummaryResponse:
    """Build an :class:`AgentSummaryResponse` from ORM + display names.

    Args:
        agent: Agent ORM instance.
        model_display_name: Resolved model display name.
        provider_display_name: Resolved provider display name.

    Returns:
        :class:`AgentSummaryResponse` instance.

    """
    return AgentSummaryResponse(
        id=agent.id,
        task_type=agent.task_type.value,
        role_name=agent.role_name,
        persona_name=agent.persona_name,
        model_id=agent.model_id,
        provider_id=agent.provider_id,
        model_display_name=model_display_name,
        provider_display_name=provider_display_name,
        is_active=agent.is_active,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
    )


def _agent_to_full(
    agent: Agent,
    model_display_name: str,
    provider_display_name: str,
) -> AgentFullResponse:
    """Build an :class:`AgentFullResponse` from ORM + display names.

    Args:
        agent: Agent ORM instance.
        model_display_name: Resolved model display name.
        provider_display_name: Resolved provider display name.

    Returns:
        :class:`AgentFullResponse` instance.

    """
    return AgentFullResponse(
        id=agent.id,
        task_type=agent.task_type.value,
        role_name=agent.role_name,
        persona_name=agent.persona_name,
        model_id=agent.model_id,
        provider_id=agent.provider_id,
        model_display_name=model_display_name,
        provider_display_name=provider_display_name,
        is_active=agent.is_active,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
        role_description=agent.role_description,
        persona_description=agent.persona_description,
        persona_svg=agent.persona_svg,
        system_message_template=agent.system_message_template,
        system_message_undo_buffer=agent.system_message_undo_buffer,
        version_id=agent.version_id,
    )


# ---------------------------------------------------------------------------
# Endpoints — static / collection routes first (before /{agent_id})
# ---------------------------------------------------------------------------


@router.get(
    "/agent-task-types",
    response_model=list[str],
    summary="List all valid agent task types",
)
async def list_agent_task_types(
    _: None = Depends(_require_admin),  # noqa: B008
) -> list[str]:
    """Return all valid AgentTaskType enum values as strings.

    Args:
        _: Admin auth guard (injected).

    Returns:
        Sorted list of task type string values.

    """
    return _service.get_agent_task_types()


@router.get(
    "/agents",
    response_model=list[AgentSummaryResponse],
    summary="List all agents",
)
async def list_agents(
    task_type: str | None = Query(default=None),  # noqa: B008
    is_active: bool = Query(default=True),  # noqa: B008
    _: None = Depends(_require_admin),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> list[AgentSummaryResponse]:
    """Return a list of Agent records with optional filters.

    Args:
        task_type: Optional filter by task type value.
        is_active: Filter by activation status (default True).
        _: Admin auth guard (injected).
        db: Injected async database session.

    Returns:
        List of :class:`AgentSummaryResponse` objects.

    """
    agents = await _service.list_agents(db, task_type=task_type, is_active=is_active)

    # Batch load model and provider display names
    model_ids = [a.model_id for a in agents]
    provider_ids = [a.provider_id for a in agents]

    models_map: dict[uuid.UUID, AvailableModel] = {}
    providers_map: dict[uuid.UUID, Provider] = {}

    if model_ids:
        models_result = await db.execute(
            select(AvailableModel).where(AvailableModel.id.in_(model_ids))
        )
        models_map = {m.id: m for m in models_result.scalars().all()}

    if provider_ids:
        providers_result = await db.execute(select(Provider).where(Provider.id.in_(provider_ids)))
        providers_map = {p.id: p for p in providers_result.scalars().all()}

    return [
        _agent_to_summary(
            a,
            models_map[a.model_id].display_name if a.model_id in models_map else str(a.model_id),
            providers_map[a.provider_id].display_name
            if a.provider_id in providers_map
            else str(a.provider_id),
        )
        for a in agents
    ]


@router.post(
    "/agents",
    response_model=AgentFullResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new agent",
)
async def create_agent(
    body: AgentCreateBody,
    _: None = Depends(_require_admin),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> AgentFullResponse:
    """Create a new Agent record.

    Args:
        body: Agent creation payload.
        _: Admin auth guard (injected).
        db: Injected async database session.

    Returns:
        The newly created :class:`AgentFullResponse`.

    Raises:
        HTTPException: 422 if the template is invalid or data constraints fail.

    """
    data = AgentCreate(
        task_type=body.task_type,
        role_name=body.role_name,
        role_description=body.role_description,
        persona_name=body.persona_name,
        persona_description=body.persona_description,
        system_message_template=body.system_message_template,
        model_id=body.model_id,
        provider_id=body.provider_id,
        persona_svg=body.persona_svg,
    )
    try:
        agent = await _service.create_agent(data, db)
    except TemplateValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    await db.commit()
    await db.refresh(agent)

    model_display_name, provider_display_name = await _load_display_names(agent, db)
    return _agent_to_full(agent, model_display_name, provider_display_name)


# NOTE: /agents/generate-persona-svg MUST be registered BEFORE /agents/{agent_id}
# to avoid FastAPI routing conflicts.


@router.post(
    "/agents/generate-persona-svg",
    response_model=PersonaSvgGenerateResult,
    summary="Generate a persona SVG avatar using an LLM",
)
async def generate_persona_svg(
    body: PersonaSvgGenerateBody,
    _: None = Depends(_require_admin),  # noqa: B008
) -> PersonaSvgGenerateResult:
    """Generate SVG markup for a persona using an LLM.

    Args:
        body: Persona SVG generation payload.
        _: Admin auth guard (injected).

    Returns:
        :class:`PersonaSvgGenerateResult` with raw SVG markup.

    Raises:
        HTTPException: 502 if the LLM call fails or returns invalid SVG.

    """
    try:
        svg = await _service.generate_persona_svg(
            persona_name=body.persona_name,
            persona_description=body.persona_description,
        )
    except PersonaSvgGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    return PersonaSvgGenerateResult(svg=svg)


# ---------------------------------------------------------------------------
# Endpoints — agent-scoped routes
# ---------------------------------------------------------------------------


@router.post(
    "/agents/{agent_id}/generate-system-message",
    response_model=SystemMessageGenerateResult,
    summary="AI-generate or regenerate a system message for an agent",
)
async def generate_system_message(
    agent_id: uuid.UUID,
    _: None = Depends(_require_admin),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> SystemMessageGenerateResult:
    """Generate or regenerate the system message template for an Agent.

    Moves any existing template to the undo buffer before writing the new one.

    Args:
        agent_id: UUID of the agent to generate a system message for.
        _: Admin auth guard (injected).
        db: Injected async database session.

    Returns:
        :class:`SystemMessageGenerateResult` with the new template.

    Raises:
        HTTPException: 404 if the agent is not found.
        HTTPException: 409 if no AgentGenerator agent is configured.
        HTTPException: 502 if the LLM call fails.

    """
    # Load agent to inspect existing template before generation
    agent_check_result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent_before = agent_check_result.scalar_one_or_none()
    if agent_before is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    had_previous = bool(agent_before.system_message_template)

    try:
        new_template = await _service.generate_system_message(agent_id, db)
    except AgentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        ) from exc
    except AgentGeneratorNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM generation failed: {exc}",
        ) from exc

    await db.commit()

    return SystemMessageGenerateResult(
        system_message_template=new_template,
        previous_message_preserved=had_previous,
    )


@router.get(
    "/agents/{agent_id}",
    response_model=AgentFullResponse,
    summary="Get a single agent by ID",
)
async def get_agent(
    agent_id: uuid.UUID,
    _: None = Depends(_require_admin),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> AgentFullResponse:
    """Return the full details of a single Agent including its undo buffer.

    Args:
        agent_id: UUID of the agent to retrieve.
        _: Admin auth guard (injected).
        db: Injected async database session.

    Returns:
        :class:`AgentFullResponse` with all fields.

    Raises:
        HTTPException: 404 if the agent is not found.

    """
    try:
        agent = await _service.get_agent(agent_id, db)
    except AgentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        ) from exc

    model_display_name, provider_display_name = await _load_display_names(agent, db)
    return _agent_to_full(agent, model_display_name, provider_display_name)


@router.patch(
    "/agents/{agent_id}",
    response_model=AgentFullResponse,
    summary="Partially update an agent",
)
async def update_agent(
    agent_id: uuid.UUID,
    body: AgentUpdateBody,
    _: None = Depends(_require_admin),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> AgentFullResponse:
    """Apply a partial update to an Agent record.

    Supports optimistic locking via ``version_id``.

    Args:
        agent_id: UUID of the agent to update.
        body: Fields to update (only non-null values are applied).
        _: Admin auth guard (injected).
        db: Injected async database session.

    Returns:
        Updated :class:`AgentFullResponse`.

    Raises:
        HTTPException: 404 if the agent is not found.
        HTTPException: 409 if ``version_id`` is stale (concurrent modification).
        HTTPException: 422 if the template or model constraint is invalid.

    """
    data = AgentUpdate(
        version_id=body.version_id,
        task_type=body.task_type,
        role_name=body.role_name,
        role_description=body.role_description,
        persona_name=body.persona_name,
        persona_description=body.persona_description,
        persona_svg=body.persona_svg,
        system_message_template=body.system_message_template,
        model_id=body.model_id,
        provider_id=body.provider_id,
        is_active=body.is_active,
    )
    try:
        agent = await _service.update_agent(agent_id, data, db)
    except AgentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        ) from exc
    except StaleVersionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except TemplateValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    await db.commit()
    await db.refresh(agent)

    model_display_name, provider_display_name = await _load_display_names(agent, db)
    return _agent_to_full(agent, model_display_name, provider_display_name)


@router.delete(
    "/agents/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete an agent",
)
async def delete_agent(
    agent_id: uuid.UUID,
    _: None = Depends(_require_admin),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> None:
    """Soft-delete an Agent by setting is_active to False.

    Args:
        agent_id: UUID of the agent to deactivate.
        _: Admin auth guard (injected).
        db: Injected async database session.

    Raises:
        HTTPException: 404 if the agent is not found.
        HTTPException: 409 if Reviewer rows still reference the agent.

    """
    try:
        await _service.deactivate_agent(agent_id, db)
    except AgentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        ) from exc
    except AgentHasDependentsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": str(exc),
                "reviewer_ids": exc.reviewer_ids,
            },
        ) from exc

    await db.commit()


@router.post(
    "/agents/{agent_id}/undo-system-message",
    response_model=AgentFullResponse,
    summary="Restore the previous system message from the undo buffer",
)
async def undo_system_message(
    agent_id: uuid.UUID,
    _: None = Depends(_require_admin),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> AgentFullResponse:
    """Swap system_message_template with system_message_undo_buffer.

    Args:
        agent_id: UUID of the agent.
        _: Admin auth guard (injected).
        db: Injected async database session.

    Returns:
        Updated :class:`AgentFullResponse` with the restored message.

    Raises:
        HTTPException: 404 if the agent is not found.
        HTTPException: 409 if the undo buffer is empty.

    """
    try:
        agent = await _service.restore_system_message(agent_id, db)
    except AgentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        ) from exc
    except NoUndoBufferError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    await db.commit()
    await db.refresh(agent)

    model_display_name, provider_display_name = await _load_display_names(agent, db)
    return _agent_to_full(agent, model_display_name, provider_display_name)
