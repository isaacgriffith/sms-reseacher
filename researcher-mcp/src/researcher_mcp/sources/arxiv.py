"""arXiv source for preprint PDF fetching."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from researcher_mcp.core.http_client import with_retry
from researcher_mcp.sources.crossref import CrossRefSource


class ArxivSource:
    """Resolves arXiv IDs from DOIs via CrossRef and downloads PDFs."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        """Initialise source.

        Args:
            client: Shared :class:`httpx.AsyncClient`.
        """
        self._client = client
        self._crossref = CrossRefSource(client)

    def _extract_arxiv_id(self, metadata: dict[str, Any]) -> str | None:
        """Extract an arXiv ID from CrossRef metadata if present."""
        for ref in metadata.get("references", []):
            doi: str = ref.get("doi") or ""
            if "arxiv" in doi.lower():
                return doi.split("/")[-1]
        for field in ("doi", "paper_id"):
            val: str = metadata.get(field) or ""
            if "arxiv" in val.lower():
                return val.split("/")[-1]
        return None

    async def fetch_pdf(self, doi: str, output_path: str) -> dict[str, Any]:
        """Attempt to resolve *doi* to an arXiv ID and download the PDF.

        Uses CrossRef metadata to locate an arXiv identifier, then
        downloads ``arxiv.org/pdf/{arxiv_id}``.

        Args:
            doi: Paper DOI string.
            output_path: Local path to save the PDF.

        Returns:
            A dict with ``success``, ``output_path``, ``source``, ``url``,
            and ``warnings`` keys.
        """
        try:
            metadata = await self._crossref.resolve_doi(doi)
        except (httpx.HTTPStatusError, httpx.TransportError):
            return {
                "success": False,
                "output_path": None,
                "source": None,
                "url": None,
                "warnings": ["CrossRef lookup failed; cannot resolve arXiv ID"],
            }

        arxiv_id = self._extract_arxiv_id(metadata)
        if not arxiv_id:
            return {
                "success": False,
                "output_path": None,
                "source": None,
                "url": None,
                "warnings": ["No arXiv ID found for this DOI"],
            }

        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
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
                "source": "arxiv",
                "url": pdf_url,
                "warnings": [],
            }
        except (httpx.HTTPStatusError, httpx.TransportError):
            return {
                "success": False,
                "output_path": None,
                "source": None,
                "url": pdf_url,
                "warnings": ["arXiv PDF download failed"],
            }
