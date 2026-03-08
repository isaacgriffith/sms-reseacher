"""Unpaywall source for open-access PDF fetching."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from researcher_mcp.core.http_client import with_retry

_BASE = "https://api.unpaywall.org/v2"


class UnpaywallSource:
    """Fetches open-access PDFs via the Unpaywall API."""

    def __init__(self, client: httpx.AsyncClient, email: str = "researcher@example.com") -> None:
        """Initialise source.

        Args:
            client: Shared :class:`httpx.AsyncClient`.
            email: Required by Unpaywall API for identification.
        """
        self._client = client
        self._email = email

    async def fetch_pdf(self, doi: str, output_path: str) -> dict[str, Any]:
        """Attempt to download open-access PDF for *doi*.

        Queries ``api.unpaywall.org/{doi}`` and downloads from
        ``best_oa_location.url_for_pdf`` if present.

        Args:
            doi: Paper DOI string.
            output_path: Local filesystem path to save the downloaded PDF.

        Returns:
            A dict with ``success``, ``output_path``, ``source``, ``url``,
            and ``warnings`` keys.
        """
        url = f"{_BASE}/{doi}"

        async def _call() -> Any:
            r = await self._client.get(url, params={"email": self._email})
            r.raise_for_status()
            return r.json()

        try:
            data = await with_retry(_call)
        except (httpx.HTTPStatusError, httpx.TransportError):
            return {
                "success": False,
                "output_path": None,
                "source": None,
                "url": None,
                "warnings": ["Unpaywall lookup failed"],
            }

        best_oa = data.get("best_oa_location") or {}
        pdf_url: str | None = best_oa.get("url_for_pdf")
        if not pdf_url:
            return {
                "success": False,
                "output_path": None,
                "source": None,
                "url": None,
                "warnings": ["No open-access PDF found on Unpaywall"],
            }

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
                "source": "unpaywall",
                "url": pdf_url,
                "warnings": [],
            }
        except (httpx.HTTPStatusError, httpx.TransportError):
            return {
                "success": False,
                "output_path": None,
                "source": None,
                "url": pdf_url,
                "warnings": ["Unpaywall PDF download failed"],
            }
