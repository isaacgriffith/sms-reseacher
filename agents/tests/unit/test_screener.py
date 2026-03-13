"""Unit tests for ScreenerAgent — structured criteria mode.

Mocks LLMClient to verify:
- ScreeningResult type returned in structured mode
- decision values: accepted / rejected / duplicate
- reasons list populated from JSON response
- fallback decision parsing when LLM returns plain text
- markdown code-fence stripping
- legacy string mode still returns raw str
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.services.screener import CriterionRef, ScreenerAgent, ScreeningResult


def _make_client(response: str) -> MagicMock:
    """Return a mock LLMClient whose complete() coroutine returns *response*."""
    client = MagicMock()
    client.complete = AsyncMock(return_value=response)
    return client


_INC = [{"id": 1, "description": "Must be peer-reviewed"}]
_EXC = [{"id": 2, "description": "No grey literature"}]
_ABSTRACT = "This paper presents a controlled experiment on TDD adoption rates."
_TITLE = "TDD Adoption: A Controlled Experiment"


def _json_response(decision: str, reasons: list[dict]) -> str:
    return json.dumps({"decision": decision, "reasons": reasons})


class TestScreeningResultShape:
    """Verify ScreeningResult structure from mocked LLM output."""

    @pytest.mark.asyncio
    async def test_returns_screening_result_type(self) -> None:
        """run() returns a ScreeningResult in structured mode."""
        resp = _json_response("accepted", [{"criterion_id": 1, "criterion_type": "inclusion", "text": "Is peer-reviewed"}])
        agent = ScreenerAgent(llm_client=_make_client(resp))
        result = await agent.run(
            inclusion_criteria=_INC,
            exclusion_criteria=_EXC,
            abstract=_ABSTRACT,
            title=_TITLE,
        )
        assert isinstance(result, ScreeningResult)

    @pytest.mark.asyncio
    async def test_accepted_decision(self) -> None:
        """decision='accepted' is correctly parsed."""
        resp = _json_response("accepted", [])
        agent = ScreenerAgent(llm_client=_make_client(resp))
        result = await agent.run(inclusion_criteria=_INC, exclusion_criteria=_EXC, abstract=_ABSTRACT)
        assert isinstance(result, ScreeningResult)
        assert result.decision == "accepted"

    @pytest.mark.asyncio
    async def test_rejected_decision(self) -> None:
        """decision='rejected' is correctly parsed."""
        resp = _json_response("rejected", [{"criterion_id": 2, "criterion_type": "exclusion", "text": "Grey literature"}])
        agent = ScreenerAgent(llm_client=_make_client(resp))
        result = await agent.run(inclusion_criteria=_INC, exclusion_criteria=_EXC, abstract=_ABSTRACT)
        assert isinstance(result, ScreeningResult)
        assert result.decision == "rejected"

    @pytest.mark.asyncio
    async def test_duplicate_decision(self) -> None:
        """decision='duplicate' is correctly parsed."""
        resp = _json_response("duplicate", [])
        agent = ScreenerAgent(llm_client=_make_client(resp))
        result = await agent.run(inclusion_criteria=_INC, exclusion_criteria=_EXC, abstract=_ABSTRACT)
        assert isinstance(result, ScreeningResult)
        assert result.decision == "duplicate"

    @pytest.mark.asyncio
    async def test_reasons_list_populated(self) -> None:
        """reasons is a list of CriterionRef objects when JSON response includes them."""
        reasons = [
            {"criterion_id": 1, "criterion_type": "inclusion", "text": "Is peer-reviewed"},
            {"criterion_id": 2, "criterion_type": "exclusion", "text": "No grey literature"},
        ]
        resp = _json_response("rejected", reasons)
        agent = ScreenerAgent(llm_client=_make_client(resp))
        result = await agent.run(inclusion_criteria=_INC, exclusion_criteria=_EXC, abstract=_ABSTRACT)
        assert isinstance(result, ScreeningResult)
        assert len(result.reasons) == 2
        assert all(isinstance(r, CriterionRef) for r in result.reasons)
        assert result.reasons[0].criterion_id == 1
        assert result.reasons[0].criterion_type == "inclusion"

    @pytest.mark.asyncio
    async def test_reasons_list_empty_when_not_provided(self) -> None:
        """reasons defaults to [] when LLM response has empty list."""
        resp = _json_response("accepted", [])
        agent = ScreenerAgent(llm_client=_make_client(resp))
        result = await agent.run(inclusion_criteria=_INC, exclusion_criteria=_EXC, abstract=_ABSTRACT)
        assert isinstance(result, ScreeningResult)
        assert result.reasons == []


class TestFallbackParsing:
    """Fallback when LLM returns non-JSON text."""

    @pytest.mark.asyncio
    async def test_plain_text_accept_fallback(self) -> None:
        """Plain text with 'accept' → decision='accepted', reasons=[]."""
        agent = ScreenerAgent(llm_client=_make_client("This paper should be accepted."))
        result = await agent.run(inclusion_criteria=_INC, exclusion_criteria=_EXC, abstract=_ABSTRACT)
        assert isinstance(result, ScreeningResult)
        assert result.decision == "accepted"
        assert result.reasons == []

    @pytest.mark.asyncio
    async def test_plain_text_reject_fallback(self) -> None:
        """Plain text without 'accept'/'duplicate' → decision='rejected'."""
        agent = ScreenerAgent(llm_client=_make_client("This paper does not meet the criteria."))
        result = await agent.run(inclusion_criteria=_INC, exclusion_criteria=_EXC, abstract=_ABSTRACT)
        assert isinstance(result, ScreeningResult)
        assert result.decision == "rejected"

    @pytest.mark.asyncio
    async def test_plain_text_duplicate_fallback(self) -> None:
        """Plain text containing 'duplicate' → decision='duplicate'."""
        agent = ScreenerAgent(llm_client=_make_client("This appears to be a duplicate entry."))
        result = await agent.run(inclusion_criteria=_INC, exclusion_criteria=_EXC, abstract=_ABSTRACT)
        assert isinstance(result, ScreeningResult)
        assert result.decision == "duplicate"


class TestMarkdownFenceStripping:
    """JSON wrapped in markdown code fences is stripped before parsing."""

    @pytest.mark.asyncio
    async def test_strips_json_code_fence(self) -> None:
        """```json ... ``` fences are stripped and the payload parsed."""
        payload = _json_response("accepted", [])
        fenced = f"```json\n{payload}\n```"
        agent = ScreenerAgent(llm_client=_make_client(fenced))
        result = await agent.run(inclusion_criteria=_INC, exclusion_criteria=_EXC, abstract=_ABSTRACT)
        assert isinstance(result, ScreeningResult)
        assert result.decision == "accepted"


class TestLegacyStringMode:
    """Legacy string mode: returns raw string, not ScreeningResult."""

    @pytest.mark.asyncio
    async def test_string_criteria_returns_raw_string(self) -> None:
        """When criteria are plain strings, run() returns a string (legacy mode)."""
        agent = ScreenerAgent(llm_client=_make_client("ACCEPTED"))
        result = await agent.run(
            inclusion_criteria="Must be peer-reviewed",
            exclusion_criteria="No grey literature",
            abstract=_ABSTRACT,
        )
        assert isinstance(result, str)
        assert result == "ACCEPTED"
