"""Service for per-study database index selection management.

Provides :class:`StudyDatabaseSelectionService` which handles reading,
saving, and computing status for study database selections.
"""

from __future__ import annotations

import os
from typing import Any

from db.models.search_integrations import (
    DatabaseIndex,
    IntegrationType,
    SearchIntegrationCredential,
    StudyDatabaseSelection,
    TestStatus,
)
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------------------------------------------------------
# Index metadata (display name, whether a credential is required, access type)
# ---------------------------------------------------------------------------

_INDEX_META: dict[str, dict[str, Any]] = {
    "ieee_xplore": {
        "requires_credential": True,
        "integration_type": IntegrationType.IEEE_XPLORE,
        "access_type": "official_api",
    },
    "acm_dl": {
        "requires_credential": False,
        "integration_type": None,
        "access_type": "unofficial_scraping",
    },
    "scopus": {
        "requires_credential": True,
        "integration_type": IntegrationType.ELSEVIER,
        "access_type": "subscription_required",
    },
    "web_of_science": {
        "requires_credential": True,
        "integration_type": IntegrationType.WEB_OF_SCIENCE,
        "access_type": "subscription_required",
    },
    "inspec": {
        "requires_credential": True,
        "integration_type": IntegrationType.ELSEVIER,
        "access_type": "subscription_required",
    },
    "science_direct": {
        "requires_credential": True,
        "integration_type": IntegrationType.ELSEVIER,
        "access_type": "subscription_required",
    },
    "springer_link": {
        "requires_credential": True,
        "integration_type": IntegrationType.SPRINGER_NATURE,
        "access_type": "official_api",
    },
    "google_scholar": {
        "requires_credential": False,
        "integration_type": IntegrationType.GOOGLE_SCHOLAR,
        "access_type": "unofficial_scraping",
    },
    "semantic_scholar": {
        "requires_credential": False,
        "integration_type": IntegrationType.SEMANTIC_SCHOLAR,
        "access_type": "official_api",
    },
}

# Env-var fallbacks: if these are non-empty, credential is available
_ENV_FALLBACKS: dict[IntegrationType, str] = {
    IntegrationType.IEEE_XPLORE: "IEEE_XPLORE_API_KEY",
    IntegrationType.ELSEVIER: "ELSEVIER_API_KEY",
    IntegrationType.WEB_OF_SCIENCE: "WOS_API_KEY",
    IntegrationType.SPRINGER_NATURE: "SPRINGER_API_KEY",
    IntegrationType.SEMANTIC_SCHOLAR: "SEMANTIC_SCHOLAR_API_KEY",
    IntegrationType.UNPAYWALL: "UNPAYWALL_EMAIL",
    IntegrationType.GOOGLE_SCHOLAR: "SCHOLARLY_PROXY_URL",
}


class StudyDatabaseSelectionService:
    """Manages per-study database index selection persistence and status computation.

    All methods are async and require an active :class:`AsyncSession`.
    """

    async def get_selection(self, study_id: int, db: AsyncSession) -> dict[str, Any]:
        """Return the current database selection for a study.

        If no selection has been saved, returns the default (Semantic Scholar
        enabled, all others disabled).

        Args:
            study_id: Integer study primary key.
            db: Active async database session.

        Returns:
            Dict matching the ``GET /studies/{study_id}/database-selection``
            response schema.

        """
        result = await db.execute(
            select(StudyDatabaseSelection).where(StudyDatabaseSelection.study_id == study_id)
        )
        rows = {row.database_index.value: row for row in result.scalars().all()}

        # Build credentials map: integration_type → credential row
        cred_result = await db.execute(select(SearchIntegrationCredential))
        creds: dict[IntegrationType, SearchIntegrationCredential] = {
            c.integration_type: c for c in cred_result.scalars().all()
        }

        selections = []
        for index_value in DatabaseIndex:
            meta = _INDEX_META.get(index_value.value, {})
            is_enabled = False
            if index_value.value in rows:
                is_enabled = rows[index_value.value].is_enabled
            elif index_value == DatabaseIndex.SEMANTIC_SCHOLAR:
                is_enabled = True  # Default: Semantic Scholar enabled

            status, cred_configured = self._compute_index_status(
                integration_type=meta.get("integration_type"),
                creds=creds,
            )
            selections.append(
                {
                    "database_index": index_value.value,
                    "is_enabled": is_enabled,
                    "status": status,
                    "requires_credential": meta.get("requires_credential", False),
                    "credential_configured": cred_configured,
                }
            )

        return {
            "study_id": study_id,
            "selections": selections,
            "snowball_enabled": False,
            "scihub_enabled": False,
            "scihub_acknowledged": False,
        }

    async def save_selection(
        self,
        study_id: int,
        selections: list[dict[str, Any]],
        snowball_enabled: bool,
        scihub_enabled: bool,
        scihub_acknowledged: bool,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Persist the database index selection for a study.

        Replaces all existing selection rows for the study.

        Args:
            study_id: Integer study primary key.
            selections: List of dicts with ``database_index`` and ``is_enabled``.
            snowball_enabled: Whether snowball search is enabled.
            scihub_enabled: Whether SciHub retrieval is enabled for this study.
            scihub_acknowledged: Whether the user has acknowledged SciHub risks.
            db: Active async database session.

        Returns:
            Updated selection dict (same schema as :meth:`get_selection`).

        """
        # Delete existing selection rows
        await db.execute(
            delete(StudyDatabaseSelection).where(StudyDatabaseSelection.study_id == study_id)
        )

        # Insert new rows
        for sel in selections:
            row = StudyDatabaseSelection(
                study_id=study_id,
                database_index=DatabaseIndex(sel["database_index"]),
                is_enabled=sel["is_enabled"],
            )
            db.add(row)

        await db.commit()
        result = await self.get_selection(study_id, db)
        result["snowball_enabled"] = snowball_enabled
        result["scihub_enabled"] = scihub_enabled
        result["scihub_acknowledged"] = scihub_acknowledged
        return result

    def _compute_index_status(
        self,
        integration_type: IntegrationType | None,
        creds: dict[IntegrationType, SearchIntegrationCredential],
    ) -> tuple[str, bool]:
        """Compute the status string and credential_configured flag for an index.

        Checks the DB credential record first, then falls back to env vars.

        Args:
            integration_type: The :class:`IntegrationType` for this index, or
                ``None`` if no credential is required.
            creds: Map of integration type to loaded credential rows.

        Returns:
            Tuple of ``(status_string, credential_configured_bool)``.
            Status is one of ``"configured"``, ``"not_configured"``, or
            ``"unreachable"``.

        """
        if integration_type is None:
            return ("configured", False)

        # Check DB credential
        cred = creds.get(integration_type)
        if cred and cred.api_key_encrypted:
            status = "configured"
            if cred.last_test_status == TestStatus.UNREACHABLE:
                status = "unreachable"
            return (status, True)

        # Check env-var fallback
        env_var = _ENV_FALLBACKS.get(integration_type, "")
        if env_var and os.environ.get(env_var, "").strip():
            return ("configured", False)

        return ("not_configured", False)
