"""Admin endpoints for LLM model management (Feature 005).

Exposes:
- ``GET /admin/providers/{id}/models`` — list all models for a provider.
- ``PATCH /admin/providers/{id}/models/{model_id}`` — enable or disable a model.
"""

from __future__ import annotations

import uuid

from db.models.agents import Agent, AvailableModel
from db.models.users import GroupMembership, GroupRole
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services.provider_service import ModelHasDependentsError

router = APIRouter(tags=["admin-models"])
logger = get_logger(__name__)


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


class AvailableModelResponse(BaseModel):
    """API response schema for an AvailableModel record.

    Attributes:
        id: Model UUID.
        provider_id: UUID of the owning Provider.
        model_identifier: Provider-native model identifier.
        display_name: Human-readable display label.
        is_enabled: Whether this model is available for agent assignment.
        version_id: Optimistic-locking counter.

    """

    id: uuid.UUID
    provider_id: uuid.UUID
    model_identifier: str
    display_name: str
    is_enabled: bool
    version_id: int

    model_config = {"from_attributes": True}


class ModelToggleBody(BaseModel):
    """Request body for toggling a model's enabled state.

    Attributes:
        is_enabled: The desired enabled state.

    """

    is_enabled: bool


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/providers/{provider_id}/models",
    response_model=list[AvailableModelResponse],
    summary="List all models for a provider",
)
async def list_models(
    provider_id: uuid.UUID,
    _: None = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> list[AvailableModelResponse]:
    """Return all AvailableModel rows for the given provider.

    Args:
        provider_id: UUID of the provider.
        _: Admin auth guard (injected).
        db: Injected async database session.

    Returns:
        List of :class:`AvailableModelResponse` ordered by model_identifier.

    """
    result = await db.execute(
        select(AvailableModel)
        .where(AvailableModel.provider_id == provider_id)
        .order_by(AvailableModel.model_identifier)
    )
    models = result.scalars().all()
    return [
        AvailableModelResponse(
            id=m.id,
            provider_id=m.provider_id,
            model_identifier=m.model_identifier,
            display_name=m.display_name,
            is_enabled=m.is_enabled,
            version_id=m.version_id,
        )
        for m in models
    ]


@router.patch(
    "/providers/{provider_id}/models/{model_id}",
    response_model=AvailableModelResponse,
    summary="Enable or disable a model",
)
async def toggle_model(
    provider_id: uuid.UUID,
    model_id: uuid.UUID,
    body: ModelToggleBody,
    _: None = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> AvailableModelResponse:
    """Toggle the enabled state of a specific model.

    Disabling a model that is currently referenced by at least one active
    agent raises HTTP 409 with the list of dependent agent IDs.

    Args:
        provider_id: UUID of the owning provider.
        model_id: UUID of the model to update.
        body: Toggle payload with the desired ``is_enabled`` state.
        _: Admin auth guard (injected).
        db: Injected async database session.

    Returns:
        Updated :class:`AvailableModelResponse`.

    Raises:
        HTTPException: 404 if the model is not found.
        HTTPException: 409 if disabling a model with active agent dependents.

    """
    result = await db.execute(
        select(AvailableModel).where(
            AvailableModel.id == model_id,
            AvailableModel.provider_id == provider_id,
        )
    )
    model = result.scalar_one_or_none()
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")

    if not body.is_enabled:
        agents_result = await db.execute(
            select(Agent).where(Agent.model_id == model_id, Agent.is_active == True)  # noqa: E712
        )
        active_agents = agents_result.scalars().all()
        if active_agents:
            exc = ModelHasDependentsError([str(a.id) for a in active_agents])
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": str(exc), "agent_ids": exc.agent_ids},
            )

    model.is_enabled = body.is_enabled
    await db.commit()
    await db.refresh(model)

    logger.info("model_toggled", model_id=str(model_id), is_enabled=body.is_enabled)
    return AvailableModelResponse(
        id=model.id,
        provider_id=model.provider_id,
        model_identifier=model.model_identifier,
        display_name=model.display_name,
        is_enabled=model.is_enabled,
        version_id=model.version_id,
    )
