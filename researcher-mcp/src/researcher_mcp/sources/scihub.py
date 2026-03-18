"""SciHub source — opt-in only, disabled by default.

WARNING: SciHub access is opt-in only (``SCIHUB_ENABLED=true``). Users are
solely responsible for compliance with applicable copyright law in their
jurisdiction. The authors of this software do not condone copyright
infringement. This module is provided for jurisdictions where access to
SciHub is legal.

``scidownl`` is a conditional import guarded by ``scihub_enabled`` — it is
never imported at module level so that deployments where SciHub is disabled
do not even load the library.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


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

    Uses ``scidownl.scihub_download`` wrapped in ``asyncio.to_thread`` to
    avoid blocking the event loop.
    """

    def __init__(
        self,
        scihub_enabled: bool = False,
        scihub_url: str = "https://sci-hub.se",
    ) -> None:
        """Initialise source.

        Args:
            scihub_enabled: Must be ``True`` to allow any outbound request.
                Defaults to ``False`` (safe default).
            scihub_url: Base URL of the SciHub mirror to use.

        """
        self._enabled = scihub_enabled
        self._url = scihub_url.rstrip("/")

    async def fetch_pdf(self, doi: str) -> dict[str, Any]:
        """Attempt to download a PDF from SciHub for *doi*.

        Raises :class:`MCPError` with code ``"SCIHUB_DISABLED"`` if
        ``SCIHUB_ENABLED`` is false — no outbound request is made.

        Uses ``scidownl.scihub_download`` wrapped in ``asyncio.to_thread``.

        Args:
            doi: Paper DOI.

        Returns:
            A dict with ``available``, ``pdf_bytes_b64``, ``source``, and
            ``open_access_url`` keys.

        Raises:
            MCPError: If SciHub access is disabled.

        """
        if not self._enabled:
            raise MCPError(
                "SCIHUB_DISABLED",
                "SciHub disabled; set SCIHUB_ENABLED=true to attempt SciHub",
            )

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = Path(tmpdir) / "paper.pdf"
                scihub_url = self._url

                def _sync_download() -> bool:
                    from scidownl import scihub_download  # type: ignore[import-untyped]

                    scihub_download(
                        doi,
                        paper_type="doi",
                        out=str(out_path),
                        scihub_url=scihub_url,
                    )
                    return out_path.exists() and out_path.stat().st_size > 0

                success = await asyncio.to_thread(_sync_download)
                if not success:
                    return {
                        "available": False,
                        "pdf_bytes_b64": None,
                        "source": "unavailable",
                        "open_access_url": None,
                    }

                pdf_bytes = out_path.read_bytes()
                return {
                    "available": True,
                    "pdf_bytes_b64": base64.b64encode(pdf_bytes).decode(),
                    "source": "scihub",
                    "open_access_url": f"{self._url}/{doi}",
                }
        except Exception as exc:  # noqa: BLE001
            logger.warning("scidownl failed doi=%s: %s", doi, exc)
            return {
                "available": False,
                "pdf_bytes_b64": None,
                "source": "unavailable",
                "open_access_url": None,
            }
