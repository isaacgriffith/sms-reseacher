"""MCP tools: get_references and get_citations for snowball sampling.

Primary source: Semantic Scholar Graph API (paper references/citations endpoint).
Fallback: CrossRef works API when Semantic Scholar returns empty.
"""

from __future__ import annotations

import logging
from typing import Any, Literal

import httpx
from fastmcp import FastMCP

from researcher_mcp.core.config import get_settings
from researcher_mcp.core.http_client import make_retry_client
from researcher_mcp.sources.semantic_scholar import SemanticScholarSource

mcp: FastMCP = FastMCP("researcher-mcp")
logger = logging.getLogger(__name__)

_client: httpx.AsyncClient | None = None
_ss: SemanticScholarSource | None = None


def _get_ss() -> SemanticScholarSource:
    """Return (lazily created) SemanticScholar source singleton."""
    global _client, _ss
    if _client is None:
        settings = get_settings()
        _client = make_retry_client()
        _ss = SemanticScholarSource(_client, rpm=settings.semantic_scholar_rpm)
    assert _ss is not None
    return _ss


def _get_client() -> httpx.AsyncClient:
    """Return (lazily created) shared HTTP client."""
    global _client
    if _client is None:
        _client = make_retry_client()
    return _client


def _intent_from_category(
    cat: str | None,
) -> Literal["methodology", "background", "result", "unknown"]:
    """Map a Semantic Scholar intent category to our intent enum value.

    Args:
        cat: S2 intents category string, e.g. ``"methodology"``.

    Returns:
        One of ``"methodology"``, ``"background"``, ``"result"``, or
        ``"unknown"``.

    """
    mapping = {
        "methodology": "methodology",
        "background": "background",
        "result": "result",
        "extends": "methodology",
    }
    return mapping.get((cat or "").lower(), "unknown")  # type: ignore[return-value]


async def _get_references_semantic_scholar(doi: str, max_results: int) -> list[dict[str, Any]]:
    """Fetch references via Semantic Scholar Graph API.

    Args:
        doi: Paper DOI string.
        max_results: Maximum number of references to return.

    Returns:
        List of reference record dicts with ``title``, ``doi``, ``intent``,
        and ``citation_source`` keys.

    """
    ss = _get_ss()
    try:
        data = await ss._get(
            f"/paper/DOI:{doi}/references",
            {
                "fields": "title,externalIds,year,authors,intents",
                "limit": str(min(max_results, 500)),
            },
        )
    except (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException) as exc:
        logger.warning("S2 get_references failed doi=%s: %s", doi, exc)
        return []

    refs = []
    for item in data.get("data", []):
        cited = item.get("citedPaper") or {}
        first_intent = (item.get("intents") or ["unknown"])[0]
        refs.append(
            {
                "title": cited.get("title", ""),
                "doi": (cited.get("externalIds") or {}).get("DOI"),
                "year": cited.get("year"),
                "authors": [{"name": a.get("name")} for a in cited.get("authors", [])],
                "intent": _intent_from_category(first_intent),
                "citation_source": "semantic_scholar",
            }
        )
    return refs


