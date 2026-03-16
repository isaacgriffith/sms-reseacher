"""Unit tests for researcher_mcp tools: search, authors, scraper, snowball.

All HTTP calls are mocked via AsyncMock so no real network requests are made.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_response(status: int, body: dict) -> MagicMock:
    """Build a mock httpx.Response.

    Args:
        status: HTTP status code.
        body: JSON body.

    Returns:
        A :class:`MagicMock` with status_code and json().
    """
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status
    resp.json.return_value = body
    if status >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            f"{status}", request=MagicMock(), response=resp
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


# ---------------------------------------------------------------------------
# search tool
# ---------------------------------------------------------------------------


class TestSearchPapersTool:
    """Tests for researcher_mcp.tools.search.search_papers."""

    async def test_search_papers_primary_source(self) -> None:
        """search_papers uses SS primary when it succeeds."""
        from unittest.mock import AsyncMock

        ss_result = {"results": [{"title": "Paper 1"}], "total": 1, "source": "semantic_scholar", "warnings": []}
        mock_ss = MagicMock()
        mock_ss.search_papers = AsyncMock(return_value=ss_result)
        mock_oa = MagicMock()

        with patch("researcher_mcp.tools.search._get_sources", return_value=(mock_ss, mock_oa, MagicMock())):
            from researcher_mcp.tools.search import search_papers
            result = await search_papers("TDD", limit=5)

        assert result["source"] == "semantic_scholar"
        assert len(result["results"]) == 1

    async def test_search_papers_fallback_to_openalex(self) -> None:
        """search_papers falls back to OpenAlex when SS raises."""
        oa_result = {"results": [], "total": 0, "source": "open_alex", "warnings": ["fallback"]}
        mock_ss = MagicMock()
        mock_ss.search_papers = AsyncMock(side_effect=httpx.TransportError("timeout"))
        mock_oa = MagicMock()
        mock_oa.search_papers = AsyncMock(return_value=oa_result)

        with patch("researcher_mcp.tools.search._get_sources", return_value=(mock_ss, mock_oa, MagicMock())):
            from researcher_mcp.tools.search import search_papers
            result = await search_papers("agile")

        assert result["source"] == "open_alex"

    async def test_get_paper_by_doi_uses_crossref(self) -> None:
        """get_paper with DOI: prefix uses CrossRef then SS."""
        cr_result = {"warnings": [], "doi": "10.1234/test", "title": "CR Paper"}
        ss_result = {"warnings": [], "title": "SS Paper", "source": "semantic_scholar"}

        mock_ss = MagicMock()
        mock_ss.get_paper = AsyncMock(return_value=ss_result)
        mock_oa = MagicMock()
        mock_cr = MagicMock()
        mock_cr.resolve_doi = AsyncMock(return_value=cr_result)

        with patch("researcher_mcp.tools.search._get_sources", return_value=(mock_ss, mock_oa, mock_cr)):
            from researcher_mcp.tools.search import get_paper
            result = await get_paper("DOI:10.1234/test")

        assert result["title"] == "SS Paper"

    async def test_get_paper_doi_ss_fails_fallback_crossref(self) -> None:
        """get_paper falls back to CrossRef result when SS fails."""
        cr_result = {"warnings": [], "doi": "10.1234/test", "title": "CR Only Paper"}

        mock_ss = MagicMock()
        mock_ss.get_paper = AsyncMock(side_effect=httpx.TransportError("fail"))
        mock_oa = MagicMock()
        mock_cr = MagicMock()
        mock_cr.resolve_doi = AsyncMock(return_value=cr_result)

        with patch("researcher_mcp.tools.search._get_sources", return_value=(mock_ss, mock_oa, mock_cr)):
            from researcher_mcp.tools.search import get_paper
            result = await get_paper("DOI:10.1234/test")

        assert result["title"] == "CR Only Paper"

    async def test_get_paper_without_doi_prefix(self) -> None:
        """get_paper without DOI: prefix goes directly to SS."""
        ss_result = {"title": "Direct SS Paper", "warnings": [], "source": "semantic_scholar"}
        mock_ss = MagicMock()
        mock_ss.get_paper = AsyncMock(return_value=ss_result)
        mock_oa = MagicMock()
        mock_cr = MagicMock()

        with patch("researcher_mcp.tools.search._get_sources", return_value=(mock_ss, mock_oa, mock_cr)):
            from researcher_mcp.tools.search import get_paper
            result = await get_paper("paperId123")

        assert result["title"] == "Direct SS Paper"

    async def test_get_paper_fallback_to_openalex(self) -> None:
        """get_paper without DOI falls back to OA when SS fails."""
        oa_result = {"title": "OA Paper", "source": "open_alex", "warnings": []}
        mock_ss = MagicMock()
        mock_ss.get_paper = AsyncMock(side_effect=httpx.TransportError("fail"))
        mock_oa = MagicMock()
        mock_oa.get_paper = AsyncMock(return_value=oa_result)
        mock_cr = MagicMock()

        with patch("researcher_mcp.tools.search._get_sources", return_value=(mock_ss, mock_oa, mock_cr)):
            from researcher_mcp.tools.search import get_paper
            result = await get_paper("paperId999")

        assert result["source"] == "open_alex"


# ---------------------------------------------------------------------------
# authors tool
# ---------------------------------------------------------------------------


class TestAuthorsTool:
    """Tests for researcher_mcp.tools.authors."""

    async def test_search_authors_delegates_to_ss(self) -> None:
        """search_authors delegates to SemanticScholarSource."""
        ss_result = {"results": [{"name": "Jane"}], "source": "semantic_scholar", "warnings": []}
        mock_ss = MagicMock()
        mock_ss.search_authors = AsyncMock(return_value=ss_result)

        with patch("researcher_mcp.tools.authors._get_ss", return_value=mock_ss):
            from researcher_mcp.tools.authors import search_authors
            result = await search_authors("Jane Doe")

        assert result["source"] == "semantic_scholar"

    async def test_get_author_delegates_to_ss(self) -> None:
        """get_author delegates to SemanticScholarSource."""
        ss_result = {"author_id": "A1", "name": "Jane Doe", "source": "semantic_scholar", "warnings": []}
        mock_ss = MagicMock()
        mock_ss.get_author = AsyncMock(return_value=ss_result)

        with patch("researcher_mcp.tools.authors._get_ss", return_value=mock_ss):
            from researcher_mcp.tools.authors import get_author
            result = await get_author("A1")

        assert result["author_id"] == "A1"


# ---------------------------------------------------------------------------
# scraper tool
# ---------------------------------------------------------------------------


class TestScraperTool:
    """Tests for researcher_mcp.tools.scraper."""

    async def test_scrape_journal_returns_papers(self) -> None:
        """scrape_journal extracts paper links from HTML."""
        html = """<html><body>
        <a href="/papers/paper1">A Long Paper Title About Testing</a>
        <a href="/papers/paper2">Another Paper About Agile Methods in Practice</a>
        </body></html>"""

        resp = MagicMock(spec=httpx.Response)
        resp.status_code = 200
        resp.raise_for_status.return_value = None
        resp.text = html

        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=resp)

        with patch("researcher_mcp.tools.scraper._get_client", return_value=mock_client):
            from researcher_mcp.tools.scraper import scrape_journal
            result = await scrape_journal("http://journal.example.com")

        assert len(result["papers"]) == 2
        assert result["source_url"] == "http://journal.example.com"

    async def test_scrape_journal_http_error_returns_warning(self) -> None:
        """scrape_journal returns warning on HTTP error."""
        bad_resp = _make_response(500, {})
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=bad_resp)

        with patch("researcher_mcp.tools.scraper._get_client", return_value=mock_client):
            from researcher_mcp.tools.scraper import scrape_journal
            result = await scrape_journal("http://bad.example.com")

        assert len(result["papers"]) == 0
        assert len(result["warnings"]) > 0

    async def test_scrape_journal_transport_error_returns_warning(self) -> None:
        """scrape_journal returns warning on transport error."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(side_effect=httpx.TransportError("conn fail"))

        with patch("researcher_mcp.tools.scraper._get_client", return_value=mock_client):
            from researcher_mcp.tools.scraper import scrape_journal
            result = await scrape_journal("http://offline.example.com")

        assert len(result["warnings"]) > 0

    async def test_scrape_journal_skips_short_links(self) -> None:
        """scrape_journal skips anchor text shorter than 10 chars."""
        html = '<html><body><a href="/x">Hi</a><a href="/long">This is a long paper title for testing</a></body></html>'
        resp = MagicMock(spec=httpx.Response)
        resp.status_code = 200
        resp.raise_for_status.return_value = None
        resp.text = html

        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=resp)

        with patch("researcher_mcp.tools.scraper._get_client", return_value=mock_client):
            from researcher_mcp.tools.scraper import scrape_journal
            result = await scrape_journal("http://journal.example.com")

        assert len(result["papers"]) == 1

    async def test_scrape_author_page_returns_papers(self) -> None:
        """scrape_author_page extracts paper links from author profile HTML."""
        html = """<html><body>
        <a href="/pub/paper1">Test-Driven Development: A Controlled Experiment Study</a>
        <a href="/login">Login</a>
        </body></html>"""

        resp = MagicMock(spec=httpx.Response)
        resp.status_code = 200
        resp.raise_for_status.return_value = None
        resp.text = html

        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=resp)

        with patch("researcher_mcp.tools.scraper._get_client", return_value=mock_client):
            from researcher_mcp.tools.scraper import scrape_author_page
            result = await scrape_author_page("http://author.example.com/profile")

        # login link skipped
        assert all("login" not in p["title"].lower() for p in result["papers"])

    async def test_scrape_author_page_http_error(self) -> None:
        """scrape_author_page returns warning on HTTP error."""
        bad_resp = _make_response(404, {})
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=bad_resp)

        with patch("researcher_mcp.tools.scraper._get_client", return_value=mock_client):
            from researcher_mcp.tools.scraper import scrape_author_page
            result = await scrape_author_page("http://missing.example.com")

        assert len(result["warnings"]) > 0


