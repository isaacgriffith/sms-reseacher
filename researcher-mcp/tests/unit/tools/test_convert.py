"""Unit tests for convert_paper_to_markdown and get_paper_markdown tools (T045).

Covers:
- pdf_bytes_b64 input path converts using MarkItDown.
- url input path downloads and converts.
- doi input path triggers fetch_paper_pdf then converts.
- enable_ocr=True uses the OCR-enabled MarkItDown client.
- Conversion failure returns MarkdownConversionResult with empty markdown.
- get_paper_markdown hit: returns stored markdown.
- get_paper_markdown miss: returns available=False.
"""

from __future__ import annotations

import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestConvertPaperToMarkdown:
    """Tests for convert_paper_to_markdown MCP tool."""

    @pytest.mark.asyncio
    async def test_pdf_bytes_b64_path_converts(self) -> None:
        """Providing pdf_bytes_b64 triggers MarkItDown conversion."""
        from researcher_mcp.tools.convert import convert_paper_to_markdown

        fake_bytes = b"%PDF-1.4 fake"
        pdf_b64 = base64.b64encode(fake_bytes).decode()

        mock_result = MagicMock()
        mock_result.text_content = "# Converted Title\n\nBody text."
        mock_markitdown = MagicMock()
        mock_markitdown.convert_stream.return_value = mock_result

        with patch("researcher_mcp.tools.convert._get_markitdown", return_value=mock_markitdown):
            result = await convert_paper_to_markdown(pdf_bytes_b64=pdf_b64)

        assert "# Converted Title" in result["markdown"]
        assert result["conversion_method"] == "markitdown"
        assert isinstance(result["word_count"], int)

    @pytest.mark.asyncio
    async def test_doi_path_fetches_pdf_then_converts(self) -> None:
        """doi input triggers fetch_paper_pdf, then converts the returned PDF."""
        from researcher_mcp.tools.convert import convert_paper_to_markdown

        fake_bytes = b"%PDF-1.4 test"
        pdf_b64 = base64.b64encode(fake_bytes).decode()

        fetch_result = {
            "available": True,
            "pdf_bytes_b64": pdf_b64,
            "source": "unpaywall",
            "open_access_url": "https://example.com/paper.pdf",
        }
        mock_result = MagicMock()
        mock_result.text_content = "# DOI Paper\n\nContent."
        mock_markitdown = MagicMock()
        mock_markitdown.convert_stream.return_value = mock_result

        with (
            patch("researcher_mcp.tools.convert.fetch_paper_pdf", new=AsyncMock(return_value=fetch_result)),
            patch("researcher_mcp.tools.convert._get_markitdown", return_value=mock_markitdown),
        ):
            result = await convert_paper_to_markdown(doi="10.1234/test")

        assert result["markdown"] is not None
        assert "DOI Paper" in result["markdown"]

    @pytest.mark.asyncio
    async def test_doi_path_unavailable_pdf_raises(self) -> None:
        """When fetch_paper_pdf cannot retrieve PDF, conversion raises/returns error state."""
        from researcher_mcp.tools.convert import convert_paper_to_markdown

        fetch_result = {
            "available": False,
            "pdf_bytes_b64": None,
            "source": "unavailable",
            "open_access_url": None,
        }
        with patch("researcher_mcp.tools.convert.fetch_paper_pdf", new=AsyncMock(return_value=fetch_result)):
            result = await convert_paper_to_markdown(doi="10.9999/unknown")

        assert result["markdown"] == ""
        assert len(result["warnings"]) > 0

    @pytest.mark.asyncio
    async def test_enable_ocr_uses_ocr_method(self) -> None:
        """enable_ocr=True uses the OCR conversion method label."""
        from researcher_mcp.tools.convert import convert_paper_to_markdown

        fake_bytes = b"%PDF-1.4 ocr"
        pdf_b64 = base64.b64encode(fake_bytes).decode()

        mock_result = MagicMock()
        mock_result.text_content = "OCR text"
        mock_markitdown = MagicMock()
        mock_markitdown.convert_stream.return_value = mock_result

        with patch("researcher_mcp.tools.convert._get_markitdown", return_value=mock_markitdown):
            result = await convert_paper_to_markdown(pdf_bytes_b64=pdf_b64, enable_ocr=True)

        assert result["conversion_method"] == "markitdown-ocr"

    @pytest.mark.asyncio
    async def test_conversion_failure_returns_empty_markdown(self) -> None:
        """MarkItDown exception returns MarkdownConversionResult with empty markdown and warning."""
        from researcher_mcp.tools.convert import convert_paper_to_markdown

        fake_bytes = b"%PDF-1.4 bad"
        pdf_b64 = base64.b64encode(fake_bytes).decode()

        mock_markitdown = MagicMock()
        mock_markitdown.convert_stream.side_effect = RuntimeError("conversion failed")

        with patch("researcher_mcp.tools.convert._get_markitdown", return_value=mock_markitdown):
            result = await convert_paper_to_markdown(pdf_bytes_b64=pdf_b64)

        assert result["markdown"] == ""
        assert len(result["warnings"]) > 0
        assert result["word_count"] == 0

    @pytest.mark.asyncio
    async def test_no_input_raises_or_returns_error(self) -> None:
        """Calling with no input returns error state or raises ValueError."""
        from researcher_mcp.tools.convert import convert_paper_to_markdown

        result = await convert_paper_to_markdown()
        # Either empty markdown with a warning, or an error result
        assert result["markdown"] == "" or "no input" in " ".join(result["warnings"]).lower()


