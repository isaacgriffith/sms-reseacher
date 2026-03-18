"""Unit tests for researcher_mcp.core.dedup.

Covers:
- DOI-keyed deduplication (case-insensitive, first occurrence wins).
- Title + first-author fallback for records without a DOI.
- Records with empty/unparseable titles are included unconditionally.
- Mixed input (some with DOI, some without) handled correctly.
"""

from __future__ import annotations

import pytest

from researcher_mcp.core.dedup import deduplicate_paper_records
from researcher_mcp.sources.base import AuthorInfo, PaperRecord


def _paper(
    title: str,
    doi: str | None = None,
    authors: list[str] | None = None,
    source: str = "test",
) -> PaperRecord:
    """Build a minimal PaperRecord for testing.

    Args:
        title: Paper title.
        doi: Optional DOI string.
        authors: Optional list of author name strings.
        source: Source database identifier.

    Returns:
        A :class:`PaperRecord` instance.
    """
    return PaperRecord(
        title=title,
        doi=doi,
        authors=[AuthorInfo(name=n) for n in (authors or [])],
        source_database=source,
    )


class TestDedupByDoi:
    """Deduplication using DOI as the primary key."""

    def test_unique_dois_all_kept(self) -> None:
        """Records with different DOIs are all preserved."""
        records = [
            _paper("Paper A", doi="10.1/a"),
            _paper("Paper B", doi="10.1/b"),
            _paper("Paper C", doi="10.1/c"),
        ]
        result = deduplicate_paper_records(records)
        assert len(result) == 3

    def test_duplicate_doi_keeps_first(self) -> None:
        """When two records share a DOI, the first is kept."""
        records = [
            _paper("First", doi="10.1/dup", source="s1"),
            _paper("Second", doi="10.1/dup", source="s2"),
        ]
        result = deduplicate_paper_records(records)
        assert len(result) == 1
        assert result[0].source_database == "s1"

    def test_doi_comparison_is_case_insensitive(self) -> None:
        """DOIs are compared case-insensitively."""
        records = [
            _paper("Paper", doi="10.1/ABC"),
            _paper("Paper", doi="10.1/abc"),
        ]
        result = deduplicate_paper_records(records)
        assert len(result) == 1

    def test_doi_whitespace_stripped(self) -> None:
        """Leading/trailing whitespace in DOIs is stripped."""
        records = [
            _paper("Paper", doi="  10.1/spaced  "),
            _paper("Paper", doi="10.1/spaced"),
        ]
        result = deduplicate_paper_records(records)
        assert len(result) == 1

    def test_multiple_duplicates_each_doi(self) -> None:
        """Three copies of the same DOI yields one record."""
        records = [
            _paper("A", doi="10.1/x"),
            _paper("B", doi="10.1/x"),
            _paper("C", doi="10.1/x"),
        ]
        result = deduplicate_paper_records(records)
        assert len(result) == 1


class TestDedupByTitleAuthor:
    """Deduplication using title+first-author fallback for DOI-less records."""

    def test_same_title_same_author_deduped(self) -> None:
        """Records without DOI but same normalised title + author are deduped."""
        records = [
            _paper("Test-Driven Development: A Survey", authors=["Beck, Kent"]),
            _paper("Test-Driven Development: A Survey", authors=["Beck, Kent"]),
        ]
        result = deduplicate_paper_records(records)
        assert len(result) == 1

    def test_same_title_different_author_not_deduped(self) -> None:
        """Records with the same title but different first authors are kept."""
        records = [
            _paper("Agile Methods", authors=["Alice"]),
            _paper("Agile Methods", authors=["Bob"]),
        ]
        result = deduplicate_paper_records(records)
        assert len(result) == 2

    def test_title_fingerprint_strips_punctuation(self) -> None:
        """Title fingerprint ignores punctuation differences."""
        records = [
            _paper("Test-Driven Development!", authors=["Smith"]),
            _paper("Test Driven Development", authors=["Smith"]),
        ]
        result = deduplicate_paper_records(records)
        assert len(result) == 1

    def test_title_fingerprint_case_insensitive(self) -> None:
        """Title fingerprint comparison is case-insensitive."""
        records = [
            _paper("AGILE METHODS IN PRACTICE", authors=["jones"]),
            _paper("agile methods in practice", authors=["Jones"]),
        ]
        result = deduplicate_paper_records(records)
        assert len(result) == 1

    def test_empty_title_included_unconditionally(self) -> None:
        """Records with empty titles are always included."""
        records = [
            _paper("", authors=["Alice"]),
            _paper("", authors=["Alice"]),
        ]
        result = deduplicate_paper_records(records)
        assert len(result) == 2

    def test_no_authors_empty_fallback_fingerprint(self) -> None:
        """Records with no authors use empty string as author fingerprint."""
        records = [
            _paper("Some Title Without Authors"),
            _paper("Some Title Without Authors"),
        ]
        result = deduplicate_paper_records(records)
        assert len(result) == 1


class TestDedupMixed:
    """Mixed scenarios combining DOI and title/author keying."""

    def test_doi_record_not_deduped_against_no_doi_record(self) -> None:
        """A record with a DOI and one without are never considered duplicates."""
        records = [
            _paper("Same Title", doi="10.1/x", authors=["Smith"]),
            _paper("Same Title", doi=None, authors=["Smith"]),
        ]
        result = deduplicate_paper_records(records)
        assert len(result) == 2

    def test_empty_input_returns_empty(self) -> None:
        """Empty input returns empty output."""
        assert deduplicate_paper_records([]) == []

    def test_ordering_preserved(self) -> None:
        """Non-duplicate records appear in their original order."""
        records = [
            _paper("C Paper", doi="10.1/c"),
            _paper("A Paper", doi="10.1/a"),
            _paper("B Paper", doi="10.1/b"),
        ]
        result = deduplicate_paper_records(records)
        assert [r.doi for r in result] == ["10.1/c", "10.1/a", "10.1/b"]

    def test_duplicate_doi_and_duplicate_title_both_deduped(self) -> None:
        """DOI duplicates and title/author duplicates each yield one record."""
        records = [
            _paper("Paper X", doi="10.1/x"),
            _paper("Paper X", doi="10.1/x"),  # DOI dup → removed
            _paper("Paper Y", authors=["Lee"]),
            _paper("Paper Y", authors=["Lee"]),  # title/author dup → removed
        ]
        result = deduplicate_paper_records(records)
        assert len(result) == 2
