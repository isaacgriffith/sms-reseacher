"""FastMCP server entrypoint for researcher-mcp."""

from __future__ import annotations

import logging

from fastmcp import FastMCP

from researcher_mcp.core.registry import build_default_registry, set_registry
from researcher_mcp.tools.authors import get_author, search_authors
from researcher_mcp.tools.convert import convert_paper_to_markdown, get_paper_markdown
from researcher_mcp.tools.pdf import fetch_paper_pdf
from researcher_mcp.tools.scraper import scrape_author_page, scrape_journal
from researcher_mcp.tools.search import (
    get_ieee_paper,
    get_paper,
    get_paper_semantic_scholar,
    get_scopus_paper,
    search_acm,
    search_google_scholar,
    search_ieee,
    search_inspec,
    search_papers,
    search_sciencedirect,
    search_scopus,
    search_semantic_scholar,
    search_springer,
    search_wos,
)
from researcher_mcp.tools.snowball import get_citations, get_references

logger = logging.getLogger(__name__)

# Initialise default source registry
set_registry(build_default_registry())

mcp = FastMCP(
    "researcher-mcp",
    instructions=(
        "SMS Researcher MCP server. Provides tools for searching academic papers, "
        "retrieving author profiles, and fetching open-access PDFs."
    ),
)

mcp.add_tool(search_papers)
mcp.add_tool(get_paper)
mcp.add_tool(search_ieee)
mcp.add_tool(get_ieee_paper)
mcp.add_tool(search_acm)
mcp.add_tool(search_google_scholar)
mcp.add_tool(search_inspec)
mcp.add_tool(search_scopus)
mcp.add_tool(get_scopus_paper)
mcp.add_tool(search_wos)
mcp.add_tool(search_sciencedirect)
mcp.add_tool(search_springer)
mcp.add_tool(search_semantic_scholar)
mcp.add_tool(get_paper_semantic_scholar)
mcp.add_tool(search_authors)
mcp.add_tool(get_author)
mcp.add_tool(fetch_paper_pdf)
mcp.add_tool(get_references)
mcp.add_tool(get_citations)
mcp.add_tool(scrape_journal)
mcp.add_tool(scrape_author_page)
mcp.add_tool(convert_paper_to_markdown)
mcp.add_tool(get_paper_markdown)


def main() -> None:
    """Start the FastMCP server on 0.0.0.0:8002.

    Legal notice: SciHub access is opt-in only (SCIHUB_ENABLED=true).
    Users are solely responsible for compliance with applicable copyright
    law in their jurisdiction.
    """
    import uvicorn

    logging.basicConfig(level=logging.INFO)
    logger.info("Starting researcher-mcp server on 0.0.0.0:8002")
    logger.warning(
        "SciHub: disabled by default. Set SCIHUB_ENABLED=true to enable "
        "(ensure compliance with local copyright law)."
    )
    uvicorn.run(mcp.http_app(), host="0.0.0.0", port=8002)


if __name__ == "__main__":
    main()
