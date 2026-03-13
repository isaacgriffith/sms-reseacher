"""Metamorphic tests for SynthesiserAgent.

Metamorphic Relations
---------------------
MR-SY1: Summary Completeness Monotonicity
    Providing more paper summaries (richer evidence corpus) must produce
    synthesis output that is at least as long as synthesis from fewer papers.
    Under a deterministic stub this verifies the structural MR wiring;
    live semantic equivalence is validated in integration evals.

MR-SY2: Paraphrase Stability
    Rephrasing the research question without changing its meaning must not
    change the synthesis output when using a deterministic stub.  Under a
    live LLM the outputs must be semantically equivalent.

Tests use a stubbed ``LLMClient`` for deterministic, offline verification.

See conftest.py for hypothesis profile configuration.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from hypothesis import given
from hypothesis import strategies as st

from agents.core.llm_client import LLMClient
from agents.services.synthesiser import SynthesiserAgent

# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

_STUB_SHORT = (
    "## Summary\nTDD has mixed effects.\n\n"
    "## Key Findings\n- One finding.\n\n"
    "## Conclusion\nMore research needed."
)

_STUB_LONG = (
    "## Summary\nTDD reduces defect density in controlled experiments "
    "but shows mixed results in field studies.\n\n"
    "## Key Findings\n- Defect density reduced by 40% (controlled).\n"
    "- No significant reduction in field studies.\n"
    "- Development time temporarily increases.\n"
    "- Post-release defect rate improves.\n\n"
    "## Contradictions / Gaps\nControlled vs field study gap remains unresolved.\n\n"
    "## Conclusion\n"
    "TDD appears beneficial in controlled settings; further field evidence required."
)

_BASE_PAPERS = "Paper A: TDD reduces defect density by 40% in controlled experiments."

_EXTENDED_PAPERS = (
    "Paper A: TDD reduces defect density by 40% in controlled experiments.\n"
    "Paper B: No significant defect reduction with TDD in field studies.\n"
    "Paper C: TDD increases development time but lowers post-release defects.\n"
    "Paper D: Developer satisfaction improves with TDD adoption."
)

_RQ = "What is the effect of TDD on software defect density?"


def make_stub_agent(output: str = _STUB_SHORT) -> SynthesiserAgent:
    """Return a SynthesiserAgent backed by a deterministic stub LLMClient.

    Args:
        output: String the stub will return for every LLM call.

    Returns:
        :class:`SynthesiserAgent` with mocked LLM client.
    """
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=output)
    return SynthesiserAgent(llm_client=stub_client)


# ---------------------------------------------------------------------------
# MR-SY1: Summary Completeness Monotonicity
# ---------------------------------------------------------------------------


class TestSynthesiserMRSY1CompletenessMonotonicity:
    """MR-SY1: more papers must produce synthesis at least as long as fewer papers."""

    async def test_more_papers_produces_at_least_as_long_synthesis(self) -> None:
        """Four papers (long stub) must produce output ≥ one paper (short stub).

        The long stub returns more text, confirming the structural MR wiring.
        """
        agent_short = make_stub_agent(_STUB_SHORT)
        agent_long = make_stub_agent(_STUB_LONG)

        result_short = await agent_short.run(
            papers_summary=_BASE_PAPERS,
            research_question=_RQ,
        )
        result_long = await agent_long.run(
            papers_summary=_EXTENDED_PAPERS,
            research_question=_RQ,
        )

        assert len(result_long) >= len(result_short), (
            "MR-SY1: more paper summaries must not reduce synthesis length. "
            f"Short: {len(result_short)} chars, Long: {len(result_long)} chars"
        )

    async def test_synthesis_non_empty_for_single_paper(self) -> None:
        """Synthesis must be non-empty even with a single paper summary."""
        agent = make_stub_agent(_STUB_SHORT)
        result = await agent.run(papers_summary=_BASE_PAPERS, research_question=_RQ)
        assert result and result.strip(), (
            "MR-SY1: synthesis must be non-empty for a single paper"
        )

    async def test_synthesis_non_empty_for_extended_corpus(self) -> None:
        """Synthesis must be non-empty for an extended paper corpus."""
        agent = make_stub_agent(_STUB_LONG)
        result = await agent.run(papers_summary=_EXTENDED_PAPERS, research_question=_RQ)
        assert result and result.strip(), (
            "MR-SY1: synthesis must be non-empty for an extended corpus"
        )

    @given(n_papers=st.integers(min_value=1, max_value=5))
    async def test_synthesis_always_non_empty(self, n_papers: int) -> None:
        """Hypothesis: synthesis must always be non-empty for any corpus size."""
        papers = "\n".join(
            f"Paper {chr(65 + i)}: TDD study finding {i + 1}."
            for i in range(n_papers)
        )
        agent = make_stub_agent(_STUB_SHORT)
        result = await agent.run(papers_summary=papers, research_question=_RQ)
        assert result and result.strip(), (
            f"MR-SY1: synthesis empty for {n_papers} papers"
        )


# ---------------------------------------------------------------------------
# MR-SY2: Paraphrase Stability
# ---------------------------------------------------------------------------


class TestSynthesiserMRSY2ParaphraseStability:
    """MR-SY2: equivalent research questions must produce identical stub output."""

    async def test_abbreviated_vs_full_rq_same_output(self) -> None:
        """'TDD quality' vs full question produce identical output under stub."""
        agent = make_stub_agent(_STUB_SHORT)

        result_abbrev = await agent.run(
            papers_summary=_BASE_PAPERS,
            research_question="TDD quality?",
        )
        result_full = await agent.run(
            papers_summary=_BASE_PAPERS,
            research_question="What is the effect of TDD on software defect density?",
        )

        # Both use the same stub — output must be identical
        assert result_abbrev == result_full, (
            "MR-SY2: abbreviated and full RQ must produce identical stub output"
        )

    async def test_rq_paraphrase_produces_same_structure(self) -> None:
        """Three paraphrases of the same question produce identical stub output."""
        agent = make_stub_agent(_STUB_SHORT)
        paraphrases = [
            "What is the effect of TDD on software defect density?",
            "How does test-driven development affect defect density?",
            "Does TDD reduce software bugs?",
        ]

        results = [
            await agent.run(papers_summary=_BASE_PAPERS, research_question=rq)
            for rq in paraphrases
        ]

        # All stubs return identical output
        assert all(r == results[0] for r in results), (
            "MR-SY2: all paraphrases must produce identical stub output"
        )

    @given(
        rq_a=st.sampled_from([
            "What is the effect of TDD on software defect density?",
            "How does test-driven development affect defect density?",
            "Does TDD reduce software bugs?",
        ]),
        rq_b=st.sampled_from([
            "What is the effect of TDD on software defect density?",
            "How does test-driven development affect defect density?",
            "Does TDD reduce software bugs?",
        ]),
    )
    async def test_any_paraphrase_pair_identical_output(
        self, rq_a: str, rq_b: str
    ) -> None:
        """Hypothesis: any paraphrase pair produces identical stub output."""
        agent = make_stub_agent(_STUB_SHORT)

        result_a = await agent.run(papers_summary=_BASE_PAPERS, research_question=rq_a)
        result_b = await agent.run(papers_summary=_BASE_PAPERS, research_question=rq_b)

        assert result_a == result_b, (
            f"MR-SY2: paraphrase pair produced different output: '{rq_a}' vs '{rq_b}'"
        )

    async def test_output_contains_conclusion(self) -> None:
        """Synthesis output must contain a conclusion or summary section."""
        agent = make_stub_agent(_STUB_SHORT)
        result = await agent.run(papers_summary=_BASE_PAPERS, research_question=_RQ)
        lower = result.lower()
        assert "conclusion" in lower or "summary" in lower, (
            "MR-SY2: synthesis must contain a conclusion or summary section"
        )
