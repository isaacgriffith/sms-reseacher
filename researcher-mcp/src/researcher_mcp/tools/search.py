"""MCP tools: search_papers and get_paper with cascade logic."""

from __future__ import annotations

from typing import Any

import httpx
from fastmcp import FastMCP

from researcher_mcp.core.config import get_settings
from researcher_mcp.core.http_client import make_retry_client
from researcher_mcp.sources.crossref import CrossRefSource
from researcher_mcp.sources.open_alex import OpenAlexSource
from researcher_mcp.sources.semantic_scholar import SemanticScholarSource

mcp: FastMCP = FastMCP("researcher-mcp")

_client: httpx.AsyncClient | None = None
_ss: SemanticScholarSource | None = None
_oa: OpenAlexSource | None = None
_cr: CrossRefSource | None = None


def _get_sources() -> tuple[SemanticScholarSource, OpenAlexSource, CrossRefSource]:
    """Return (lazily created) source singletons."""
    global _client, _ss, _oa, _cr
    if _client is None:
        settings = get_settings()
        _client = make_retry_client()
        _ss = SemanticScholarSource(_client, rpm=settings.semantic_scholar_rpm)
        _oa = OpenAlexSource(_client, rpm=settings.open_alex_rpm)
        _cr = CrossRefSource(_client)
    assert _ss is not None and _oa is not None and _cr is not None
    return _ss, _oa, _cr


@mcp.tool()
async def search_papers(
    query: str,
    limit: int = 10,
    year_from: int | None = None,
    year_to: int | None = None,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Search for academic papers across configured sources.

    Uses Semantic Scholar as the primary source with OpenAlex as cascade
    fallback on failure.

    Args:
        query: Free-text search query.
        limit: Maximum number of results (1–100).
        year_from: Earliest publication year filter.
        year_to: Latest publication year filter.
        fields: Fields to include in results.

    Returns:
        Dict with ``results``, ``total``, ``source``, and ``warnings``.
    """
    ss, oa, _ = _get_sources()
    try:
        return await ss.search_papers(query, limit, year_from, year_to, fields)
    except (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException):
        result = await oa.search_papers(query, limit, year_from, year_to, fields)
        return result


@mcp.tool()
async def get_paper(
    paper_id: str,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Retrieve full metadata for a single paper.

    For DOI-prefixed IDs (``DOI:10.xxxx/...``), CrossRef is queried first
    for enrichment; falls back through Semantic Scholar → OpenAlex.

    Args:
        paper_id: Semantic Scholar paper ID or DOI (prefix with ``DOI:``).
        fields: Fields to return.

    Returns:
        Dict matching the paper metadata schema.
    """
    ss, oa, cr = _get_sources()
    warnings: list[str] = []

    if paper_id.startswith("DOI:"):
        doi = paper_id[4:]
        try:
            cr_data = await cr.resolve_doi(doi)
            warnings.extend(cr_data.get("warnings", []))
            try:
                ss_data = await ss.get_paper(paper_id, fields)
                ss_data["warnings"] = warnings + ss_data.get("warnings", [])
                return ss_data
            except (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException):
                cr_data["warnings"] = warnings
                return cr_data
        except (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException):
            pass

    try:
        return await ss.get_paper(paper_id, fields)
    except (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException):
        result = await oa.get_paper(paper_id, fields)
        return result
