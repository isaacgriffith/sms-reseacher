"""Unit tests for ExpertAgent.

Mocks LLMClient to verify Pydantic output shape and non-empty suggestions.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.services.expert import ExpertAgent, ExpertPaper


def _make_mock_client(response_json: str) -> MagicMock:
    """Return a mock LLMClient whose complete() returns *response_json*."""
    client = MagicMock()
    client.complete = AsyncMock(return_value=response_json)
    return client


_VALID_RESPONSE = json.dumps([
    {
        "title": "Empirical Study of TDD",
        "authors": ["Carol White", "Dave Brown"],
        "year": 2021,
        "venue": "ICSE",
        "doi": "10.1145/tdd.2021",
        "rationale": "Seminal empirical study on TDD outcomes.",
    },
    {
        "title": "Test-Driven Development in Practice",
        "authors": ["Eve Black"],
        "year": 2020,
        "venue": "TSE",
        "doi": None,
        "rationale": "Practitioner perspective on TDD.",
    },
])


class TestExpertAgentOutputShape:
    """Verify ExpertAgent produces valid ExpertPaper list from mocked LLM output."""

    @pytest.mark.asyncio
    async def test_returns_list(self) -> None:
        """run() returns a list."""
        agent = ExpertAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_non_empty_suggestions(self) -> None:
        """result is a non-empty list of ExpertPaper objects."""
        agent = ExpertAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        assert len(result) > 0
        assert all(isinstance(p, ExpertPaper) for p in result)

    @pytest.mark.asyncio
    async def test_paper_fields_populated(self) -> None:
        """Each ExpertPaper has title, authors list, and non-empty rationale."""
        agent = ExpertAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        paper = result[0]
        assert paper.title == "Empirical Study of TDD"
        assert isinstance(paper.authors, list)
        assert len(paper.authors) > 0
        assert paper.rationale

    @pytest.mark.asyncio
    async def test_optional_doi_allowed(self) -> None:
        """ExpertPaper.doi may be None without validation error."""
        agent = ExpertAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        assert result[1].doi is None

    @pytest.mark.asyncio
    async def test_strips_markdown_code_fences(self) -> None:
        """run() strips ```json ... ``` fences before parsing."""
        fenced = f"```json\n{_VALID_RESPONSE}\n```"
        agent = ExpertAgent(llm_client=_make_mock_client(fenced))
        result = await agent.run(topic="TDD", variant="PICO")
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_optional_pico_fields_accepted(self) -> None:
        """Keyword arguments are forwarded without raising."""
        agent = ExpertAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(
            topic="TDD",
            variant="PICO",
            population="software engineers",
            intervention="TDD",
            comparison="no TDD",
            outcome="code quality",
            objectives=["Obj1"],
            questions=["Q1"],
        )
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_max_tokens_passed_to_client(self) -> None:
        """complete() is called with max_tokens=4096."""
        client = _make_mock_client(_VALID_RESPONSE)
        agent = ExpertAgent(llm_client=client)
        await agent.run(topic="TDD", variant="PICO")
        call_kwargs = client.complete.call_args.kwargs
        assert call_kwargs.get("max_tokens") == 4096
