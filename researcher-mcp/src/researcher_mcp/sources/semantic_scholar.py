"""Semantic Scholar API source."""

from __future__ import annotations

from typing import Any

import httpx

from researcher_mcp.core.http_client import TokenBucket, with_retry

_BASE = "https://api.semanticscholar.org/graph/v1"


class SemanticScholarSource:
    """Wraps the Semantic Scholar Graph API."""

    def __init__(self, client: httpx.AsyncClient, rpm: int = 100) -> None:
        """Initialise source.

        Args:
            client: Shared :class:`httpx.AsyncClient`.
            rpm: Requests-per-minute cap (token bucket).

        """
        self._client = client
        self._bucket = TokenBucket(rpm)

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Execute a GET with rate limiting and retry."""
        await self._bucket.acquire()
        url = f"{_BASE}{path}"

        async def _call() -> Any:
            r = await self._client.get(url, params=params)
            r.raise_for_status()
            return r.json()

        return await with_retry(_call)

    async def search_papers(
        self,
        query: str,
        limit: int = 10,
        year_from: int | None = None,
        year_to: int | None = None,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Search papers on Semantic Scholar."""
        params: dict[str, Any] = {
            "query": query,
            "limit": limit,
            "fields": ",".join(fields or ["title", "externalIds", "year", "authors"]),
        }
        if year_from or year_to:
            lo = year_from or ""
            hi = year_to or ""
            params["year"] = f"{lo}-{hi}"
        data = await self._get("/paper/search", params)
        papers = []
        for p in data.get("data", []):
            papers.append(
                {
                    "title": p.get("title"),
                    "doi": (p.get("externalIds") or {}).get("DOI"),
                    "year": p.get("year"),
                    "abstract": p.get("abstract"),
                    "authors": [
                        {"name": a.get("name"), "author_id": a.get("authorId")}
                        for a in p.get("authors", [])
                    ],
                    "venue": p.get("venue"),
                    "citations": p.get("citationCount"),
                    "paper_id": p.get("paperId", ""),
                }
            )
        return {
            "results": papers,
            "total": data.get("total", len(papers)),
            "source": "semantic_scholar",
            "warnings": [],
        }

    async def get_paper(self, paper_id: str, fields: list[str] | None = None) -> dict[str, Any]:
        """Retrieve full metadata for a single paper."""
        f = ",".join(
            fields or ["title", "abstract", "externalIds", "year", "authors", "references"]
        )
        data = await self._get(f"/paper/{paper_id}", {"fields": f})
        refs = [
            {"title": r.get("title"), "doi": (r.get("externalIds") or {}).get("DOI")}
            for r in data.get("references", [])
        ]
        return {
            "paper_id": data.get("paperId", paper_id),
            "title": data.get("title"),
            "abstract": data.get("abstract"),
            "doi": (data.get("externalIds") or {}).get("DOI"),
            "year": data.get("year"),
            "authors": [
                {"name": a.get("name"), "author_id": a.get("authorId")}
                for a in data.get("authors", [])
            ],
            "venue": data.get("venue"),
            "citations": data.get("citationCount"),
            "references": refs,
            "source": "semantic_scholar",
            "warnings": [],
        }

    async def search_authors(self, query: str, limit: int = 10) -> dict[str, Any]:
        """Search authors by name."""
        data = await self._get(
            "/author/search",
            {"query": query, "limit": limit, "fields": "name,affiliations,paperCount,hIndex"},
        )
        authors = [
            {
                "author_id": a.get("authorId", ""),
                "name": a.get("name", ""),
                "affiliations": a.get("affiliations", []),
                "paper_count": a.get("paperCount"),
                "h_index": a.get("hIndex"),
            }
            for a in data.get("data", [])
        ]
        return {"results": authors, "source": "semantic_scholar", "warnings": []}

    async def get_author(self, author_id: str, limit: int = 50) -> dict[str, Any]:
        """Retrieve full profile and papers for a single author."""
        data = await self._get(
            f"/author/{author_id}",
            {"fields": f"name,affiliations,paperCount,hIndex,papers.limit({limit})"},
        )
        papers = [
            {
                "paper_id": p.get("paperId", ""),
                "title": p.get("title", ""),
                "year": p.get("year"),
                "doi": (p.get("externalIds") or {}).get("DOI"),
                "citations": p.get("citationCount"),
            }
            for p in data.get("papers", [])
        ]
        return {
            "author_id": data.get("authorId", author_id),
            "name": data.get("name", ""),
            "affiliations": data.get("affiliations", []),
            "paper_count": data.get("paperCount"),
            "h_index": data.get("hIndex"),
            "papers": papers,
            "source": "semantic_scholar",
            "warnings": [],
        }
