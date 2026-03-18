"""ScienceDirect source adapter via pybliometrics.

Implements the :class:`DatabaseSource` protocol using
``pybliometrics.ScienceDirectSearch`` and ``ArticleRetrieval``.  All
pybliometrics calls are synchronous and wrapped in :func:`asyncio.to_thread`.
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
from researcher_mcp.sources.scopus import _configure_pybliometrics


class ScienceDirectSource:
    """Wraps ScienceDirect search and article retrieval via pybliometrics.

    Shares the same Elsevier credentials as :class:`ScopusSource`.

    Attributes:
        _api_key: Elsevier API key.
        _inst_token: Elsevier institutional token.

    """

    def __init__(self, api_key: str = "", inst_token: str = "") -> None:
        """Initialise ScienceDirectSource.

        Args:
            api_key: Elsevier API key.
            inst_token: Elsevier institutional token (optional).

        """
        self._api_key = api_key
        self._inst_token = inst_token

    def _normalise_record(self, item: Any) -> PaperRecord:
        """Convert a pybliometrics ScienceDirectSearch result to :class:`PaperRecord`.

        Args:
            item: A single result object from ``ScienceDirectSearch.results``.

        Returns:
            A normalised :class:`PaperRecord`.

        """
        doi = normalise_doi(getattr(item, "doi", None))
        title = normalise_title(getattr(item, "title", "") or "")

        authors: list[AuthorInfo] = []
        raw_authors = getattr(item, "authors", None)
        if raw_authors:
            for part in str(raw_authors).split(";"):
                name = part.strip()
                if name:
                    authors.append(AuthorInfo(name=name))

        year: int | None = None
        date_raw = getattr(item, "coverDisplayDate", None) or getattr(item, "publicationDate", None)
        if date_raw:
            import re

            m = re.search(r"\b(19|20)\d{2}\b", str(date_raw))
            if m:
                year = int(m.group(0))

        return PaperRecord(
            doi=doi,
            title=title,
            abstract=getattr(item, "description", None),
            authors=authors,
            year=year,
            venue=getattr(item, "publicationName", None),
            open_access=bool(getattr(item, "openaccess", False)),
            source_database="science_direct",
            raw_id=getattr(item, "eid", None) or getattr(item, "identifier", None),
        )

    async def search(
        self,
        query: str,
        max_results: int = 100,
        year_from: int | None = None,
        year_to: int | None = None,
        open_access_only: bool = False,
    ) -> list[PaperRecord]:
        """Search ScienceDirect for papers matching *query*.

        Args:
            query: Free-text or boolean search string.
            max_results: Maximum records to return.
            year_from: Earliest publication year filter.
            year_to: Latest publication year filter.
            open_access_only: If True, restrict to open-access articles.

        Returns:
            List of :class:`PaperRecord` objects.

        """

        def _run() -> list[PaperRecord]:
            from pybliometrics.sciencedirect import ScienceDirectSearch  # noqa: PLC0415

            _configure_pybliometrics(self._api_key, self._inst_token)
            search_query = query
            if open_access_only:
                search_query += " AND OPENACCESS(1)"
            if year_from:
                search_query += f" AND PUBYEAR > {year_from - 1}"
            if year_to:
                search_query += f" AND PUBYEAR < {year_to + 1}"

            sc = ScienceDirectSearch(search_query, count=min(max_results, 100))
            results = sc.results or []
            return [self._normalise_record(r) for r in results[:max_results]]

        return await asyncio.to_thread(_run)

    async def get_paper(self, doi: str) -> PaperRecord | None:
        """Retrieve a single ScienceDirect paper by DOI.

        Args:
            doi: Paper DOI without the ``https://doi.org/`` prefix.

        Returns:
            A :class:`PaperRecord` if found, or ``None``.

        """

        def _run() -> PaperRecord | None:
            try:
                from pybliometrics.sciencedirect import ArticleRetrieval  # noqa: PLC0415
            except ImportError:
                return None

            _configure_pybliometrics(self._api_key, self._inst_token)
            try:
                article = ArticleRetrieval(f"DOI:{doi}")
            except Exception:  # noqa: BLE001
                return None

            authors: list[AuthorInfo] = []
            for a in article.authors or []:
                name = getattr(a, "indexed_name", None) or getattr(a, "given_name", None)
                if name:
                    authors.append(AuthorInfo(name=str(name)))

            year: int | None = None
            if article.coverDate:
                import re

                m = re.search(r"\b(19|20)\d{2}\b", str(article.coverDate))
                if m:
                    year = int(m.group(0))

            return PaperRecord(
                doi=normalise_doi(doi),
                title=normalise_title(article.title or ""),
                abstract=article.abstract,
                authors=authors,
                year=year,
                venue=getattr(article, "publicationName", None),
                source_database="science_direct",
            )

        return await asyncio.to_thread(_run)
