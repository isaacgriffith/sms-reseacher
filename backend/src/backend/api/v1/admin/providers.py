"""Admin endpoints for LLM provider management (Feature 005).

Exposes:
- ``GET /admin/providers`` — list all configured providers.
- ``POST /admin/providers`` — add a new provider.
- ``GET /admin/providers/{id}`` — get a single provider.
- ``PATCH /admin/providers/{id}`` — update a provider.
- ``DELETE /admin/providers/{id}`` — delete a provider (if no dependent agents).
- ``POST /admin/providers/{id}/refresh-models`` — re-fetch model list from provider API.
"""

from __future__ import annotations

import uuid

from db.models.agents import Provider, ProviderType
from db.models.users import GroupMembership, GroupRole
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services.provider_service import (
    ProviderCreate,
    ProviderFetchError,
    ProviderHasDependentsError,
    ProviderService,
    ProviderUpdate,
)

router = APIRouter(tags=["admin-providers"])
logger = get_logger(__name__)
_service = ProviderService()


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


class ProviderResponse(BaseModel):
    """API response schema for a Provider record.

    The ``api_key_encrypted`` field is never returned; instead ``has_api_key``
    indicates whether an API key is stored.

    Attributes:
        id: Provider UUID.
        provider_type: Enum value: anthropic, openai, or ollama.
        display_name: Unique human-readable name.
        has_api_key: True if an encrypted API key is stored.
        base_url: Optional base URL (Ollama only).
        is_enabled: Whether the provider is active.
        version_id: Optimistic-locking counter.

    """

    id: uuid.UUID
    provider_type: ProviderType
    display_name: str
    has_api_key: bool
    base_url: str | None
    is_enabled: bool
    version_id: int

    model_config = {"from_attributes": True}


class ModelRefreshResponse(BaseModel):
    """Response schema for a model-refresh operation.

    Attributes:
        models_added: Number of new models inserted.
        models_removed: Number of models no longer in the provider catalog.
        models_total: Total models stored after the refresh.

    """

    models_added: int
    models_removed: int
    models_total: int


def _provider_to_response(p: Provider) -> ProviderResponse:
    """Convert a Provider ORM instance to a :class:`ProviderResponse`.

    Args:
        p: Provider ORM instance.

    Returns:
        :class:`ProviderResponse` with ``has_api_key`` derived from the
        encrypted field rather than exposing it.

    """
    return ProviderResponse(
        id=p.id,
        provider_type=p.provider_type,
        display_name=p.display_name,
        has_api_key=p.api_key_encrypted is not None,
        base_url=p.base_url,
        is_enabled=p.is_enabled,
        version_id=p.version_id,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/providers",
    response_model=list[ProviderResponse],
    summary="List all LLM providers",
)
async def list_providers(
    _: None = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> list[ProviderResponse]:
    """Return all configured LLM providers.

    Args:
        _: Admin auth guard (injected).
        db: Injected async database session.

    Returns:
        List of :class:`ProviderResponse` objects.

    """
    providers = await _service.list_providers(db)
    return [_provider_to_response(p) for p in providers]


@router.post(
    "/providers",
    response_model=ProviderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new LLM provider",
)
async def create_provider(
    body: ProviderCreate,
    _: None = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> ProviderResponse:
    """Create a new provider and trigger an initial model-list refresh.

    The refresh is attempted after creation; a failure does not roll back
    the provider record — it is logged as a warning and the 201 is still
    returned.

    Args:
        body: Provider creation payload.
        _: Admin auth guard (injected).
        db: Injected async database session.

    Returns:
        The newly created :class:`ProviderResponse`.

    """
    provider = await _service.create_provider(body, db)
    try:
        await _service.refresh_models(provider.id, db)
    except (ProviderFetchError, Exception) as exc:  # noqa: BLE001
        logger.warning(
            "initial_model_refresh_failed",
            provider_id=str(provider.id),
            error=str(exc),
        )
    await db.refresh(provider)
    return _provider_to_response(provider)


@router.get(
    "/providers/{provider_id}",
    response_model=ProviderResponse,
    summary="Get a single LLM provider",
)
async def get_provider(
    provider_id: uuid.UUID,
    _: None = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> ProviderResponse:
    """Retrieve a single provider by ID.

    Args:
        provider_id: UUID of the provider.
        _: Admin auth guard (injected).
        db: Injected async database session.

    Returns:
        :class:`ProviderResponse` for the provider.

    Raises:
        HTTPException: 404 if not found.

    """
    provider = await _service.get_provider(provider_id, db)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    return _provider_to_response(provider)


@router.patch(
    "/providers/{provider_id}",
    response_model=ProviderResponse,
    summary="Partially update a provider",
)
async def update_provider(
    provider_id: uuid.UUID,
    body: ProviderUpdate,
    _: None = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> ProviderResponse:
    """Apply a partial update to a provider.

    Args:
        provider_id: UUID of the provider to update.
        body: Partial update payload.
        _: Admin auth guard (injected).
        db: Injected async database session.

    Returns:
        Updated :class:`ProviderResponse`.

    Raises:
        HTTPException: 404 if not found.

    """
    try:
        provider = await _service.update_provider(provider_id, body, db)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found"
        ) from exc
    return _provider_to_response(provider)


@router.delete(
    "/providers/{provider_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a provider",
)
async def delete_provider(
    provider_id: uuid.UUID,
    _: None = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> None:
    """Delete a provider if it has no dependent agents.

    Args:
        provider_id: UUID of the provider to delete.
        _: Admin auth guard (injected).
        db: Injected async database session.

    Raises:
        HTTPException: 404 if not found.
        HTTPException: 409 if agents reference this provider.

    """
    try:
        await _service.delete_provider(provider_id, db)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found"
        ) from exc
    except ProviderHasDependentsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": str(exc), "agent_ids": exc.agent_ids},
        ) from exc


@router.post(
    "/providers/{provider_id}/refresh-models",
    response_model=ModelRefreshResponse,
    summary="Refresh model list from provider API",
)
async def refresh_models(
    provider_id: uuid.UUID,
    _: None = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> ModelRefreshResponse:
    """Re-fetch the model catalog from the upstream provider API.

    Args:
        provider_id: UUID of the provider to refresh.
        _: Admin auth guard (injected).
        db: Injected async database session.

    Returns:
        :class:`ModelRefreshResponse` with add/remove/total counts.

    Raises:
        HTTPException: 404 if provider not found.
        HTTPException: 502 if the upstream provider API is unreachable.

    """
    try:
        result = await _service.refresh_models(provider_id, db)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found"
        ) from exc
    except ProviderFetchError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch models from provider: {exc}",
        ) from exc
    return ModelRefreshResponse(
        models_added=result.models_added,
        models_removed=result.models_removed,
        models_total=result.models_total,
    )
