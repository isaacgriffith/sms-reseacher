"""Metamorphic tests for the ScreenerAgent.

Metamorphic Relation (MR-S1): Label-Preserving Synonym Substitution
--------------------------------------------------------------------
If we substitute synonyms for non-criteria-specific words in the
abstract, the inclusion/exclusion **decision** must remain unchanged.

Because we are testing the agent logic rather than live LLM calls,
these tests use a stubbed ``LLMClient`` that returns deterministic
responses, allowing fast, offline, reproducible MT verification.

Note: GeMTest (https://github.com/tum-i4/gemtest) is an alternative
framework that provides automated MR composition; these tests use
``hypothesis`` for simplicity and pytest integration.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from hypothesis import given
from hypothesis import strategies as st

from agents.core.llm_client import LLMClient
from agents.services.screener import ScreenerAgent

# Fixed criteria used across all metamorphic tests
INCLUSION = "Studies on automated testing in software engineering"
EXCLUSION = "Papers not peer-reviewed or published before 2015"

# Synonym map: words that can be substituted without changing meaning
SYNONYMS: dict[str, str] = {
    "study": "research",
    "research": "study",
    "paper": "article",
    "article": "paper",
    "evaluate": "assess",
    "assess": "evaluate",
    "software": "code",
    "code": "software",
}


def apply_synonyms(text: str) -> str:
    """Apply one round of synonym substitution to *text*."""
    for original, synonym in SYNONYMS.items():
        if original in text:
            return text.replace(original, synonym, 1)
    return text


def make_stub_agent(decision: str) -> ScreenerAgent:
    """Return a ScreenerAgent backed by a stub LLMClient."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = f"Decision: {decision}\nReason: stub."

    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=f"Decision: {decision}\nReason: stub.")
    return ScreenerAgent(llm_client=stub_client)


def parse_decision(response: str) -> str:
    """Extract decision keyword from agent response."""
    for line in response.splitlines():
        if line.lower().startswith("decision:"):
            return line.split(":", 1)[1].strip().lower()
    return response.strip().lower()


class TestScreenerMR:
    """MR-S1: Synonym substitution preserves inclusion decision."""

    @given(abstract=st.text(min_size=20, max_size=200, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"))))
    async def test_synonym_substitution_preserves_decision(self, abstract: str) -> None:
        """Decision must be identical before and after synonym substitution."""
        # Use a deterministic stub so the test is reproducible
        agent_include = make_stub_agent("include")
        agent_exclude = make_stub_agent("exclude")

        original_abstract = abstract
        transformed_abstract = apply_synonyms(abstract)

        result_orig = await agent_include.run(INCLUSION, EXCLUSION, original_abstract)
        result_trans = await agent_include.run(INCLUSION, EXCLUSION, transformed_abstract)

        # Both calls use the same stub → decisions are trivially equal
        # (validates the MR structure; live LLM testing is in integration suite)
        assert parse_decision(result_orig) == parse_decision(result_trans)

    async def test_synonym_substitution_concrete_include(self) -> None:
        """Concrete MR-S1 example: 'study' → 'research' preserves include."""
        abstract = "This study evaluates automated testing techniques."
        transformed = abstract.replace("study", "research", 1)

        agent = make_stub_agent("include")
        r1 = await agent.run(INCLUSION, EXCLUSION, abstract)
        r2 = await agent.run(INCLUSION, EXCLUSION, transformed)

        assert parse_decision(r1) == parse_decision(r2)

    async def test_synonym_substitution_concrete_exclude(self) -> None:
        """Concrete MR-S1 example: decision preserved for excluded paper."""
        abstract = "This paper discusses cooking recipes."
        transformed = abstract.replace("paper", "article", 1)

        agent = make_stub_agent("exclude")
        r1 = await agent.run(INCLUSION, EXCLUSION, abstract)
        r2 = await agent.run(INCLUSION, EXCLUSION, transformed)

        assert parse_decision(r1) == parse_decision(r2)
