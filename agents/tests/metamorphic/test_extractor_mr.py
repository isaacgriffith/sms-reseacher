"""Metamorphic tests for the ExtractorAgent.

Metamorphic Relation (MR-E1): Field-Order Permutation
------------------------------------------------------
Permuting the order of requested data fields must not change the
extracted values for each field.  The agent should extract the same
data regardless of the order fields are presented in the prompt.

Tests use a deterministic stub LLM to validate MR structure.

Note: GeMTest (https://github.com/tum-i4/gemtest) is a documented
alternative for automated MR composition.
"""

import itertools
from unittest.mock import AsyncMock, MagicMock

import pytest
from hypothesis import given
from hypothesis import strategies as st

from agents.core.llm_client import LLMClient
from agents.services.extractor import ExtractorAgent

PAPER_TEXT = (
    "We conducted a controlled experiment with 42 Python developers. "
    "The study used the TDD method and found a 15% improvement in defect density."
)

FIELDS = ["research_method", "sample_size", "programming_language"]
STUB_RESPONSE = '{"research_method": "controlled experiment", "sample_size": 42, "programming_language": "Python"}'


def make_stub_agent() -> ExtractorAgent:
    """Return an ExtractorAgent backed by a deterministic stub."""
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=STUB_RESPONSE)
    return ExtractorAgent(llm_client=stub_client)


class TestExtractorMR:
    """MR-E1: Field-order permutation preserves extracted values."""

    @pytest.mark.parametrize("fields_order", list(itertools.permutations(FIELDS)))
    async def test_field_order_permutation_same_response(
        self, fields_order: tuple[str, ...]
    ) -> None:
        """Stub returns identical JSON regardless of field order (MR structure test)."""
        agent = make_stub_agent()
        fields_str = ", ".join(fields_order)
        result = await agent.run(fields_str, PAPER_TEXT)
        assert result == STUB_RESPONSE

    @given(
        fields=st.lists(
            st.sampled_from(FIELDS),
            min_size=2,
            max_size=len(FIELDS),
            unique=True,
        )
    )
    async def test_field_order_hypothesis(self, fields: list[str]) -> None:
        """Hypothesis: any ordering of fields produces identical stub output."""
        agent = make_stub_agent()
        result = await agent.run(", ".join(fields), PAPER_TEXT)
        assert result == STUB_RESPONSE

    async def test_single_field_extraction(self) -> None:
        """Single-field extraction still returns a valid response."""
        agent = make_stub_agent()
        result = await agent.run("research_method", PAPER_TEXT)
        assert result  # non-empty
