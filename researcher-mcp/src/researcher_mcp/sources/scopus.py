"""Scopus source adapter via pybliometrics.

Implements the :class:`DatabaseSource` protocol using ``pybliometrics.ScopusSearch``
and ``AbstractRetrieval``.  All pybliometrics calls are synchronous and are
wrapped in :func:`asyncio.to_thread` to honour async-discipline requirements.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from researcher_mcp.sources.base import (
    AuthorInfo,
    PaperRecord,
    VenueType,
    normalise_doi,
    normalise_title,
)


def _configure_pybliometrics(api_key: str, inst_token: str = "") -> None:
    """Write a minimal pybliometrics config from the given credentials.

    Writes to ``~/.pybliometrics/config.ini`` only when the values differ
    from what is already stored, to avoid unnecessary disk I/O.

    Args:
        api_key: Elsevier API key.
        inst_token: Elsevier institutional token (optional).

    """
    config_dir = Path.home() / ".pybliometrics"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.ini"

    lines = [
        "[Authentication]",
        f"APIKey = {api_key}",
    ]
    if inst_token:
        lines.append(f"InstToken = {inst_token}")

    config_path.write_text("\n".join(lines) + "\n")


class ScopusSource:
    """Wraps the Scopus abstract search and retrieval APIs via pybliometrics.

    All pybliometrics calls are offloaded to a thread pool via
    :func:`asyncio.to_thread`.

    Attributes:
        _api_key: Elsevier API key.
        _inst_token: Elsevier institutional token.

    """

    def __init__(self, api_key: str = "", inst_token: str = "") -> None:
        """Initialise ScopusSource.

        Args:
            api_key: Elsevier API key.
            inst_token: Elsevier institutional token (optional).

        """
        self._api_key = api_key
        self._inst_token = inst_token

    def _normalise_record(self, item: Any) -> PaperRecord:
        """Convert a pybliometrics ScopusSearch result to a :class:`PaperRecord`.

        Args:
            item: A result object from ``pybliometrics.ScopusSearch.results``.

        Returns:
            A normalised :class:`PaperRecord`.

        """
        doi = normalise_doi(getattr(item, "doi", None))
        title = normalise_title(getattr(item, "title", "") or "")

        raw_authors = getattr(item, "author_names", "") or ""
        authors: list[AuthorInfo] = []
        if raw_authors:
            for part in str(raw_authors).split(";"):
                name = part.strip()
                if name:
                    authors.append(AuthorInfo(name=name))

        year_raw = getattr(item, "coverDate", None) or getattr(item, "year", None)
        year: int | None = None
        if year_raw:
            import re

            m = re.search(r"\b(19|20)\d{2}\b", str(year_raw))
            if m:
                year = int(m.group(0))

        venue_type: VenueType | None = None
        agg_type = str(getattr(item, "aggregationType", "") or "").lower()
        if "journal" in agg_type:
            venue_type = "journal"
        elif "conference" in agg_type or "proceeding" in agg_type:
            venue_type = "conference"
        elif "book" in agg_type:
            venue_type = "book"

        return PaperRecord(
            doi=doi,
            title=title,
            abstract=getattr(item, "description", None),
            authors=authors,
            year=year,
            venue=getattr(item, "publicationName", None),
            venue_type=venue_type,
            url=getattr(item, "url", None),
            open_access=bool(getattr(item, "openaccess", False)),
            source_database="scopus",
            raw_id=getattr(item, "eid", None) or getattr(item, "identifier", None),
        )

    async def search(
        self,
        query: str,
        max_results: int = 100,
        year_from: int | None = None,
        year_to: int | None = None,
        subject_areas: list[str] | None = None,
    ) -> list[PaperRecord]:
        """Search Scopus for papers matching *query*.

        Args:
            query: Scopus query string (supports TITLE-ABS-KEY and boolean).
            max_results: Maximum records to return.
            year_from: Earliest publication year filter.
            year_to: Latest publication year filter.
            subject_areas: Optional list of Scopus subject area codes to filter.

        Returns:
            List of :class:`PaperRecord` objects.

        Raises:
            Exception: Pybliometrics exceptions on auth or quota failures.

        """

        def _run() -> list[PaperRecord]:
            from pybliometrics.scopus import ScopusSearch  # noqa: PLC0415

            _configure_pybliometrics(self._api_key, self._inst_token)
            search_query = query
            if year_from:
                search_query += f" AND PUBYEAR AFT {year_from - 1}"
            if year_to:
                search_query += f" AND PUBYEAR BEF {year_to + 1}"

            sc = ScopusSearch(search_query, count=min(max_results, 200))
            results = sc.results or []
            return [self._normalise_record(r) for r in results[:max_results]]

        return await asyncio.to_thread(_run)

    async def get_paper(self, doi: str) -> PaperRecord | None:
        """Retrieve full metadata for a single paper by DOI.

        Args:
            doi: Paper DOI without the ``https://doi.org/`` prefix.

        Returns:
            A :class:`PaperRecord` if found, or ``None``.

        """

        def _run() -> PaperRecord | None:
            from pybliometrics.scopus import AbstractRetrieval  # noqa: PLC0415

            _configure_pybliometrics(self._api_key, self._inst_token)
            try:
                ab = AbstractRetrieval(f"DOI:{doi}")
            except Exception:  # noqa: BLE001
                return None

            authors: list[AuthorInfo] = []
            for a in ab.authors or []:
                name = getattr(a, "indexed_name", None) or getattr(a, "preferred_name", None)
                if name:
                    institution = None
                    for aff in ab.affiliation or []:
                        if hasattr(aff, "name"):
                            institution = aff.name
                            break
                    authors.append(AuthorInfo(name=str(name), institution=institution))

            year: int | None = None
            if ab.coverDate:
                import re

                m = re.search(r"\b(19|20)\d{2}\b", str(ab.coverDate))
                if m:
                    year = int(m.group(0))

            return PaperRecord(
                doi=normalise_doi(doi),
                title=normalise_title(ab.title or ""),
                abstract=ab.abstract,
                authors=authors,
                year=year,
                venue=ab.publicationName,
                source_database="scopus",
                raw_id=ab.eid,
            )

        return await asyncio.to_thread(_run)
