"""Unit tests for researcher_mcp sources: SemanticScholar, CrossRef, OpenAlex, arXiv, Unpaywall, SciHub.

All HTTP calls are mocked via AsyncMock so no real network requests are made.
"""

from __future__ import annotations

import json
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
        body: JSON body to return from .json().

    Returns:
        A :class:`MagicMock` with status_code, json(), and raise_for_status().
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


def _make_client(response: MagicMock) -> MagicMock:
    """Build a mock httpx.AsyncClient whose .get returns response.

    Args:
        response: The mock response to return from .get.

    Returns:
        A :class:`MagicMock` spec'd to :class:`httpx.AsyncClient`.
    """
    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock(return_value=response)
    return client


# ---------------------------------------------------------------------------
# SemanticScholarSource
# ---------------------------------------------------------------------------


class TestSemanticScholarSource:
    """Tests for researcher_mcp.sources.semantic_scholar.SemanticScholarSource."""

    async def test_search_papers_returns_results(self) -> None:
        """search_papers parses API response into expected schema."""
        from researcher_mcp.sources.semantic_scholar import SemanticScholarSource

        body = {
            "data": [
                {
                    "title": "A TDD Study",
                    "externalIds": {"DOI": "10.1234/test"},
                    "year": 2022,
                    "abstract": "A study on TDD.",
                    "authors": [{"name": "Alice", "authorId": "A1"}],
                    "venue": "ICSE",
                    "citationCount": 10,
                    "paperId": "p123",
                }
            ],
            "total": 1,
        }
        client = _make_client(_make_response(200, body))
        ss = SemanticScholarSource(client, rpm=600)

        result = await ss.search_papers("TDD", limit=5)

        assert result["source"] == "semantic_scholar"
        assert len(result["results"]) == 1
        paper = result["results"][0]
        assert paper["title"] == "A TDD Study"
        assert paper["doi"] == "10.1234/test"

    async def test_search_papers_with_year_filter(self) -> None:
        """search_papers passes year filter to API."""
        from researcher_mcp.sources.semantic_scholar import SemanticScholarSource

        body = {"data": [], "total": 0}
        client = _make_client(_make_response(200, body))
        ss = SemanticScholarSource(client, rpm=600)

        result = await ss.search_papers("test", year_from=2020, year_to=2023)

        assert result["total"] == 0
        call_kwargs = client.get.call_args[1]
        assert "2020" in str(call_kwargs.get("params", {}))

    async def test_get_paper_returns_full_metadata(self) -> None:
        """get_paper returns full paper metadata including references."""
        from researcher_mcp.sources.semantic_scholar import SemanticScholarSource

        body = {
            "paperId": "p999",
            "title": "Research on CI/CD",
            "abstract": "Continuous integration study.",
            "externalIds": {"DOI": "10.9999/cicd"},
            "year": 2021,
            "authors": [{"name": "Bob", "authorId": "B1"}],
            "venue": "JSS",
            "citationCount": 5,
            "references": [
                {"title": "Ref Paper", "externalIds": {"DOI": "10.1111/ref"}}
            ],
        }
        client = _make_client(_make_response(200, body))
        ss = SemanticScholarSource(client, rpm=600)

        result = await ss.get_paper("p999")

        assert result["paper_id"] == "p999"
        assert result["doi"] == "10.9999/cicd"
        assert len(result["references"]) == 1

    async def test_search_authors_returns_list(self) -> None:
        """search_authors returns a list of author dicts."""
        from researcher_mcp.sources.semantic_scholar import SemanticScholarSource

        body = {
            "data": [
                {
                    "authorId": "A42",
                    "name": "Jane Doe",
                    "affiliations": ["MIT"],
                    "paperCount": 30,
                    "hIndex": 12,
                }
            ]
        }
        client = _make_client(_make_response(200, body))
        ss = SemanticScholarSource(client, rpm=600)

        result = await ss.search_authors("Jane Doe", limit=5)

        assert result["source"] == "semantic_scholar"
        assert len(result["results"]) == 1
        assert result["results"][0]["name"] == "Jane Doe"

    async def test_get_author_returns_profile(self) -> None:
        """get_author returns profile dict with papers list."""
        from researcher_mcp.sources.semantic_scholar import SemanticScholarSource

        body = {
            "authorId": "A99",
            "name": "Carol Smith",
            "affiliations": ["CMU"],
            "paperCount": 10,
            "hIndex": 5,
            "papers": [
                {
                    "paperId": "px1",
                    "title": "Testing Paper",
                    "year": 2020,
                    "externalIds": {"DOI": "10.5555/tp"},
                    "citationCount": 2,
                }
            ],
        }
        client = _make_client(_make_response(200, body))
        ss = SemanticScholarSource(client, rpm=600)

        result = await ss.get_author("A99")

        assert result["author_id"] == "A99"
        assert result["name"] == "Carol Smith"
        assert len(result["papers"]) == 1


