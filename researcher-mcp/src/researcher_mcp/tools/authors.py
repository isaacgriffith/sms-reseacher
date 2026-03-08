"""MCP tools: search_authors and get_author via SemanticScholar."""

from __future__ import annotations

from typing import Any

import httpx
from fastmcp import FastMCP

from researcher_mcp.core.config import get_settings
from researcher_mcp.core.http_client import make_retry_client
from researcher_mcp.sources.semantic_scholar import SemanticScholarSource

mcp: FastMCP = FastMCP("researcher-mcp")

_client: httpx.AsyncClient | None = None
_ss: SemanticScholarSource | None = None


def _get_ss() -> SemanticScholarSource:
    global _client, _ss
    if _client is None:
        settings = get_settings()
        _client = make_retry_client()
        _ss = SemanticScholarSource(_client, rpm=settings.semantic_scholar_rpm)
    assert _ss is not None
    return _ss


@mcp.tool()
async def search_authors(
    query: str,
    limit: int = 10,
) -> dict[str, Any]:
    """Search for academic authors by name.

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
    """Retrieve full profile and publication list for a single author.

    Args:
        author_id: Semantic Scholar author ID.
        limit: Maximum papers to include in the profile.

    Returns:
        Dict with author profile and papers list.
    """
    return await _get_ss().get_author(author_id, limit)
