"""Integration tests for GET /api/v1/papers/{paper_id}/markdown (T037 + T046).

Covers:
- GET /papers/{paper_id}/markdown returns 200 with available=False for a paper with no markdown.
- GET /papers/{paper_id}/markdown returns 200 with available=True after markdown is stored.
- GET /papers/{paper_id}/markdown returns 404 for unknown paper_id.
- GET /papers/{paper_id}/markdown returns 401 for unauthenticated request.
- store_paper_markdown stores markdown, source, and converted_at on the Paper row.
- get_paper_markdown returns None when no markdown is stored.
- get_paper_markdown returns stored markdown and metadata when available.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.auth import create_access_token
from db.models import Paper
from db.models.search_integrations import FullTextSource
from db.models.users import GroupMembership, GroupRole, ResearchGroup


def _bearer(user_id: int) -> dict[str, str]:
    """Return Authorization headers for *user_id*."""
    return {"Authorization": f"Bearer {create_access_token(user_id=user_id)}"}


async def _setup_study_and_paper(client, db_engine, user) -> tuple[int, int]:
    """Create group, membership, study, and a Paper row.

    Returns:
        Tuple of (study_id, paper_id).
    """
    maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with maker() as session:
        group = ResearchGroup(name="Markdown Test Lab")
        session.add(group)
        await session.flush()
        session.add(
            GroupMembership(group_id=group.id, user_id=user.id, role=GroupRole.ADMIN)
        )
        await session.commit()
        group_id = group.id

    resp = await client.post(
        f"/api/v1/groups/{group_id}/studies",
        json={
            "name": "Markdown Test Study",
            "topic": "Paper conversion",
            "study_type": "SMS",
            "research_objectives": ["Obj 1"],
            "research_questions": ["RQ1"],
        },
        headers=_bearer(user.id),
    )
    assert resp.status_code == 201
    study_id = resp.json()["id"]

    # Insert paper directly into the DB
    async with maker() as session:
        paper = Paper(
            title="Test Paper",
            doi="10.1234/test",
            abstract="An abstract",
            authors=[{"name": "Author One"}],
            year=2023,
        )
        session.add(paper)
        await session.commit()
        await session.refresh(paper)
        paper_id = paper.id

    return study_id, paper_id


class TestGetPaperMarkdownEndpoint:
    """GET /api/v1/papers/{paper_id}/markdown endpoint tests."""

    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client) -> None:
        """No auth token returns 401."""
        resp = await client.get("/api/v1/papers/1/markdown")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_unknown_paper_returns_404(self, client, alice) -> None:
        """Unknown paper_id returns 404."""
        user, _ = alice
        resp = await client.get("/api/v1/papers/999999/markdown", headers=_bearer(user.id))
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_paper_without_markdown_returns_available_false(
        self, client, alice, db_engine
    ) -> None:
        """Paper with no full text returns available=False."""
        user, _ = alice
        _, paper_id = await _setup_study_and_paper(client, db_engine, user)

        resp = await client.get(f"/api/v1/papers/{paper_id}/markdown", headers=_bearer(user.id))
        assert resp.status_code == 200
        body = resp.json()
        assert body["paper_id"] == paper_id
        assert body["available"] is False
        assert body["markdown"] is None

    @pytest.mark.asyncio
    async def test_paper_with_markdown_returns_available_true(
        self, client, alice, db_engine
    ) -> None:
        """Paper with stored markdown returns available=True and the markdown text."""
        user, _ = alice
        _, paper_id = await _setup_study_and_paper(client, db_engine, user)

        # Store markdown directly in DB
        maker = async_sessionmaker(db_engine, expire_on_commit=False)
        async with maker() as session:
            from sqlalchemy import select

            result = await session.execute(select(Paper).where(Paper.id == paper_id))
            paper = result.scalar_one()
            paper.full_text_markdown = "# Title\n\nContent."
            paper.full_text_source = FullTextSource.UNPAYWALL
            paper.full_text_converted_at = datetime.now(UTC)
            await session.commit()

        resp = await client.get(f"/api/v1/papers/{paper_id}/markdown", headers=_bearer(user.id))
        assert resp.status_code == 200
        body = resp.json()
        assert body["available"] is True
        assert body["markdown"] == "# Title\n\nContent."
        assert body["full_text_source"] == "unpaywall"
        assert body["converted_at"] is not None


class TestStorePaperMarkdown:
    """Tests for store_paper_markdown and get_paper_markdown service methods."""

    @pytest.mark.asyncio
    async def test_get_paper_markdown_returns_none_when_not_stored(self, db_engine) -> None:
        """get_paper_markdown returns None markdown when paper has none."""
        from sqlalchemy import select
        from backend.services.paper_markdown import get_paper_markdown

        maker = async_sessionmaker(db_engine, expire_on_commit=False)

        async with maker() as session:
            paper = Paper(title="No Markdown Paper", doi="10.1/nm", year=2022)
            session.add(paper)
            await session.commit()
            await session.refresh(paper)
            paper_id = paper.id

        async with maker() as session:
            result = await get_paper_markdown(session, paper_id)

        assert result is not None
        assert result["available"] is False
        assert result["markdown"] is None

    @pytest.mark.asyncio
    async def test_store_paper_markdown_persists_markdown(self, db_engine) -> None:
        """store_paper_markdown writes full_text_markdown and source to the Paper row."""
        from sqlalchemy import select
        from backend.services.paper_markdown import store_paper_markdown, get_paper_markdown

        maker = async_sessionmaker(db_engine, expire_on_commit=False)

        async with maker() as session:
            paper = Paper(title="Conversion Paper", doi="10.1/conv", year=2023)
            session.add(paper)
            await session.commit()
            await session.refresh(paper)
            paper_id = paper.id

        async with maker() as session:
            await store_paper_markdown(
                session,
                paper_id,
                markdown="## Section\n\nBody text.",
                source=FullTextSource.DIRECT,
            )

        async with maker() as session:
            result = await get_paper_markdown(session, paper_id)

        assert result["available"] is True
        assert result["markdown"] == "## Section\n\nBody text."
        assert result["full_text_source"] == FullTextSource.DIRECT
        assert result["converted_at"] is not None
