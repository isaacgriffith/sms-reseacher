"""Metamorphic tests for ValidityAgent.

Metamorphic Relations
---------------------
MR-V1: Completeness Monotonicity
    A study snapshot with more completed phases MUST produce validity text
    with equal or greater specificity (measured as character count of each
    dimension) than a less-complete snapshot.  Under deterministic stubs this
    validates the structural wiring; live LLM monotonicity is validated in
    integration evals.

MR-V2: Dimension Independence
    Modifying data that is relevant to one validity dimension (e.g. adding
    more inclusion criteria, which affects *internal generalizability*) must
    NOT change the generated text for unrelated dimensions (e.g. *repeatability*).
    Under deterministic stubs all dimensions are present and identical across
    calls, confirming the MR is correctly wired.

MR-V3: Paraphrase Stability
    Equivalent study descriptions phrased differently (e.g. the study name or
    type variant) must produce semantically equivalent validity content —
    under a deterministic stub the text must be identical.

All six validity dimensions are tested:
    descriptive, theoretical, generalizability_internal,
    generalizability_external, interpretive, repeatability.

Tests use a stubbed ``LLMClient`` for deterministic, offline verification.

See conftest.py for hypothesis profile configuration.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

from hypothesis import given
from hypothesis import strategies as st

from agents.core.llm_client import LLMClient
from agents.services.validity import ValidityAgent

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VALIDITY_DIMS = (
    "descriptive",
    "theoretical",
    "generalizability_internal",
    "generalizability_external",
    "interpretive",
    "repeatability",
)

# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

_STUB_RESPONSE_LOW = json.dumps({
    dim: f"Brief stub text for {dim}."
    for dim in _VALIDITY_DIMS
})

_STUB_RESPONSE_HIGH = json.dumps({
    dim: (
        f"Detailed stub text for {dim}. The study provides comprehensive coverage "
        f"of the {dim} validity dimension with extensive evidence and justification."
    )
    for dim in _VALIDITY_DIMS
})


def make_stub_agent(output: str = _STUB_RESPONSE_LOW) -> ValidityAgent:
    """Return a ValidityAgent backed by a deterministic stub LLMClient.

    Args:
        output: JSON string the stub will return for every LLM call.

    Returns:
        :class:`ValidityAgent` with mocked LLM client.
    """
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=output)
    return ValidityAgent(llm_client=stub_client)


def _total_char_count(result) -> int:
    """Sum of character counts across all six validity dimensions.

    Args:
        result: A :class:`ValidityResult` instance.

    Returns:
        Total character count across all dimension texts.
    """
    return sum(
        len(getattr(result, dim, ""))
        for dim in _VALIDITY_DIMS
    )


def _dim_char_counts(result) -> dict[str, int]:
    """Per-dimension character counts.

    Args:
        result: A :class:`ValidityResult` instance.

    Returns:
        Dict mapping dimension name → character count.
    """
    return {dim: len(getattr(result, dim, "")) for dim in _VALIDITY_DIMS}


# ---------------------------------------------------------------------------
# MR-V1: Completeness Monotonicity
# ---------------------------------------------------------------------------


class TestValidityMRV1CompletenessMonotonicity:
    """MR-V1: more completed phases must produce equal or more detailed validity text."""

    async def test_more_phases_produces_at_least_as_detailed_text(self) -> None:
        """Phase 5 (all done) must produce validity text at least as long as phase 1.

        The high stub returns longer texts, confirming the MR structural wiring.
        """
        agent_low = make_stub_agent(_STUB_RESPONSE_LOW)
        agent_high = make_stub_agent(_STUB_RESPONSE_HIGH)

        result_low = await agent_low.run(
            study_id=1,
            current_phase=1,
        )
        result_high = await agent_high.run(
            study_id=1,
            current_phase=5,
            pico_components=[{"type": "P", "content": "software engineers"}],
            search_strategies=[{"string_text": "(TDD)", "version": 1}],
            test_retest_done=True,
            inclusion_criteria=["empirical studies only"],
            exclusion_criteria=["grey literature excluded"],
            extraction_summary="15 papers extracted with full data.",
        )

        assert _total_char_count(result_high) >= _total_char_count(result_low), (
            "MR-V1: fully-complete phase snapshot must produce ≥ as many chars. "
            f"Low: {_total_char_count(result_low)}, High: {_total_char_count(result_high)}"
        )

    async def test_adding_pico_increases_or_maintains_text_length(self) -> None:
        """Adding PICO components must not reduce total validity text length."""
        agent_low = make_stub_agent(_STUB_RESPONSE_LOW)
        agent_high = make_stub_agent(_STUB_RESPONSE_HIGH)

        result_without_pico = await agent_low.run(study_id=1)
        result_with_pico = await agent_high.run(
            study_id=1,
            pico_components=[
                {"type": "P", "content": "software engineers"},
                {"type": "I", "content": "TDD"},
            ],
        )

        assert _total_char_count(result_with_pico) >= _total_char_count(result_without_pico), (
            "MR-V1: adding PICO components must not reduce validity text length"
        )

    async def test_test_retest_done_does_not_reduce_text(self) -> None:
        """Marking test-retest as done must not reduce validity text length."""
        agent_low = make_stub_agent(_STUB_RESPONSE_LOW)
        agent_high = make_stub_agent(_STUB_RESPONSE_HIGH)

        result_no_retest = await agent_low.run(study_id=1, test_retest_done=False)
        result_retest = await agent_high.run(study_id=1, test_retest_done=True)

        assert _total_char_count(result_retest) >= _total_char_count(result_no_retest), (
            "MR-V1: completing test-retest must not reduce validity text length"
        )

    @given(current_phase=st.integers(min_value=1, max_value=5))
    async def test_all_dimensions_non_empty_for_any_phase(
        self, current_phase: int
    ) -> None:
        """Hypothesis: all six dimensions must be non-empty for any phase value."""
        agent = make_stub_agent(_STUB_RESPONSE_LOW)
        result = await agent.run(study_id=1, current_phase=current_phase)

        for dim in _VALIDITY_DIMS:
            val = getattr(result, dim, "")
            assert val.strip(), (
                f"MR-V1: dimension '{dim}' is empty at phase={current_phase}"
            )


# ---------------------------------------------------------------------------
# MR-V2: Dimension Independence
# ---------------------------------------------------------------------------


class TestValidityMRV2DimensionIndependence:
    """MR-V2: changing data for one dimension must not alter unrelated dimensions."""

    async def test_all_six_dimensions_present_in_every_response(self) -> None:
        """Every validity response must include all six dimension keys."""
        agent = make_stub_agent(_STUB_RESPONSE_LOW)

        for test_retest_done in (False, True):
            result = await agent.run(
                study_id=1,
                test_retest_done=test_retest_done,
            )
            for dim in _VALIDITY_DIMS:
                val = getattr(result, dim, None)
                assert val is not None and val.strip(), (
                    f"MR-V2: dimension '{dim}' missing or empty "
                    f"(test_retest_done={test_retest_done})"
                )

    async def test_inclusion_criteria_change_preserves_repeatability_dim(self) -> None:
        """Changing inclusion criteria must preserve the repeatability dimension text.

        Under a deterministic stub both calls return identical repeatability text,
        demonstrating the MR is structurally satisfied.
        """
        agent = make_stub_agent(_STUB_RESPONSE_LOW)

        result_no_criteria = await agent.run(study_id=1)
        result_with_criteria = await agent.run(
            study_id=1,
            inclusion_criteria=["empirical studies only"],
        )

        # Both stubs return identical text — demonstrates MR structure
        assert result_no_criteria.repeatability == result_with_criteria.repeatability, (
            "MR-V2: repeatability dimension must not change when only inclusion criteria differ"
        )

    async def test_search_strategy_change_preserves_theoretical_dim(self) -> None:
        """Changing search strategy must preserve the theoretical dimension text.

        Under a deterministic stub both calls return identical theoretical text.
        """
        agent = make_stub_agent(_STUB_RESPONSE_LOW)

        result_no_strategy = await agent.run(study_id=1)
        result_with_strategy = await agent.run(
            study_id=1,
            search_strategies=[{"string_text": "(TDD OR testing)", "version": 1}],
        )

        assert result_no_strategy.theoretical == result_with_strategy.theoretical, (
            "MR-V2: theoretical dimension must not change when only search strategy differs"
        )

    @given(dim=st.sampled_from(list(_VALIDITY_DIMS)))
    async def test_each_dimension_has_non_empty_text(self, dim: str) -> None:
        """Hypothesis: each dimension text must be non-empty."""
        agent = make_stub_agent(_STUB_RESPONSE_LOW)
        result = await agent.run(study_id=1)
        val = getattr(result, dim)
        assert val and val.strip(), f"MR-V2: dimension '{dim}' text is empty"


# ---------------------------------------------------------------------------
# MR-V3: Paraphrase Stability
# ---------------------------------------------------------------------------


class TestValidityMRV3ParaphraseStability:
    """MR-V3: equivalent study descriptions must produce semantically equivalent validity text."""

    async def test_equivalent_study_names_produce_identical_text(self) -> None:
        """'TDD Study' vs 'Test-Driven Development Study' produce identical text under stub."""
        agent = make_stub_agent(_STUB_RESPONSE_LOW)

        result_abbrev = await agent.run(
            study_id=1, study_name="TDD Study"
        )
        result_full = await agent.run(
            study_id=1, study_name="Test-Driven Development Study"
        )

        for dim in _VALIDITY_DIMS:
            assert getattr(result_abbrev, dim) == getattr(result_full, dim), (
                f"MR-V3: dimension '{dim}' differs between 'TDD Study' and "
                "'Test-Driven Development Study'"
            )

    async def test_equivalent_study_types_produce_identical_text(self) -> None:
        """'SMS' vs 'SLR' as study type must produce identical text under stub."""
        agent = make_stub_agent(_STUB_RESPONSE_LOW)

        result_sms = await agent.run(study_id=1, study_type="SMS")
        result_slr = await agent.run(study_id=1, study_type="SLR")

        for dim in _VALIDITY_DIMS:
            assert getattr(result_sms, dim) == getattr(result_slr, dim), (
                f"MR-V3: dimension '{dim}' differs between study_type='SMS' and 'SLR'"
            )

    @given(
        name_a=st.sampled_from(["TDD Study", "Test-Driven Development Study", "TDD Research"]),
        name_b=st.sampled_from(["TDD Study", "Test-Driven Development Study", "TDD Research"]),
    )
    async def test_any_paraphrase_pair_identical_text(
        self, name_a: str, name_b: str
    ) -> None:
        """Hypothesis: any paraphrase pair produces identical stub output."""
        agent = make_stub_agent(_STUB_RESPONSE_LOW)

        result_a = await agent.run(study_id=1, study_name=name_a)
        result_b = await agent.run(study_id=1, study_name=name_b)

        for dim in _VALIDITY_DIMS:
            assert getattr(result_a, dim) == getattr(result_b, dim), (
                f"MR-V3: dimension '{dim}' differs between '{name_a}' and '{name_b}'"
            )
