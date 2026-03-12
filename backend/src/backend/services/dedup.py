"""Paper deduplication service for systematic mapping studies.

Two-stage deduplication:
1. Exact DOI match against existing CandidatePapers for the study.
2. Fuzzy title similarity (≥0.90) + author name overlap → probable duplicate.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class DedupResult:
    """Result of a deduplication check for one paper.

    Attributes:
        is_duplicate: True if this paper is a definite or probable duplicate.
        is_definite: True for exact DOI matches; False for fuzzy matches.
        candidate_id: The existing CandidatePaper.id it duplicates, or None.
    """

    is_duplicate: bool
    is_definite: bool
    candidate_id: int | None = None


async def check_duplicate(
    *,
    study_id: int,
    doi: str | None,
    title: str,
    authors: list[dict] | None = None,
    db: AsyncSession,
) -> DedupResult:
    """Check whether a paper is a duplicate of an existing candidate in the study.

    Performs two-stage deduplication:
    - Stage 1: Exact DOI match (case-insensitive, stripped).
    - Stage 2: Fuzzy title similarity ≥ 0.90 on WRatio + author name overlap.

    Args:
        study_id: The study to check against.
        doi: DOI of the candidate paper (may be None).
        title: Title of the candidate paper.
        authors: Optional list of author dicts with ``name`` key.
        db: Async SQLAlchemy session.

    Returns:
        :class:`DedupResult` indicating whether a duplicate was found.
    """
    from db.models.candidate import CandidatePaper
    from db.models import Paper

    # Stage 1: Exact DOI match
    if doi:
        norm_doi = doi.lower().strip()
        result = await db.execute(
            select(CandidatePaper, Paper)
            .join(Paper, CandidatePaper.paper_id == Paper.id)
            .where(
                CandidatePaper.study_id == study_id,
                Paper.doi.isnot(None),
            )
        )
        for cp, paper in result.all():
            if paper.doi and paper.doi.lower().strip() == norm_doi:
                return DedupResult(is_duplicate=True, is_definite=True, candidate_id=cp.id)

    # Stage 2: Fuzzy title + author overlap
    title_norm = title.strip().lower()
    result = await db.execute(
        select(CandidatePaper, Paper)
        .join(Paper, CandidatePaper.paper_id == Paper.id)
        .where(CandidatePaper.study_id == study_id)
    )
    candidate_author_names = {
        a.get("name", "").lower().strip()
        for a in (authors or [])
        if a.get("name")
    }

    for cp, paper in result.all():
        # Title similarity
        similarity = fuzz.WRatio(title_norm, paper.title.strip().lower()) / 100.0
        if similarity < 0.90:
            continue

        # Author overlap check (if we have author data on both sides)
        if candidate_author_names and paper.authors:
            paper_author_names = {
                a.get("name", "").lower().strip()
                for a in paper.authors
                if a.get("name")
            }
            # Require at least one overlapping author name
            if not candidate_author_names.intersection(paper_author_names):
                # No author overlap despite high title similarity — not a duplicate
                continue

        return DedupResult(is_duplicate=True, is_definite=False, candidate_id=cp.id)

    return DedupResult(is_duplicate=False, is_definite=False, candidate_id=None)
