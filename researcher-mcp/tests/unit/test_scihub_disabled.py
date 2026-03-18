"""Unit test: SCIHUB_ENABLED=false causes SciHub to be skipped (T036)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from researcher_mcp.sources.scihub import MCPError, SciHubSource
from researcher_mcp.tools.pdf import fetch_paper_pdf


class TestSciHubDisabled:
    """Verify SciHub is skipped when SCIHUB_ENABLED=false."""

    async def test_scihub_raises_mcp_error_when_disabled(self) -> None:
        """SciHubSource.fetch_pdf raises MCPError('SCIHUB_DISABLED') when disabled."""
        source = SciHubSource(scihub_enabled=False)
        with pytest.raises(MCPError) as exc_info:
            await source.fetch_pdf("10.1/test")
        assert exc_info.value.code == "SCIHUB_DISABLED"

    async def test_fetch_paper_pdf_no_scihub_request_when_disabled(self) -> None:
        """fetch_paper_pdf returns available=False when SCIHUB_ENABLED=false."""
        miss = {
            "available": False,
            "source": "unavailable",
            "pdf_bytes_b64": None,
            "open_access_url": None,
        }
        mock_settings = MagicMock(
            scihub_enabled=False,
            scihub_url="https://sci-hub.se",
            unpaywall_email="test@example.com",
        )

        with (
            patch("researcher_mcp.tools.pdf.get_settings", return_value=mock_settings),
            patch("researcher_mcp.tools.pdf._try_unpaywall", new=AsyncMock(return_value=miss)),
            patch("researcher_mcp.tools.pdf._try_direct", new=AsyncMock(return_value=miss)),
        ):
            result = await fetch_paper_pdf("10.1/test", allow_scihub=True)

        # SCIHUB_ENABLED=false means SciHub is not attempted even with allow_scihub=True
        assert result["available"] is False
        assert result["source"] == "unavailable"
