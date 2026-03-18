"""Google Scholar source adapter.

Implements the :class:`DatabaseSource` protocol using the ``scholarly`` library.
All ``scholarly`` calls are synchronous and CPU-bound; they are wrapped with
:func:`asyncio.to_thread` to honour the Constitution's async-discipline
requirement.

WARNING: Google Scholar does not have an official API.  Use of ``scholarly``
may violate Google's Terms of Service and CAPTCHA detection may block requests.
Using a proxy (``scholarly_proxy_url`` setting) is strongly recommended in
production environments.
"""

from __future__ import annotations

import asyncio
from typing import Any

from researcher_mcp.sources.base import (
    AuthorInfo,
    PaperRecord,
    normalise_doi,
    normalise_title,
)


def _get_scholarly() -> Any:
    """Import and return the scholarly module.

    Returns:
        The ``scholarly`` module.

    Raises:
        ImportError: If the ``scholarly`` package is not installed.

    """
    import scholarly  # noqa: PLC0415

    return scholarly


class GoogleScholarSource:
    """Academic paper search via Google Scholar using the ``scholarly`` library.

    Synchronous ``scholarly`` calls are offloaded to a thread pool via
    :func:`asyncio.to_thread`.

    Attributes:
        _proxy_url: Optional HTTP proxy URL for ``scholarly`` requests.

    """

    def __init__(self, proxy_url: str = "") -> None:
        """Initialise GoogleScholarSource.

        Args:
            proxy_url: Optional HTTP(S) proxy URL passed to ``scholarly``'s
                proxy configuration.  Empty string disables proxy.

        """
        self._proxy_url = proxy_url

    def _configure_scholarly(self) -> None:
        """Configure scholarly proxy settings if a proxy URL is provided.

        This should be called inside :func:`asyncio.to_thread` because
        ``scholarly`` performs network I/O during configuration.
        """
        scholarly_mod = _get_scholarly()
        if self._proxy_url:
            scholarly_mod.scholarly.use_proxy(scholarly_mod.ProxyGenerator())

    def _normalise_result(self, item: dict[str, Any]) -> PaperRecord:
        """Convert a scholarly search result to a :class:`PaperRecord`.

        Args:
            item: A dict returned by ``scholarly.search_pubs``.

        Returns:
            A normalised :class:`PaperRecord`.

        """
        bib = item.get("bib", {})
        title = normalise_title(bib.get("title", ""))

        raw_authors = bib.get("author", "")
        if isinstance(raw_authors, str):
            author_names = [a.strip() for a in raw_authors.split(" and ") if a.strip()]
        elif isinstance(raw_authors, list):
            author_names = [str(a).strip() for a in raw_authors if str(a).strip()]
        else:
            author_names = []
        authors = [AuthorInfo(name=n) for n in author_names]

        year_raw = bib.get("pub_year")
        year: int | None = None
        try:
            year = int(year_raw) if year_raw else None
        except ValueError, TypeError:
            year = None

        doi = normalise_doi(
            item.get("externalids", {}).get("DOI")
            if hasattr(item.get("externalids"), "get")
            else None
        )

        return PaperRecord(
            doi=doi,
            title=title,
            abstract=bib.get("abstract"),
            authors=authors,
            year=year,
            venue=bib.get("venue") or bib.get("journal"),
            url=item.get("pub_url"),
            source_database="google_scholar",
            raw_id=item.get("scholar_id"),
        )

    async def search(
        self,
        query: str,
        max_results: int = 100,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[PaperRecord]:
        """Search Google Scholar for papers matching *query*.

        Args:
            query: Free-text search query.
            max_results: Maximum number of results to return.
            year_from: Earliest publication year filter.
            year_to: Latest publication year filter.

        Returns:
            List of :class:`PaperRecord` objects.  Returns an empty list on
            CAPTCHA block or other failures.

        """

        def _run() -> list[dict[str, Any]]:
            scholarly_mod = _get_scholarly()
            if self._proxy_url:
                pg = scholarly_mod.ProxyGenerator()
                try:
                    pg.SingleProxy(self._proxy_url)
                    scholarly_mod.scholarly.use_proxy(pg)
                except Exception:  # noqa: BLE001
                    pass

            search_query = query
            if year_from:
                search_query = f"{search_query} after:{year_from - 1}"
            if year_to:
                search_query = f"{search_query} before:{year_to + 1}"

            results: list[dict[str, Any]] = []
            try:
                for pub in scholarly_mod.scholarly.search_pubs(search_query):
                    results.append(dict(pub))
                    if len(results) >= max_results:
                        break
            except Exception:  # noqa: BLE001
                pass
            return results

        try:
            raw_results = await asyncio.to_thread(_run)
        except Exception:  # noqa: BLE001
            return []

        return [self._normalise_result(r) for r in raw_results if r.get("bib", {}).get("title")]

    async def get_paper(self, doi: str) -> PaperRecord | None:
        """Look up a Google Scholar entry by DOI.

        Args:
            doi: Paper DOI string.

        Returns:
            A :class:`PaperRecord` if a matching result is found, or ``None``.

        """

        def _run() -> dict[str, Any] | None:
            scholarly_mod = _get_scholarly()
            try:
                results = list(scholarly_mod.scholarly.search_pubs(f"doi:{doi}"))
                if results:
                    return dict(results[0])
            except Exception:  # noqa: BLE001
                pass
            return None

        try:
            raw = await asyncio.to_thread(_run)
        except Exception:  # noqa: BLE001
            return None

        if raw is None or not raw.get("bib", {}).get("title"):
            return None
        return self._normalise_result(raw)
