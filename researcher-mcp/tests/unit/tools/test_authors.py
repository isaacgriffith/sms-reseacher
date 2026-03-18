"""Unit tests for researcher_mcp.tools.authors (T059).

Tests search_author_semantic_scholar and get_author_semantic_scholar tools.
All SemanticScholarSource calls are mocked — no real HTTP requests.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from researcher_mcp.sources.base import AuthorDetail, AuthorProfile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ss_author(**kwargs) -> dict:
    """Build a minimal raw author dict as returned by SemanticScholarSource."""
    base = {
        "author_id": "12345",
        "name": "Leslie Lamport",
        "affiliations": ["Microsoft Research"],
        "paper_count": 50,
        "h_index": 30,
    }
    base.update(kwargs)
    return base


def _make_ss_paper(**kwargs) -> dict:
    """Build a minimal raw paper dict as returned by SemanticScholarSource.get_author."""
    base = {
        "paper_id": "abc123",
        "title": "Time, Clocks, and the Ordering of Events",
        "year": 1978,
        "doi": "10.1145/359545.359563",
        "citations": 10000,
    }
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# Tests for search_author_semantic_scholar
# ---------------------------------------------------------------------------


class TestSearchAuthorSemanticScholar:
    """Tests for search_author_semantic_scholar."""

    @pytest.mark.asyncio
    async def test_returns_author_profiles(self) -> None:
        """Returns a list of AuthorProfile when source has results."""
        raw_results = {"results": [_make_ss_author()], "source": "semantic_scholar", "warnings": []}
        mock_ss = MagicMock()
        mock_ss.search_authors = AsyncMock(return_value=raw_results)

        with patch("researcher_mcp.tools.authors._get_ss", return_value=mock_ss):
            from researcher_mcp.tools.authors import search_author_semantic_scholar
            result = await search_author_semantic_scholar(name="Leslie Lamport")

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], AuthorProfile)
        assert result[0].author_id == "12345"
        assert result[0].name == "Leslie Lamport"

    @pytest.mark.asyncio
    async def test_empty_result_when_no_authors_found(self) -> None:
        """Returns empty list when search yields no authors."""
        mock_ss = MagicMock()
        mock_ss.search_authors = AsyncMock(
            return_value={"results": [], "source": "semantic_scholar", "warnings": []}
        )

        with patch("researcher_mcp.tools.authors._get_ss", return_value=mock_ss):
            from researcher_mcp.tools.authors import search_author_semantic_scholar
            result = await search_author_semantic_scholar(name="Nonexistent Author XYZ")

        assert result == []

    @pytest.mark.asyncio
    async def test_appends_institution_to_query(self) -> None:
        """Institution is appended to the query string passed to the source."""
        mock_ss = MagicMock()
        mock_ss.search_authors = AsyncMock(
            return_value={"results": [], "source": "semantic_scholar", "warnings": []}
        )

        with patch("researcher_mcp.tools.authors._get_ss", return_value=mock_ss):
            from researcher_mcp.tools.authors import search_author_semantic_scholar
            await search_author_semantic_scholar(name="Alice", institution="MIT")

        call_args = mock_ss.search_authors.call_args
        assert "MIT" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_profile_url_contains_author_id(self) -> None:
        """Profile URL is constructed from the author_id."""
        raw_results = {"results": [_make_ss_author(author_id="99999")], "source": "semantic_scholar", "warnings": []}
        mock_ss = MagicMock()
        mock_ss.search_authors = AsyncMock(return_value=raw_results)

        with patch("researcher_mcp.tools.authors._get_ss", return_value=mock_ss):
            from researcher_mcp.tools.authors import search_author_semantic_scholar
            result = await search_author_semantic_scholar(name="Test Author")

        assert "99999" in result[0].profile_url

    @pytest.mark.asyncio
    async def test_multiple_authors_returned(self) -> None:
        """Multiple authors in results are all mapped."""
        raw_results = {
            "results": [
                _make_ss_author(author_id="1", name="Author One"),
                _make_ss_author(author_id="2", name="Author Two"),
            ],
            "source": "semantic_scholar",
            "warnings": [],
        }
        mock_ss = MagicMock()
        mock_ss.search_authors = AsyncMock(return_value=raw_results)

        with patch("researcher_mcp.tools.authors._get_ss", return_value=mock_ss):
            from researcher_mcp.tools.authors import search_author_semantic_scholar
            result = await search_author_semantic_scholar(name="Author")

        assert len(result) == 2
        assert result[0].name == "Author One"
        assert result[1].name == "Author Two"


# ---------------------------------------------------------------------------
# Tests for get_author_semantic_scholar
# ---------------------------------------------------------------------------


class TestGetAuthorSemanticScholar:
    """Tests for get_author_semantic_scholar."""

    @pytest.mark.asyncio
    async def test_returns_author_detail_with_papers(self) -> None:
        """Returns AuthorDetail with papers list populated."""
        raw_author = {
            **_make_ss_author(),
            "papers": [_make_ss_paper()],
        }
        mock_ss = MagicMock()
        mock_ss.get_author = AsyncMock(return_value=raw_author)

        with patch("researcher_mcp.tools.authors._get_ss", return_value=mock_ss):
            from researcher_mcp.tools.authors import get_author_semantic_scholar
            result = await get_author_semantic_scholar(author_id="12345")

        assert isinstance(result, AuthorDetail)
        assert result.author_id == "12345"
        assert len(result.papers) == 1
        assert result.papers[0].title == "Time, Clocks, and the Ordering of Events"

    @pytest.mark.asyncio
    async def test_returns_author_detail_with_empty_papers(self) -> None:
        """Returns AuthorDetail with empty papers when none available."""
        raw_author = {**_make_ss_author(), "papers": []}
        mock_ss = MagicMock()
        mock_ss.get_author = AsyncMock(return_value=raw_author)

        with patch("researcher_mcp.tools.authors._get_ss", return_value=mock_ss):
            from researcher_mcp.tools.authors import get_author_semantic_scholar
            result = await get_author_semantic_scholar(author_id="12345")

        assert isinstance(result, AuthorDetail)
        assert result.papers == []

    @pytest.mark.asyncio
    async def test_paper_doi_mapped_correctly(self) -> None:
        """DOI is correctly mapped from the raw paper dict."""
        raw_author = {
            **_make_ss_author(),
            "papers": [_make_ss_paper(doi="10.1145/test")],
        }
        mock_ss = MagicMock()
        mock_ss.get_author = AsyncMock(return_value=raw_author)

        with patch("researcher_mcp.tools.authors._get_ss", return_value=mock_ss):
            from researcher_mcp.tools.authors import get_author_semantic_scholar
            result = await get_author_semantic_scholar(author_id="12345")

        assert result.papers[0].doi == "10.1145/test"

    @pytest.mark.asyncio
    async def test_author_profile_fields_populated(self) -> None:
        """AuthorDetail inherits all AuthorProfile fields."""
        raw_author = {
            **_make_ss_author(
                author_id="55",
                name="Bob",
                affiliations=["INRIA"],
                paper_count=20,
                h_index=10,
            ),
            "papers": [],
        }
        mock_ss = MagicMock()
        mock_ss.get_author = AsyncMock(return_value=raw_author)

        with patch("researcher_mcp.tools.authors._get_ss", return_value=mock_ss):
            from researcher_mcp.tools.authors import get_author_semantic_scholar
            result = await get_author_semantic_scholar(author_id="55")

        assert result.name == "Bob"
        assert result.affiliations == ["INRIA"]
        assert result.paper_count == 20
        assert result.h_index == 10
