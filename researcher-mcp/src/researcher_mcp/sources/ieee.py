"""IEEE Xplore REST API source adapter.

Implements the :class:`DatabaseSource` protocol by calling the IEEE Xplore
REST API v1 at ``https://ieeexploreapi.ieee.org/api/v1/search/articles``.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from researcher_mcp.sources.base import (
    AuthorInfo,
    PaperRecord,
    VenueType,
    normalise_doi,
    normalise_title,
)

_BASE_URL = "https://ieeexploreapi.ieee.org/api/v1/search/articles"


class IEEESource:
    """Wraps the IEEE Xplore REST API for academic paper search and retrieval.

    Requires a valid ``IEEEXPLORE_API_KEY``.  Calls are made synchronously in
    a thread via :func:`asyncio.to_thread` to comply with the async-discipline
    requirement (Constitution Principle IX).

    Attributes:
        _api_key: IEEE Xplore REST API key.
        _client: Shared :class:`httpx.AsyncClient`.

    """

    def __init__(self, client: httpx.AsyncClient, api_key: str = "") -> None:
        """Initialise the IEEESource.

        Args:
            client: Shared :class:`httpx.AsyncClient`.
            api_key: IEEE Xplore API key.  An empty string results in 401
                responses from the API.

        """
        self._client = client
        self._api_key = api_key

    def _normalise_record(self, item: dict[str, Any]) -> PaperRecord:
        """Convert a raw IEEE Xplore article record to a :class:`PaperRecord`.

        Args:
            item: A single article dict from the IEEE Xplore API response.

        Returns:
            A normalised :class:`PaperRecord`.

        """
        raw_authors: list[Any] = item.get("authors", {}).get("authors", [])
        authors = [
            AuthorInfo(
                name=a.get("full_name", ""),
                institution=a.get("affiliation"),
            )
            for a in raw_authors
            if a.get("full_name")
        ]

        doi = normalise_doi(item.get("doi"))
        title = normalise_title(item.get("title") or "")
        year_raw = item.get("publication_year")
        year = int(year_raw) if year_raw else None

        venue_type: VenueType | None = None
        content_type = item.get("content_type", "")
        if "Journal" in content_type:
            venue_type = "journal"
        elif "Conference" in content_type:
            venue_type = "conference"

        return PaperRecord(
            doi=doi,
            title=title,
            abstract=item.get("abstract"),
            authors=authors,
            year=year,
            venue=item.get("publication_title"),
            venue_type=venue_type,
            url=item.get("html_url") or item.get("pdf_url"),
            open_access=bool(item.get("open_access_flag", False)),
            source_database="ieee_xplore",
            raw_id=str(item.get("article_number", "")),
        )

    async def _get(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a GET request to the IEEE Xplore API.

        Args:
            params: Query parameters dict.

        Returns:
            Parsed JSON response body as a dict.

        Raises:
            httpx.HTTPStatusError: On 4xx/5xx responses.
            httpx.TransportError: On network failures.

        """
        headers = {"apikey": self._api_key}

        async def _call() -> dict[str, Any]:
            r = await self._client.get(_BASE_URL, params=params, headers=headers)
            r.raise_for_status()
            return r.json()  # type: ignore[return-value]

        return await asyncio.to_thread(_call)  # type: ignore[arg-type]

    async def search(
        self,
        query: str,
        max_results: int = 100,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[PaperRecord]:
        """Search IEEE Xplore for papers matching *query*.

        Args:
            query: Free-text or boolean search query.
            max_results: Maximum number of records to return (capped at 200 by
                the API).
            year_from: Earliest publication year (inclusive).
            year_to: Latest publication year (inclusive).

        Returns:
            List of :class:`PaperRecord` objects, possibly empty on failure.

        Raises:
            httpx.HTTPStatusError: On authentication or server errors.
            httpx.TransportError: On network failures.

        """
        params: dict[str, Any] = {
            "querytext": query,
            "max_records": min(max_results, 200),
            "start_record": 1,
            "sort_order": "desc",
            "sort_field": "article_number",
        }
        if year_from:
            params["start_year"] = year_from
        if year_to:
            params["end_year"] = year_to

        async def _fetch() -> dict[str, Any]:
            r = await self._client.get(_BASE_URL, params=params, headers={"apikey": self._api_key})
            r.raise_for_status()
            return r.json()  # type: ignore[return-value]

        data = await _fetch()
        articles: list[dict[str, Any]] = data.get("articles", [])
        return [self._normalise_record(a) for a in articles]

    async def get_paper(self, doi: str) -> PaperRecord | None:
        """Retrieve a single paper from IEEE Xplore by DOI.

        Args:
            doi: Paper DOI without the ``https://doi.org/`` prefix.

        Returns:
            A :class:`PaperRecord` if found, or ``None``.

        """
        params: dict[str, Any] = {"doi": doi, "max_records": 1}

        async def _fetch() -> dict[str, Any]:
            r = await self._client.get(_BASE_URL, params=params, headers={"apikey": self._api_key})
            r.raise_for_status()
            return r.json()  # type: ignore[return-value]

        try:
            data = await _fetch()
        except httpx.HTTPStatusError, httpx.TransportError:
            return None

        articles = data.get("articles", [])
        if not articles:
            return None
        return self._normalise_record(articles[0])

    async def get_paper_by_article_number(self, article_number: str) -> PaperRecord | None:
        """Retrieve a single paper by IEEE article number.

        Args:
            article_number: The IEEE-native article identifier string.

        Returns:
            A :class:`PaperRecord` if found, or ``None``.

        """
        params: dict[str, Any] = {"article_number": article_number, "max_records": 1}

        async def _fetch() -> dict[str, Any]:
            r = await self._client.get(_BASE_URL, params=params, headers={"apikey": self._api_key})
            r.raise_for_status()
            return r.json()  # type: ignore[return-value]

        try:
            data = await _fetch()
        except httpx.HTTPStatusError, httpx.TransportError:
            return None

        articles = data.get("articles", [])
        if not articles:
            return None
        return self._normalise_record(articles[0])
