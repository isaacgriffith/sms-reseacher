"""MCP tools: get_references and get_citations for snowball sampling."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from researcher_mcp.core.http_client import make_retry_client

logger = logging.getLogger(__name__)

_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    """Return (lazily created) shared HTTP client."""
    global _client
    if _client is None:
        _client = make_retry_client()
    return _client


async def get_references(doi: str, max_results: int = 50) -> dict[str, Any]:
    """Fetch the reference list of a paper (backward snowball).

    Queries the OpenAlex API for papers cited by the given DOI.

    Args:
        doi: DOI of the source paper (e.g. ``"10.1145/3368089.3409682"``).
        max_results: Maximum number of references to return (1–200).

    Returns:
        Dict with ``references`` (list of paper dicts), ``total``, ``doi``, and
        ``warnings``.
    """
    client = _get_client()
    max_results = max(1, min(max_results, 200))
    warnings: list[str] = []
    references: list[dict[str, Any]] = []

    try:
        # OpenAlex: fetch the work by DOI, then retrieve its reference list
        oa_url = f"https://api.openalex.org/works/doi:{doi}"
        params: dict[str, Any] = {"select": "id,doi,title,referenced_works"}

        resp = await client.get(oa_url, params=params, timeout=30.0)
        resp.raise_for_status()
        work = resp.json()

        referenced_work_ids: list[str] = work.get("referenced_works", [])[:max_results]

        if referenced_work_ids:
            # Batch fetch metadata for referenced works
            ids_filter = "|".join(
                wid.split("/")[-1] for wid in referenced_work_ids
            )
            batch_resp = await client.get(
                "https://api.openalex.org/works",
                params={
                    "filter": f"openalex_id:{ids_filter}",
                    "per-page": min(len(referenced_work_ids), 50),
                    "select": "id,doi,title,authorships,publication_year,primary_location",
                },
                timeout=30.0,
            )
            batch_resp.raise_for_status()
            batch_data = batch_resp.json()
            for item in batch_data.get("results", []):
                references.append(_normalize_openalex_paper(item))

    except httpx.HTTPStatusError as exc:
        warnings.append(f"OpenAlex HTTP error: {exc.response.status_code}")
    except (httpx.TransportError, httpx.TimeoutException) as exc:
        warnings.append(f"OpenAlex connection error: {exc}")
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"get_references error: {exc}")

    return {
        "references": references,
        "total": len(references),
        "doi": doi,
        "warnings": warnings,
    }


async def get_citations(doi: str, max_results: int = 50) -> dict[str, Any]:
    """Fetch papers that cite the given DOI (forward snowball).

    Queries the OpenAlex API for papers that reference the given DOI.

    Args:
        doi: DOI of the source paper.
        max_results: Maximum number of citing papers to return (1–200).

    Returns:
        Dict with ``citations`` (list of paper dicts), ``total``, ``doi``, and
        ``warnings``.
    """
    client = _get_client()
    max_results = max(1, min(max_results, 200))
    warnings: list[str] = []
    citations: list[dict[str, Any]] = []

    try:
        # OpenAlex: citing_works filter
        resp = await client.get(
            "https://api.openalex.org/works",
            params={
                "filter": f"cites:doi:{doi}",
                "per-page": min(max_results, 50),
                "select": "id,doi,title,authorships,publication_year,primary_location",
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("results", []):
            citations.append(_normalize_openalex_paper(item))

    except httpx.HTTPStatusError as exc:
        warnings.append(f"OpenAlex HTTP error: {exc.response.status_code}")
    except (httpx.TransportError, httpx.TimeoutException) as exc:
        warnings.append(f"OpenAlex connection error: {exc}")
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"get_citations error: {exc}")

    return {
        "citations": citations,
        "total": len(citations),
        "doi": doi,
        "warnings": warnings,
    }


def _normalize_openalex_paper(item: dict[str, Any]) -> dict[str, Any]:
    """Normalize an OpenAlex work result into the standard paper dict format."""
    authorships = item.get("authorships", [])
    authors = [
        {
            "name": a.get("author", {}).get("display_name", ""),
            "institution": (
                a.get("institutions", [{}])[0].get("display_name", "")
                if a.get("institutions")
                else ""
            ),
        }
        for a in authorships
    ]
    primary_location = item.get("primary_location") or {}
    source = primary_location.get("source") or {}

    return {
        "title": item.get("title", ""),
        "doi": item.get("doi", "").replace("https://doi.org/", "") if item.get("doi") else None,
        "year": item.get("publication_year"),
        "authors": authors,
        "venue": source.get("display_name"),
        "source_url": item.get("doi"),
    }
