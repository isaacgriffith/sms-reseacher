"""MCP tools: author search and profile retrieval via Semantic Scholar.

Provides both the legacy dict-returning tools (search_authors, get_author)
and the new strongly-typed tools (search_author_semantic_scholar,
get_author_semantic_scholar) that return Pydantic models.
"""

from __future__ import annotations

from typing import Any

import httpx
from fastmcp import FastMCP

from researcher_mcp.core.config import get_settings
from researcher_mcp.core.http_client import make_retry_client
from researcher_mcp.sources.base import AuthorDetail, AuthorProfile, PaperRecord
from researcher_mcp.sources.semantic_scholar import SemanticScholarSource

mcp: FastMCP = FastMCP("researcher-mcp")

_client: httpx.AsyncClient | None = None
_ss: SemanticScholarSource | None = None


def _get_ss() -> SemanticScholarSource:
    """Return or initialise the shared SemanticScholarSource instance.

    Returns:
        The cached :class:`SemanticScholarSource` instance.

    """
    global _client, _ss
    if _client is None:
        settings = get_settings()
        _client = make_retry_client()
        _ss = SemanticScholarSource(_client, rpm=settings.semantic_scholar_rpm)
    assert _ss is not None
    return _ss


def _map_author_profile(raw: dict[str, Any]) -> AuthorProfile:
    """Map a raw SemanticScholarSource author dict to an AuthorProfile.

    Args:
        raw: Dict as returned by :meth:`SemanticScholarSource.search_authors`.

    Returns:
        :class:`AuthorProfile` with normalised fields.

    """
    return AuthorProfile(
        author_id=raw.get("author_id", ""),
        name=raw.get("name", ""),
        affiliations=raw.get("affiliations") or [],
        paper_count=raw.get("paper_count") or 0,
        citation_count=raw.get("citation_count") or 0,
        h_index=raw.get("h_index") or 0,
        profile_url=f"https://www.semanticscholar.org/author/{raw.get('author_id', '')}",
        fields_of_study=raw.get("fields_of_study") or [],
    )


def _map_paper(p: dict[str, Any]) -> PaperRecord:
    """Map a raw paper dict from get_author to a PaperRecord.

    Args:
        p: Raw paper dict with paper_id, title, year, doi, citations keys.

    Returns:
        :class:`PaperRecord` with normalised fields.

    """
    return PaperRecord(
        doi=p.get("doi"),
        title=p.get("title") or "",
        year=p.get("year"),
        source_database="semantic_scholar",
        raw_id=p.get("paper_id"),
        authors=[],
    )


@mcp.tool()
async def search_authors(
    query: str,
    limit: int = 10,
) -> dict[str, Any]:
    """Search for academic authors by name (legacy dict response).

    Args:
        query: Author name query string.
        limit: Maximum number of results.

    Returns:
        Dict with ``results``, ``source``, and ``warnings``.

    """
    return await _get_ss().search_authors(query, limit)


@mcp.tool()
async def get_author(
    author_id: str,
    limit: int = 50,
) -> dict[str, Any]:
    """Retrieve full profile and publication list for a single author (legacy dict response).

    Args:
        author_id: Semantic Scholar author ID.
        limit: Maximum papers to include in the profile.

    Returns:
        Dict with author profile and papers list.

    """
    return await _get_ss().get_author(author_id, limit)


@mcp.tool()
async def search_author_semantic_scholar(
    name: str,
    institution: str | None = None,
    limit: int = 10,
) -> list[AuthorProfile]:
    """Search for academic authors by name via Semantic Scholar.

    Args:
        name: Author name to search for.
        institution: Optional institution filter appended to the query.
        limit: Maximum number of author profiles to return.

    Returns:
        List of :class:`AuthorProfile` objects, possibly empty.

    """
    query = name
    if institution:
        query = f"{name} {institution}"
    raw = await _get_ss().search_authors(query, limit)
    return [_map_author_profile(a) for a in raw.get("results", [])]


@mcp.tool()
async def get_author_semantic_scholar(author_id: str) -> AuthorDetail:
    """Retrieve a full author profile including paper list from Semantic Scholar.

    Args:
        author_id: Semantic Scholar author identifier.

    Returns:
        :class:`AuthorDetail` with profile fields and a ``papers`` list.

    """
    raw = await _get_ss().get_author(author_id)
    profile = _map_author_profile(raw)
    papers = [_map_paper(p) for p in raw.get("papers", [])]
    return AuthorDetail(**profile.model_dump(), papers=papers)
