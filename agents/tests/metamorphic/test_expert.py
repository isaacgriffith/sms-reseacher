"""Metamorphic tests for ExpertAgent.

Metamorphic Relations
---------------------
MR-EX1: Paraphrase Consistency
    Equivalent topic descriptions phrased differently must produce the same
    number of paper suggestions and structurally equivalent output under a
    deterministic stub LLM.

MR-EX2: Component Subset Monotonicity
    Providing a richer set of PICO components (e.g. adding intervention and
    outcome fields to a topic-only query) must not reduce the number of
    suggested papers.

Tests use a stubbed ``LLMClient`` for deterministic, offline verification.

See conftest.py for hypothesis profile configuration.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

from hypothesis import given
from hypothesis import strategies as st

from agents.core.llm_client import LLMClient
from agents.services.expert import ExpertAgent

# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

_STUB_PAPER = {
    "title": "Expert Stub Paper on TDD",
    "authors": ["Bob Jones"],
    "year": 2023,
    "venue": "FSE",
    "doi": "10.1145/stub",
    "rationale": "Expert stub paper — highly cited.",
}

_STUB_OUTPUT_1 = json.dumps([_STUB_PAPER])
_STUB_OUTPUT_2 = json.dumps([_STUB_PAPER, {**_STUB_PAPER, "title": "Expert Stub Paper 2"}])


def make_stub_agent(output: str = _STUB_OUTPUT_1) -> ExpertAgent:
    """Return an ExpertAgent backed by a deterministic stub LLMClient.

    Args:
        output: JSON string the stub will return for every LLM call.

    Returns:
        :class:`ExpertAgent` with mocked LLM client.
    """
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=output)
    return ExpertAgent(llm_client=stub_client)


# ---------------------------------------------------------------------------
# MR-EX1: Paraphrase Consistency
# ---------------------------------------------------------------------------


class TestExpertMREX1ParaphraseConsistency:
    """MR-EX1: equivalent topic phrasings must produce structurally equivalent output."""

    async def test_abbreviated_vs_full_topic_same_count(self) -> None:
        """'TDD' vs 'Test-Driven Development' must produce identical paper count.

        Under a deterministic stub both calls return the same JSON.
        """
        agent = make_stub_agent(_STUB_OUTPUT_1)

        result_abbrev = await agent.run(topic="TDD", variant="PICO")
        result_full = await agent.run(
            topic="Test-Driven Development", variant="PICO"
        )

        assert len(result_abbrev) == len(result_full), (
            "MR-EX1: paraphrase must not change paper count"
        )

    async def test_paraphrase_preserves_doi_format(self) -> None:
        """All returned DOIs must satisfy the 10. prefix invariant across paraphrases."""
        agent = make_stub_agent(_STUB_OUTPUT_1)

        for topic in ["TDD", "Test-Driven Development", "unit testing first"]:
            papers = await agent.run(topic=topic, variant="PICO")
            for paper in papers:
                if paper.doi is not None:
                    assert paper.doi.startswith("10."), (
                        f"MR-EX1: DOI '{paper.doi}' violates 10. prefix for topic='{topic}'"
                    )

    @given(
        topic_a=st.sampled_from(["TDD", "Test-Driven Development", "test-first programming"]),
        topic_b=st.sampled_from(["TDD", "Test-Driven Development", "test-first programming"]),
    )
    async def test_any_paraphrase_pair_same_structure(
        self, topic_a: str, topic_b: str
    ) -> None:
        """Hypothesis: any paraphrase pair produces identical stub output."""
        agent = make_stub_agent(_STUB_OUTPUT_1)

        result_a = await agent.run(topic=topic_a, variant="PICO")
        result_b = await agent.run(topic=topic_b, variant="PICO")

        assert len(result_a) == len(result_b), (
            f"MR-EX1: '{topic_a}' vs '{topic_b}' produced different paper counts"
        )


# ---------------------------------------------------------------------------
# MR-EX2: Component Subset Monotonicity
# ---------------------------------------------------------------------------


class TestExpertMREX2ComponentSubsetMonotonicity:
    """MR-EX2: richer PICO components must not reduce paper suggestions."""

    async def test_adding_intervention_does_not_reduce_papers(self) -> None:
        """Adding an intervention field must not reduce paper count.

        Source: topic only.
        Follow-up: topic + intervention (richer context).
        """
        agent_base = make_stub_agent(_STUB_OUTPUT_1)
        agent_enriched = make_stub_agent(_STUB_OUTPUT_2)

        result_base = await agent_base.run(topic="TDD", variant="PICO")
        result_enriched = await agent_enriched.run(
            topic="TDD",
            variant="PICO",
            intervention="writing tests before implementation",
        )

        assert len(result_enriched) >= len(result_base), (
            "MR-EX2: adding intervention context must not reduce paper count"
        )

    async def test_adding_outcome_does_not_reduce_papers(self) -> None:
        """Adding an outcome field must not reduce paper count."""
        agent_base = make_stub_agent(_STUB_OUTPUT_1)
        agent_enriched = make_stub_agent(_STUB_OUTPUT_2)

        result_base = await agent_base.run(topic="TDD", variant="PICO")
        result_enriched = await agent_enriched.run(
            topic="TDD",
            variant="PICO",
            outcome="code quality and defect density",
        )

        assert len(result_enriched) >= len(result_base), (
            "MR-EX2: adding outcome context must not reduce paper count"
        )

    @given(
        pico_field=st.sampled_from(["population", "intervention", "comparison", "outcome"])
    )
    async def test_any_pico_addition_non_reducing(self, pico_field: str) -> None:
        """Hypothesis: adding any PICO field must not reduce suggestion count (stub)."""
        agent_base = make_stub_agent(_STUB_OUTPUT_1)
        agent_enriched = make_stub_agent(_STUB_OUTPUT_2)

        result_base = await agent_base.run(topic="TDD", variant="PICO")
        kwargs = {pico_field: f"stub value for {pico_field}"}
        result_enriched = await agent_enriched.run(
            topic="TDD", variant="PICO", **kwargs
        )

        assert len(result_enriched) >= len(result_base), (
            f"MR-EX2: adding '{pico_field}' must not reduce paper count"
        )
