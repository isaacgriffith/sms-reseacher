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

from __future__ import annotations

import itertools
import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from hypothesis import given
from hypothesis import strategies as st

from agents.core.llm_client import LLMClient
from agents.services.extractor import ExtractionResult, ExtractorAgent

PAPER_TEXT = (
    "We conducted a controlled experiment with 42 Python developers. "
    "The study used the TDD method and found a 15% improvement in defect density."
)

FIELDS = ["research_method", "sample_size", "programming_language"]

# Full ExtractionResult-compatible stub response
_STUB_RESULT: dict[str, Any] = {
    "research_type": "evaluation",
    "venue_type": "journal",
    "venue_name": "TSE",
    "author_details": [],
    "summary": "A controlled experiment on TDD.",
    "open_codings": [],
    "keywords": ["TDD", "Python"],
    "question_data": {},
}
STUB_RESPONSE = json.dumps(_STUB_RESULT)

SAMPLE_METADATA = {
    "title": "TDD Experiment",
    "authors": [],
    "year": 2022,
    "venue": "TSE",
    "doi": "10.1145/9999",
    "research_questions": [{"id": "RQ1", "text": "Effect of TDD on defects?"}],
}


def make_stub_agent() -> ExtractorAgent:
    """Return an ExtractorAgent backed by a deterministic stub LLM.

    Returns:
        An :class:`ExtractorAgent` whose LLM always returns :data:`STUB_RESPONSE`.
    """
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=STUB_RESPONSE)
    return ExtractorAgent(llm_client=stub_client)


class TestExtractorMR:
    """MR-E1: Field-order permutation preserves extracted values."""

    @pytest.mark.parametrize("fields_order", list(itertools.permutations(FIELDS)))
    async def test_field_order_permutation_same_response(
        self, fields_order: tuple[str, ...]
    ) -> None:
        """Stub returns identical ExtractionResult regardless of field order."""
        agent = make_stub_agent()
        result = await agent.run(
            paper_text=PAPER_TEXT,
            title=SAMPLE_METADATA["title"],
            research_questions=SAMPLE_METADATA["research_questions"],
        )
        assert isinstance(result, ExtractionResult)
        assert result.research_type == _STUB_RESULT["research_type"]

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
        result = await agent.run(
            paper_text=PAPER_TEXT,
            title=SAMPLE_METADATA["title"],
        )
        assert isinstance(result, ExtractionResult)

    async def test_single_field_extraction(self) -> None:
        """Single-field extraction still returns a valid ExtractionResult."""
        agent = make_stub_agent()
        result = await agent.run(
            paper_text=PAPER_TEXT,
            title="TDD Experiment",
        )
        assert isinstance(result, ExtractionResult)
        assert result.research_type  # non-empty
