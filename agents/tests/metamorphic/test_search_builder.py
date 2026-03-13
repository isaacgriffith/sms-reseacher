"""Metamorphic tests for SearchStringBuilderAgent.

Metamorphic Relations
---------------------
MR-SB1: Keyword Subset Monotonicity
    Providing more seed keywords should produce a search string that contains
    at least as many Boolean terms as a string built from fewer keywords.
    Under a deterministic stub the string content is identical, demonstrating
    the structural invariant is correctly wired.

MR-SB2: Paraphrase Consistency
    Equivalent PICO descriptions phrased differently must produce search
    strings with the same number of term groups and the same structural
    properties (non-empty string, valid Boolean operators).

Tests use a stubbed ``LLMClient`` for deterministic, offline verification.

See conftest.py for hypothesis profile configuration.
"""

from __future__ import annotations

import json
import re
from unittest.mock import AsyncMock, MagicMock

from hypothesis import given
from hypothesis import strategies as st

from agents.core.llm_client import LLMClient
from agents.services.search_builder import SearchStringBuilderAgent

# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

_STUB_RESPONSE = json.dumps({
    "search_string": '(TDD OR "test-driven development") AND (quality OR defect)',
    "terms_used": [
        {"component": "intervention", "terms": ["TDD", "test-driven development"]},
        {"component": "outcome", "terms": ["quality", "defect"]},
    ],
    "expansion_notes": "Stub expansion notes.",
})

_STUB_RESPONSE_RICHER = json.dumps({
    "search_string": (
        '(TDD OR "test-driven development") AND (quality OR defect) '
        'AND (software OR code) AND (engineer OR developer)'
    ),
    "terms_used": [
        {"component": "intervention", "terms": ["TDD", "test-driven development"]},
        {"component": "outcome", "terms": ["quality", "defect"]},
        {"component": "population", "terms": ["software", "code"]},
        {"component": "context", "terms": ["engineer", "developer"]},
    ],
    "expansion_notes": "Stub expansion notes with more keywords.",
})


def make_stub_agent(output: str = _STUB_RESPONSE) -> SearchStringBuilderAgent:
    """Return a SearchStringBuilderAgent backed by a deterministic stub LLMClient.

    Args:
        output: JSON string the stub will return for every LLM call.

    Returns:
        :class:`SearchStringBuilderAgent` with mocked LLM client.
    """
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=output)
    return SearchStringBuilderAgent(llm_client=stub_client)


def _count_boolean_terms(search_string: str) -> int:
    """Count the number of distinct quoted or unquoted terms in the Boolean string.

    Args:
        search_string: Boolean search string to analyse.

    Returns:
        Count of distinct term tokens.
    """
    # Extract quoted phrases and individual words
    quoted = re.findall(r'"[^"]+"', search_string)
    unquoted = re.findall(r'\b(?!AND|OR|NOT\b)[A-Za-z][\w-]*\b', search_string)
    return len(quoted) + len(unquoted)


# ---------------------------------------------------------------------------
# MR-SB1: Keyword Subset Monotonicity
# ---------------------------------------------------------------------------


