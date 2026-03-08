"""SciHub source — opt-in only, disabled by default.

WARNING: SciHub access is opt-in only (``SCIHUB_ENABLED=true``). Users are
solely responsible for compliance with applicable copyright law in their
jurisdiction. The authors of this software do not condone copyright
infringement. This module is provided for jurisdictions where access to
SciHub is legal.
"""

from __future__ import annotations

from typing import Any

import httpx

from researcher_mcp.core.http_client import with_retry


class MCPError(Exception):
    """Raised to signal an MCP-level error with a structured code."""

    def __init__(self, code: str, message: str = "") -> None:
        """Create an MCPError.

        Args:
            code: Machine-readable error code (e.g. ``"SCIHUB_DISABLED"``).
            message: Human-readable detail.
        """
        super().__init__(message or code)
        self.code = code


class SciHubSource:
    """Attempts to fetch paper PDFs from SciHub (opt-in, default disabled).

    This source MUST only be instantiated when ``SCIHUB_ENABLED=true`` is
    explicitly set by the operator. Every public method checks the flag at
    call time as a defence-in-depth measure.
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        scihub_enabled: bool = False,
        scihub_url: str = "https://sci-hub.se",
    ) -> None:
        """Initialise source.

        Args:
            client: Shared :class:`httpx.AsyncClient`.
            scihub_enabled: Must be ``True`` to allow any outbound request.
                Defaults to ``False`` (safe default).
            scihub_url: Base URL of the SciHub mirror to use.
        """
        self._client = client
        self._enabled = scihub_enabled
        self._url = scihub_url.rstrip("/")

    async def fetch_pdf(self, doi: str, output_path: str) -> dict[str, Any]:
        """Attempt to download a PDF from SciHub for *doi*.

        Raises :class:`MCPError` with code ``"SCIHUB_DISABLED"`` if
        ``SCIHUB_ENABLED`` is false — no outbound request is made.

        Args:
            doi: Paper DOI.
            output_path: Local path to save the PDF.

        Returns:
            A dict with ``success``, ``output_path``, ``source``, ``url``,
            and ``warnings`` keys.

        Raises:
            MCPError: If SciHub access is disabled.
        """
        if not self._enabled:
            raise MCPError(
                "SCIHUB_DISABLED",
                "SciHub disabled; set SCIHUB_ENABLED=true to attempt SciHub",
            )

        from pathlib import Path

        target_url = f"{self._url}/{doi}"
        try:
            async def _get_page() -> str:
                r = await self._client.get(target_url, follow_redirects=True)
                r.raise_for_status()
                return r.text

            page_html = await with_retry(_get_page)
        except (httpx.HTTPStatusError, httpx.TransportError):
            return {
                "success": False,
                "output_path": None,
                "source": None,
                "url": target_url,
                "warnings": ["SciHub page fetch failed"],
            }

        import re

        pdf_match = re.search(r'src=["\']([^"\']+\.pdf[^"\']*)["\']', page_html)
        if not pdf_match:
            return {
                "success": False,
                "output_path": None,
                "source": None,
                "url": target_url,
                "warnings": ["SciHub: no PDF link found on page"],
            }

        pdf_url = pdf_match.group(1)
        if pdf_url.startswith("//"):
            pdf_url = f"https:{pdf_url}"

        try:
            async def _download() -> bytes:
                r = await self._client.get(pdf_url, follow_redirects=True)
                r.raise_for_status()
                return r.content

            content = await with_retry(_download)
            dest = Path(output_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
            return {
                "success": True,
                "output_path": str(dest),
                "source": "scihub",
                "url": pdf_url,
                "warnings": [
                    "PDF served by SciHub. Ensure compliance with local copyright law."
                ],
            }
        except (httpx.HTTPStatusError, httpx.TransportError):
            return {
                "success": False,
                "output_path": None,
                "source": None,
                "url": pdf_url,
                "warnings": ["SciHub PDF download failed"],
            }
