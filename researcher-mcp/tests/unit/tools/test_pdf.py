"""Unit tests for the upgraded fetch_paper_pdf waterfall tool (T036).

Covers:
- Unpaywall success path returns PdfFetchResult with source="unpaywall".
- Unpaywall miss → direct URL fallback returns source="direct".
- Unpaywall miss → direct miss → SciHub disabled guard returns available=False.
- Unpaywall miss → direct miss → SciHub allowed path returns source="scihub".
- All three sources fail → available=False, source="unavailable".
- allow_scihub=False prevents SciHub even when SCIHUB_ENABLED=True.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_settings():
    """Return a mock settings object with SciHub disabled by default."""
    s = MagicMock()
    s.scihub_enabled = False
    s.scihub_url = "https://sci-hub.se"
    s.unpaywall_email = "test@example.com"
    return s


class TestFetchPaperPdfTool:
    """Tests for the fetch_paper_pdf MCP tool waterfall."""

    @pytest.mark.asyncio
    async def test_unpaywall_success_returns_unpaywall_source(self, mock_settings) -> None:
        """Unpaywall success short-circuits the waterfall."""
        from researcher_mcp.tools.pdf import fetch_paper_pdf

        unpaywall_result = {
            "available": True,
            "source": "unpaywall",
            "pdf_bytes_b64": "dGVzdA==",
            "open_access_url": "https://example.com/paper.pdf",
        }
        with (
            patch("researcher_mcp.tools.pdf.get_settings", return_value=mock_settings),
            patch("researcher_mcp.tools.pdf._try_unpaywall", new=AsyncMock(return_value=unpaywall_result)),
        ):
            result = await fetch_paper_pdf(doi="10.1234/test")
            assert result["available"] is True
            assert result["source"] == "unpaywall"
            assert result["pdf_bytes_b64"] == "dGVzdA=="

    @pytest.mark.asyncio
    async def test_unpaywall_miss_falls_back_to_direct_url(self, mock_settings) -> None:
        """When Unpaywall finds no OA copy, direct URL is tried."""
        from researcher_mcp.tools.pdf import fetch_paper_pdf

        unpaywall_miss = {"available": False, "source": "unavailable", "pdf_bytes_b64": None, "open_access_url": None}
        direct_hit = {
            "available": True,
            "source": "direct",
            "pdf_bytes_b64": "dGVzdA==",
            "open_access_url": "https://example.com/paper.pdf",
        }
        with (
            patch("researcher_mcp.tools.pdf.get_settings", return_value=mock_settings),
            patch("researcher_mcp.tools.pdf._try_unpaywall", new=AsyncMock(return_value=unpaywall_miss)),
            patch("researcher_mcp.tools.pdf._try_direct", new=AsyncMock(return_value=direct_hit)),
        ):
            result = await fetch_paper_pdf(doi="10.1234/test", url="https://example.com/paper.pdf")
            assert result["available"] is True
            assert result["source"] == "direct"

    @pytest.mark.asyncio
    async def test_scihub_disabled_guard(self, mock_settings) -> None:
        """When SCIHUB_ENABLED=False, allow_scihub=True request returns available=False."""
        from researcher_mcp.tools.pdf import fetch_paper_pdf

        miss = {"available": False, "source": "unavailable", "pdf_bytes_b64": None, "open_access_url": None}
        with (
            patch("researcher_mcp.tools.pdf.get_settings", return_value=mock_settings),
            patch("researcher_mcp.tools.pdf._try_unpaywall", new=AsyncMock(return_value=miss)),
            patch("researcher_mcp.tools.pdf._try_direct", new=AsyncMock(return_value=miss)),
        ):
            result = await fetch_paper_pdf(doi="10.1234/test", allow_scihub=True)
            assert result["available"] is False
            assert result["source"] == "unavailable"

    @pytest.mark.asyncio
    async def test_scihub_allowed_path(self, mock_settings) -> None:
        """When SCIHUB_ENABLED=True and allow_scihub=True, SciHub is tried."""
        mock_settings.scihub_enabled = True
        from researcher_mcp.tools.pdf import fetch_paper_pdf

        miss = {"available": False, "source": "unavailable", "pdf_bytes_b64": None, "open_access_url": None}
        scihub_hit = {
            "available": True,
            "source": "scihub",
            "pdf_bytes_b64": "dGVzdA==",
            "open_access_url": None,
        }
        with (
            patch("researcher_mcp.tools.pdf.get_settings", return_value=mock_settings),
            patch("researcher_mcp.tools.pdf._try_unpaywall", new=AsyncMock(return_value=miss)),
            patch("researcher_mcp.tools.pdf._try_direct", new=AsyncMock(return_value=miss)),
            patch("researcher_mcp.tools.pdf._try_scihub", new=AsyncMock(return_value=scihub_hit)),
        ):
            result = await fetch_paper_pdf(doi="10.1234/test", allow_scihub=True)
            assert result["available"] is True
            assert result["source"] == "scihub"

    @pytest.mark.asyncio
    async def test_all_sources_fail_returns_unavailable(self, mock_settings) -> None:
        """When all sources fail, result is available=False, source='unavailable'."""
        from researcher_mcp.tools.pdf import fetch_paper_pdf

        miss = {"available": False, "source": "unavailable", "pdf_bytes_b64": None, "open_access_url": None}
        with (
            patch("researcher_mcp.tools.pdf.get_settings", return_value=mock_settings),
            patch("researcher_mcp.tools.pdf._try_unpaywall", new=AsyncMock(return_value=miss)),
            patch("researcher_mcp.tools.pdf._try_direct", new=AsyncMock(return_value=miss)),
        ):
            result = await fetch_paper_pdf(doi="10.1234/test")
            assert result["available"] is False
            assert result["source"] == "unavailable"
            assert result["pdf_bytes_b64"] is None

    @pytest.mark.asyncio
    async def test_allow_scihub_false_prevents_scihub_even_when_enabled(self, mock_settings) -> None:
        """allow_scihub=False (default) never calls SciHub even if server has it enabled."""
        mock_settings.scihub_enabled = True
        from researcher_mcp.tools.pdf import fetch_paper_pdf

        miss = {"available": False, "source": "unavailable", "pdf_bytes_b64": None, "open_access_url": None}
        scihub_mock = AsyncMock(return_value={"available": True, "source": "scihub", "pdf_bytes_b64": "x", "open_access_url": None})
        with (
            patch("researcher_mcp.tools.pdf.get_settings", return_value=mock_settings),
            patch("researcher_mcp.tools.pdf._try_unpaywall", new=AsyncMock(return_value=miss)),
            patch("researcher_mcp.tools.pdf._try_direct", new=AsyncMock(return_value=miss)),
            patch("researcher_mcp.tools.pdf._try_scihub", new=scihub_mock),
        ):
            result = await fetch_paper_pdf(doi="10.1234/test", allow_scihub=False)
            assert result["available"] is False
            scihub_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_scihub_mcp_error_caught_returns_unavailable(self, mock_settings) -> None:
        """MCPError from SciHub is caught and returns unavailable result."""
        mock_settings.scihub_enabled = True
        from researcher_mcp.tools.pdf import fetch_paper_pdf
        from researcher_mcp.sources.scihub import MCPError

        miss = {"available": False, "source": "unavailable", "pdf_bytes_b64": None, "open_access_url": None}
        with (
            patch("researcher_mcp.tools.pdf.get_settings", return_value=mock_settings),
            patch("researcher_mcp.tools.pdf._try_unpaywall", new=AsyncMock(return_value=miss)),
            patch("researcher_mcp.tools.pdf._try_direct", new=AsyncMock(return_value=miss)),
            patch("researcher_mcp.tools.pdf._try_scihub", new=AsyncMock(side_effect=MCPError("SCIHUB_DISABLED"))),
        ):
            result = await fetch_paper_pdf(doi="10.1234/test", allow_scihub=True)
            assert result["available"] is False


class TestTryDirectHelper:
    """Tests for the _try_direct internal helper function."""

    @pytest.mark.asyncio
    async def test_try_direct_success(self) -> None:
        """_try_direct returns available=True on successful download."""
        import base64
        from unittest.mock import patch, MagicMock, AsyncMock
        import httpx

        pdf_content = b"%PDF-1.4 direct"
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.content = pdf_content
        mock_resp.raise_for_status.return_value = None

        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=mock_resp)

        with patch("researcher_mcp.tools.pdf.make_retry_client", return_value=mock_client):
            from researcher_mcp.tools.pdf import _try_direct

            result = await _try_direct("https://example.com/paper.pdf")

        assert result["available"] is True
        assert result["source"] == "direct"
        assert base64.b64decode(result["pdf_bytes_b64"]) == pdf_content

    @pytest.mark.asyncio
    async def test_try_direct_http_error_returns_unavailable(self) -> None:
        """_try_direct returns unavailable on HTTP error."""
        from unittest.mock import patch, MagicMock, AsyncMock
        import httpx

        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError("404", request=MagicMock(), response=MagicMock())
        )

        with patch("researcher_mcp.tools.pdf.make_retry_client", return_value=mock_client):
            from researcher_mcp.tools.pdf import _try_direct

            result = await _try_direct("https://example.com/notfound.pdf")

        assert result["available"] is False

    @pytest.mark.asyncio
    async def test_try_direct_transport_error_returns_unavailable(self) -> None:
        """_try_direct returns unavailable on TransportError."""
        from unittest.mock import patch, MagicMock, AsyncMock
        import httpx

        mock_client = MagicMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(side_effect=httpx.TransportError("network error"))

        with patch("researcher_mcp.tools.pdf.make_retry_client", return_value=mock_client):
            from researcher_mcp.tools.pdf import _try_direct

            result = await _try_direct("https://example.com/error.pdf")

        assert result["available"] is False

    @pytest.mark.asyncio
    async def test_try_unpaywall_delegates_to_source(self) -> None:
        """_try_unpaywall creates UnpaywallSource and calls fetch_pdf."""
        from unittest.mock import patch, MagicMock, AsyncMock

        fetch_result = {
            "available": True,
            "source": "unpaywall",
            "pdf_bytes_b64": "dGVzdA==",
            "open_access_url": "https://example.com/paper.pdf",
        }

        with patch("researcher_mcp.tools.pdf.make_retry_client", return_value=MagicMock()):
            with patch("researcher_mcp.tools.pdf.UnpaywallSource") as mock_uw_cls:
                mock_uw = MagicMock()
                mock_uw.fetch_pdf = AsyncMock(return_value=fetch_result)
                mock_uw_cls.return_value = mock_uw

                from researcher_mcp.tools.pdf import _try_unpaywall

                result = await _try_unpaywall("10.1234/test", "test@example.com")

        assert result["available"] is True
        assert result["source"] == "unpaywall"

    @pytest.mark.asyncio
    async def test_try_scihub_delegates_to_source(self) -> None:
        """_try_scihub creates SciHubSource and calls fetch_pdf."""
        from unittest.mock import patch, AsyncMock

        scihub_result = {
            "available": True,
            "source": "scihub",
            "pdf_bytes_b64": "dGVzdA==",
            "open_access_url": None,
        }

        with patch("researcher_mcp.tools.pdf.SciHubSource") as mock_sh_cls:
            mock_sh = MagicMock()
            mock_sh.fetch_pdf = AsyncMock(return_value=scihub_result)
            mock_sh_cls.return_value = mock_sh

            from researcher_mcp.tools.pdf import _try_scihub

            result = await _try_scihub(
                "10.1234/test", scihub_enabled=True, scihub_url="https://sci-hub.se"
            )

        assert result["available"] is True
