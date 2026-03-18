"""Service functions for storing and retrieving paper full-text Markdown (T049).

Provides ``store_paper_markdown`` and ``get_paper_markdown`` to update and
query the ``full_text_markdown``, ``full_text_source``, and
``full_text_converted_at`` columns on the ``Paper`` model.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from db.models import Paper
from db.models.search_integrations import FullTextSource
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def store_paper_markdown(
    db: AsyncSession,
    paper_id: int,
    markdown: str,
    source: FullTextSource,
) -> None:
    """Persist full-text Markdown for a paper.

    Updates ``full_text_markdown``, ``full_text_source``, and
    ``full_text_converted_at`` on the given paper row and commits.

    Args:
        db: Active async database session.
        paper_id: Primary key of the :class:`Paper` row to update.
        markdown: Converted Markdown text to store.
        source: The :class:`FullTextSource` provenance enum value.

    Raises:
        ValueError: If no paper with *paper_id* exists.

    """
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if paper is None:
        raise ValueError(f"Paper {paper_id} not found")

    paper.full_text_markdown = markdown
    paper.full_text_source = source
    paper.full_text_converted_at = datetime.now(UTC)
    await db.commit()


async def get_paper_markdown(
    db: AsyncSession,
    paper_id: int,
) -> dict[str, Any]:
    """Return stored full-text Markdown metadata for a paper.

    Args:
        db: Active async database session.
        paper_id: Primary key of the :class:`Paper` row to query.

    Returns:
        Dict with ``paper_id``, ``doi``, ``markdown``, ``available``,
        ``full_text_source``, and ``converted_at`` keys.  ``available`` is
        ``True`` only when ``full_text_markdown`` is non-empty.

    Raises:
        ValueError: If no paper with *paper_id* exists.

    """
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if paper is None:
        raise ValueError(f"Paper {paper_id} not found")

    has_markdown = bool(paper.full_text_markdown)
    return {
        "paper_id": paper.id,
        "doi": paper.doi,
        "markdown": paper.full_text_markdown if has_markdown else None,
        "available": has_markdown,
        "full_text_source": paper.full_text_source,
        "converted_at": (
            paper.full_text_converted_at.isoformat() if paper.full_text_converted_at else None
        ),
    }
