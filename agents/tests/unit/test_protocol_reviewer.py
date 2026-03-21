"""Unit tests for ProtocolReviewerAgent.

Mocks LLMClient to verify:
- Well-formed JSON is parsed into a ProtocolReviewResult.
- Malformed JSON response falls back gracefully.
- Markdown code-fence stripping works before JSON parsing.
- issues list is correctly populated with ProtocolIssue objects.
- system_message_override replaces the system prompt.
- Empty issues list is valid (protocol passes review).
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.services.protocol_reviewer import (
    ProtocolIssue,
    ProtocolReviewResult,
    ProtocolReviewerAgent,
)


def _make_client(response: str) -> MagicMock:
    """Return a mock LLMClient whose complete() coroutine returns *response*."""
    client = MagicMock()
    client.complete = AsyncMock(return_value=response)
    return client


_PROTOCOL = {
    "background": "This review examines TDD practices in agile teams.",
    "rationale": "Prior work has not synthesised TDD effect sizes systematically.",
    "research_questions": ["RQ1: What is the effect of TDD on defect density?"],
    "pico_population": "Agile software development teams",
    "pico_intervention": "Test-driven development (TDD)",
    "pico_comparison": "Traditional development without TDD",
    "pico_outcome": "Defect density",
    "pico_context": None,
    "search_strategy": "(TDD OR 'test-driven') AND ('defect density' OR quality)",
    "inclusion_criteria": ["Empirical studies", "Peer-reviewed journals or conferences"],
    "exclusion_criteria": ["Grey literature", "Non-English publications"],
    "data_extraction_strategy": "Extract effect sizes, sample sizes, and confidence intervals.",
    "synthesis_approach": "meta_analysis",
    "dissemination_strategy": "Journal publication and conference presentation.",
    "timetable": "Q1 2026: search; Q2 2026: screening; Q3 2026: extraction; Q4 2026: synthesis",
}


def _json_review(issues: list[dict], overall_assessment: str) -> str:
    """Serialize a review result as JSON string."""
    return json.dumps({"issues": issues, "overall_assessment": overall_assessment})


class TestProtocolReviewResultParsing:
    """Verify well-formed JSON is parsed into ProtocolReviewResult."""

    @pytest.mark.asyncio
    async def test_returns_protocol_review_result_type(self) -> None:
        """review() returns a ProtocolReviewResult in normal operation."""
        resp = _json_review([], "Protocol looks good.")
        agent = ProtocolReviewerAgent(llm_client=_make_client(resp))
        result = await agent.review(_PROTOCOL)
        assert isinstance(result, ProtocolReviewResult)

    @pytest.mark.asyncio
    async def test_empty_issues_on_clean_protocol(self) -> None:
        """issues is empty when the LLM finds no problems."""
        resp = _json_review([], "No issues found.")
        agent = ProtocolReviewerAgent(llm_client=_make_client(resp))
        result = await agent.review(_PROTOCOL)
        assert result.issues == []
        assert result.overall_assessment == "No issues found."

    @pytest.mark.asyncio
    async def test_single_issue_parsed(self) -> None:
        """A single issue is correctly parsed into a ProtocolIssue."""
        issue = {
            "section": "research_questions",
            "severity": "major",
            "description": "RQ1 is not answerable with the stated PICO.",
            "suggestion": "Rewrite RQ1 to align with the Intervention and Outcome.",
        }
        resp = _json_review([issue], "One major issue found.")
        agent = ProtocolReviewerAgent(llm_client=_make_client(resp))
        result = await agent.review(_PROTOCOL)
        assert len(result.issues) == 1
        assert isinstance(result.issues[0], ProtocolIssue)
        assert result.issues[0].section == "research_questions"
        assert result.issues[0].severity == "major"

    @pytest.mark.asyncio
    async def test_multiple_issues_parsed(self) -> None:
        """Multiple issues are all parsed into ProtocolIssue objects."""
        issues = [
            {
                "section": "search_strategy",
                "severity": "critical",
                "description": "Boolean operators are missing.",
                "suggestion": "Add AND/OR operators between terms.",
            },
            {
                "section": "timetable",
                "severity": "minor",
                "description": "Timetable is very tight.",
                "suggestion": "Allow more time for the screening phase.",
            },
        ]
        resp = _json_review(issues, "Two issues found.")
        agent = ProtocolReviewerAgent(llm_client=_make_client(resp))
        result = await agent.review(_PROTOCOL)
        assert len(result.issues) == 2
        assert all(isinstance(i, ProtocolIssue) for i in result.issues)

    @pytest.mark.asyncio
    async def test_severity_values_preserved(self) -> None:
        """Severity fields are exactly preserved from the LLM response."""
        issues = [
            {"section": "a", "severity": "critical", "description": "x", "suggestion": "y"},
            {"section": "b", "severity": "major", "description": "x", "suggestion": "y"},
            {"section": "c", "severity": "minor", "description": "x", "suggestion": "y"},
        ]
        resp = _json_review(issues, "Assessment.")
        agent = ProtocolReviewerAgent(llm_client=_make_client(resp))
        result = await agent.review(_PROTOCOL)
        severities = [i.severity for i in result.issues]
        assert severities == ["critical", "major", "minor"]


class TestMalformedResponseHandling:
    """review() handles malformed LLM responses without raising."""

    @pytest.mark.asyncio
    async def test_plain_text_fallback(self) -> None:
        """Plain-text response is stored as overall_assessment with no issues."""
        agent = ProtocolReviewerAgent(llm_client=_make_client("The protocol needs work."))
        result = await agent.review(_PROTOCOL)
        assert isinstance(result, ProtocolReviewResult)
        assert result.issues == []
        assert "protocol needs work" in result.overall_assessment

    @pytest.mark.asyncio
    async def test_partial_json_fallback(self) -> None:
        """Truncated JSON response falls back gracefully."""
        agent = ProtocolReviewerAgent(llm_client=_make_client('{"issues": ['))
        result = await agent.review(_PROTOCOL)
        assert isinstance(result, ProtocolReviewResult)


class TestMarkdownFenceStripping:
    """JSON wrapped in markdown code fences is stripped before parsing."""

    @pytest.mark.asyncio
    async def test_json_code_fence_stripped(self) -> None:
        """```json ... ``` fences are stripped and the payload parsed."""
        payload = _json_review([], "Clean protocol.")
        fenced = f"```json\n{payload}\n```"
        agent = ProtocolReviewerAgent(llm_client=_make_client(fenced))
        result = await agent.review(_PROTOCOL)
        assert isinstance(result, ProtocolReviewResult)
        assert result.overall_assessment == "Clean protocol."

    @pytest.mark.asyncio
    async def test_generic_code_fence_stripped(self) -> None:
        """``` ... ``` (no language) fences are also stripped."""
        payload = _json_review([], "Good protocol.")
        fenced = f"```\n{payload}\n```"
        agent = ProtocolReviewerAgent(llm_client=_make_client(fenced))
        result = await agent.review(_PROTOCOL)
        assert result.overall_assessment == "Good protocol."


class TestSystemMessageOverride:
    """System message override replaces the default system prompt."""

    @pytest.mark.asyncio
    async def test_override_is_used(self) -> None:
        """system_message_override is passed to the LLM client."""
        client = _make_client(_json_review([], "Reviewed."))
        agent = ProtocolReviewerAgent(
            llm_client=client,
            system_message_override="Custom instructions.",
        )
        await agent.review(_PROTOCOL)
        call_args = client.complete.call_args
        messages = call_args[0][0]
        system_msgs = [m for m in messages if m.get("role") == "system"]
        assert len(system_msgs) >= 1
        assert system_msgs[0]["content"] == "Custom instructions."
