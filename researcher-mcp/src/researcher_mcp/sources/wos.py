"""Web of Science Starter API source adapter.

Implements the :class:`DatabaseSource` protocol using the Clarivate Web of
Science Starter API v1 at ``https://api.clarivate.com/apis/wos-starter/v1``.
"""

from __future__ import annotations

from typing import Any

import httpx

from researcher_mcp.sources.base import (
    AuthorInfo,
    PaperRecord,
    VenueType,
    normalise_doi,
    normalise_title,
)

_BASE_URL = "https://api.clarivate.com/apis/wos-starter/v1"


class WoSSource:
    """Wraps the Clarivate Web of Science Starter REST API.

    Attributes:
        _client: Shared :class:`httpx.AsyncClient`.
        _api_key: Clarivate WoS Starter API key.

    """

    def __init__(self, client: httpx.AsyncClient, api_key: str = "") -> None:
        """Initialise WoSSource.

        Args:
            client: Shared :class:`httpx.AsyncClient`.
            api_key: Clarivate WoS Starter API key.

        """
        self._client = client
        self._api_key = api_key

    def _headers(self) -> dict[str, str]:
        """Build required WoS API request headers.

        Returns:
            Dict of HTTP header key/value pairs.

        """
        return {
            "X-ApiKey": self._api_key,
            "Accept": "application/json",
        }

    def _normalise_record(self, item: dict[str, Any]) -> PaperRecord:
        """Convert a raw WoS Starter API record to a :class:`PaperRecord`.

        Args:
            item: A single record dict from the WoS Starter API response.

        Returns:
            A normalised :class:`PaperRecord`.

        """
        # Extract title from the identifiers section
        names = item.get("names", {})
        title_raw = item.get("title", "")
        if isinstance(title_raw, dict):
            title_raw = title_raw.get("value", "")
        elif not title_raw:
            for t in item.get("titles", []):
                if t.get("type") == "item":
                    title_raw = t.get("title", "")
                    break
        title = normalise_title(str(title_raw))

        # Extract DOI from identifiers
        doi: str | None = None
        for ident in item.get("identifiers", {}).get("doi", []):
            doi = normalise_doi(str(ident))
            break

        # Extract authors
        authors: list[AuthorInfo] = []
        for author in names.get("authors", []):
            display = author.get("displayName") or author.get("wosStandard") or ""
            if display:
                authors.append(AuthorInfo(name=display))

        # Extract publication year
        year: int | None = None
        pub_year = item.get("source", {}).get("publishYear")
        if pub_year:
            try:
                year = int(pub_year)
            except ValueError, TypeError:
                pass

        # Extract venue
        venue = item.get("source", {}).get("sourceTitle")

        # Determine venue type
        doc_type = str(item.get("doctype", {}).get("code", "")).upper()
        venue_type: VenueType | None = None
        if doc_type in ("J", "JA", "JR"):
            venue_type = "journal"
        elif doc_type in ("C", "CP"):
            venue_type = "conference"
        elif doc_type in ("B", "BC"):
            venue_type = "book"

        uid = item.get("uid", "")
        url = f"https://www.webofscience.com/wos/woscc/full-record/{uid}" if uid else None

        return PaperRecord(
            doi=doi,
            title=title,
            abstract=item.get("abstract", {}).get("text", [{}])[0].get("value")
            if item.get("abstract")
            else None,
            authors=authors,
            year=year,
            venue=venue,
            venue_type=venue_type,
            url=url,
            source_database="web_of_science",
            raw_id=uid,
        )

    async def search(
        self,
        query: str,
        max_results: int = 100,
        year_from: int | None = None,
        year_to: int | None = None,
        edition: str | None = None,
    ) -> list[PaperRecord]:
        """Search Web of Science for papers matching *query*.

        Args:
            query: WoS query string (supports field tags like ``TS=``, ``TI=``).
            max_results: Maximum records to return.
            year_from: Earliest publication year filter.
            year_to: Latest publication year filter.
            edition: WoS database edition (``"WOS"``, ``"MEDLINE"``, ``"BIOSIS"``).

        Returns:
            List of :class:`PaperRecord` objects.

        Raises:
            httpx.HTTPStatusError: On 401/403 responses.
            httpx.TransportError: On network failures.

        """
        params: dict[str, Any] = {
            "q": query,
            "limit": min(max_results, 50),
            "page": 1,
        }
        if year_from:
            params["publishTimeSpan"] = f"{year_from}01-{year_to or 9999}12"
        if edition:
            params["edition"] = edition

        r = await self._client.get(
            f"{_BASE_URL}/documents",
            params=params,
            headers=self._headers(),
        )
        r.raise_for_status()
        data = r.json()
        hits = data.get("hits", [])
        return [self._normalise_record(h) for h in hits]

    async def get_paper(self, doi: str) -> PaperRecord | None:
        """Retrieve a single paper from WoS by DOI.

        Args:
            doi: Paper DOI without the ``https://doi.org/`` prefix.

        Returns:
            A :class:`PaperRecord` if found, or ``None``.

        """
        params: dict[str, Any] = {
            "q": f"DO={doi}",
            "limit": 1,
        }
        try:
            r = await self._client.get(
                f"{_BASE_URL}/documents",
                params=params,
                headers=self._headers(),
            )
            r.raise_for_status()
        except httpx.HTTPStatusError, httpx.TransportError:
            return None

        hits = r.json().get("hits", [])
        if not hits:
            return None
        return self._normalise_record(hits[0])