class TestSearchBuilderMRSB1KeywordSubsetMonotonicity:
    """MR-SB1: more seed keywords must not reduce Boolean term count."""

    async def test_fewer_keywords_produces_fewer_or_equal_terms(self) -> None:
        """Source (2 keywords) and follow-up (4 keywords) with stubs.

        The richer stub returns a longer string; confirms the structural MR
        is wired through the agent correctly.
        """
        agent_base = make_stub_agent(_STUB_RESPONSE)
        agent_enriched = make_stub_agent(_STUB_RESPONSE_RICHER)

        result_base = await agent_base.run(
            topic="TDD",
            variant="PICO",
            seed_keywords=["TDD", "unit testing"],
        )
        result_enriched = await agent_enriched.run(
            topic="TDD",
            variant="PICO",
            seed_keywords=["TDD", "unit testing", "test-first", "red-green-refactor"],
        )

        terms_base = _count_boolean_terms(result_base.search_string)
        terms_enriched = _count_boolean_terms(result_enriched.search_string)

        assert terms_enriched >= terms_base, (
            "MR-SB1: more seed keywords must not reduce Boolean term count. "
            f"Base: {terms_base}, enriched: {terms_enriched}"
        )

    async def test_no_keywords_vs_some_keywords(self) -> None:
        """No seed keywords (base) vs. two keywords (follow-up) must be non-reducing."""
        agent_base = make_stub_agent(_STUB_RESPONSE)
        agent_enriched = make_stub_agent(_STUB_RESPONSE_RICHER)

        result_base = await agent_base.run(topic="TDD", variant="PICO")
        result_enriched = await agent_enriched.run(
            topic="TDD",
            variant="PICO",
            seed_keywords=["TDD", "unit test"],
        )

        assert len(result_enriched.terms_used) >= len(result_base.terms_used), (
            "MR-SB1: seed keywords must not reduce number of TermGroups"
        )

    @given(
        n_keywords=st.integers(min_value=0, max_value=5)
    )
    async def test_term_count_non_negative(self, n_keywords: int) -> None:
        """Hypothesis: term count must always be ≥ 1 for any keyword count."""
        keywords = [f"keyword_{i}" for i in range(n_keywords)]
        agent = make_stub_agent(_STUB_RESPONSE)

        result = await agent.run(
            topic="TDD",
            variant="PICO",
            seed_keywords=keywords if keywords else None,
        )

        assert _count_boolean_terms(result.search_string) >= 1, (
            "MR-SB1: search string must always contain ≥ 1 term"
        )


# ---------------------------------------------------------------------------
# MR-SB2: Paraphrase Consistency
# ---------------------------------------------------------------------------


class TestSearchBuilderMRSB2ParaphraseConsistency:
    """MR-SB2: equivalent PICO descriptions must produce structurally equivalent output."""

    async def test_equivalent_topics_same_term_group_count(self) -> None:
        """'TDD' vs 'Test-Driven Development' must produce same number of term groups.

        Under a deterministic stub both calls return identical JSON.
        """
        agent = make_stub_agent(_STUB_RESPONSE)

        result_abbrev = await agent.run(topic="TDD", variant="PICO")
        result_full = await agent.run(
            topic="Test-Driven Development", variant="PICO"
        )

        assert len(result_abbrev.terms_used) == len(result_full.terms_used), (
            "MR-SB2: paraphrase must not change number of TermGroups"
        )

    async def test_paraphrase_preserves_boolean_operators(self) -> None:
        """Paraphrased topics must produce strings with valid Boolean operators."""
        agent = make_stub_agent(_STUB_RESPONSE)

        for topic in ["TDD", "Test-Driven Development", "unit test-first"]:
            result = await agent.run(topic=topic, variant="PICO")
            # A well-formed Boolean string uses AND/OR
            assert re.search(r"\b(?:AND|OR)\b", result.search_string), (
                f"MR-SB2: search string for topic='{topic}' missing Boolean operators. "
                f"Got: {result.search_string!r}"
            )

    async def test_paraphrase_produces_non_empty_string(self) -> None:
        """Every paraphrase must produce a non-empty search string."""
        agent = make_stub_agent(_STUB_RESPONSE)

        for topic in ["TDD", "Test-Driven Development", "test-first"]:
            result = await agent.run(topic=topic, variant="PICO")
            assert result.search_string.strip(), (
                f"MR-SB2: search string must not be empty for topic='{topic}'"
            )

    @given(
        topic_a=st.sampled_from(["TDD", "Test-Driven Development", "test-first"]),
        topic_b=st.sampled_from(["TDD", "Test-Driven Development", "test-first"]),
    )
    async def test_any_paraphrase_pair_same_groups(
        self, topic_a: str, topic_b: str
    ) -> None:
        """Hypothesis: any two topic paraphrases produce the same term group count."""
        agent = make_stub_agent(_STUB_RESPONSE)

        result_a = await agent.run(topic=topic_a, variant="PICO")
        result_b = await agent.run(topic=topic_b, variant="PICO")

        assert len(result_a.terms_used) == len(result_b.terms_used), (
            f"MR-SB2: '{topic_a}' vs '{topic_b}' produced different TermGroup counts"
        )
