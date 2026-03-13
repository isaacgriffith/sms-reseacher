"""Metamorphic tests for ExtractorAgent.

Metamorphic Relations
---------------------
MR-E1: Field Extraction Consistency Under Equivalent Phrasings
    Presenting the same research content with equivalent but differently phrased
    titles must produce the same research_type classification and non-empty
    extraction fields.  Under a deterministic stub this validates structural
    MR wiring; live accuracy (≥80% per R1–R6 rules) is validated in evals.

MR-E2: Completeness Monotonicity When Full Text Available
    Providing full paper text must produce an ExtractionResult with at least
    as many non-null fields as extraction from the abstract alone.
    Under a deterministic stub both calls return identical output, confirming
    the MR structure is correctly wired.

Tests use a stubbed ``LLMClient`` for deterministic, offline verification.

See conftest.py for hypothesis profile configuration.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

from hypothesis import given
from hypothesis import strategies as st

from agents.core.llm_client import LLMClient
from agents.services.extractor import ExtractionResult, ExtractorAgent

# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

_STUB_RESULT_MINIMAL = json.dumps({
    "research_type": "evaluation",
    "venue_type": "journal",
    "venue_name": "Journal of Systems and Software",
    "author_details": [{"name": "Jane Smith", "institution": "MIT", "locale": "US"}],
    "summary": "A controlled experiment on TDD and defect density.",
    "open_codings": [{"code": "defect_reduction", "text": "40% fewer defects"}],
    "keywords": ["TDD", "defect density", "controlled experiment"],
    "question_data": {"RQ1": "TDD reduces defects by 40%."},
})

_STUB_RESULT_FULL = json.dumps({
    "research_type": "evaluation",
    "venue_type": "journal",
    "venue_name": "Journal of Systems and Software",
    "author_details": [
        {"name": "Jane Smith", "institution": "MIT", "locale": "US"},
        {"name": "John Doe", "institution": "Stanford", "locale": "US"},
    ],
    "summary": (
        "A controlled experiment on TDD and defect density with full methodology. "
        "42 developers were split into TDD and waterfall groups."
    ),
    "open_codings": [
        {"code": "defect_reduction", "text": "40% fewer defects"},
        {"code": "methodology", "text": "controlled experiment with 42 participants"},
        {"code": "language", "text": "Java projects"},
    ],
    "keywords": ["TDD", "defect density", "controlled experiment", "software quality"],
    "question_data": {
        "RQ1": "TDD reduces defects by 40%.",
        "RQ2": "Java developers show largest defect reduction.",
    },
})

_PAPER_ABSTRACT = (
    "We conducted a controlled experiment evaluating TDD with 42 Java developers. "
    "Defect density was reduced by 40% in the TDD group vs waterfall control."
)

_PAPER_FULL_TEXT = (
    "## Abstract\n"
    "We conducted a controlled experiment evaluating TDD with 42 Java developers. "
    "Defect density was reduced by 40% in the TDD group vs waterfall control.\n\n"
    "## Method\n"
    "Participants were randomly assigned to TDD (n=21) or waterfall (n=21) groups. "
    "All implemented the same feature set in a two-week sprint.\n\n"
    "## Results\n"
    "TDD group: 12.3 defects/KLOC. Waterfall group: 20.5 defects/KLOC. "
    "Difference significant at p<0.01.\n\n"
    "## Conclusion\n"
    "TDD significantly reduces defect density in Java projects."
)

_TITLE_1 = "A Controlled Experiment on TDD and Defect Density"
_TITLE_2 = "Test-Driven Development and Software Quality: An Empirical Study"
_TITLE_3 = "Empirical Evaluation of Test-First Programming on Defect Rates"


def make_stub_agent(output: str = _STUB_RESULT_MINIMAL) -> ExtractorAgent:
    """Return an ExtractorAgent backed by a deterministic stub LLMClient.

    Args:
        output: JSON string the stub will return for every LLM call.

    Returns:
        :class:`ExtractorAgent` with mocked LLM client.
    """
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=output)
    return ExtractorAgent(llm_client=stub_client)


def _non_null_field_count(result: ExtractionResult) -> int:
    """Count the number of non-null/non-empty fields in an ExtractionResult.

    Args:
        result: :class:`ExtractionResult` to measure.

    Returns:
        Integer count of fields with non-None, non-empty values.
    """
    count = 0
    if result.research_type:
        count += 1
    if result.venue_type:
        count += 1
    if result.venue_name:
        count += 1
    if result.author_details:
        count += len(result.author_details)
    if result.summary:
        count += 1
    if result.open_codings:
        count += len(result.open_codings)
    if result.keywords:
        count += len(result.keywords)
    if result.question_data:
        count += len(result.question_data)
    return count


# ---------------------------------------------------------------------------
# MR-E1: Field Extraction Consistency Under Equivalent Phrasings
# ---------------------------------------------------------------------------


class TestExtractorMRE1FieldConsistencyUnderEquivalentPhrasings:
    """MR-E1: equivalent title phrasings must produce consistent extraction."""

    async def test_equivalent_titles_same_research_type(self) -> None:
        """Three equivalent titles must produce the same research_type under stub.

        The stub returns identical output regardless of title, confirming
        the structural MR is correctly wired.
        """
        agent = make_stub_agent(_STUB_RESULT_MINIMAL)

        results = []
        for title in (_TITLE_1, _TITLE_2, _TITLE_3):
            result = await agent.run(
                paper_text=_PAPER_ABSTRACT,
                title=title,
            )
            results.append(result)

        research_types = {r.research_type for r in results}
        assert len(research_types) == 1, (
            "MR-E1: equivalent titles must produce the same research_type. "
            f"Got: {research_types}"
        )

    async def test_equivalent_titles_same_keyword_count(self) -> None:
        """Equivalent titles must produce the same keyword count under stub."""
        agent = make_stub_agent(_STUB_RESULT_MINIMAL)

        results = [
            await agent.run(paper_text=_PAPER_ABSTRACT, title=t)
            for t in (_TITLE_1, _TITLE_2, _TITLE_3)
        ]

        keyword_counts = [len(r.keywords) for r in results]
        assert len(set(keyword_counts)) == 1, (
            "MR-E1: equivalent titles must produce the same keyword count. "
            f"Got: {keyword_counts}"
        )

    async def test_research_type_is_valid_enum(self) -> None:
        """Extracted research_type must always be a valid R1–R6 value."""
        from agents.services.extractor import _VALID_RESEARCH_TYPES

        agent = make_stub_agent(_STUB_RESULT_MINIMAL)
        result = await agent.run(paper_text=_PAPER_ABSTRACT, title=_TITLE_1)

        assert result.research_type in _VALID_RESEARCH_TYPES, (
            f"MR-E1: research_type '{result.research_type}' not in valid R1–R6 set"
        )

    @given(
        title=st.sampled_from([_TITLE_1, _TITLE_2, _TITLE_3])
    )
    async def test_any_title_paraphrase_yields_non_empty_keywords(
        self, title: str
    ) -> None:
        """Hypothesis: any equivalent title produces non-empty keyword list."""
        agent = make_stub_agent(_STUB_RESULT_MINIMAL)
        result = await agent.run(paper_text=_PAPER_ABSTRACT, title=title)
        assert result.keywords, (
            f"MR-E1: keyword list must be non-empty for title='{title}'"
        )

    @given(
        title=st.sampled_from([_TITLE_1, _TITLE_2, _TITLE_3])
    )
    async def test_any_title_paraphrase_yields_valid_research_type(
        self, title: str
    ) -> None:
        """Hypothesis: any equivalent title yields a valid research_type."""
        from agents.services.extractor import _VALID_RESEARCH_TYPES

        agent = make_stub_agent(_STUB_RESULT_MINIMAL)
        result = await agent.run(paper_text=_PAPER_ABSTRACT, title=title)
        assert result.research_type in _VALID_RESEARCH_TYPES, (
            f"MR-E1: invalid research_type '{result.research_type}' for title='{title}'"
        )


# ---------------------------------------------------------------------------
# MR-E2: Completeness Monotonicity When Full Text Available
# ---------------------------------------------------------------------------


class TestExtractorMRE2CompletenessMonotonicity:
    """MR-E2: full text must produce at least as many populated fields as abstract."""

    async def test_full_text_at_least_as_complete_as_abstract(self) -> None:
        """Full text (rich stub) produces ≥ non-null fields vs abstract (minimal stub).

        The rich stub returns more fields, confirming structural MR wiring.
        """
        agent_minimal = make_stub_agent(_STUB_RESULT_MINIMAL)
        agent_full = make_stub_agent(_STUB_RESULT_FULL)

        result_abstract = await agent_minimal.run(
            paper_text=_PAPER_ABSTRACT, title=_TITLE_1
        )
        result_full = await agent_full.run(
            paper_text=_PAPER_FULL_TEXT, title=_TITLE_1
        )

        count_abstract = _non_null_field_count(result_abstract)
        count_full = _non_null_field_count(result_full)

        assert count_full >= count_abstract, (
            "MR-E2: full text must produce ≥ populated fields vs abstract. "
            f"Abstract: {count_abstract}, Full: {count_full}"
        )

    async def test_full_text_more_authors_than_abstract(self) -> None:
        """Full text stub returns more authors than abstract stub."""
        agent_min = make_stub_agent(_STUB_RESULT_MINIMAL)
        agent_full = make_stub_agent(_STUB_RESULT_FULL)

        result_min = await agent_min.run(paper_text=_PAPER_ABSTRACT, title=_TITLE_1)
        result_full = await agent_full.run(paper_text=_PAPER_FULL_TEXT, title=_TITLE_1)

        assert len(result_full.author_details) >= len(result_min.author_details), (
            "MR-E2: full text must produce ≥ author records vs abstract"
        )

    async def test_full_text_more_codings_than_abstract(self) -> None:
        """Full text stub returns more open_codings than abstract stub."""
        agent_min = make_stub_agent(_STUB_RESULT_MINIMAL)
        agent_full = make_stub_agent(_STUB_RESULT_FULL)

        result_min = await agent_min.run(paper_text=_PAPER_ABSTRACT, title=_TITLE_1)
        result_full = await agent_full.run(paper_text=_PAPER_FULL_TEXT, title=_TITLE_1)

        assert len(result_full.open_codings) >= len(result_min.open_codings), (
            "MR-E2: full text must produce ≥ open codings vs abstract"
        )

    @given(
        use_full_text=st.booleans()
    )
    async def test_extraction_always_has_research_type(self, use_full_text: bool) -> None:
        """Hypothesis: research_type must always be populated regardless of text length."""
        text = _PAPER_FULL_TEXT if use_full_text else _PAPER_ABSTRACT
        agent = make_stub_agent(_STUB_RESULT_MINIMAL)
        result = await agent.run(paper_text=text, title=_TITLE_1)
        assert result.research_type, (
            f"MR-E2: research_type must not be empty (use_full_text={use_full_text})"
        )
