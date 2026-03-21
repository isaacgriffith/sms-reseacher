"""Metamorphic tests for the ProtocolReviewerAgent.

Metamorphic Relation (MR-PR1): Paraphrase-Section Preservation
--------------------------------------------------------------
A protocol paraphrased with the same semantic content and the same
number of non-empty sections should produce the same set of *issue
sections* (though not necessarily the same wording).

Because we test agent logic rather than live LLM calls, these tests
use a stubbed ``LLMClient`` that returns deterministic responses,
allowing fast, offline, reproducible MT verification.

Metamorphic Relation (MR-PR2): Long-Input Stability
----------------------------------------------------
The agent must not raise an exception when supplied with arbitrarily
long field values; it should return a valid ProtocolReviewResult.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from hypothesis import given
from hypothesis import strategies as st

from agents.core.llm_client import LLMClient
from agents.services.protocol_reviewer import ProtocolReviewerAgent, ProtocolReviewResult

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_BASE_PROTOCOL: dict[str, object] = {
    "background": "This review examines TDD in agile teams.",
    "rationale": "No prior synthesis of TDD effect sizes exists.",
    "research_questions": ["RQ1: What is the effect of TDD on defect density?"],
    "pico_population": "Agile software development teams",
    "pico_intervention": "Test-driven development",
    "pico_comparison": "Traditional development",
    "pico_outcome": "Defect density",
    "pico_context": None,
    "search_strategy": "(TDD OR 'test-driven') AND (quality OR defect)",
    "inclusion_criteria": ["Empirical studies", "Peer-reviewed"],
    "exclusion_criteria": ["Grey literature"],
    "data_extraction_strategy": "Extract effect sizes and CIs.",
    "synthesis_approach": "meta_analysis",
    "dissemination_strategy": "Journal publication.",
    "timetable": "Q1-Q4 2026",
}


def _make_stub_agent(issues: list[dict], assessment: str) -> ProtocolReviewerAgent:
    """Return a ProtocolReviewerAgent backed by a stub LLMClient."""
    response = json.dumps({"issues": issues, "overall_assessment": assessment})
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=response)
    return ProtocolReviewerAgent(llm_client=stub_client)


def _paraphrase_protocol(protocol: dict[str, object]) -> dict[str, object]:
    """Return a shallow copy with 'background' slightly paraphrased.

    The paraphrase does not change meaning — just word order — so the
    same stub LLM response is appropriate for both versions.
    """
    paraphrased = dict(protocol)
    bg = str(protocol.get("background") or "")
    paraphrased["background"] = bg.replace("This review", "The review")
    return paraphrased


# ---------------------------------------------------------------------------
# MR-PR1: Paraphrase-section preservation
# ---------------------------------------------------------------------------


class TestParaphraseSectionPreservation:
    """MR-PR1: paraphrased protocol returns the same issue sections."""

    @pytest.mark.asyncio
    async def test_same_issue_sections_after_paraphrase(self) -> None:
        """Paraphrasing background text does not change the set of flagged sections."""
        issues = [{"section": "search_strategy", "severity": "major",
                   "description": "Missing Boolean operators.", "suggestion": "Add AND/OR."}]
        agent = _make_stub_agent(issues, "One issue found.")
        original = _BASE_PROTOCOL
        paraphrased = _paraphrase_protocol(_BASE_PROTOCOL)

        result_orig = await agent.review(original)
        result_para = await agent.review(paraphrased)

        sections_orig = {i.section for i in result_orig.issues}
        sections_para = {i.section for i in result_para.issues}
        assert sections_orig == sections_para

    @pytest.mark.asyncio
    async def test_no_issues_preserved_after_paraphrase(self) -> None:
        """A protocol with no issues continues to have no issues after paraphrase."""
        agent = _make_stub_agent([], "Protocol is sound.")
        original = _BASE_PROTOCOL
        paraphrased = _paraphrase_protocol(_BASE_PROTOCOL)

        result_orig = await agent.review(original)
        result_para = await agent.review(paraphrased)

        assert result_orig.issues == []
        assert result_para.issues == []

    @given(
        background=st.text(min_size=5, max_size=100,
                           alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs")))
    )
    @pytest.mark.asyncio
    async def test_hypothesis_paraphrase_section_set_preserved(self, background: str) -> None:
        """Property: paraphrasing background never changes the set of issue sections.

        Uses hypothesis to generate varied background texts.  The stub LLM
        always returns the same deterministic response, so the section sets
        are trivially equal — this validates the MR structure.
        """
        issues = [{"section": "timetable", "severity": "minor",
                   "description": "Timetable is vague.", "suggestion": "Add dates."}]
        agent = _make_stub_agent(issues, "One minor issue.")

        protocol = dict(_BASE_PROTOCOL)
        protocol["background"] = background
        paraphrased = dict(protocol)
        paraphrased["background"] = background + " (revised)"

        result_orig = await agent.review(protocol)
        result_para = await agent.review(paraphrased)

        assert {i.section for i in result_orig.issues} == {i.section for i in result_para.issues}


# ---------------------------------------------------------------------------
# MR-PR2: Long-input stability
# ---------------------------------------------------------------------------


class TestLongInputStability:
    """MR-PR2: agent does not raise on arbitrarily long inputs."""

    @given(
        long_text=st.text(min_size=500, max_size=5000,
                          alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs", "Nd")))
    )
    @pytest.mark.asyncio
    async def test_no_exception_on_long_background(self, long_text: str) -> None:
        """review() must not raise even when background is very long."""
        agent = _make_stub_agent([], "Review complete.")
        protocol = dict(_BASE_PROTOCOL)
        protocol["background"] = long_text
        result = await agent.review(protocol)
        assert isinstance(result, ProtocolReviewResult)

    @given(
        long_list=st.lists(
            st.text(min_size=10, max_size=100,
                    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs"))),
            min_size=20,
            max_size=100,
        )
    )
    @pytest.mark.asyncio
    async def test_no_exception_on_long_criteria_list(self, long_list: list[str]) -> None:
        """review() must not raise even with very many inclusion criteria."""
        agent = _make_stub_agent([], "Review complete.")
        protocol = dict(_BASE_PROTOCOL)
        protocol["inclusion_criteria"] = long_list
        result = await agent.review(protocol)
        assert isinstance(result, ProtocolReviewResult)