# ---------------------------------------------------------------------------
# CrossRefSource
# ---------------------------------------------------------------------------


class TestCrossRefSource:
    """Tests for researcher_mcp.sources.crossref.CrossRefSource."""

    async def test_resolve_doi_returns_paper_schema(self) -> None:
        """resolve_doi parses CrossRef message into the paper schema."""
        from researcher_mcp.sources.crossref import CrossRefSource

        body = {
            "message": {
                "title": ["TDD Effects on Quality"],
                "author": [{"given": "Alice", "family": "Tester"}],
                "published": {"date-parts": [[2021]]},
                "container-title": ["IEEE TSE"],
                "abstract": "We study TDD.",
                "is-referenced-by-count": 15,
            }
        }
        client = _make_client(_make_response(200, body))
        cr = CrossRefSource(client)

        result = await cr.resolve_doi("10.1234/tdd")

        assert result["title"] == "TDD Effects on Quality"
        assert result["doi"] == "10.1234/tdd"
        assert result["year"] == 2021
        assert result["venue"] == "IEEE TSE"
        assert result["source"] == "crossref"

    async def test_resolve_doi_empty_body(self) -> None:
        """resolve_doi handles empty message gracefully."""
        from researcher_mcp.sources.crossref import CrossRefSource

        body = {"message": {}}
        client = _make_client(_make_response(200, body))
        cr = CrossRefSource(client)

        result = await cr.resolve_doi("10.9999/empty")

        assert result["title"] == ""
        assert result["year"] is None


# ---------------------------------------------------------------------------
# OpenAlexSource
# ---------------------------------------------------------------------------


class TestOpenAlexSource:
    """Tests for researcher_mcp.sources.open_alex.OpenAlexSource."""

    async def test_search_papers_returns_results(self) -> None:
        """search_papers parses OpenAlex API response."""
        from researcher_mcp.sources.open_alex import OpenAlexSource

        body = {
            "results": [
                {
                    "id": "W1234",
                    "title": "Software Testing Study",
                    "doi": "https://doi.org/10.1234/test",
                    "publication_year": 2022,
                    "authorships": [
                        {"author": {"display_name": "Alice", "id": "A1"}}
                    ],
                    "primary_location": {
                        "source": {"display_name": "ICSE"}
                    },
                    "cited_by_count": 7,
                }
            ],
            "meta": {"count": 1},
        }
        client = _make_client(_make_response(200, body))
        oa = OpenAlexSource(client, rpm=600)

        result = await oa.search_papers("software testing")

        assert result["source"] == "open_alex"
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Software Testing Study"
        assert result["results"][0]["doi"] == "10.1234/test"

    async def test_map_work_extracts_doi(self) -> None:
        """_map_work strips https://doi.org/ prefix correctly."""
        from researcher_mcp.sources.open_alex import OpenAlexSource

        client = MagicMock(spec=httpx.AsyncClient)
        oa = OpenAlexSource(client, rpm=600)

        work = {"doi": "https://doi.org/10.1234/work", "title": "Work Title",
                "publication_year": 2020, "authorships": [], "primary_location": None,
                "cited_by_count": 0, "id": "W42"}
        result = oa._map_work(work)
        assert result["doi"] == "10.1234/work"

    async def test_map_work_handles_null_doi(self) -> None:
        """_map_work returns None for missing doi."""
        from researcher_mcp.sources.open_alex import OpenAlexSource

        client = MagicMock(spec=httpx.AsyncClient)
        oa = OpenAlexSource(client, rpm=600)
        work = {"doi": None, "title": "No DOI", "publication_year": 2020,
                "authorships": [], "primary_location": None, "cited_by_count": 0, "id": "W0"}
        result = oa._map_work(work)
        assert result["doi"] is None

    async def test_get_paper_by_doi_prefix(self) -> None:
        """get_paper with DOI: prefix queries correct path."""
        from researcher_mcp.sources.open_alex import OpenAlexSource

        work_body = {
            "id": "W9", "title": "DOI Paper", "doi": "https://doi.org/10.9/dp",
            "publication_year": 2022, "authorships": [], "primary_location": None,
            "cited_by_count": 0,
        }
        client = _make_client(_make_response(200, work_body))
        oa = OpenAlexSource(client, rpm=600)

        result = await oa.get_paper("DOI:10.9/dp")

        assert result["source"] == "open_alex"


