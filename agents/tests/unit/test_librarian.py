"""Unit tests for LibrarianAgent.

Mocks LLMClient to verify Pydantic output shape and non-empty suggestions.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.services.librarian import LibrarianAgent, LibrarianResult, SuggestedAuthor, SuggestedPaper


def _make_mock_client(response_json: str) -> MagicMock:
    """Return a mock LLMClient whose complete() returns *response_json*."""
    client = MagicMock()
    client.complete = AsyncMock(return_value=response_json)
    return client


_VALID_RESPONSE = json.dumps({
    "papers": [
        {
            "title": "A Survey of TDD Practices",
            "authors": ["Alice Smith", "Bob Jones"],
            "year": 2022,
            "venue": "JSS",
            "doi": "10.1234/jss.2022.001",
            "rationale": "Directly relevant to TDD research.",
        }
    ],
    "authors": [
        {
            "author_name": "Alice Smith",
            "institution": "MIT",
            "profile_url": "https://dblp.org/alice",
            "rationale": "Prolific TDD researcher.",
        }
    ],
})


class TestLibrarianAgentOutputShape:
    """Verify LibrarianAgent produces valid LibrarianResult from mocked LLM output."""

    @pytest.mark.asyncio
    async def test_returns_librarian_result_type(self) -> None:
        """run() returns a LibrarianResult instance."""
        agent = LibrarianAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        assert isinstance(result, LibrarianResult)

    @pytest.mark.asyncio
    async def test_papers_non_empty(self) -> None:
        """result.papers is a non-empty list of SuggestedPaper objects."""
        agent = LibrarianAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        assert len(result.papers) > 0
        assert all(isinstance(p, SuggestedPaper) for p in result.papers)

    @pytest.mark.asyncio
    async def test_authors_non_empty(self) -> None:
        """result.authors is a non-empty list of SuggestedAuthor objects."""
        agent = LibrarianAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        assert len(result.authors) > 0
        assert all(isinstance(a, SuggestedAuthor) for a in result.authors)

    @pytest.mark.asyncio
    async def test_paper_fields_populated(self) -> None:
        """Each SuggestedPaper has title, authors list, and non-empty rationale."""
        agent = LibrarianAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        paper = result.papers[0]
        assert paper.title == "A Survey of TDD Practices"
        assert isinstance(paper.authors, list)
        assert paper.rationale

    @pytest.mark.asyncio
    async def test_strips_markdown_code_fences(self) -> None:
        """run() strips ```json ... ``` fences before parsing."""
        fenced = f"```json\n{_VALID_RESPONSE}\n```"
        agent = LibrarianAgent(llm_client=_make_mock_client(fenced))
        result = await agent.run(topic="TDD", variant="PICO")
        assert len(result.papers) == 1

    @pytest.mark.asyncio
    async def test_optional_pico_fields_forwarded(self) -> None:
        """Keyword arguments are accepted without raising."""
        agent = LibrarianAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(
            topic="TDD",
            variant="PICO",
            population="software engineers",
            intervention="TDD",
            comparison="no TDD",
            outcome="code quality",
            objectives=["Obj1"],
            questions=["Q1"],
            existing_seeds=["Paper A"],
        )
        assert isinstance(result, LibrarianResult)
