"""SpringerLink source adapter via springernature-api-client.

Implements the :class:`DatabaseSource` protocol using the
``springernature_api_client.MetaAPI`` for searching the SpringerNature
Metadata API.  All calls are synchronous and wrapped in :func:`asyncio.to_thread`.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any

from researcher_mcp.sources.base import (
    AuthorInfo,
    PaperRecord,
    VenueType,
    normalise_doi,
    normalise_title,
)


class SpringerSource:
    """Searches SpringerLink via the SpringerNature Metadata API.

    Uses ``springernature_api_client.MetaAPI`` wrapped in
    :func:`asyncio.to_thread`.

    Attributes:
        _api_key: SpringerNature API key.

    """

    def __init__(self, api_key: str = "") -> None:
        """Initialise SpringerSource.

        Args:
            api_key: SpringerNature Metadata API key.

        """
        self._api_key = api_key

    def _normalise_record(self, item: dict[str, Any]) -> PaperRecord:
        """Convert a raw SpringerNature metadata record to a :class:`PaperRecord`.

        Args:
            item: A single record dict from the Springer Metadata API.

        Returns:
            A normalised :class:`PaperRecord`.

        """
        doi = normalise_doi(item.get("doi"))
        title = normalise_title(item.get("title", "") or "")

        raw_creators = item.get("creators", [])
        authors: list[AuthorInfo] = []
        for creator in raw_creators:
            name = creator.get("creator", "") or ""
            if name:
                authors.append(AuthorInfo(name=name))

        year: int | None = None
        pub_date = item.get("publicationDate", "") or item.get("onlineDate", "")
        if pub_date:
            m = re.search(r"\b(19|20)\d{2}\b", str(pub_date))
            if m:
                year = int(m.group(0))

        content_type = item.get("contentType", "")
        venue_type: VenueType | None = None
        if "Journal" in content_type:
            venue_type = "journal"
        elif "Chapter" in content_type or "Book" in content_type:
            venue_type = "book"
        elif "Conference" in content_type:
            venue_type = "conference"

        url = item.get("url", [{}])[0].get("value") if item.get("url") else None

        return PaperRecord(
            doi=doi,
            title=title,
            abstract=item.get("abstract"),
            authors=authors,
            year=year,
            venue=item.get("publicationName"),
            venue_type=venue_type,
            url=url,
            open_access=bool(item.get("openaccess") == "true" or item.get("openaccess") is True),
            source_database="springer_link",
            raw_id=item.get("identifier") or item.get("doi"),
        )

    async def search(
        self,
        query: str,
        max_results: int = 100,
        year_from: int | None = None,
        year_to: int | None = None,
        open_access_only: bool = False,
    ) -> list[PaperRecord]:
        """Search SpringerNature Metadata API for papers matching *query*.

        Args:
            query: Free-text search query.
            max_results: Maximum records to return.
            year_from: Earliest publication year filter.
            year_to: Latest publication year filter.
            open_access_only: If True, restrict to open-access content.

        Returns:
            List of :class:`PaperRecord` objects.

        """

        def _run() -> list[PaperRecord]:
            from springernature_api_client import MetaAPI  # noqa: PLC0415

            api = MetaAPI(api_key=self._api_key)
            params: dict[str, Any] = {
                "q": query,
                "p": min(max_results, 50),
                "s": 1,
            }
            if year_from:
                params["dateFrom"] = f"{year_from}-01-01"
            if year_to:
                params["dateTo"] = f"{year_to}-12-31"
            if open_access_only:
                params["openaccess"] = "true"

            result = api.search(**params)
            records: list[dict[str, Any]] = []
            if isinstance(result, dict):
                records = result.get("records", []) or result.get("result", [])
            return [self._normalise_record(r) for r in records[:max_results]]

        try:
            return await asyncio.to_thread(_run)
        except Exception:  # noqa: BLE001
            return []

    async def get_paper(self, doi: str) -> PaperRecord | None:
        """Retrieve a SpringerNature paper by DOI.

        Args:
            doi: Paper DOI without the ``https://doi.org/`` prefix.

        Returns:
            A :class:`PaperRecord` if found, or ``None``.

        """

        def _run() -> PaperRecord | None:
            from springernature_api_client import MetaAPI  # noqa: PLC0415

            api = MetaAPI(api_key=self._api_key)
            try:
                result = api.search(q=f"doi:{doi}", p=1)
            except Exception:  # noqa: BLE001
                return None

            if not isinstance(result, dict):
                return None
            records = result.get("records", []) or result.get("result", [])
            if not records:
                return None
            return self._normalise_record(records[0])

        try:
            return await asyncio.to_thread(_run)
        except Exception:  # noqa: BLE001
            return None