# ---------------------------------------------------------------------------
# ArxivSource
# ---------------------------------------------------------------------------


class TestArxivSource:
    """Tests for researcher_mcp.sources.arxiv.ArxivSource."""

    async def test_fetch_pdf_no_arxiv_id_returns_warning(self) -> None:
        """fetch_pdf returns a warning when no arXiv ID is found."""
        from researcher_mcp.sources.arxiv import ArxivSource

        crossref_resp = _make_response(200, {
            "message": {"title": ["Some Paper"], "author": [], "published": {}, "references": []}
        })
        client = _make_client(crossref_resp)
        arxiv = ArxivSource(client)

        result = await arxiv.fetch_pdf("10.1234/nodoi", "/tmp/test.pdf")

        assert result["success"] is False
        assert "No arXiv ID" in result["warnings"][0]

    async def test_fetch_pdf_crossref_failure_returns_warning(self) -> None:
        """fetch_pdf returns warning when CrossRef lookup fails."""
        from researcher_mcp.sources.arxiv import ArxivSource

        client = MagicMock(spec=httpx.AsyncClient)
        client.get = AsyncMock(side_effect=httpx.TransportError("conn error"))
        arxiv = ArxivSource(client)

        result = await arxiv.fetch_pdf("10.1234/error", "/tmp/test.pdf")

        assert result["success"] is False
        assert "CrossRef" in result["warnings"][0]

    def test_extract_arxiv_id_from_doi(self) -> None:
        """_extract_arxiv_id finds arxiv ID from doi field."""
        from researcher_mcp.sources.arxiv import ArxivSource

        client = MagicMock(spec=httpx.AsyncClient)
        arxiv = ArxivSource(client)
        metadata = {"doi": "arxiv/2301.01234", "references": []}
        result = arxiv._extract_arxiv_id(metadata)
        assert result == "2301.01234"

    def test_extract_arxiv_id_from_reference(self) -> None:
        """_extract_arxiv_id finds arxiv ID in references list."""
        from researcher_mcp.sources.arxiv import ArxivSource

        client = MagicMock(spec=httpx.AsyncClient)
        arxiv = ArxivSource(client)
        metadata = {
            "references": [{"doi": "https://arxiv.org/abs/2301.99999"}],
            "doi": "",
        }
        result = arxiv._extract_arxiv_id(metadata)
        assert result == "2301.99999"

    def test_extract_arxiv_id_none_when_absent(self) -> None:
        """_extract_arxiv_id returns None when no arxiv ID exists."""
        from researcher_mcp.sources.arxiv import ArxivSource

        client = MagicMock(spec=httpx.AsyncClient)
        arxiv = ArxivSource(client)
        result = arxiv._extract_arxiv_id({"doi": "10.1234/nodoi", "references": []})
        assert result is None


# ---------------------------------------------------------------------------
# UnpaywallSource
# ---------------------------------------------------------------------------


class TestUnpaywallSource:
    """Tests for researcher_mcp.sources.unpaywall.UnpaywallSource."""

    async def test_fetch_pdf_no_oa_returns_warning(self) -> None:
        """fetch_pdf returns warning when no OA location found."""
        from researcher_mcp.sources.unpaywall import UnpaywallSource

        body = {"best_oa_location": None}
        client = _make_client(_make_response(200, body))
        up = UnpaywallSource(client, email="test@example.com")

        result = await up.fetch_pdf("10.1234/oa", "/tmp/test.pdf")

        assert result["success"] is False
        assert "No open-access" in result["warnings"][0]

    async def test_fetch_pdf_download_success(self, tmp_path: Path) -> None:
        """fetch_pdf downloads and saves PDF when OA location found."""
        from researcher_mcp.sources.unpaywall import UnpaywallSource

        lookup_body = {"best_oa_location": {"url_for_pdf": "https://example.com/paper.pdf"}}
        pdf_content = b"%PDF-1.4 test content"

        pdf_resp = MagicMock(spec=httpx.Response)
        pdf_resp.status_code = 200
        pdf_resp.raise_for_status.return_value = None
        pdf_resp.content = pdf_content

        lookup_resp = _make_response(200, lookup_body)

        client = MagicMock(spec=httpx.AsyncClient)
        client.get = AsyncMock(side_effect=[lookup_resp, pdf_resp])
        up = UnpaywallSource(client, email="test@example.com")

        out_path = str(tmp_path / "paper.pdf")
        result = await up.fetch_pdf("10.1234/oa", out_path)

        assert result["success"] is True
        assert result["source"] == "unpaywall"
        assert Path(out_path).read_bytes() == pdf_content

    async def test_fetch_pdf_lookup_failure_returns_warning(self) -> None:
        """fetch_pdf returns warning when Unpaywall API call fails."""
        from researcher_mcp.sources.unpaywall import UnpaywallSource

        client = MagicMock(spec=httpx.AsyncClient)
        client.get = AsyncMock(side_effect=httpx.TransportError("fail"))
        up = UnpaywallSource(client)

        result = await up.fetch_pdf("10.1234/bad", "/tmp/test.pdf")

        assert result["success"] is False
        assert "Unpaywall lookup failed" in result["warnings"]