class TestGetPaperMarkdownTool:
    """Tests for get_paper_markdown MCP tool."""

    @pytest.mark.asyncio
    async def test_hit_returns_stored_markdown(self) -> None:
        """When markdown exists in backend, returns it."""
        from researcher_mcp.tools.convert import get_paper_markdown

        stored = {
            "available": True,
            "markdown": "# Stored\n\nText.",
            "converted_at": "2025-01-01T00:00:00Z",
            "full_text_source": "unpaywall",
        }
        with patch("researcher_mcp.tools.convert._fetch_stored_markdown", new=AsyncMock(return_value=stored)):
            result = await get_paper_markdown(doi="10.1234/test")

        assert result["available"] is True
        assert result["markdown"] == "# Stored\n\nText."
        assert result["converted_at"] is not None

    @pytest.mark.asyncio
    async def test_miss_returns_available_false(self) -> None:
        """When no stored markdown, returns available=False."""
        from researcher_mcp.tools.convert import get_paper_markdown

        miss = {
            "available": False,
            "markdown": None,
            "converted_at": None,
        }
        with patch("researcher_mcp.tools.convert._fetch_stored_markdown", new=AsyncMock(return_value=miss)):
            result = await get_paper_markdown(doi="10.9999/missing")

        assert result["available"] is False
        assert result["markdown"] is None


