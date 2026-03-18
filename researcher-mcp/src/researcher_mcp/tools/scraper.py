"""MCP tools: scrape_journal and scrape_author_page for supplemental discovery."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from researcher_mcp.core.http_client import make_retry_client

logger = logging.getLogger(__name__)

_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    """Return (lazily created) shared HTTP client."""
    global _client
    if _client is None:
        _client = make_retry_client()
    return _client


async def scrape_journal(
    journal_url: str,
    year_from: int | None = None,
    year_to: int | None = None,
    max_results: int = 50,
) -> dict[str, Any]:
    """Scrape a journal or proceedings page to discover papers.

    Fetches the URL and extracts paper links/titles from the HTML.
    This is a best-effort scraper; results vary by site structure.

    Args:
        journal_url: URL of the journal TOC or proceedings index page.
        year_from: Earliest publication year to include (optional filter).
        year_to: Latest publication year to include (optional filter).
        max_results: Maximum number of papers to return.

    Returns:
        Dict with ``papers`` (list of minimal paper dicts), ``source_url``,
        ``total``, and ``warnings``.

    """
    client = _get_client()
    warnings: list[str] = []
    papers: list[dict[str, Any]] = []

    try:
        headers = {"User-Agent": "SMS-Researcher/1.0 (academic research tool)"}
        resp = await client.get(journal_url, headers=headers, timeout=30.0, follow_redirects=True)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        base_url = f"{urlparse(journal_url).scheme}://{urlparse(journal_url).netloc}"

        # Extract candidate paper links — look for common academic site patterns
        seen_hrefs: set[str] = set()
        for tag in soup.find_all("a", href=True):
            href: str = tag["href"]
            text = tag.get_text(strip=True)

            # Skip navigation/non-paper links
            if not text or len(text) < 10:
                continue
            if any(kw in href.lower() for kw in ["login", "register", "cart", "javascript"]):
                continue

            full_url = urljoin(base_url, href) if not href.startswith("http") else href
            if full_url in seen_hrefs:
                continue
            seen_hrefs.add(full_url)

            papers.append(
                {
                    "title": text[:512],
                    "source_url": full_url,
                    "doi": None,
                    "year": None,
                    "authors": [],
                    "venue": journal_url,
                }
            )

            if len(papers) >= max_results:
                break

    except httpx.HTTPStatusError as exc:
        warnings.append(f"HTTP error {exc.response.status_code} fetching {journal_url}")
    except (httpx.TransportError, httpx.TimeoutException) as exc:
        warnings.append(f"Connection error: {exc}")
    except Exception as exc:  # noqa: BLE001
        logger.warning("scrape_journal error: %s", exc)
        warnings.append(f"Scraping error: {exc}")

    return {
        "papers": papers,
        "source_url": journal_url,
        "total": len(papers),
        "warnings": warnings,
    }


async def scrape_author_page(
    profile_url: str,
    max_results: int = 50,
) -> dict[str, Any]:
    """Scrape an author profile page to extract their paper list.

    Args:
        profile_url: URL of the author's profile page (Google Scholar,
            DBLP, personal page, etc.).
        max_results: Maximum number of papers to return.

    Returns:
        Dict with ``papers`` (list of minimal paper dicts), ``source_url``,
        ``total``, and ``warnings``.

    """
    client = _get_client()
    warnings: list[str] = []
    papers: list[dict[str, Any]] = []

    try:
        headers = {"User-Agent": "SMS-Researcher/1.0 (academic research tool)"}
        resp = await client.get(profile_url, headers=headers, timeout=30.0, follow_redirects=True)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        base_url = f"{urlparse(profile_url).scheme}://{urlparse(profile_url).netloc}"

        seen_hrefs: set[str] = set()
        for tag in soup.find_all("a", href=True):
            href: str = tag["href"]
            text = tag.get_text(strip=True)

            if not text or len(text) < 10:
                continue
            if any(kw in href.lower() for kw in ["login", "register", "javascript"]):
                continue

            full_url = urljoin(base_url, href) if not href.startswith("http") else href
            if full_url in seen_hrefs:
                continue
            seen_hrefs.add(full_url)

            papers.append(
                {
                    "title": text[:512],
                    "source_url": full_url,
                    "doi": None,
                    "year": None,
                    "authors": [],
                    "venue": None,
                }
            )

            if len(papers) >= max_results:
                break

    except httpx.HTTPStatusError as exc:
        warnings.append(f"HTTP error {exc.response.status_code} fetching {profile_url}")
    except (httpx.TransportError, httpx.TimeoutException) as exc:
        warnings.append(f"Connection error: {exc}")
    except Exception as exc:  # noqa: BLE001
        logger.warning("scrape_author_page error: %s", exc)
        warnings.append(f"Scraping error: {exc}")

    return {
        "papers": papers,
        "source_url": profile_url,
        "total": len(papers),
        "warnings": warnings,
    }
