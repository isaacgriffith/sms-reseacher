"""Deduplication logic for merged paper record sets from multiple sources.

Uses DOI as the primary deduplication key.  When two records share a DOI,
the one that arrived earlier in the input list is kept.  For records without
a DOI, a normalised ``(title, first_author_last_name)`` fingerprint is used
as a fallback key.
"""

from __future__ import annotations

import re

from researcher_mcp.sources.base import PaperRecord, first_author_last_name


def _title_fingerprint(title: str) -> str:
    """Produce a lowercase, punctuation-stripped fingerprint for a title.

    Args:
        title: Raw paper title string.

    Returns:
        Lowercased string with all non-alphanumeric characters collapsed to a
        single space and leading/trailing whitespace removed.
    """
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def deduplicate_paper_records(records: list[PaperRecord]) -> list[PaperRecord]:
    """Remove duplicate paper records, preserving the first occurrence of each.

    Deduplication strategy (applied in priority order):

    1. **DOI key**: Two records are duplicates if they share the same non-empty
       DOI string (case-insensitive comparison).
    2. **Title + first-author fallback**: For records without a DOI, two records
       are considered duplicates if their normalised title fingerprint AND
       first-author last name both match (both lowercased).

    Records that cannot be fingerprinted (empty title, no DOI) are included
    unconditionally rather than silently dropped.

    Args:
        records: List of :class:`~researcher_mcp.sources.base.PaperRecord`
            objects from one or more database sources, possibly containing
            duplicates.

    Returns:
        Deduplicated list with the same ordering as the input (first occurrence
        of each unique paper retained).
    """
    seen_dois: set[str] = set()
    seen_fingerprints: set[tuple[str, str]] = set()
    result: list[PaperRecord] = []

    for record in records:
        # Primary key: DOI
        if record.doi:
            doi_key = record.doi.strip().lower()
            if doi_key in seen_dois:
                continue
            seen_dois.add(doi_key)
            result.append(record)
            continue

        # Fallback key: (title_fingerprint, first_author_last_name)
        title_fp = _title_fingerprint(record.title)
        author_fp = first_author_last_name(record.authors)

        if not title_fp:
            # Cannot fingerprint — include unconditionally
            result.append(record)
            continue

        fingerprint = (title_fp, author_fp)
        if fingerprint in seen_fingerprints:
            continue
        seen_fingerprints.add(fingerprint)
        result.append(record)

    return result
