"""Admin endpoints for search integration credential management (Feature 006).

Exposes:
- ``GET /admin/search-integrations`` — list all integration credential summaries.
- ``GET /admin/search-integrations/{type}`` — single integration summary.
- ``PUT /admin/search-integrations/{type}`` — upsert (create or update) credentials.
- ``POST /admin/search-integrations/{type}/test`` — run a connectivity probe.

All endpoints require the ``admin`` role.  Raw key bytes are **never** returned.
"""

from __future__ import annotations

from db.models.search_integrations import IntegrationType, SearchIntegrationCredential
from db.models.users import GroupMembership, GroupRole
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.config import get_logger
from backend.core.database import get_db
from backend.services.credential_service import CredentialService, VersionConflictError

router = APIRouter(tags=["admin-search-integrations"])
logger = get_logger(__name__)
_service = CredentialService()

# ---------------------------------------------------------------------------
# Integration metadata
# ---------------------------------------------------------------------------

_DISPLAY = {
    IntegrationType.IEEE_XPLORE: ("IEEE Xplore", "official_api"),
    IntegrationType.ELSEVIER: ("Elsevier (Scopus/SciDirect/Inspec)", "subscription_required"),
    IntegrationType.WEB_OF_SCIENCE: ("Web of Science", "subscription_required"),
    IntegrationType.SPRINGER_NATURE: ("Springer Nature", "official_api"),
    IntegrationType.SEMANTIC_SCHOLAR: ("Semantic Scholar", "official_api"),
    IntegrationType.UNPAYWALL: ("Unpaywall", "official_api"),
    IntegrationType.GOOGLE_SCHOLAR: ("Google Scholar", "unofficial_scraping"),
}

# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------


