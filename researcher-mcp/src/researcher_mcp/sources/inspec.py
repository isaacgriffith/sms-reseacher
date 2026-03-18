"""Inspec (Engineering Village) source adapter.

Implements the :class:`DatabaseSource` protocol using the Elsevier Engineering
Village REST API.  Requires ``ELSEVIER_API_KEY`` (and optionally
``ELSEVIER_INST_TOKEN`` for institutional access).
"""

from __future__ import annotations

from typing import Any

import httpx

from researcher_mcp.sources.base import (
    AuthorInfo,
    PaperRecord,
    normalise_doi,
    normalise_title,
)

_BASE_URL = "https://api.elsevier.com/content/ev/results"
_DEFAULT_DATABASES = ["INS", "CPX"]


class InspecSource:
    """Searches the Inspec database via the Elsevier Engineering Village REST API.

    Attributes:
        _client: Shared :class:`httpx.AsyncClient`.
        _api_key: Elsevier API key.
        _inst_token: Elsevier institutional token for expanded access.

    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        api_key: str = "",
        inst_token: str = "",
    ) -> None:
        """Initialise InspecSource.

        Args:
            client: Shared :class:`httpx.AsyncClient`.
            api_key: Elsevier API key.
            inst_token: Elsevier institutional token (optional).

        """
        self._client = client
        self._api_key = api_key
        self._inst_token = inst_token

    def _headers(self) -> dict[str, str]:
        """Build the required Elsevier API request headers.

        Returns:
            Dict of HTTP header key/value pairs.

        """
        headers = {
            "X-ELS-APIKey": self._api_key,
            "Accept": "application/json",
        }
        if self._inst_token:
            headers["X-ELS-Insttoken"] = self._inst_token
        return headers

    def _normalise_record(self, item: dict[str, Any]) -> PaperRecord:
        """Convert a raw Engineering Village record to a :class:`PaperRecord`.

        Args:
            item: A single record dict from the EV API response.

        Returns:
            A normalised :class:`PaperRecord`.

        """
        coredata = item.get("coredata", item)
        title = normalise_title(coredata.get("dc:title") or coredata.get("title") or "")
        doi = normalise_doi(coredata.get("prism:doi") or coredata.get("doi"))

        raw_authors = coredata.get("authors", {}).get("author", [])
        if isinstance(raw_authors, dict):
            raw_authors = [raw_authors]
        authors = [
            AuthorInfo(
                name=a.get("preferred-name", {}).get("$") or a.get("$", ""),
                institution=a.get("affiliation", {}).get("$"),
            )
            for a in raw_authors
            if isinstance(a, dict)
        ]

        year_raw = coredata.get("prism:coverDate") or coredata.get("prism:coverDisplayDate", "")
        year: int | None = None
        if year_raw:
            import re

            m = re.search(r"\b(19|20)\d{2}\b", str(year_raw))
            if m:
                year = int(m.group(0))

        return PaperRecord(
            doi=doi,
            title=title,
            abstract=coredata.get("dc:description"),
            authors=authors,
            year=year,
            venue=coredata.get("prism:publicationName"),
            url=coredata.get("prism:url") or coredata.get("link", [{}])[0].get("@href"),
            source_database="inspec",
            raw_id=coredata.get("eid") or coredata.get("dc:identifier"),
        )

    async def search(
        self,
        query: str,
        max_results: int = 100,
        year_from: int | None = None,
        year_to: int | None = None,
        databases: list[str] | None = None,
    ) -> list[PaperRecord]:
        """Search Engineering Village / Inspec for papers.

        Args:
            query: Keyword or boolean search string.
            max_results: Maximum number of records to return.
            year_from: Earliest publication year filter.
            year_to: Latest publication year filter.
            databases: List of EV database codes (default: ``["INS", "CPX"]``).

        Returns:
            List of :class:`PaperRecord` objects.

        Raises:
            httpx.HTTPStatusError: On 401 (auth failed) or 403 (access denied).
            httpx.TransportError: On network failures.

        """
        dbs = "|".join(databases or _DEFAULT_DATABASES)
        params: dict[str, Any] = {
            "query": query,
            "database": dbs,
            "count": min(max_results, 100),
            "start": 1,
            "view": "COMPLETE",
        }
        if year_from:
            params["pub-date-start"] = f"{year_from}0101"
        if year_to:
            params["pub-date-end"] = f"{year_to}1231"

        r = await self._client.get(_BASE_URL, params=params, headers=self._headers())
        r.raise_for_status()
        data = r.json()
        results = data.get("results-found", {}).get("entry", []) or data.get(
            "search-results", {}
        ).get("entry", [])
        if isinstance(results, dict):
            results = [results]
        return [self._normalise_record(e) for e in results]

    async def get_paper(self, doi: str) -> PaperRecord | None:
        """Retrieve a single paper from Engineering Village by DOI.

        Args:
            doi: Paper DOI without the ``https://doi.org/`` prefix.

        Returns:
            A :class:`PaperRecord` if found, or ``None``.

        """
        params: dict[str, Any] = {
            "query": f"doi({doi})",
            "database": "|".join(_DEFAULT_DATABASES),
            "count": 1,
        }
        try:
            r = await self._client.get(_BASE_URL, params=params, headers=self._headers())
            r.raise_for_status()
        except httpx.HTTPStatusError, httpx.TransportError:
            return None

        data = r.json()
        results = data.get("results-found", {}).get("entry", []) or data.get(
            "search-results", {}
        ).get("entry", [])
        if isinstance(results, dict):
            results = [results]
        if not results:
            return None
        return self._normalise_record(results[0])
