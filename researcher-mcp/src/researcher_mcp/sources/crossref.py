"""CrossRef source for DOI resolution and metadata enrichment."""

from __future__ import annotations

from typing import Any

import httpx

from researcher_mcp.core.http_client import with_retry

_BASE = "https://api.crossref.org"


class CrossRefSource:
    """Queries CrossRef to resolve DOI metadata."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        """Initialise source.

        Args:
            client: Shared :class:`httpx.AsyncClient`.

        """
        self._client = client

    async def resolve_doi(self, doi: str) -> dict[str, Any]:
        """Resolve *doi* via CrossRef and return enriched paper metadata.

        Args:
            doi: The DOI string (without ``https://doi.org/`` prefix).

        Returns:
            A dict matching the shared paper schema with
            ``source="crossref"``.

        """
        url = f"{_BASE}/works/{doi}"

        async def _call() -> Any:
            r = await self._client.get(url)
            r.raise_for_status()
            return r.json()

        data = await with_retry(_call)
        work = data.get("message", {})
        authors = [
            {
                "name": f"{a.get('given', '')} {a.get('family', '')}".strip(),
                "author_id": None,
            }
            for a in work.get("author", [])
        ]
        title_list: list[str] = work.get("title", [])
        title = title_list[0] if title_list else ""
        year_parts = work.get("published", {}).get("date-parts", [[]])
        year = year_parts[0][0] if year_parts and year_parts[0] else None
        container: list[str] = work.get("container-title", [])
        venue = container[0] if container else None
        return {
            "paper_id": doi,
            "title": title,
            "abstract": work.get("abstract"),
            "doi": doi,
            "year": year,
            "authors": authors,
            "venue": venue,
            "citations": work.get("is-referenced-by-count"),
            "references": [],
            "source": "crossref",
            "warnings": [],
        }
