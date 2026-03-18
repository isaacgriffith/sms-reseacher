"""GET /papers/{paper_id}/markdown endpoint (T041).

Returns stored full-text Markdown for a paper.  Used by AI agents and the
frontend paper detail view.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.auth import CurrentUser, get_current_user
from backend.core.database import get_db
from backend.services.paper_markdown import get_paper_markdown

router = APIRouter(tags=["papers"])


class PaperMarkdownResponse(BaseModel):
    """Response body for GET /papers/{paper_id}/markdown."""

    paper_id: int
    doi: str | None
    markdown: str | None
    available: bool
    full_text_source: str | None
    converted_at: str | None


@router.get(
    "/papers/{paper_id}/markdown",
    response_model=PaperMarkdownResponse,
    summary="Get stored full-text Markdown for a paper",
)
async def get_paper_markdown_endpoint(
    paper_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaperMarkdownResponse:
    """Return stored full-text Markdown for *paper_id*.

    Does not trigger conversion — returns what is already stored.  If no
    Markdown has been converted yet, ``available`` will be ``False`` and
    ``markdown`` will be ``None``.

    Args:
        paper_id: Integer primary key of the paper.
        current_user: Injected authenticated user from JWT.
        db: Injected async database session.

    Returns:
        :class:`PaperMarkdownResponse` with stored Markdown metadata.

    Raises:
        HTTPException: 404 if no paper with *paper_id* exists.

    """
    try:
        data = await get_paper_markdown(db, paper_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper {paper_id} not found",
        ) from exc

    return PaperMarkdownResponse(
        paper_id=data["paper_id"],
        doi=data["doi"],
        markdown=data["markdown"],
        available=data["available"],
        full_text_source=(
            data["full_text_source"].value
            if hasattr(data["full_text_source"], "value")
            else data["full_text_source"]
        )
        if data["full_text_source"]
        else None,
        converted_at=data["converted_at"],
    )
