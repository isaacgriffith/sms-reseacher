"""Unit tests for SearchStringBuilderAgent.

Mocks LLMClient to verify Pydantic output shape, non-empty boolean string,
and terms_used presence.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.services.search_builder import (
    SearchStringBuilderAgent,
    SearchStringResult,
    TermGroup,
)


def _make_mock_client(response_json: str) -> MagicMock:
    """Return a mock LLMClient whose complete() returns *response_json*."""
    client = MagicMock()
    client.complete = AsyncMock(return_value=response_json)
    return client


_VALID_RESPONSE = json.dumps({
    "search_string": '(TDD OR "test-driven") AND ("code quality" OR defect)',
    "terms_used": [
        {"component": "intervention", "terms": ["TDD", "test-driven development"]},
        {"component": "outcome", "terms": ["code quality", "defect rate"]},
    ],
    "expansion_notes": "Synonyms expanded via MeSH and IEEE Thesaurus.",
})


class TestSearchStringBuilderAgentOutputShape:
    """Verify SearchStringBuilderAgent produces valid SearchStringResult from mocked LLM."""

    @pytest.mark.asyncio
    async def test_returns_search_string_result_type(self) -> None:
        """run() returns a SearchStringResult instance."""
        agent = SearchStringBuilderAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        assert isinstance(result, SearchStringResult)

    @pytest.mark.asyncio
    async def test_search_string_non_empty(self) -> None:
        """result.search_string is a non-empty string."""
        agent = SearchStringBuilderAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        assert result.search_string
        assert len(result.search_string) > 0

    @pytest.mark.asyncio
    async def test_terms_used_non_empty(self) -> None:
        """result.terms_used is a non-empty list of TermGroup objects."""
        agent = SearchStringBuilderAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        assert len(result.terms_used) > 0
        assert all(isinstance(tg, TermGroup) for tg in result.terms_used)

    @pytest.mark.asyncio
    async def test_terms_used_components_populated(self) -> None:
        """Each TermGroup has a non-empty component name and terms list."""
        agent = SearchStringBuilderAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        for tg in result.terms_used:
            assert tg.component
            assert len(tg.terms) > 0

    @pytest.mark.asyncio
    async def test_expansion_notes_present(self) -> None:
        """result.expansion_notes is a non-empty string."""
        agent = SearchStringBuilderAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        assert result.expansion_notes

    @pytest.mark.asyncio
    async def test_strips_markdown_code_fences(self) -> None:
        """run() strips ```json ... ``` fences before parsing."""
        fenced = f"```json\n{_VALID_RESPONSE}\n```"
        agent = SearchStringBuilderAgent(llm_client=_make_mock_client(fenced))
        result = await agent.run(topic="TDD", variant="PICO")
        assert len(result.terms_used) == 2

    @pytest.mark.asyncio
    async def test_optional_pico_fields_forwarded(self) -> None:
        """All optional PICO fields are accepted without raising."""
        agent = SearchStringBuilderAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(
            topic="TDD",
            variant="PICO",
            population="software engineers",
            intervention="TDD",
            comparison="waterfall",
            outcome="code quality",
            context="industry projects",
            objectives=["Identify empirical TDD studies"],
            questions=["Does TDD reduce defects?"],
            seed_keywords=["test-driven", "unit testing"],
            inclusion_criteria=["must be empirical"],
            exclusion_criteria=["grey literature excluded"],
        )
        assert isinstance(result, SearchStringResult)

    @pytest.mark.asyncio
    async def test_search_string_contains_boolean_operators(self) -> None:
        """The generated search string contains at least one boolean operator."""
        agent = SearchStringBuilderAgent(llm_client=_make_mock_client(_VALID_RESPONSE))
        result = await agent.run(topic="TDD", variant="PICO")
        upper = result.search_string.upper()
        assert any(op in upper for op in ("AND", "OR", "NOT"))
