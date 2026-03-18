"""Unit test: cascade fallback when primary source (Semantic Scholar) fails."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from researcher_mcp.tools.search import search_papers
from researcher_mcp.sources.base import PaperRecord


class TestSearchCascade:
    """Verify search_papers records failures and returns results from available sources."""

    async def test_failed_source_recorded_in_sources_failed(self) -> None:
        """When SemanticScholar raises HTTPStatusError(500), the failure is recorded."""
        ss_error = httpx.HTTPStatusError(
            "Server Error",
            request=MagicMock(),
            response=MagicMock(status_code=500),
        )
        oa_papers = [PaperRecord(title="OA Paper", doi="10.1/oa", source_database="open_alex")]

        mock_ss = MagicMock()
        mock_ss.search = AsyncMock(side_effect=ss_error)
        mock_oa = MagicMock()
        mock_oa.search = AsyncMock(return_value=oa_papers)

        mock_registry = MagicMock()
        mock_registry.get_enabled = MagicMock(
            return_value=[("semantic_scholar", mock_ss), ("open_alex", mock_oa)]
        )

        with patch("researcher_mcp.tools.search.get_registry", return_value=mock_registry):
            result = await search_papers("software engineering")

        # Failed source should be recorded
        failed_names = [f.source for f in result.sources_failed]
        assert "semantic_scholar" in failed_names

        # OA results should be present
        assert len(result.papers) >= 1