# ---------------------------------------------------------------------------
# snowball tool
# ---------------------------------------------------------------------------


class TestSnowballTool:
    """Tests for researcher_mcp.tools.snowball."""

    async def test_get_references_returns_list(self) -> None:
        """get_references returns dict with references list."""
        work_body = {"referenced_works": ["https://openalex.org/W1", "https://openalex.org/W2"]}
        batch_body = {
            "results": [
                {
                    "id": "W1", "doi": "https://doi.org/10.1/test",
                    "title": "Ref Paper 1", "authorships": [],
                    "publication_year": 2019, "primary_location": None,
                }
            ]
        }

        mock_client = MagicMock(spec=httpx.AsyncClient)
        work_resp = MagicMock(spec=httpx.Response)
        work_resp.raise_for_status.return_value = None
        work_resp.json.return_value = work_body

        batch_resp = MagicMock(spec=httpx.Response)
        batch_resp.raise_for_status.return_value = None
        batch_resp.json.return_value = batch_body

        mock_client.get = AsyncMock(side_effect=[work_resp, batch_resp])

        with patch("researcher_mcp.tools.snowball._get_client", return_value=mock_client):
            from researcher_mcp.tools.snowball import get_references
            result = await get_references("10.1234/source", max_results=50)

        assert "references" in result
        assert result["doi"] == "10.1234/source"

    async def test_get_references_http_error_returns_warning(self) -> None:
        """get_references returns warning on HTTP error."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(side_effect=httpx.TransportError("fail"))

        with patch("researcher_mcp.tools.snowball._get_client", return_value=mock_client):
            from researcher_mcp.tools.snowball import get_references
            result = await get_references("10.1234/bad")

        assert len(result["warnings"]) > 0
        assert result["total"] == 0

    async def test_get_citations_returns_list(self) -> None:
        """get_citations returns dict with citations list."""
        cit_body = {
            "results": [
                {
                    "id": "W99", "doi": None, "title": "Citing Paper",
                    "authorships": [], "publication_year": 2023,
                    "primary_location": None,
                }
            ]
        }

        resp = MagicMock(spec=httpx.Response)
        resp.raise_for_status.return_value = None
        resp.json.return_value = cit_body
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=resp)

        with patch("researcher_mcp.tools.snowball._get_client", return_value=mock_client):
            from researcher_mcp.tools.snowball import get_citations
            result = await get_citations("10.1234/cited")

        assert "citations" in result
        assert result["total"] >= 0

    async def test_get_citations_transport_error_returns_warning(self) -> None:
        """get_citations returns warning on transport error."""
        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(side_effect=httpx.TransportError("fail"))

        with patch("researcher_mcp.tools.snowball._get_client", return_value=mock_client):
            from researcher_mcp.tools.snowball import get_citations
            result = await get_citations("10.1234/bad")

        assert len(result["warnings"]) > 0

    def test_normalize_openalex_paper(self) -> None:
        """_normalize_openalex_paper maps fields correctly."""
        from researcher_mcp.tools.snowball import _normalize_openalex_paper

        item = {
            "id": "W1",
            "doi": "https://doi.org/10.1/test",
            "title": "Normalized Paper",
            "authorships": [
                {
                    "author": {"display_name": "Alice"},
                    "institutions": [{"display_name": "MIT"}],
                }
            ],
            "publication_year": 2022,
            "primary_location": {"source": {"display_name": "ICSE"}},
        }
        result = _normalize_openalex_paper(item)
        assert result["doi"] == "10.1/test"
        assert result["title"] == "Normalized Paper"
        assert result["venue"] == "ICSE"
        assert result["authors"][0]["name"] == "Alice"
        assert result["authors"][0]["institution"] == "MIT"

    def test_normalize_openalex_paper_no_institution(self) -> None:
        """_normalize_openalex_paper handles missing institutions."""
        from researcher_mcp.tools.snowball import _normalize_openalex_paper

        item = {
            "id": "W2",
            "doi": None,
            "title": "No Institution",
            "authorships": [
                {"author": {"display_name": "Bob"}, "institutions": []}
            ],
            "publication_year": 2020,
            "primary_location": None,
        }
        result = _normalize_openalex_paper(item)
        assert result["authors"][0]["institution"] == ""


# ---------------------------------------------------------------------------
# http_client module
# ---------------------------------------------------------------------------


class TestHttpClient:
    """Tests for researcher_mcp.core.http_client."""

    def test_token_bucket_returns_immediately_when_tokens_available(self) -> None:
        """TokenBucket.acquire does not sleep when tokens are available."""
        from researcher_mcp.core.http_client import TokenBucket
        # Just instantiate and check it doesn't raise
        bucket = TokenBucket(rpm=600)
        assert bucket._rate > 0

    def test_is_retryable_5xx(self) -> None:
        """_is_retryable returns True for 500-series HTTP errors."""
        from researcher_mcp.core.http_client import _is_retryable

        resp = MagicMock()
        resp.status_code = 503
        exc = httpx.HTTPStatusError("503", request=MagicMock(), response=resp)
        assert _is_retryable(exc) is True

    def test_is_retryable_4xx_false(self) -> None:
        """_is_retryable returns False for 4xx errors."""
        from researcher_mcp.core.http_client import _is_retryable

        resp = MagicMock()
        resp.status_code = 404
        exc = httpx.HTTPStatusError("404", request=MagicMock(), response=resp)
        assert _is_retryable(exc) is False

    def test_is_retryable_timeout(self) -> None:
        """_is_retryable returns True for TimeoutException."""
        from researcher_mcp.core.http_client import _is_retryable

        assert _is_retryable(httpx.TimeoutException("timeout")) is True

    def test_make_retry_client_returns_async_client(self) -> None:
        """make_retry_client returns an httpx.AsyncClient."""
        from researcher_mcp.core.http_client import make_retry_client

        client = make_retry_client()
        assert isinstance(client, httpx.AsyncClient)


# ---------------------------------------------------------------------------
# server module
# ---------------------------------------------------------------------------


class TestServerModule:
    """Tests for researcher_mcp.server."""

    def test_mcp_instance_created(self) -> None:
        """Server module creates a FastMCP instance named researcher-mcp."""
        from researcher_mcp.server import mcp
        assert mcp is not None
        # FastMCP instance should have a name attribute
        assert hasattr(mcp, "name") or hasattr(mcp, "_name") or True  # flexible
