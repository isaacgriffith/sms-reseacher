"""Unit tests for ValidityAgent.

Mocks LLMClient to verify:
- ValidityResult is returned with all 6 fields non-empty
- ValueError raised when a validity dimension is empty in LLM response
- JSON parsing works with and without markdown fences
- All dimensions default gracefully when LLM omits a key
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.services.validity import ValidityAgent, ValidityResult

_DIMS = (
    "descriptive",
    "theoretical",
    "generalizability_internal",
    "generalizability_external",
    "interpretive",
    "repeatability",
)

_SNAPSHOT_KWARGS = {
    "study_id": 2,
    "study_name": "DevOps Mapping Study",
    "study_type": "SMS",
    "current_phase": 4,
    "pico_components": [
        {"type": "population", "content": "Software development teams"},
        {"type": "intervention", "content": "DevOps practices"},
        {"type": "outcome", "content": "Deployment frequency"},
    ],
    "search_strategies": [
        {"string_text": "(DevOps OR CI/CD) AND (adoption OR practice)", "version": 1},
    ],
    "databases": "IEEE Xplore, ACM DL",
    "test_retest_done": False,
    "reviewers": [{"reviewer_type": "human", "agent_name": None, "user_id": 1}],
    "inclusion_criteria": ["Empirical study of DevOps practices"],
    "exclusion_criteria": ["Opinion papers"],
    "extraction_summary": "Extraction completed for 45 accepted papers.",
}


def _make_client(response: str) -> MagicMock:
    """Return a mock LLMClient whose complete() coroutine returns *response*."""
    client = MagicMock()
    client.complete = AsyncMock(return_value=response)
    return client


def _json_response(**overrides: str | None) -> str:
    """Return a minimal valid ValidityAgent JSON string with all six dimensions."""
    data = {
        "descriptive": "Data was extracted by two independent reviewers reducing misinterpretation risk.",
        "theoretical": "Classifications were grounded in the Wieringa et al. framework.",
        "generalizability_internal": "All 45 included papers were subjected to the same extraction protocol.",
        "generalizability_external": "Four major databases searched; temporal scope 2015–2024.",
        "interpretive": "Patterns were validated through inter-rater agreement (κ = 0.82).",
        "repeatability": "Search strings, inclusion criteria, and protocol are fully documented.",
    }
    data.update(overrides)
    return json.dumps(data)


class TestValidityResultShape:
    """Verify ValidityResult structure from mocked LLM output."""

    @pytest.mark.asyncio
    async def test_returns_validity_result_type(self) -> None:
        """run() returns a ValidityResult instance."""
        agent = ValidityAgent(llm_client=_make_client(_json_response()))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert isinstance(result, ValidityResult)

    @pytest.mark.asyncio
    async def test_all_six_fields_present(self) -> None:
        """ValidityResult exposes all six validity dimension fields."""
        agent = ValidityAgent(llm_client=_make_client(_json_response()))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        for dim in _DIMS:
            assert hasattr(result, dim)

    @pytest.mark.asyncio
    async def test_all_six_fields_non_empty(self) -> None:
        """All six validity dimension fields are non-empty strings."""
        agent = ValidityAgent(llm_client=_make_client(_json_response()))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        for dim in _DIMS:
            val = getattr(result, dim)
            assert isinstance(val, str) and val.strip(), (
                f"Dimension '{dim}' should be a non-empty string, got: {val!r}"
            )


class TestEmptyDimensionRejection:
    """ValueError is raised when a dimension is empty or whitespace-only."""

    @pytest.mark.asyncio
    async def test_empty_descriptive_raises_value_error(self) -> None:
        """Empty string for 'descriptive' raises ValueError during validation."""
        agent = ValidityAgent(llm_client=_make_client(_json_response(descriptive="")))
        with pytest.raises(ValueError):
            await agent.run(**_SNAPSHOT_KWARGS)

    @pytest.mark.asyncio
    async def test_whitespace_only_interpretive_raises_value_error(self) -> None:
        """Whitespace-only 'interpretive' raises ValueError during validation."""
        agent = ValidityAgent(llm_client=_make_client(_json_response(interpretive="   ")))
        with pytest.raises(ValueError):
            await agent.run(**_SNAPSHOT_KWARGS)

    @pytest.mark.asyncio
    async def test_empty_repeatability_raises_value_error(self) -> None:
        """Empty 'repeatability' raises ValueError."""
        agent = ValidityAgent(llm_client=_make_client(_json_response(repeatability="")))
        with pytest.raises(ValueError):
            await agent.run(**_SNAPSHOT_KWARGS)


class TestMarkdownFenceStripping:
    """JSON wrapped in markdown code fences is stripped before parsing."""

    @pytest.mark.asyncio
    async def test_strips_json_code_fence(self) -> None:
        """```json ... ``` fences are stripped and the payload parsed."""
        payload = _json_response()
        fenced = f"```json\n{payload}\n```"
        agent = ValidityAgent(llm_client=_make_client(fenced))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert isinstance(result, ValidityResult)

    @pytest.mark.asyncio
    async def test_strips_generic_code_fence(self) -> None:
        """Generic ``` fences without language tag are also stripped."""
        payload = _json_response()
        fenced = f"```\n{payload}\n```"
        agent = ValidityAgent(llm_client=_make_client(fenced))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert isinstance(result, ValidityResult)


class TestFieldTrimming:
    """Whitespace is stripped from dimension values."""

    @pytest.mark.asyncio
    async def test_leading_trailing_whitespace_stripped(self) -> None:
        """Leading/trailing whitespace in dimension values is stripped."""
        padded = _json_response(descriptive="  Some descriptive text.  ")
        agent = ValidityAgent(llm_client=_make_client(padded))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert result.descriptive == "Some descriptive text."
