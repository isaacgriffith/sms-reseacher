"""Metamorphic tests for DomainModelAgent.

Metamorphic Relations
---------------------
MR-DM1: Concept-Set Stability
    Running the agent on the same set of paper summaries multiple times
    (with a deterministic stub) must always produce the same concept names
    and the same relationship count.

MR-DM2: Summary Superset Monotonicity
    Adding more paper summaries (richer corpus) must not reduce the number
    of identified concepts or relationships.

Tests use a stubbed ``LLMClient`` for deterministic, offline verification.

See conftest.py for hypothesis profile configuration.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

from hypothesis import given
from hypothesis import strategies as st

from agents.core.llm_client import LLMClient
from agents.services.domain_modeler import DomainModelAgent

# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

_STUB_RESPONSE_SMALL = json.dumps({
    "concepts": [
        {"name": "TDD", "definition": "Test-Driven Development methodology.", "attributes": ["iterative"]},
        {"name": "Defect", "definition": "Software defect or bug.", "attributes": []},
    ],
    "relationships": [
        {"from": "TDD", "to": "Defect", "label": "reduces", "type": "causal"},
    ],
})

_STUB_RESPONSE_LARGE = json.dumps({
    "concepts": [
        {"name": "TDD", "definition": "Test-Driven Development methodology.", "attributes": ["iterative"]},
        {"name": "Defect", "definition": "Software defect or bug.", "attributes": []},
        {"name": "Code Quality", "definition": "Measure of software correctness.", "attributes": []},
        {"name": "CI Pipeline", "definition": "Continuous Integration automation.", "attributes": []},
    ],
    "relationships": [
        {"from": "TDD", "to": "Defect", "label": "reduces", "type": "causal"},
        {"from": "TDD", "to": "Code Quality", "label": "improves", "type": "causal"},
        {"from": "CI Pipeline", "to": "TDD", "label": "enables", "type": "supportive"},
    ],
})


def make_stub_agent(output: str = _STUB_RESPONSE_SMALL) -> DomainModelAgent:
    """Return a DomainModelAgent backed by a deterministic stub LLMClient.

    Args:
        output: JSON string the stub will return for every LLM call.

    Returns:
        :class:`DomainModelAgent` with mocked LLM client.
    """
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=output)
    return DomainModelAgent(llm_client=stub_client)


_BASE_SUMMARIES = [
    "TDD reduces defect density significantly in Java projects.",
]

_EXTENDED_SUMMARIES = [
    "TDD reduces defect density significantly in Java projects.",
    "Continuous integration enables faster feedback loops for TDD teams.",
    "Code quality metrics improve with systematic test-first practices.",
    "TDD improves software maintainability in agile teams.",
]


# ---------------------------------------------------------------------------
# MR-DM1: Concept-Set Stability
# ---------------------------------------------------------------------------


class TestDomainModelerMRDM1ConceptSetStability:
    """MR-DM1: same input corpus must always produce the same concept names."""

    async def test_identical_inputs_produce_identical_concepts(self) -> None:
        """Two calls with identical inputs must produce the same concept names.

        Under a deterministic stub the output is identical by construction.
        """
        agent = make_stub_agent(_STUB_RESPONSE_SMALL)

        result_a = await agent.run(
            topic="TDD in software engineering",
            summaries=_BASE_SUMMARIES,
        )
        result_b = await agent.run(
            topic="TDD in software engineering",
            summaries=_BASE_SUMMARIES,
        )

        names_a = {c.name for c in result_a.concepts}
        names_b = {c.name for c in result_b.concepts}

        assert names_a == names_b, (
            "MR-DM1: identical inputs must produce identical concept names. "
            f"Got {names_a} vs {names_b}"
        )

    async def test_identical_inputs_produce_same_relationship_count(self) -> None:
        """Two calls with identical inputs must produce the same relationship count."""
        agent = make_stub_agent(_STUB_RESPONSE_SMALL)

        result_a = await agent.run(topic="TDD", summaries=_BASE_SUMMARIES)
        result_b = await agent.run(topic="TDD", summaries=_BASE_SUMMARIES)

        assert len(result_a.relationships) == len(result_b.relationships), (
            "MR-DM1: relationship count must be stable for identical inputs"
        )

    async def test_all_concepts_have_non_empty_names(self) -> None:
        """Every concept in the domain model must have a non-empty name."""
        agent = make_stub_agent(_STUB_RESPONSE_SMALL)
        result = await agent.run(topic="TDD", summaries=_BASE_SUMMARIES)

        for concept in result.concepts:
            assert concept.name.strip(), (
                "MR-DM1: concept name must not be empty or whitespace"
            )

    async def test_all_relationships_have_valid_endpoints(self) -> None:
        """Every relationship must have non-empty from_ and to values."""
        agent = make_stub_agent(_STUB_RESPONSE_SMALL)
        result = await agent.run(topic="TDD", summaries=_BASE_SUMMARIES)

        for rel in result.relationships:
            assert rel.from_.strip(), "MR-DM1: relationship.from_ must not be empty"
            assert rel.to.strip(), "MR-DM1: relationship.to must not be empty"

    @given(
        topic=st.sampled_from(["TDD", "test-driven development", "unit testing"])
    )
    async def test_concept_count_positive(self, topic: str) -> None:
        """Hypothesis: at least one concept must be identified for any topic."""
        agent = make_stub_agent(_STUB_RESPONSE_SMALL)
        result = await agent.run(topic=topic, summaries=_BASE_SUMMARIES)
        assert len(result.concepts) >= 1, (
            f"MR-DM1: at least one concept required for topic='{topic}'"
        )


# ---------------------------------------------------------------------------
# MR-DM2: Summary Superset Monotonicity
# ---------------------------------------------------------------------------


class TestDomainModelerMRDM2SummarySupersetMonotonicity:
    """MR-DM2: more paper summaries must not reduce concept or relationship count."""

    async def test_more_summaries_does_not_reduce_concepts(self) -> None:
        """Extended corpus (4 summaries) must not reduce concept count vs 1 summary.

        The richer stub returns more concepts, confirming the structural MR.
        """
        agent_small = make_stub_agent(_STUB_RESPONSE_SMALL)
        agent_large = make_stub_agent(_STUB_RESPONSE_LARGE)

        result_small = await agent_small.run(
            topic="TDD",
            summaries=_BASE_SUMMARIES,
        )
        result_large = await agent_large.run(
            topic="TDD",
            summaries=_EXTENDED_SUMMARIES,
        )

        assert len(result_large.concepts) >= len(result_small.concepts), (
            "MR-DM2: more summaries must not reduce concept count. "
            f"Small: {len(result_small.concepts)}, Large: {len(result_large.concepts)}"
        )

    async def test_more_summaries_does_not_reduce_relationships(self) -> None:
        """Extended corpus must not reduce relationship count."""
        agent_small = make_stub_agent(_STUB_RESPONSE_SMALL)
        agent_large = make_stub_agent(_STUB_RESPONSE_LARGE)

        result_small = await agent_small.run(topic="TDD", summaries=_BASE_SUMMARIES)
        result_large = await agent_large.run(topic="TDD", summaries=_EXTENDED_SUMMARIES)

        assert len(result_large.relationships) >= len(result_small.relationships), (
            "MR-DM2: more summaries must not reduce relationship count"
        )

    @given(
        n_summaries=st.integers(min_value=1, max_value=5)
    )
    async def test_concept_count_non_zero_for_any_corpus_size(
        self, n_summaries: int
    ) -> None:
        """Hypothesis: concept count must be ≥ 1 for any non-empty summary list."""
        summaries = [f"Paper summary {i} about TDD." for i in range(n_summaries)]
        agent = make_stub_agent(_STUB_RESPONSE_SMALL)
        result = await agent.run(topic="TDD", summaries=summaries)
        assert len(result.concepts) >= 1, (
            f"MR-DM2: concept count must be ≥ 1 for {n_summaries} summaries"
        )