async def _require_admin(
    current_user: CurrentUser = Depends(get_current_user),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> None:
    """Raise HTTP 403 if the caller is not a group admin.

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


class IntegrationSummary(BaseModel):
    """API response schema for a single search integration credential record.

    Raw key bytes are **never** included; only ``has_api_key`` and
    ``configured_via`` indicate key availability.
    """

    integration_type: str
    display_name: str
    access_type: str
    has_api_key: bool
    has_auxiliary_token: bool
    configured_via: str
    last_tested_at: str | None
    last_test_status: str | None
    version_id: int


class PutCredentialRequest(BaseModel):
    """Request body for PUT /admin/search-integrations/{type}.

    Passing ``api_key=None`` clears the stored key (integration falls back to
    the env-var).  ``version_id`` is required when updating an existing record
    (optimistic locking).
    """

    api_key: str | None = None
    auxiliary_token: str | None = None
    config_json: dict | None = None
    version_id: int | None = None


class TestResult(BaseModel):
    """Response from POST /admin/search-integrations/{type}/test."""

    integration_type: str
    status: str
    message: str
    tested_at: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_summary(
    integration_type: IntegrationType,
    cred: SearchIntegrationCredential | None,
) -> IntegrationSummary:
    """Build an :class:`IntegrationSummary` from an ORM row and type metadata.

    Args:
        integration_type: The :class:`IntegrationType` for this record.
        cred: The ORM credential row, or ``None`` if not persisted yet.

    Returns:
        :class:`IntegrationSummary` suitable for the API response.

    """
    display_name, access_type = _DISPLAY.get(integration_type, (integration_type.value, "unknown"))
    configured_via = _service.configured_via(integration_type, cred)
    return IntegrationSummary(
        integration_type=integration_type.value,
        display_name=display_name,
        access_type=access_type,
        has_api_key=bool(cred and cred.api_key_encrypted),
        has_auxiliary_token=bool(cred and cred.auxiliary_token_encrypted),
        configured_via=configured_via,
        last_tested_at=cred.last_tested_at.isoformat() if cred and cred.last_tested_at else None,
        last_test_status=cred.last_test_status.value if cred and cred.last_test_status else None,
        version_id=cred.version_id if cred else 0,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/search-integrations",
    response_model=list[IntegrationSummary],
    summary="List all search integration credentials",
)
async def list_search_integrations(
    _: None = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[IntegrationSummary]:
    """Return a summary for every known :class:`IntegrationType`.

    The response always contains all types (not just those with stored credentials).
    Raw keys are never included.

    Args:
        _: Admin guard dependency (raises 403 if not admin).
        db: Injected async database session.

    Returns:
        List of :class:`IntegrationSummary` objects — one per :class:`IntegrationType`.

    """
    result = await db.execute(select(SearchIntegrationCredential))
    creds: dict[IntegrationType, SearchIntegrationCredential] = {
        c.integration_type: c for c in result.scalars().all()
    }
    return [_to_summary(it, creds.get(it)) for it in IntegrationType]


@router.get(
    "/search-integrations/{integration_type}",
    response_model=IntegrationSummary,
    summary="Get a single search integration credential",
)
async def get_search_integration(
    integration_type: str,
    _: None = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
) -> IntegrationSummary:
    """Return the credential summary for a single integration type.

    Args:
        integration_type: String value of the :class:`IntegrationType`.
        _: Admin guard dependency.
        db: Injected async database session.

    Returns:
        :class:`IntegrationSummary` for the requested type.

    Raises:
        HTTPException: 404 if ``integration_type`` is not a valid value.

    """
    try:
        it = IntegrationType(integration_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown integration type: {integration_type!r}",
        ) from exc
    cred = await _service.get_credential(it, db)
    return _to_summary(it, cred)


@router.put(
    "/search-integrations/{integration_type}",
    response_model=IntegrationSummary,
    summary="Create or update search integration credentials",
)
async def upsert_search_integration(
    integration_type: str,
    body: PutCredentialRequest,
    _: None = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
) -> IntegrationSummary:
    """Upsert the credential record for an integration type.

    Passing ``api_key: null`` clears the stored key (env-var fallback).
    ``version_id`` is required for updates (omit for first creation).

    Args:
        integration_type: String value of the :class:`IntegrationType`.
        body: Credential update payload.
        _: Admin guard dependency.
        db: Injected async database session.

    Returns:
        Updated :class:`IntegrationSummary`.

    Raises:
        HTTPException: 404 if ``integration_type`` is not a valid value.
        HTTPException: 409 if the ``version_id`` does not match the stored record.

    """
    try:
        it = IntegrationType(integration_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown integration type: {integration_type!r}",
        ) from exc
    try:
        cred = await _service.upsert_credential(
            integration_type=it,
            api_key=body.api_key,
            auxiliary_token=body.auxiliary_token,
            config_json=body.config_json,
            version_id=body.version_id,
            db=db,
        )
    except VersionConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Version conflict: the record was modified by another request",
        ) from exc
    return _to_summary(it, cred)


@router.post(
    "/search-integrations/{integration_type}/test",
    response_model=TestResult,
    summary="Test connectivity for a search integration",
)
async def test_search_integration(
    integration_type: str,
    _: None = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
) -> TestResult:
    """Run a lightweight connectivity probe for an integration type.

    The result is persisted to ``last_tested_at`` / ``last_test_status`` on
    the credential record.

    Args:
        integration_type: String value of the :class:`IntegrationType`.
        _: Admin guard dependency.
        db: Injected async database session.

    Returns:
        :class:`TestResult` with ``status``, ``message``, and ``tested_at``.

    Raises:
        HTTPException: 404 if ``integration_type`` is not a valid value.

    """
    try:
        it = IntegrationType(integration_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown integration type: {integration_type!r}",
        ) from exc
    cred = await _service.get_credential(it, db)
    result = await _service.run_connectivity_test(it, cred, db)
    return TestResult(
        integration_type=integration_type,
        status=result["status"],
        message=result["message"],
        tested_at=result["tested_at"],
    )
