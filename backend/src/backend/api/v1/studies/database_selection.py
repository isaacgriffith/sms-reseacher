"""Database selection endpoints for per-study academic index configuration.

Exposes:
- ``GET /studies/{study_id}/database-selection`` — return current selection.
- ``PUT /studies/{study_id}/database-selection`` — save selection.
"""

from __future__ import annotations

import os
from typing import Any

from db.models.search_integrations import DatabaseIndex
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user, require_study_member
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services.database_selection import StudyDatabaseSelectionService

router = APIRouter(tags=["database-selection"])
logger = get_logger(__name__)
_service = StudyDatabaseSelectionService()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class DatabaseSelectionItem(BaseModel):
    """A single database index toggle in a PUT request.

    Attributes:
        database_index: One of the :class:`DatabaseIndex` enum values.
        is_enabled: Whether this index should be enabled for the study.

    """

    database_index: str
    is_enabled: bool

    @field_validator("database_index")
    @classmethod
    def validate_database_index(cls, v: str) -> str:
        """Validate that database_index is a known DatabaseIndex value.

        Args:
            v: The raw string value to validate.

        Returns:
            The validated string value.

        Raises:
            ValueError: If the value is not a valid DatabaseIndex.

        """
        valid = {e.value for e in DatabaseIndex}
        if v not in valid:
            raise ValueError(f"Invalid database_index: {v!r}. Must be one of {sorted(valid)}")
        return v


class PutDatabaseSelectionRequest(BaseModel):
    """Request body for PUT /studies/{study_id}/database-selection.

    Attributes:
        selections: List of index toggles to save.
        snowball_enabled: Whether snowball citation search is enabled.
        scihub_enabled: Whether SciHub retrieval is enabled for this study.
        scihub_acknowledged: User acknowledgment of SciHub legal/ethical risks.

    """

    selections: list[DatabaseSelectionItem]
    snowball_enabled: bool = False
    scihub_enabled: bool = False
    scihub_acknowledged: bool = False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/studies/{study_id}/database-selection",
    summary="Get study database index selection",
)
async def get_database_selection(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict[str, Any]:
    """Return the database index selection for a study.

    If no selection has been saved, returns the default (Semantic Scholar
    enabled, all others disabled).

    Args:
        study_id: Integer study primary key from the URL path.
        current_user: Injected authenticated user.
        db: Injected async database session.

    Returns:
        Dict with ``study_id``, ``selections``, ``snowball_enabled``,
        ``scihub_enabled``, and ``scihub_acknowledged``.

    Raises:
        HTTPException: 401 if unauthenticated.
        HTTPException: 403 if the user is not a member of the study.
        HTTPException: 404 if the study does not exist.

    """
    await require_study_member(study_id, current_user, db)
    return await _service.get_selection(study_id, db)


@router.put(
    "/studies/{study_id}/database-selection",
    summary="Save study database index selection",
)
async def put_database_selection(
    study_id: int,
    body: PutDatabaseSelectionRequest,
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict[str, Any]:
    """Save the database index selection for a study.

    SciHub dual-gate: ``scihub_enabled=True`` requires both
    ``scihub_acknowledged=True`` in the request body AND
    ``SCIHUB_ENABLED=true`` in the server environment.

    Args:
        study_id: Integer study primary key from the URL path.
        body: :class:`PutDatabaseSelectionRequest` with the new selection.
        current_user: Injected authenticated user.
        db: Injected async database session.

    Returns:
        Updated selection dict (same schema as GET response).

    Raises:
        HTTPException: 401 if unauthenticated.
        HTTPException: 403 if the user is not a study member, or if
            ``scihub_enabled=True`` but server-level ``SCIHUB_ENABLED`` is false.
        HTTPException: 404 if the study does not exist.
        HTTPException: 422 if ``scihub_enabled=True`` without acknowledgment.

    """
    await require_study_member(study_id, current_user, db)

    if body.scihub_enabled:
        if not body.scihub_acknowledged:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "scihub_acknowledged must be true when scihub_enabled is true. "
                    "Acknowledge that SciHub use must comply with local copyright law."
                ),
            )
        server_scihub = os.environ.get("SCIHUB_ENABLED", "false").lower() in ("true", "1", "yes")
        if not server_scihub:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "SciHub is not enabled on this server. "
                    "Set SCIHUB_ENABLED=true to allow SciHub access."
                ),
            )

    logger.info(
        "database_selection_updated",
        study_id=study_id,
        user_id=current_user.user_id,
        index_count=len(body.selections),
    )

    return await _service.save_selection(
        study_id=study_id,
        selections=[s.model_dump() for s in body.selections],
        snowball_enabled=body.snowball_enabled,
        scihub_enabled=body.scihub_enabled,
        scihub_acknowledged=body.scihub_acknowledged,
        db=db,
    )
