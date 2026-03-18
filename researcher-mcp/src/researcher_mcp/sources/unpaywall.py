"""Unpaywall source for open-access PDF link resolution.

Uses the ``unpywall`` library (wraps Unpaywall's REST API) to find open-access
PDF URLs for a given DOI.  All ``unpywall`` calls are wrapped in
``asyncio.to_thread`` because the library is synchronous.
"""

from __future__ import annotations

import asyncio
import base64
import logging
from typing import Any

import httpx

from researcher_mcp.core.http_client import with_retry

logger = logging.getLogger(__name__)


class UnpaywallSource:
    """Resolves open-access PDF links via the Unpaywall API.

    Uses ``unpywall.Unpywall.get_pdf_link(doi)`` to obtain the best OA URL,
    then downloads the PDF bytes using the shared ``httpx`` client.
    """

    def __init__(self, client: httpx.AsyncClient, email: str = "researcher@example.com") -> None:
        """Initialise source.

        Args:
            client: Shared :class:`httpx.AsyncClient`.
            email: Required by Unpaywall API for identification (Unpaywall ToS).

        """
        self._client = client
        self._email = email

    async def get_pdf_link(self, doi: str) -> str | None:
        """Return the best open-access PDF URL for *doi*, or None if unavailable.

        Delegates to ``unpywall.Unpywall.get_pdf_link`` in a thread to avoid
        blocking the event loop with the synchronous unpywall calls.

        Args:
            doi: Paper DOI string.

        Returns:
            A PDF URL string, or None when no open-access version is found.

        """
        try:
            import unpywall  # type: ignore[import-untyped]

            email = self._email

            def _sync() -> str | None:
                unpywall.Unpywall.email = email  # type: ignore[attr-defined]
                return unpywall.Unpywall.get_pdf_link(doi)  # type: ignore[attr-defined]

            return await asyncio.to_thread(_sync)
        except Exception as exc:  # noqa: BLE001
            logger.warning("unpywall.get_pdf_link failed doi=%s: %s", doi, exc)
            return None

    async def fetch_pdf_bytes(self, pdf_url: str) -> bytes | None:
        """Download PDF bytes from *pdf_url*.

        Args:
            pdf_url: Direct URL to the PDF file.

        Returns:
            Raw PDF bytes, or None on download failure.

        """
        try:

            async def _download() -> bytes:
                r = await self._client.get(pdf_url, follow_redirects=True, timeout=60.0)
                r.raise_for_status()
                return r.content

            return await with_retry(_download)
        except (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException) as exc:
            logger.warning("unpaywall PDF download failed url=%s: %s", pdf_url, exc)
            return None

    async def fetch_pdf(self, doi: str) -> dict[str, Any]:
        """Attempt to retrieve a PDF via Unpaywall for *doi*.

        Queries Unpaywall for an open-access URL, then downloads the file.

        Args:
            doi: Paper DOI string.

        Returns:
            A dict with ``available``, ``source``, ``pdf_bytes_b64``, and
            ``open_access_url`` keys.

        """
        pdf_url = await self.get_pdf_link(doi)
        if not pdf_url:
            return {
                "available": False,
                "source": "unavailable",
                "pdf_bytes_b64": None,
                "open_access_url": None,
            }

        content = await self.fetch_pdf_bytes(pdf_url)
        if content is None:
            return {
                "available": False,
                "source": "unavailable",
                "pdf_bytes_b64": None,
                "open_access_url": pdf_url,
            }

        return {
            "available": True,
            "source": "unpaywall",
            "pdf_bytes_b64": base64.b64encode(content).decode(),
            "open_access_url": pdf_url,
        }
