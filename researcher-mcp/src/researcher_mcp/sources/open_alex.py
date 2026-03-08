"""OpenAlex source — cascade fallback for paper search and retrieval."""

from __future__ import annotations

from typing import Any

import httpx

from researcher_mcp.core.http_client import TokenBucket, with_retry

_BASE = "https://api.openalex.org"


class OpenAlexSource:
    """Wraps the OpenAlex API as a cascade fallback for paper data."""

    def __init__(self, client: httpx.AsyncClient, rpm: int = 300) -> None:
        """Initialise source.

        Args:
            client: Shared :class:`httpx.AsyncClient`.
            rpm: Requests-per-minute cap.
        """
        self._client = client
        self._bucket = TokenBucket(rpm)

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET with rate limiting and retry."""
        await self._bucket.acquire()
        url = f"{_BASE}{path}"

        async def _call() -> Any:
            r = await self._client.get(url, params=params)
            r.raise_for_status()
            return r.json()

        return await with_retry(_call)

    def _map_work(self, work: dict[str, Any]) -> dict[str, Any]:
        """Map an OpenAlex 'work' object to the shared paper schema."""
        doi_raw: str = work.get("doi") or ""
        doi = doi_raw.removeprefix("https://doi.org/") if doi_raw else None
        authors = [
            {
                "name": a.get("author", {}).get("display_name", ""),
                "author_id": a.get("author", {}).get("id"),
            }
            for a in work.get("authorships", [])
        ]
        return {
            "title": work.get("title"),
            "doi": doi,
            "year": work.get("publication_year"),
            "abstract": None,
            "authors": authors,
            "venue": (work.get("primary_location") or {}).get("source", {}).get("display_name"),
            "citations": work.get("cited_by_count"),
            "paper_id": work.get("id", ""),
        }

    async def search_papers(
        self,
        query: str,
        limit: int = 10,
        year_from: int | None = None,
        year_to: int | None = None,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Search papers via OpenAlex full-text search."""
        params: dict[str, Any] = {
            "search": query,
            "per-page": limit,
            "select": "id,title,doi,publication_year,authorships,primary_location,cited_by_count",
        }
        if year_from or year_to:
            lo = year_from or 1000
            hi = year_to or 9999
            params["filter"] = f"publication_year:{lo}-{hi}"
        data = await self._get("/works", params)
        results = [self._map_work(w) for w in data.get("results", [])]
        return {
            "results": results,
            "total": data.get("meta", {}).get("count", len(results)),
            "source": "open_alex",
            "warnings": ["Served by OpenAlex (Semantic Scholar unavailable)"],
        }

    async def get_paper(self, paper_id: str, fields: list[str] | None = None) -> dict[str, Any]:
        """Retrieve paper metadata from OpenAlex by DOI or OpenAlex ID."""
        if paper_id.startswith("DOI:"):
            doi = paper_id[4:]
            path = f"/works/https://doi.org/{doi}"
        else:
            path = f"/works/{paper_id}"
        data = await self._get(path)
        result = self._map_work(data)
        result["references"] = []
        result["source"] = "open_alex"
        result["warnings"] = ["Served by OpenAlex (Semantic Scholar unavailable)"]
        return result