class TestConvertUrlPath:
    """Tests for the URL download path of convert_paper_to_markdown."""

    @pytest.mark.asyncio
    async def test_url_path_downloads_and_converts(self) -> None:
        """URL input downloads PDF and then converts."""
        import base64
        import httpx
        from unittest.mock import patch, MagicMock, AsyncMock

        from researcher_mcp.tools.convert import convert_paper_to_markdown

        pdf_bytes = b"%PDF-1.4 url test"

        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.content = pdf_bytes
        mock_resp.raise_for_status.return_value = None

        mock_result = MagicMock()
        mock_result.text_content = "# From URL\n\nContent."
        mock_markitdown = MagicMock()
        mock_markitdown.convert_stream.return_value = mock_result

        with (
            patch("researcher_mcp.tools.convert.httpx.AsyncClient") as mock_client_cls,
            patch("researcher_mcp.tools.convert._get_markitdown", return_value=mock_markitdown),
        ):
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = await convert_paper_to_markdown(url="https://example.com/paper.pdf")

        assert "From URL" in result["markdown"]

    @pytest.mark.asyncio
    async def test_url_path_returns_warning_on_http_error(self) -> None:
        """URL download failure returns empty markdown with warning."""
        import httpx
        from unittest.mock import patch, MagicMock, AsyncMock

        from researcher_mcp.tools.convert import convert_paper_to_markdown

        with patch("researcher_mcp.tools.convert.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                side_effect=httpx.HTTPStatusError("403", request=MagicMock(), response=MagicMock())
            )
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = await convert_paper_to_markdown(url="https://example.com/forbidden.pdf")

        assert result["markdown"] == ""
        assert len(result["warnings"]) > 0
        assert "download failed" in result["warnings"][0].lower()

    @pytest.mark.asyncio
    async def test_url_path_returns_warning_on_transport_error(self) -> None:
        """Transport error during URL download returns empty markdown with warning."""
        import httpx
        from unittest.mock import patch, MagicMock, AsyncMock

        from researcher_mcp.tools.convert import convert_paper_to_markdown

        with patch("researcher_mcp.tools.convert.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=httpx.TransportError("connection refused"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = await convert_paper_to_markdown(url="https://example.com/broken.pdf")

        assert result["markdown"] == ""
        assert len(result["warnings"]) > 0


class TestConvertBytesHelper:
    """Tests for the _convert_bytes internal helper."""

    @pytest.mark.asyncio
    async def test_convert_bytes_returns_word_count(self) -> None:
        """_convert_bytes returns correct word count in result."""
        from unittest.mock import patch, MagicMock
        from researcher_mcp.tools.convert import _convert_bytes

        mock_result = MagicMock()
        mock_result.text_content = "Hello world foo bar"
        mock_markitdown = MagicMock()
        mock_markitdown.convert_stream.return_value = mock_result

        with patch("researcher_mcp.tools.convert._get_markitdown", return_value=mock_markitdown):
            result = await _convert_bytes(b"%PDF-1.4 test", enable_ocr=False)

        assert result["word_count"] == 4
        assert result["conversion_method"] == "markitdown"

    @pytest.mark.asyncio
    async def test_convert_bytes_ocr_method_label(self) -> None:
        """_convert_bytes sets method to 'markitdown-ocr' when enable_ocr=True."""
        from unittest.mock import patch, MagicMock
        from researcher_mcp.tools.convert import _convert_bytes

        mock_result = MagicMock()
        mock_result.text_content = "OCR converted text"
        mock_markitdown = MagicMock()
        mock_markitdown.convert_stream.return_value = mock_result

        with patch("researcher_mcp.tools.convert._get_markitdown", return_value=mock_markitdown):
            result = await _convert_bytes(b"%PDF-1.4 test", enable_ocr=True)

        assert result["conversion_method"] == "markitdown-ocr"


class TestFetchStoredMarkdown:
    """Tests for the _fetch_stored_markdown internal helper."""

    @pytest.mark.asyncio
    async def test_fetch_stored_markdown_with_paper_id(self) -> None:
        """_fetch_stored_markdown queries backend with paper_id."""
        import httpx
        from unittest.mock import patch, MagicMock, AsyncMock
        from researcher_mcp.tools.convert import _fetch_stored_markdown

        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "available": True,
            "markdown": "# Stored\n\nContent.",
            "converted_at": "2025-01-01T00:00:00Z",
            "full_text_source": "unpaywall",
        }

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_settings = MagicMock()
        mock_settings.backend_url = "http://localhost:8000"

        with (
            patch("researcher_mcp.tools.convert.get_settings", return_value=mock_settings),
            patch("researcher_mcp.tools.convert.httpx.AsyncClient", return_value=mock_client),
        ):
            result = await _fetch_stored_markdown(paper_id="123")

        assert result["available"] is True
        assert result["markdown"] == "# Stored\n\nContent."

    @pytest.mark.asyncio
    async def test_fetch_stored_markdown_returns_unavailable_on_exception(self) -> None:
        """_fetch_stored_markdown returns unavailable when backend call fails."""
        import httpx
        from unittest.mock import patch, MagicMock, AsyncMock
        from researcher_mcp.tools.convert import _fetch_stored_markdown

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        mock_settings = MagicMock()
        mock_settings.backend_url = "http://localhost:8000"

        with (
            patch("researcher_mcp.tools.convert.get_settings", return_value=mock_settings),
            patch("researcher_mcp.tools.convert.httpx.AsyncClient", return_value=mock_client),
        ):
            result = await _fetch_stored_markdown(paper_id="999")

        assert result["available"] is False
        assert result["markdown"] is None

    @pytest.mark.asyncio
    async def test_fetch_stored_markdown_no_paper_id_returns_unavailable(self) -> None:
        """_fetch_stored_markdown returns unavailable when no paper_id provided."""
        from unittest.mock import patch, MagicMock
        from researcher_mcp.tools.convert import _fetch_stored_markdown

        mock_settings = MagicMock()
        mock_settings.backend_url = "http://localhost:8000"

        with patch("researcher_mcp.tools.convert.get_settings", return_value=mock_settings):
            result = await _fetch_stored_markdown(doi="10.1234/test")

        assert result["available"] is False


class TestMakeResult:
    """Tests for the _make_result helper."""

    def test_make_result_counts_words(self) -> None:
        """_make_result computes correct word count."""
        from researcher_mcp.tools.convert import _make_result

        result = _make_result("hello world test", "markitdown")
        assert result["word_count"] == 3
        assert result["markdown"] == "hello world test"
        assert result["conversion_method"] == "markitdown"
        assert result["warnings"] == []

    def test_make_result_empty_text_zero_words(self) -> None:
        """_make_result returns zero word count for empty text."""
        from researcher_mcp.tools.convert import _make_result

        result = _make_result("", "markitdown")
        assert result["word_count"] == 0

    def test_make_result_with_warnings(self) -> None:
        """_make_result includes provided warnings."""
        from researcher_mcp.tools.convert import _make_result

        result = _make_result("", "markitdown", warnings=["Something went wrong"])
        assert len(result["warnings"]) == 1
        assert "Something went wrong" in result["warnings"][0]
