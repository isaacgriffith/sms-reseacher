"""Unit tests for the upgraded search_papers fan-out tool (T013).

Tests cover:
- Fan-out across multiple mocked sources via SourceRegistry.
- Partial failure: failed sources recorded in sources_failed, successful merged.
- Deduplication applied across merged results.
- Empty indices list returns empty result.
- All-fail scenario returns empty papers with all failures reported.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from researcher_mcp.sources.base import AuthorInfo, PaperRecord


def _paper(title: str, doi: str | None = None, source: str = "test") -> PaperRecord:
    """Build a minimal PaperRecord for test assertions.

    Args:
        title: Paper title.
        doi: Optional DOI string.
        source: Source database identifier.

    Returns:
        A :class:`PaperRecord` instance.
    """
    return PaperRecord(title=title, doi=doi, source_database=source)


class TestSearchPapersFanOut:
    """Tests for the upgraded search_papers tool (fan-out via SourceRegistry)."""

    async def test_single_source_returns_papers(self) -> None:
        """Fan-out with one enabled source returns its results."""
        papers = [_paper("Paper A", doi="10.1/a", source="semantic_scholar")]
        mock_src = MagicMock()
        mock_src.search = AsyncMock(return_value=papers)

        mock_registry = MagicMock()
        mock_registry.get_enabled.return_value = [("semantic_scholar", mock_src)]

        with patch(
            "researcher_mcp.tools.search.get_registry", return_value=mock_registry
        ):
            from researcher_mcp.tools.search import search_papers

            result = await search_papers(query="TDD", indices=["semantic_scholar"])

        assert len(result.papers) == 1
        assert result.papers[0].title == "Paper A"
        assert result.sources_queried == ["semantic_scholar"]
        assert result.sources_failed == []

    async def test_multiple_sources_merged(self) -> None:
        """Fan-out across two sources merges their results."""
        papers_a = [_paper("IEEE Paper", doi="10.1/a", source="ieee_xplore")]
        papers_b = [_paper("SS Paper", doi="10.1/b", source="semantic_scholar")]
        mock_ieee = MagicMock()
        mock_ieee.search = AsyncMock(return_value=papers_a)
        mock_ss = MagicMock()
        mock_ss.search = AsyncMock(return_value=papers_b)

        mock_registry = MagicMock()
        mock_registry.get_enabled.return_value = [
            ("ieee_xplore", mock_ieee),
            ("semantic_scholar", mock_ss),
        ]

        with patch(
            "researcher_mcp.tools.search.get_registry", return_value=mock_registry
        ):
            from researcher_mcp.tools.search import search_papers

            result = await search_papers(query="agile")

        assert len(result.papers) == 2
        assert result.sources_failed == []
        assert set(result.sources_queried) == {"ieee_xplore", "semantic_scholar"}

    async def test_failed_source_recorded_in_sources_failed(self) -> None:
        """A source that raises an exception is recorded in sources_failed."""
        good_papers = [_paper("Good", doi="10.1/g", source="scopus")]
        mock_good = MagicMock()
        mock_good.search = AsyncMock(return_value=good_papers)
        mock_bad = MagicMock()
        mock_bad.search = AsyncMock(side_effect=Exception("connection refused"))

        mock_registry = MagicMock()
        mock_registry.get_enabled.return_value = [
            ("scopus", mock_good),
            ("ieee_xplore", mock_bad),
        ]

        with patch(
            "researcher_mcp.tools.search.get_registry", return_value=mock_registry
        ):
            from researcher_mcp.tools.search import search_papers

            result = await search_papers(query="ML")

        assert len(result.papers) == 1
        assert len(result.sources_failed) == 1
        assert result.sources_failed[0].source == "ieee_xplore"
        assert result.sources_queried == ["scopus", "ieee_xplore"]

    async def test_deduplication_applied(self) -> None:
        """Duplicate papers from different sources are deduplicated."""
        # Same DOI from two sources
        paper_a = _paper("Same Paper", doi="10.1/dup", source="ieee_xplore")
        paper_b = _paper("Same Paper", doi="10.1/dup", source="semantic_scholar")
        mock_src_a = MagicMock()
        mock_src_a.search = AsyncMock(return_value=[paper_a])
        mock_src_b = MagicMock()
        mock_src_b.search = AsyncMock(return_value=[paper_b])

        mock_registry = MagicMock()
        mock_registry.get_enabled.return_value = [
            ("ieee_xplore", mock_src_a),
            ("semantic_scholar", mock_src_b),
        ]

        with patch(
            "researcher_mcp.tools.search.get_registry", return_value=mock_registry
        ):
            from researcher_mcp.tools.search import search_papers

            result = await search_papers(query="dup test")

        assert len(result.papers) == 1

    async def test_all_sources_fail_returns_empty_with_all_failures(self) -> None:
        """When all sources fail, papers is empty and all are in sources_failed."""
        mock_a = MagicMock()
        mock_a.search = AsyncMock(side_effect=Exception("timeout"))
        mock_b = MagicMock()
        mock_b.search = AsyncMock(side_effect=Exception("auth error"))

        mock_registry = MagicMock()
        mock_registry.get_enabled.return_value = [
            ("ieee_xplore", mock_a),
            ("scopus", mock_b),
        ]

        with patch(
            "researcher_mcp.tools.search.get_registry", return_value=mock_registry
        ):
            from researcher_mcp.tools.search import search_papers

            result = await search_papers(query="fail test")

        assert result.papers == []
        assert len(result.sources_failed) == 2

    async def test_none_indices_uses_all_registered(self) -> None:
        """Passing indices=None fans out to all registered sources."""
        papers = [_paper("P1", doi="10.1/1", source="scopus")]
        mock_src = MagicMock()
        mock_src.search = AsyncMock(return_value=papers)

        mock_registry = MagicMock()
        mock_registry.get_enabled.return_value = [("scopus", mock_src)]

        with patch(
            "researcher_mcp.tools.search.get_registry", return_value=mock_registry
        ):
            from researcher_mcp.tools.search import search_papers

            result = await search_papers(query="test", indices=None)

        mock_registry.get_enabled.assert_called_once_with(None)
        assert len(result.papers) == 1

    async def test_truncated_flag_when_results_exceed_max(self) -> None:
        """truncated is True when total results across sources exceed max_results."""
        # Create more papers than max_results
        many_papers = [
            _paper(f"Paper {i}", doi=f"10.1/{i}", source="ss") for i in range(50)
        ]
        mock_src = MagicMock()
        mock_src.search = AsyncMock(return_value=many_papers)

        mock_registry = MagicMock()
        mock_registry.get_enabled.return_value = [("semantic_scholar", mock_src)]

        with patch(
            "researcher_mcp.tools.search.get_registry", return_value=mock_registry
        ):
            from researcher_mcp.tools.search import search_papers

            result = await search_papers(query="big", max_results=10)

        # Result should be truncated to max_results
        assert len(result.papers) <= 10
        assert result.truncated is True

    async def test_total_found_reflects_pre_truncation_count(self) -> None:
        """total_found reflects how many unique papers were found before truncation."""
        papers = [
            _paper(f"Paper {i}", doi=f"10.1/{i}", source="ss") for i in range(5)
        ]
        mock_src = MagicMock()
        mock_src.search = AsyncMock(return_value=papers)

        mock_registry = MagicMock()
        mock_registry.get_enabled.return_value = [("semantic_scholar", mock_src)]

        with patch(
            "researcher_mcp.tools.search.get_registry", return_value=mock_registry
        ):
            from researcher_mcp.tools.search import search_papers

            result = await search_papers(query="test", max_results=100)

        assert result.total_found == 5
        assert result.truncated is False


class TestClassifyError:
    """Tests for _classify_error helper."""

    def test_classify_401_error(self) -> None:
        """401 in message maps to auth_failed."""
        from researcher_mcp.tools.search import _classify_error

        exc = Exception("401 Unauthorized")
        assert _classify_error(exc) == "auth_failed"

    def test_classify_403_error(self) -> None:
        """403 in message maps to auth_failed."""
        from researcher_mcp.tools.search import _classify_error

        exc = Exception("403 Forbidden")
        assert _classify_error(exc) == "auth_failed"

    def test_classify_auth_in_message(self) -> None:
        """'auth' in message maps to auth_failed."""
        from researcher_mcp.tools.search import _classify_error

        exc = Exception("authentication failed")
        assert _classify_error(exc) == "auth_failed"

    def test_classify_429_rate_limited(self) -> None:
        """429 in message maps to rate_limited."""
        from researcher_mcp.tools.search import _classify_error

        exc = Exception("429 Too Many Requests")
        assert _classify_error(exc) == "rate_limited"

    def test_classify_rate_in_message(self) -> None:
        """'rate' in message maps to rate_limited."""
        from researcher_mcp.tools.search import _classify_error

        exc = Exception("rate limit exceeded")
        assert _classify_error(exc) == "rate_limited"

    def test_classify_timeout_error(self) -> None:
        """timeout in message maps to unreachable."""
        from researcher_mcp.tools.search import _classify_error

        exc = Exception("connection timeout")
        assert _classify_error(exc) == "unreachable"

    def test_classify_transport_error(self) -> None:
        """transport in message maps to unreachable."""
        from researcher_mcp.tools.search import _classify_error

        exc = Exception("transport error")
        assert _classify_error(exc) == "unreachable"

    def test_classify_unknown_error(self) -> None:
        """Unknown error maps to unreachable."""
        from researcher_mcp.tools.search import _classify_error

        exc = Exception("some random failure")
        assert _classify_error(exc) == "unreachable"


class TestPerSourceTools:
    """Tests for per-source search tool functions."""

    async def test_search_ieee_returns_papers(self) -> None:
        """search_ieee() calls registry.get('ieee_xplore').search()."""
        papers = [_paper("IEEE Paper", doi="10.1109/p1", source="ieee_xplore")]
        mock_src = MagicMock()
        mock_src.search = AsyncMock(return_value=papers)

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_ieee

            result = await search_ieee(query="software")

        assert len(result) == 1
        assert result[0].title == "IEEE Paper"

    async def test_search_ieee_returns_empty_when_not_registered(self) -> None:
        """search_ieee() returns [] when source not in registry."""
        mock_registry = MagicMock()
        mock_registry.get.return_value = None

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_ieee

            result = await search_ieee(query="test")

        assert result == []

    async def test_get_ieee_paper_returns_none_when_not_registered(self) -> None:
        """get_ieee_paper() returns None when source not in registry."""
        mock_registry = MagicMock()
        mock_registry.get.return_value = None

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import get_ieee_paper

            result = await get_ieee_paper(article_number="12345")

        assert result is None

    async def test_get_ieee_paper_returns_none_when_wrong_type(self) -> None:
        """get_ieee_paper() returns None when source is not IEEESource instance."""
        mock_src = MagicMock()  # not an IEEESource

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import get_ieee_paper

            result = await get_ieee_paper(article_number="12345")

        assert result is None

    async def test_search_acm_returns_result_dict(self) -> None:
        """search_acm() returns dict with 'papers' and 'truncated' keys."""
        papers = [_paper("ACM Paper", doi="10.1145/p1", source="acm_dl")]
        mock_src = MagicMock()
        mock_src.search = AsyncMock(return_value=papers)

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_acm

            result = await search_acm(query="ACM test")

        assert "papers" in result
        assert "truncated" in result
        assert len(result["papers"]) == 1

    async def test_search_acm_returns_empty_when_not_registered(self) -> None:
        """search_acm() returns empty dict when source not in registry."""
        mock_registry = MagicMock()
        mock_registry.get.return_value = None

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_acm

            result = await search_acm(query="test")

        assert result == {"papers": [], "truncated": False}

    async def test_search_acm_truncated_flag(self) -> None:
        """search_acm() sets truncated=True when papers count equals max_results."""
        papers = [_paper(f"Paper {i}", doi=f"10.1/{i}", source="acm_dl") for i in range(5)]
        mock_src = MagicMock()
        mock_src.search = AsyncMock(return_value=papers)

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_acm

            result = await search_acm(query="test", max_results=5)

        assert result["truncated"] is True

    async def test_search_google_scholar_returns_papers(self) -> None:
        """search_google_scholar() calls registry source.search()."""
        papers = [_paper("Scholar Paper", doi="10.1/gs1", source="google_scholar")]
        mock_src = MagicMock()
        mock_src.search = AsyncMock(return_value=papers)

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_google_scholar

            result = await search_google_scholar(query="test")

        assert len(result) == 1

    async def test_search_google_scholar_returns_empty_when_not_registered(self) -> None:
        """search_google_scholar() returns [] when source not in registry."""
        mock_registry = MagicMock()
        mock_registry.get.return_value = None

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_google_scholar

            result = await search_google_scholar(query="test")

        assert result == []

    async def test_search_inspec_returns_papers(self) -> None:
        """search_inspec() calls InspecSource.search() via registry."""
        from researcher_mcp.sources.inspec import InspecSource

        papers = [_paper("Inspec Paper", doi="10.1/i1", source="inspec")]
        mock_src = MagicMock(spec=InspecSource)
        mock_src.search = AsyncMock(return_value=papers)

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_inspec

            result = await search_inspec(query="inspec test", databases=["INS"])

        assert len(result) == 1

    async def test_search_inspec_returns_empty_when_not_registered(self) -> None:
        """search_inspec() returns [] when source not found or wrong type."""
        mock_registry = MagicMock()
        mock_registry.get.return_value = None

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_inspec

            result = await search_inspec(query="test")

        assert result == []

    async def test_search_scopus_returns_papers(self) -> None:
        """search_scopus() calls ScopusSource.search() via registry."""
        from researcher_mcp.sources.scopus import ScopusSource

        papers = [_paper("Scopus Paper", doi="10.1/s1", source="scopus")]
        mock_src = MagicMock(spec=ScopusSource)
        mock_src.search = AsyncMock(return_value=papers)

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_scopus

            result = await search_scopus(query="ML test", subject_areas=["COMP"])

        assert len(result) == 1

    async def test_search_scopus_returns_empty_when_not_registered(self) -> None:
        """search_scopus() returns [] when source not registered."""
        mock_registry = MagicMock()
        mock_registry.get.return_value = None

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_scopus

            result = await search_scopus(query="test")

        assert result == []

    async def test_get_scopus_paper_returns_record(self) -> None:
        """get_scopus_paper() returns PaperRecord from ScopusSource."""
        from researcher_mcp.sources.scopus import ScopusSource

        paper = _paper("Scopus Ret", doi="10.1/s2", source="scopus")
        mock_src = MagicMock(spec=ScopusSource)
        mock_src.get_paper = AsyncMock(return_value=paper)

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import get_scopus_paper

            result = await get_scopus_paper(doi="10.1/s2")

        assert result is not None

    async def test_get_scopus_paper_returns_none_when_no_identifier(self) -> None:
        """get_scopus_paper() returns None when neither doi nor eid provided."""
        from researcher_mcp.sources.scopus import ScopusSource

        mock_src = MagicMock(spec=ScopusSource)
        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import get_scopus_paper

            result = await get_scopus_paper()

        assert result is None

    async def test_get_scopus_paper_uses_eid_when_doi_absent(self) -> None:
        """get_scopus_paper() uses eid when doi not given."""
        from researcher_mcp.sources.scopus import ScopusSource

        paper = _paper("Scopus By EID", doi=None, source="scopus")
        mock_src = MagicMock(spec=ScopusSource)
        mock_src.get_paper = AsyncMock(return_value=paper)

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import get_scopus_paper

            result = await get_scopus_paper(eid="2-s2.0-12345")

        mock_src.get_paper.assert_called_once_with("2-s2.0-12345")

    async def test_search_wos_returns_papers(self) -> None:
        """search_wos() calls WoSSource.search() via registry."""
        from researcher_mcp.sources.wos import WoSSource

        papers = [_paper("WoS Paper", doi="10.1/w1", source="web_of_science")]
        mock_src = MagicMock(spec=WoSSource)
        mock_src.search = AsyncMock(return_value=papers)

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_wos

            result = await search_wos(query="TS=software", edition="WOS")

        assert len(result) == 1

    async def test_search_wos_returns_empty_when_not_registered(self) -> None:
        """search_wos() returns [] when source not found."""
        mock_registry = MagicMock()
        mock_registry.get.return_value = None

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_wos

            result = await search_wos(query="test")

        assert result == []

    async def test_search_sciencedirect_returns_papers(self) -> None:
        """search_sciencedirect() calls ScienceDirectSource.search() via registry."""
        from researcher_mcp.sources.science_direct import ScienceDirectSource

        papers = [_paper("SD Paper", doi="10.1/sd1", source="science_direct")]
        mock_src = MagicMock(spec=ScienceDirectSource)
        mock_src.search = AsyncMock(return_value=papers)

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_sciencedirect

            result = await search_sciencedirect(query="elsevier test", open_access_only=True)

        assert len(result) == 1

    async def test_search_sciencedirect_returns_empty_when_not_registered(self) -> None:
        """search_sciencedirect() returns [] when source not found."""
        mock_registry = MagicMock()
        mock_registry.get.return_value = None

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_sciencedirect

            result = await search_sciencedirect(query="test")

        assert result == []

    async def test_search_springer_returns_papers(self) -> None:
        """search_springer() calls SpringerSource.search() via registry."""
        from researcher_mcp.sources.springer import SpringerSource

        papers = [_paper("Springer Paper", doi="10.1007/sp1", source="springer_link")]
        mock_src = MagicMock(spec=SpringerSource)
        mock_src.search = AsyncMock(return_value=papers)

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_springer

            result = await search_springer(query="springer test", open_access_only=True)

        assert len(result) == 1

    async def test_search_springer_returns_empty_when_not_registered(self) -> None:
        """search_springer() returns [] when source not found."""
        mock_registry = MagicMock()
        mock_registry.get.return_value = None

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_springer

            result = await search_springer(query="test")

        assert result == []

    async def test_search_semantic_scholar_returns_papers(self) -> None:
        """search_semantic_scholar() calls registry source.search()."""
        papers = [_paper("SS Paper", doi="10.1/ss1", source="semantic_scholar")]
        mock_src = MagicMock()
        mock_src.search = AsyncMock(return_value=papers)

        mock_registry = MagicMock()
        mock_registry.get.return_value = mock_src

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_semantic_scholar

            result = await search_semantic_scholar(query="TDD")

        assert len(result) == 1

    async def test_search_semantic_scholar_returns_empty_when_not_registered(self) -> None:
        """search_semantic_scholar() returns [] when source not found."""
        mock_registry = MagicMock()
        mock_registry.get.return_value = None

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            from researcher_mcp.tools.search import search_semantic_scholar

            result = await search_semantic_scholar(query="test")

        assert result == []

    async def test_get_paper_semantic_scholar_returns_error_with_no_input(self) -> None:
        """get_paper_semantic_scholar() returns error dict when no id provided."""
        from researcher_mcp.sources.semantic_scholar import SemanticScholarSource
        from researcher_mcp.core.config import get_settings
        from researcher_mcp.core.http_client import make_retry_client

        mock_ss = MagicMock(spec=SemanticScholarSource)
        mock_ss.get_paper = AsyncMock(return_value={"error": "not found"})
        mock_oa = MagicMock()
        mock_cr = MagicMock()

        with patch("researcher_mcp.tools.search._get_legacy_sources", return_value=(mock_ss, mock_oa, mock_cr)):
            from researcher_mcp.tools.search import get_paper_semantic_scholar

            result = await get_paper_semantic_scholar()

        assert "error" in result
