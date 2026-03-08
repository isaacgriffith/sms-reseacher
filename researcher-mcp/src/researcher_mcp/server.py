"""FastMCP server entrypoint for researcher-mcp."""

from __future__ import annotations

import logging

from fastmcp import FastMCP

from researcher_mcp.tools.authors import get_author, search_authors
from researcher_mcp.tools.pdf import fetch_paper_pdf
from researcher_mcp.tools.scraper import scrape_author_page, scrape_journal
from researcher_mcp.tools.search import get_paper, search_papers
from researcher_mcp.tools.snowball import get_citations, get_references

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "researcher-mcp",
    instructions=(
        "SMS Researcher MCP server. Provides tools for searching academic papers, "
        "retrieving author profiles, and fetching open-access PDFs."
    ),
)

mcp.add_tool(search_papers)
mcp.add_tool(get_paper)
mcp.add_tool(search_authors)
mcp.add_tool(get_author)
mcp.add_tool(fetch_paper_pdf)
mcp.add_tool(get_references)
mcp.add_tool(get_citations)
mcp.add_tool(scrape_journal)
mcp.add_tool(scrape_author_page)


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
