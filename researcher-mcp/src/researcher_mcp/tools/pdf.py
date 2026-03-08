"""MCP tool: fetch_paper_pdf with Unpaywall → arXiv → SciHub cascade."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from researcher_mcp.core.config import get_settings
from researcher_mcp.core.http_client import make_retry_client
from researcher_mcp.sources.arxiv import ArxivSource
from researcher_mcp.sources.scihub import MCPError, SciHubSource
from researcher_mcp.sources.unpaywall import UnpaywallSource

mcp: FastMCP = FastMCP("researcher-mcp")


@mcp.tool()
async def fetch_paper_pdf(
    doi: str,
    output_path: str,
) -> dict[str, Any]:
    """Attempt to fetch a paper PDF from open-access sources.

    Cascade order: Unpaywall → arXiv → SciHub (opt-in only).

    Args:
        doi: Paper DOI string.
        output_path: Local filesystem path to save the downloaded PDF.

    Returns:
        Dict with ``success``, ``output_path``, ``source``, ``url``,
        and ``warnings`` keys.
    """
    settings = get_settings()
    client = make_retry_client()
    warnings: list[str] = []

    unpaywall = UnpaywallSource(client, email=settings.unpaywall_email)
    result = await unpaywall.fetch_pdf(doi, output_path)
    if result["success"]:
        return result
    warnings.extend(result.get("warnings", []))

    arxiv = ArxivSource(client)
    result = await arxiv.fetch_pdf(doi, output_path)
    if result["success"]:
        return result
    warnings.extend(result.get("warnings", []))

    scihub = SciHubSource(
        client,
        scihub_enabled=settings.scihub_enabled,
        scihub_url=settings.scihub_url,
    )
    try:
        result = await scihub.fetch_pdf(doi, output_path)
        if result["success"]:
            return result
        warnings.extend(result.get("warnings", []))
    except MCPError as exc:
        warnings.append(str(exc))

    return {
        "success": False,
        "output_path": None,
        "source": None,
        "url": None,
        "warnings": warnings,
    }
