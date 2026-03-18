"""MCP tool: fetch_paper_pdf with Unpaywall -> direct URL -> SciHub cascade.

Priority waterfall:
1. Unpaywall (open-access metadata from unpywall library)
2. Direct URL (user-supplied URL downloaded via httpx)
3. SciHub (opt-in only; both server-level SCIHUB_ENABLED and allow_scihub=True required)
"""

from __future__ import annotations

import base64
import logging
from typing import Any

import httpx
from fastmcp import FastMCP

from researcher_mcp.core.config import get_settings
from researcher_mcp.core.http_client import make_retry_client
from researcher_mcp.sources.scihub import MCPError, SciHubSource
from researcher_mcp.sources.unpaywall import UnpaywallSource

mcp: FastMCP = FastMCP("researcher-mcp")
logger = logging.getLogger(__name__)

_UNAVAILABLE: dict[str, Any] = {
    "available": False,
    "source": "unavailable",
    "pdf_bytes_b64": None,
    "open_access_url": None,
}


async def _try_unpaywall(doi: str, email: str) -> dict[str, Any]:
    """Attempt Unpaywall OA lookup for *doi*.

    Args:
        doi: Paper DOI string.
        email: Unpaywall API identification email.

    Returns:
        Dict with ``available``, ``source``, ``pdf_bytes_b64``, and
        ``open_access_url`` keys.

    """
    client = make_retry_client()
    src = UnpaywallSource(client, email=email)
    return await src.fetch_pdf(doi)


async def _try_direct(url: str) -> dict[str, Any]:
    """Download a PDF directly from *url*.

    Args:
        url: Direct PDF URL supplied by the caller.

    Returns:
        Dict with ``available``, ``source``, ``pdf_bytes_b64``, and
        ``open_access_url`` keys.

    """
    try:
        client = make_retry_client()
        resp = await client.get(url, follow_redirects=True, timeout=60.0)
        resp.raise_for_status()
        pdf_bytes_b64 = base64.b64encode(resp.content).decode()
        return {
            "available": True,
            "source": "direct",
            "pdf_bytes_b64": pdf_bytes_b64,
            "open_access_url": url,
        }
    except (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException) as exc:
        logger.warning("_try_direct failed url=%s: %s", url, exc)
        return _UNAVAILABLE


async def _try_scihub(doi: str, scihub_enabled: bool, scihub_url: str) -> dict[str, Any]:
    """Attempt SciHub retrieval for *doi*.

    Args:
        doi: Paper DOI string.
        scihub_enabled: Server-level SciHub enablement flag.
        scihub_url: Base URL of the SciHub mirror.

    Returns:
        Dict with ``available``, ``source``, ``pdf_bytes_b64``, and
        ``open_access_url`` keys.

    """
    src = SciHubSource(scihub_enabled=scihub_enabled, scihub_url=scihub_url)
    return await src.fetch_pdf(doi)


@mcp.tool()
async def fetch_paper_pdf(
    doi: str,
    url: str | None = None,
    allow_scihub: bool = False,
) -> dict[str, Any]:
    """Fetch a paper PDF from open-access sources using a priority waterfall.

    Cascade order: Unpaywall -> direct URL (if *url* provided) -> SciHub (opt-in
    only: requires both SCIHUB_ENABLED=true server setting AND
    allow_scihub=True in this call).

    Args:
        doi: Paper DOI string (required for Unpaywall and SciHub lookups).
        url: Optional direct PDF URL to try if Unpaywall has no OA copy.
        allow_scihub: Caller opt-in to SciHub.  Only honoured when the server
            has SCIHUB_ENABLED=true configured.

    Returns:
        Dict with ``available``, ``source``, ``pdf_bytes_b64``, and
        ``open_access_url`` keys.  ``source`` is one of
        "unpaywall", "direct", "scihub", or "unavailable".

    """
    settings = get_settings()

    # Step 1: Unpaywall
    result = await _try_unpaywall(doi, settings.unpaywall_email)
    if result["available"]:
        return result

    # Step 2: Direct URL
    if url:
        result = await _try_direct(url)
        if result["available"]:
            return result

    # Step 3: SciHub - dual gate: server-level + caller opt-in
    if allow_scihub and settings.scihub_enabled:
        try:
            result = await _try_scihub(doi, settings.scihub_enabled, settings.scihub_url)
            if result["available"]:
                return result
        except MCPError:
            pass  # SCIHUB_DISABLED raised by source as defence-in-depth

    return _UNAVAILABLE
