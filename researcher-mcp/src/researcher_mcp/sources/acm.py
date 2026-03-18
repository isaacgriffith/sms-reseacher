"""ACM Digital Library source adapter.

Implements the :class:`DatabaseSource` protocol by scraping the ACM DL search
interface via HTTP + BeautifulSoup.  A conservative rate limit of 10 RPM is
enforced using a :class:`TokenBucket`.

WARNING: ACM DL does not provide an official public search API.  This scraper
is intended for research use only and must comply with ACM's terms of service.
Institutional subscribers should prefer direct database access tools.
"""

from __future__ import annotations

from typing import Any

import httpx

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None  # type: ignore[assignment,misc]

from researcher_mcp.core.http_client import TokenBucket
from researcher_mcp.sources.base import (
    AuthorInfo,
    PaperRecord,
    normalise_doi,
    normalise_title,
)

_SEARCH_URL = "https://dl.acm.org/action/doSearch"
_RPM = 10


class AcmSearchResult:
    """Result container for ACM DL scraping.

    Attributes:
        papers: List of normalised :class:`PaperRecord` objects.
        truncated: True if the result set was cut short by rate limiting.

    """

    def __init__(self, papers: list[PaperRecord], truncated: bool = False) -> None:
        """Initialise AcmSearchResult.

        Args:
            papers: List of normalised paper records.
            truncated: Whether the result set was truncated.

        """
        self.papers = papers
        self.truncated = truncated


class ACMSource:
    """Scrapes the ACM Digital Library for academic paper records.

    Uses a conservative token-bucket rate limiter (10 RPM) to avoid CAPTCHA
    blocks.  Returns only abstract-level metadata; full-text requires
    institutional access.

    Attributes:
        _client: Shared :class:`httpx.AsyncClient`.
        _bucket: :class:`TokenBucket` enforcing the 10 RPM cap.

    """

    def __init__(self, client: httpx.AsyncClient, rpm: int = _RPM) -> None:
        """Initialise ACMSource.

        Args:
            client: Shared :class:`httpx.AsyncClient`.
            rpm: Requests-per-minute cap (default: 10 — conservative).

        """
        self._client = client
        self._bucket = TokenBucket(rpm)

    def _parse_results_html(self, html: str) -> list[PaperRecord]:
        """Extract paper records from ACM DL search results HTML.

        Args:
            html: Raw HTML string from the ACM DL search response.

        Returns:
            List of :class:`PaperRecord` objects extracted from the page.

        """
        if BeautifulSoup is None:
            return []

        soup = BeautifulSoup(html, "html.parser")
        records: list[PaperRecord] = []

        for item in soup.select("li.search__item"):
            title_el = item.select_one("h5.issue-item__title a, h3.issue-item__title a")
            if not title_el:
                continue
            title = normalise_title(title_el.get_text())
            if not title:
                continue

            href = str(title_el.get("href") or "")
            doi: str | None = None
            if "/doi/" in href:
                doi = normalise_doi(href.split("/doi/", 1)[-1])

            authors: list[AuthorInfo] = []
            for author_el in item.select("ul.rlist--inline li a"):
                name = author_el.get_text(strip=True)
                if name:
                    authors.append(AuthorInfo(name=name))

            year_el = item.select_one("span.issue-item__detail")
            year: int | None = None
            if year_el:
                import re

                m = re.search(r"\b(19|20)\d{2}\b", year_el.get_text())
                if m:
                    year = int(m.group(0))

            venue_el = item.select_one("span.epub-section__title")
            venue = venue_el.get_text(strip=True) if venue_el else None

            records.append(
                PaperRecord(
                    doi=doi,
                    title=title,
                    authors=authors,
                    year=year,
                    venue=venue,
                    source_database="acm_dl",
                    url=f"https://dl.acm.org{href}" if href.startswith("/") else href,
                )
            )

        return records

    async def search(
        self,
        query: str,
        max_results: int = 100,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[PaperRecord]:
        """Search the ACM Digital Library for papers matching *query*.

        Args:
            query: Keyword search query.
            max_results: Maximum records to return.
            year_from: Earliest publication year filter.
            year_to: Latest publication year filter.

        Returns:
            List of :class:`PaperRecord` objects.  Returns an empty list on
            rate-limit or scraping failure rather than raising.

        """
        await self._bucket.acquire()

        params: dict[str, Any] = {
            "AllField": query,
            "pageSize": min(max_results, 50),
            "startPage": 0,
        }
        if year_from:
            params["AfterYear"] = year_from
        if year_to:
            params["BeforeYear"] = year_to

        try:
            r = await self._client.get(
                _SEARCH_URL,
                params=params,
                headers={"Accept": "text/html"},
                follow_redirects=True,
            )
            if r.status_code == 429:
                return []
            r.raise_for_status()
        except httpx.HTTPStatusError, httpx.TransportError:
            return []

        return self._parse_results_html(r.text)

    async def get_paper(self, doi: str) -> PaperRecord | None:
        """Retrieve a single ACM paper by DOI via scraping.

        Args:
            doi: Paper DOI string.

        Returns:
            A :class:`PaperRecord` if found and parseable, or ``None``.

        """
        await self._bucket.acquire()
        url = f"https://dl.acm.org/doi/{doi}"
        try:
            r = await self._client.get(url, follow_redirects=True)
            r.raise_for_status()
        except httpx.HTTPStatusError, httpx.TransportError:
            return None

        if BeautifulSoup is None:
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        title_el = soup.select_one("h1.citation__title")
        if not title_el:
            return None
        title = normalise_title(title_el.get_text())

        authors: list[AuthorInfo] = []
        for a_el in soup.select("span.loa__author-name"):
            name = a_el.get_text(strip=True)
            if name:
                authors.append(AuthorInfo(name=name))

        year: int | None = None
        date_el = soup.select_one("span.CitationCoverDate")
        if date_el:
            import re

            m = re.search(r"\b(19|20)\d{2}\b", date_el.get_text())
            if m:
                year = int(m.group(0))

        return PaperRecord(
            doi=normalise_doi(doi),
            title=title,
            authors=authors,
            year=year,
            source_database="acm_dl",
            url=url,
        )