async def _get_references_crossref(doi: str, max_results: int) -> list[dict[str, Any]]:
    """Fetch references via CrossRef works API as fallback.

    Args:
        doi: Paper DOI string.
        max_results: Maximum number of references to return.

    Returns:
        List of reference record dicts with ``citation_source="crossref"``.

    """
    client = _get_client()
    try:
        resp = await client.get(
            f"https://api.crossref.org/works/{doi}",
            params={"select": "reference"},
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        refs_raw = (data.get("message") or {}).get("reference") or []
    except (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException) as exc:
        logger.warning("CrossRef get_references failed doi=%s: %s", doi, exc)
        return []

    refs = []
    for item in refs_raw[:max_results]:
        refs.append(
            {
                "title": item.get("article-title") or item.get("unstructured", ""),
                "doi": item.get("DOI"),
                "year": item.get("year"),
                "authors": [],
                "intent": "unknown",
                "citation_source": "crossref",
            }
        )
    return refs


async def _get_citations_semantic_scholar(doi: str, max_results: int) -> list[dict[str, Any]]:
    """Fetch citing papers via Semantic Scholar Graph API.

    Args:
        doi: Paper DOI string.
        max_results: Maximum number of citing papers to return.

    Returns:
        List of citation record dicts with ``citation_source="semantic_scholar"``.

    """
    ss = _get_ss()
    try:
        data = await ss._get(
            f"/paper/DOI:{doi}/citations",
            {"fields": "title,externalIds,year,authors", "limit": str(min(max_results, 500))},
        )
    except (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException) as exc:
        logger.warning("S2 get_citations failed doi=%s: %s", doi, exc)
        return []

    cites = []
    for item in data.get("data", []):
        citing = item.get("citingPaper") or {}
        cites.append(
            {
                "title": citing.get("title", ""),
                "doi": (citing.get("externalIds") or {}).get("DOI"),
                "year": citing.get("year"),
                "authors": [{"name": a.get("name")} for a in citing.get("authors", [])],
                "citation_source": "semantic_scholar",
            }
        )
    return cites


async def _get_citations_crossref(doi: str, max_results: int) -> list[dict[str, Any]]:
    """Fetch citing papers via OpenAlex as CrossRef fallback.

    CrossRef does not provide a citing-works endpoint; uses OpenAlex instead.

    Args:
        doi: Paper DOI string.
        max_results: Maximum number of citing papers to return.

    Returns:
        List of citation record dicts with ``citation_source="crossref"``.

    """
    client = _get_client()
    try:
        resp = await client.get(
            "https://api.openalex.org/works",
            params={
                "filter": f"cites:doi:{doi}",
                "per-page": min(max_results, 50),
                "select": "id,doi,title,authorships,publication_year",
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException) as exc:
        logger.warning("OpenAlex get_citations fallback failed doi=%s: %s", doi, exc)
        return []

    cites = []
    for item in data.get("results", []):
        authorships = item.get("authorships", [])
        authors = [{"name": a.get("author", {}).get("display_name", "")} for a in authorships]
        cites.append(
            {
                "title": item.get("title", ""),
                "doi": item.get("doi", "").replace("https://doi.org/", "")
                if item.get("doi")
                else None,
                "year": item.get("publication_year"),
                "authors": authors,
                "citation_source": "crossref",
            }
        )
    return cites


async def get_references(doi: str, max_results: int = 200) -> list[dict[str, Any]]:
    """Fetch the reference list of a paper (backward snowball).

    Uses Semantic Scholar as primary source, falls back to CrossRef when S2
    returns no results.

    Args:
        doi: DOI of the source paper (e.g. ``"10.1145/3368089.3409682"``).
        max_results: Maximum number of references to return (1-200).

    Returns:
        List of reference record dicts, each with ``title``, ``doi``,
        ``year``, ``authors``, ``intent``, and ``citation_source`` fields.

    """
    max_results = max(1, min(max_results, 200))
    refs = await _get_references_semantic_scholar(doi, max_results)
    if not refs:
        refs = await _get_references_crossref(doi, max_results)
    return refs[:max_results]


async def get_citations(doi: str, max_results: int = 200) -> list[dict[str, Any]]:
    """Fetch papers that cite the given DOI (forward snowball).

    Uses Semantic Scholar as primary source, falls back to OpenAlex (as
    CrossRef substitute) when S2 returns no results.

    Args:
        doi: DOI of the source paper.
        max_results: Maximum number of citing papers to return (1-200).

    Returns:
        List of citation record dicts, each with ``title``, ``doi``,
        ``year``, ``authors``, and ``citation_source`` fields.

    """
    max_results = max(1, min(max_results, 200))
    cites = await _get_citations_semantic_scholar(doi, max_results)
    if not cites:
        cites = await _get_citations_crossref(doi, max_results)
    return cites[:max_results]
