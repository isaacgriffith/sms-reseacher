"""Metamorphic tests for the SynthesiserAgent.

Metamorphic Relation (MR-SY1): Paper-Order Permutation
------------------------------------------------------
Permuting the order of paper summaries provided to the synthesiser
must produce semantically equivalent output.  In the unit form we
approximate this by verifying that a deterministic stub returns the
same response regardless of ordering — validating the MR structure.
Semantic equivalence of live LLM responses is validated in integration
tests using embedding-based similarity.

Note: GeMTest (https://github.com/tum-i4/gemtest) is a documented
alternative for automated MR composition.
"""

import itertools
from unittest.mock import AsyncMock, MagicMock

import pytest
from hypothesis import given
from hypothesis import strategies as st

from agents.core.llm_client import LLMClient
from agents.services.synthesiser import SynthesiserAgent

RESEARCH_QUESTION = "What is the effect of TDD on software quality?"

PAPERS = [
    "Paper A: TDD improves defect density by 15% in controlled experiments.",
    "Paper B: No significant quality improvement found with TDD in field studies.",
    "Paper C: TDD increases development time but reduces post-release defects.",
]

STUB_SYNTHESIS = (
    "## Summary\nTDD has mixed effects on software quality.\n\n"
    "## Key Findings\n- Defect density may improve.\n- Development time increases.\n\n"
    "## Contradictions / Gaps\nControlled vs field study results differ.\n\n"
    "## Conclusion\nFurther evidence is needed."
)


def make_stub_agent() -> SynthesiserAgent:
    """Return a SynthesiserAgent backed by a deterministic stub."""
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=STUB_SYNTHESIS)
    return SynthesiserAgent(llm_client=stub_client)


def join_papers(papers: list[str] | tuple[str, ...]) -> str:
    """Join paper summaries into a single newline-separated string."""
    return "\n".join(papers)


class TestSynthesiserMR:
    """MR-SY1: Paper-order permutation preserves synthesised output (stub)."""

    @pytest.mark.parametrize("order", list(itertools.permutations(range(len(PAPERS)))))
    async def test_paper_order_permutation(self, order: tuple[int, ...]) -> None:
        """Stub returns identical synthesis for any paper ordering."""
        agent = make_stub_agent()
        papers_str = join_papers([PAPERS[i] for i in order])
        result = await agent.run(papers_str, RESEARCH_QUESTION)
        assert result == STUB_SYNTHESIS

    @given(
        indices=st.permutations(list(range(len(PAPERS))))
    )
    async def test_paper_order_hypothesis(self, indices: list[int]) -> None:
        """Hypothesis: any permutation of paper indices produces stable stub output."""
        agent = make_stub_agent()
        papers_str = join_papers([PAPERS[i] for i in indices])
        result = await agent.run(papers_str, RESEARCH_QUESTION)
        assert result == STUB_SYNTHESIS

    async def test_single_paper_synthesis(self) -> None:
        """Synthesis works with a single paper summary."""
        agent = make_stub_agent()
        result = await agent.run(PAPERS[0], RESEARCH_QUESTION)
        assert result

    async def test_empty_papers_summary_runs(self) -> None:
        """Agent accepts an empty papers_summary without raising."""
        agent = make_stub_agent()
        result = await agent.run("", RESEARCH_QUESTION)
        assert isinstance(result, str)
