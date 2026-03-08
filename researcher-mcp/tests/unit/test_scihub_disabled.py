"""Unit test: SCIHUB_ENABLED=false causes SciHub to be skipped."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from researcher_mcp.sources.scihub import MCPError, SciHubSource
from researcher_mcp.tools.pdf import fetch_paper_pdf


class TestSciHubDisabled:
    """Verify SciHub is skipped when SCIHUB_ENABLED=false."""

    async def test_scihub_raises_mcp_error_when_disabled(self) -> None:
        """SciHubSource.fetch_pdf raises MCPError('SCIHUB_DISABLED') when disabled."""
        source = SciHubSource(MagicMock(), scihub_enabled=False)
        with pytest.raises(MCPError) as exc_info:
            await source.fetch_pdf("10.1/test", "/tmp/test.pdf")
        assert exc_info.value.code == "SCIHUB_DISABLED"

    async def test_fetch_paper_pdf_no_scihub_request_when_disabled(self) -> None:
        """fetch_paper_pdf returns success=False with SciHub-disabled warning."""
        unpaywall_fail = {
            "success": False, "output_path": None,
            "source": None, "url": None,
            "warnings": ["No open-access PDF found on Unpaywall"],
        }
        arxiv_fail = {
            "success": False, "output_path": None,
            "source": None, "url": None,
            "warnings": ["No arXiv ID found for this DOI"],
        }
        mock_settings = MagicMock(
            scihub_enabled=False,
            scihub_url="https://sci-hub.se",
            unpaywall_email="test@example.com",
        )

        with (
            patch("researcher_mcp.tools.pdf.get_settings", return_value=mock_settings),
            patch("researcher_mcp.tools.pdf.make_retry_client", return_value=MagicMock()),
            patch(
                "researcher_mcp.tools.pdf.UnpaywallSource",
                return_value=MagicMock(fetch_pdf=AsyncMock(return_value=unpaywall_fail)),
            ),
            patch(
                "researcher_mcp.tools.pdf.ArxivSource",
                return_value=MagicMock(fetch_pdf=AsyncMock(return_value=arxiv_fail)),
            ),
            patch(
                "researcher_mcp.tools.pdf.SciHubSource",
                return_value=MagicMock(
                    fetch_pdf=AsyncMock(
                        side_effect=MCPError(
                            "SCIHUB_DISABLED",
                            "SciHub disabled; set SCIHUB_ENABLED=true to attempt SciHub",
                        )
                    )
                ),
            ),
        ):
            result = await fetch_paper_pdf("10.1/test", "/tmp/test.pdf")

        assert result["success"] is False
        assert any("SciHub disabled" in w for w in result["warnings"])
