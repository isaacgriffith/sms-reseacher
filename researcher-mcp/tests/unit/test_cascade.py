"""Unit test: cascade fallback when primary source (Semantic Scholar) fails."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from researcher_mcp.tools.search import search_papers


class TestSearchCascade:
    """Verify search_papers cascades to OpenAlex when Semantic Scholar fails."""

    async def test_cascade_to_open_alex_on_5xx(self) -> None:
        """When SemanticScholar raises HTTPStatusError(500), OpenAlex is used."""
        ss_error = httpx.HTTPStatusError(
            "Server Error",
            request=MagicMock(),
            response=MagicMock(status_code=500),
        )
        oa_result = {
            "results": [{"title": "Test Paper", "doi": "10.1/test", "paper_id": "oa-1"}],
            "total": 1,
            "source": "open_alex",
            "warnings": ["Served by OpenAlex (Semantic Scholar unavailable)"],
        }

        with (
            patch(
                "researcher_mcp.tools.search._get_sources",
                return_value=(
                    MagicMock(search_papers=AsyncMock(side_effect=ss_error)),
                    MagicMock(search_papers=AsyncMock(return_value=oa_result)),
                    MagicMock(),
                ),
            ),
        ):
            result = await search_papers("software engineering", limit=5)

        assert result["source"] == "open_alex"
        assert len(result["results"]) >= 1
