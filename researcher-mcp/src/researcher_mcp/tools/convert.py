"""MCP tools: convert_paper_to_markdown and get_paper_markdown (T047).

Uses MarkItDown for PDF-to-Markdown conversion.  All MarkItDown calls are
wrapped in ``asyncio.to_thread`` since the library is synchronous.

Conversion priority order for ``convert_paper_to_markdown``:
1. ``pdf_bytes_b64`` — caller-supplied base64-encoded PDF bytes.
2. ``url`` — direct URL downloaded via httpx then converted.
3. ``doi`` — triggers ``fetch_paper_pdf`` internally, then converts.
"""

from __future__ import annotations

import asyncio
import base64
import io
import logging
from typing import Any

import httpx
from fastmcp import FastMCP

from researcher_mcp.core.config import get_settings
from researcher_mcp.tools.pdf import fetch_paper_pdf

mcp: FastMCP = FastMCP("researcher-mcp")
logger = logging.getLogger(__name__)


def _get_markitdown(enable_ocr: bool = False) -> Any:
    """Return a configured MarkItDown instance.

    Args:
        enable_ocr: When True, instantiate MarkItDown with an LLM client for
            OCR-assisted conversion.

    Returns:
        A ``MarkItDown`` instance.

    """
    from markitdown import MarkItDown  # type: ignore[import-untyped]

    if enable_ocr:
        settings = get_settings()
        if settings.markitdown_ocr_model:
            try:
                import anthropic  # type: ignore[import-untyped, import-not-found]

                llm_client = anthropic.Anthropic()
                return MarkItDown(llm_client=llm_client, llm_model=settings.markitdown_ocr_model)
            except Exception:  # noqa: BLE001
                pass
    return MarkItDown()


def _make_result(
    text: str,
    method: str,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    """Build a MarkdownConversionResult dict.

    Args:
        text: Converted Markdown text.
        method: Conversion method identifier.
        warnings: Optional list of warning messages.

    Returns:
        Dict matching the ``MarkdownConversionResult`` schema.

    """
    words = len(text.split()) if text else 0
    return {
        "markdown": text,
        "title": None,
        "page_count": None,
        "word_count": words,
        "conversion_method": method,
        "warnings": warnings or [],
    }


async def _fetch_stored_markdown(
    doi: str | None = None,
    paper_id: str | None = None,
) -> dict[str, Any]:
    """Fetch stored Markdown from the backend API.

    Queries ``GET /api/v1/papers/{paper_id}/markdown`` via httpx.

    Args:
        doi: Paper DOI (used to look up paper_id if paper_id not provided).
        paper_id: Backend paper primary key.

    Returns:
        Dict with ``available``, ``markdown``, ``converted_at``,
        and ``full_text_source`` keys.

    """
    settings = get_settings()
    backend_url = getattr(settings, "backend_url", "http://localhost:8000")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if paper_id:
                resp = await client.get(f"{backend_url}/api/v1/papers/{paper_id}/markdown")
                resp.raise_for_status()
                data = resp.json()
                return {
                    "available": data.get("available", False),
                    "markdown": data.get("markdown"),
                    "converted_at": data.get("converted_at"),
                    "full_text_source": data.get("full_text_source"),
                }
    except Exception as exc:  # noqa: BLE001
        logger.warning("_fetch_stored_markdown failed: %s", exc)

    return {"available": False, "markdown": None, "converted_at": None}


async def _convert_bytes(pdf_bytes: bytes, enable_ocr: bool) -> dict[str, Any]:
    """Convert raw PDF bytes to Markdown using MarkItDown.

    Args:
        pdf_bytes: Raw PDF bytes to convert.
        enable_ocr: Whether to enable OCR-assisted conversion.

    Returns:
        A MarkdownConversionResult dict.

    """
    method = "markitdown-ocr" if enable_ocr else "markitdown"
    try:
        md = _get_markitdown(enable_ocr=enable_ocr)

        def _sync_convert() -> str:
            stream = io.BytesIO(pdf_bytes)
            result = md.convert_stream(stream, file_extension=".pdf")
            return result.text_content

        text = await asyncio.to_thread(_sync_convert)
        return _make_result(text, method)
    except Exception as exc:  # noqa: BLE001
        logger.warning("MarkItDown conversion failed: %s", exc)
        return _make_result("", method, warnings=[f"Conversion error: {exc}"])


@mcp.tool()
async def convert_paper_to_markdown(
    pdf_bytes_b64: str | None = None,
    url: str | None = None,
    doi: str | None = None,
    enable_ocr: bool = False,
) -> dict[str, Any]:
    """Convert a paper PDF to Markdown using MarkItDown.

    Input priority: ``pdf_bytes_b64`` > ``url`` > ``doi``.  When a ``doi`` is
    provided, ``fetch_paper_pdf`` is called internally to obtain the PDF.

    Args:
        pdf_bytes_b64: Base64-encoded PDF bytes to convert directly.
        url: Direct URL to download the PDF from before converting.
        doi: Paper DOI — triggers ``fetch_paper_pdf`` to obtain the PDF.
        enable_ocr: When True, enables OCR-assisted conversion via an LLM
            (requires ``MARKITDOWN_OCR_MODEL`` to be set).

    Returns:
        Dict matching ``MarkdownConversionResult`` schema with keys
        ``markdown``, ``title``, ``page_count``, ``word_count``,
        ``conversion_method``, and ``warnings``.

    """
    method = "markitdown-ocr" if enable_ocr else "markitdown"

    if pdf_bytes_b64:
        pdf_bytes = base64.b64decode(pdf_bytes_b64)
        return await _convert_bytes(pdf_bytes, enable_ocr)

    if url:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(url, follow_redirects=True)
                resp.raise_for_status()
                pdf_bytes = resp.content
            return await _convert_bytes(pdf_bytes, enable_ocr)
        except (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException) as exc:
            logger.warning("URL download failed url=%s: %s", url, exc)
            return _make_result("", method, warnings=[f"URL download failed: {exc}"])

    if doi:
        fetch_result = await fetch_paper_pdf(doi=doi)
        if not fetch_result.get("available") or not fetch_result.get("pdf_bytes_b64"):
            return _make_result(
                "",
                method,
                warnings=[
                    f"Could not retrieve PDF for DOI {doi}: source={fetch_result.get('source')}"
                ],
            )
        pdf_bytes = base64.b64decode(fetch_result["pdf_bytes_b64"])
        return await _convert_bytes(pdf_bytes, enable_ocr)

    # No valid input provided
    return _make_result(
        "", method, warnings=["No input provided: supply pdf_bytes_b64, url, or doi"]
    )


@mcp.tool()
async def get_paper_markdown(
    doi: str | None = None,
    paper_id: str | None = None,
) -> dict[str, Any]:
    """Return stored Markdown for a paper already converted.

    Does not re-run conversion.  Call ``convert_paper_to_markdown`` first to
    produce and store Markdown.

    Args:
        doi: Paper DOI (used if *paper_id* is not available).
        paper_id: Backend paper primary key as a string.

    Returns:
        Dict matching ``StoredMarkdownResult`` schema with keys ``markdown``,
        ``converted_at``, and ``available``.

    """
    stored = await _fetch_stored_markdown(doi=doi, paper_id=paper_id)
    return {
        "markdown": stored.get("markdown"),
        "converted_at": stored.get("converted_at"),
        "available": stored.get("available", False),
    }