# ---------------------------------------------------------------------------
# SciHubSource
# ---------------------------------------------------------------------------


class TestSciHubSource:
    """Tests for researcher_mcp.sources.scihub.SciHubSource."""

    async def test_fetch_pdf_disabled_raises_mcp_error(self) -> None:
        """fetch_pdf raises MCPError when scihub_enabled=False."""
        from researcher_mcp.sources.scihub import MCPError, SciHubSource

        client = MagicMock(spec=httpx.AsyncClient)
        sh = SciHubSource(client, scihub_enabled=False)

        with pytest.raises(MCPError) as exc_info:
            await sh.fetch_pdf("10.1234/paper", "/tmp/test.pdf")

        assert exc_info.value.code == "SCIHUB_DISABLED"

    async def test_mcp_error_code_attribute(self) -> None:
        """MCPError stores code as attribute."""
        from researcher_mcp.sources.scihub import MCPError

        err = MCPError("TEST_CODE", "test message")
        assert err.code == "TEST_CODE"
        assert "test message" in str(err)

    async def test_mcp_error_code_only(self) -> None:
        """MCPError with only code uses code as message."""
        from researcher_mcp.sources.scihub import MCPError

        err = MCPError("CODE_ONLY")
        assert err.code == "CODE_ONLY"
        assert "CODE_ONLY" in str(err)

    async def test_fetch_pdf_page_fetch_fails_returns_warning(self) -> None:
        """fetch_pdf when page fetch fails returns warning dict."""
        from researcher_mcp.sources.scihub import SciHubSource

        client = MagicMock(spec=httpx.AsyncClient)
        client.get = AsyncMock(side_effect=httpx.TransportError("fail"))
        sh = SciHubSource(client, scihub_enabled=True)

        result = await sh.fetch_pdf("10.1234/paper", "/tmp/test.pdf")

        assert result["success"] is False
        assert "SciHub page fetch failed" in result["warnings"]

    async def test_fetch_pdf_no_pdf_link_returns_warning(self) -> None:
        """fetch_pdf when no PDF link found on page returns warning."""
        from researcher_mcp.sources.scihub import SciHubSource

        page_resp = MagicMock(spec=httpx.Response)
        page_resp.status_code = 200
        page_resp.raise_for_status.return_value = None
        page_resp.text = "<html><body>No PDF here</body></html>"

        client = MagicMock(spec=httpx.AsyncClient)
        client.get = AsyncMock(return_value=page_resp)
        sh = SciHubSource(client, scihub_enabled=True)

        result = await sh.fetch_pdf("10.1234/paper", "/tmp/test.pdf")

        assert result["success"] is False
        assert "no PDF link" in result["warnings"][0]

    async def test_fetch_pdf_download_success(self, tmp_path: Path) -> None:
        """fetch_pdf succeeds when PDF link found and download works."""
        from researcher_mcp.sources.scihub import SciHubSource

        page_html = '<html><body><iframe src="https://cdn.scihub.se/file.pdf"></iframe></body></html>'
        page_resp = MagicMock(spec=httpx.Response)
        page_resp.status_code = 200
        page_resp.raise_for_status.return_value = None
        page_resp.text = page_html

        pdf_resp = MagicMock(spec=httpx.Response)
        pdf_resp.status_code = 200
        pdf_resp.raise_for_status.return_value = None
        pdf_resp.content = b"%PDF-1.4"

        client = MagicMock(spec=httpx.AsyncClient)
        client.get = AsyncMock(side_effect=[page_resp, pdf_resp])
        sh = SciHubSource(client, scihub_enabled=True)

        out_path = str(tmp_path / "paper.pdf")
        result = await sh.fetch_pdf("10.1234/paper", out_path)

        assert result["success"] is True
        assert result["source"] == "scihub"
