"""Base protocol and shared data types for academic database source adapters.

Defines:
- :class:`AuthorInfo` — normalised author record shared across all sources.
- :class:`PaperRecord` — normalised paper record returned by all source adapters.
- :class:`DatabaseSource` — structural protocol every source adapter must satisfy.
- Helper functions for normalising raw API data to :class:`PaperRecord`.
"""

from __future__ import annotations

import re
from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class AuthorInfo(BaseModel):
    """A single author on a paper.

    Attributes:
        name: Full display name of the author.
        institution: Affiliated institution, if available.
        orcid: ORCID identifier, if available.

    """

    name: str
    institution: str | None = None
    orcid: str | None = None


VenueType = Literal["journal", "conference", "book", "preprint", "report", "other"]


class PaperRecord(BaseModel):
    """Normalised paper record returned by all database source adapters.

    Every field except ``title`` and ``source_database`` is optional to
    accommodate sources that provide only partial metadata.

    Attributes:
        doi: DOI string without the ``https://doi.org/`` prefix, or None.
        title: Paper title (always present).
        abstract: Abstract text, or None if unavailable.
        authors: List of :class:`AuthorInfo` records.
        year: Publication year as an integer, or None.
        venue: Journal/conference/book name, or None.
        venue_type: Controlled vocabulary venue category, or None.
        url: Canonical URL for the paper's landing page, or None.
        open_access: True if the paper is known to be openly accessible.
        source_database: Identifier of the database that produced this record
            (e.g. ``"semantic_scholar"``, ``"scopus"``).
        raw_id: Source-native identifier (e.g. Semantic Scholar paper ID), or None.

    """

    doi: str | None = None
    title: str
    abstract: str | None = None
    authors: list[AuthorInfo] = Field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    venue_type: VenueType | None = None
    url: str | None = None
    open_access: bool = False
    source_database: str
    raw_id: str | None = None


class AuthorProfile(BaseModel):
    """Normalised author profile returned by the author search tools.

    Attributes:
        author_id: Source-native identifier for the author.
        name: Full display name.
        affiliations: List of institutional affiliations.
        paper_count: Total number of papers indexed by the source.
        citation_count: Total citations received.
        h_index: Author h-index.
        profile_url: URL to the author's profile page.
        fields_of_study: Broad research areas from source metadata.

    """

    author_id: str
    name: str
    affiliations: list[str] = Field(default_factory=list)
    paper_count: int = 0
    citation_count: int = 0
    h_index: int = 0
    profile_url: str = ""
    fields_of_study: list[str] = Field(default_factory=list)


class AuthorDetail(AuthorProfile):
    """Full author profile including paper list.

    Attributes:
        papers: List of :class:`PaperRecord` objects for the author's publications.

    """

    papers: list[PaperRecord] = Field(default_factory=list)


@runtime_checkable
class DatabaseSource(Protocol):
    """Structural protocol for academic database source adapters.

    All source classes must implement ``search`` to satisfy this protocol.
    The ``get_paper`` method is optional — sources that expose per-DOI
    retrieval should implement it; those that do not may raise
    ``NotImplementedError``.
    """

    async def search(
        self,
        query: str,
        max_results: int = 100,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> list[PaperRecord]:
        """Execute a keyword search and return normalised results.

        Args:
            query: Keyword or boolean search string.
            max_results: Maximum number of records to return.
            year_from: Earliest publication year to include (inclusive).
            year_to: Latest publication year to include (inclusive).

        Returns:
            List of :class:`PaperRecord` objects, possibly empty.

        """
        ...

    async def get_paper(self, doi: str) -> PaperRecord | None:
        """Retrieve a single paper by DOI.

        Args:
            doi: DOI string without the ``https://doi.org/`` prefix.

        Returns:
            A :class:`PaperRecord` if found, or None.

        """
        ...


# ── Normalisation helpers ─────────────────────────────────────────────────────


def normalise_doi(raw: str | None) -> str | None:
    """Strip common DOI URL prefixes and whitespace, returning a bare DOI.

    Args:
        raw: Raw DOI string that may include ``https://doi.org/`` or similar.

    Returns:
        Bare DOI string (e.g. ``10.1145/3377811.3380376``), or None if input
        is None or empty.

    """
    if not raw:
        return None
    cleaned = raw.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:", "DOI:"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]
    return cleaned or None


def normalise_title(raw: str | None) -> str:
    """Strip excess whitespace and HTML entities from a title string.

    Args:
        raw: Raw title text, possibly containing embedded HTML or extra spaces.

    Returns:
        Cleaned title string, or an empty string if input is None.

    """
    if not raw:
        return ""
    # Collapse runs of whitespace (including newlines from multi-line records)
    return re.sub(r"\s+", " ", raw).strip()


def first_author_last_name(authors: list[AuthorInfo]) -> str:
    """Extract the last name of the first author for deduplication.

    Args:
        authors: List of :class:`AuthorInfo` records from a paper.

    Returns:
        Lowercased last name token of the first author, or an empty string
        if the list is empty or the name cannot be parsed.

    """
    if not authors:
        return ""
    parts = authors[0].name.strip().split()
    return parts[-1].lower() if parts else ""


def parse_author_list(raw_authors: list[Any]) -> list[AuthorInfo]:
    """Convert a heterogeneous list of author representations to AuthorInfo objects.

    Accepts dicts with ``name``, ``authorName``, or ``author_name`` keys, or
    plain strings.

    Args:
        raw_authors: List of raw author records from a source API response.

    Returns:
        List of :class:`AuthorInfo` instances.

    """
    result: list[AuthorInfo] = []
    for item in raw_authors:
        if isinstance(item, dict):
            name = item.get("name") or item.get("authorName") or item.get("author_name") or ""
            institution = item.get("institution") or item.get("affiliation")
            orcid = item.get("orcid")
            if name:
                result.append(AuthorInfo(name=str(name), institution=institution, orcid=orcid))
        elif isinstance(item, str) and item.strip():
            result.append(AuthorInfo(name=item.strip()))
    return result
