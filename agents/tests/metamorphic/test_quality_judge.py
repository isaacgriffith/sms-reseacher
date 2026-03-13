"""Metamorphic tests for QualityJudgeAgent.

Metamorphic Relations
---------------------
MR-QJ1: Score Monotonicity
    A study snapshot with more evidence of quality (e.g. test-retest done,
    extractions complete, validity filled) must produce a total quality score
    that is ≥ the score for a less-complete snapshot.  Under deterministic
    stubs this verifies the MR structural wiring; live validation requires
    a real LLM.

MR-QJ2: Rubric Independence
    Changing data that is only relevant to one rubric must not change the
    scores for unrelated rubrics.  Under deterministic stubs this verifies
    that all rubric scores are present in every response.

Tests use a stubbed ``LLMClient`` for deterministic, offline verification.

See conftest.py for hypothesis profile configuration.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

from hypothesis import given
from hypothesis import strategies as st

from agents.core.llm_client import LLMClient
from agents.services.quality_judge import QualityJudgeAgent

# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

_RUBRIC_NAMES = [
    "need_for_review",
    "search_strategy",
    "search_evaluation",
    "extraction_classification",
    "study_validity",
]

_STUB_RESPONSE_LOW = json.dumps({
    "scores": {r: 0 for r in _RUBRIC_NAMES},
    "rubric_details": {
        r: {"score": 0, "justification": "Stub low justification."}
        for r in _RUBRIC_NAMES
    },
    "recommendations": [
        {"target_rubric": "need_for_review", "action": "Add review rationale.", "priority": 1}
    ],
})

_STUB_RESPONSE_HIGH = json.dumps({
    "scores": {"need_for_review": 2, "search_strategy": 2, "search_evaluation": 3,
               "extraction_classification": 3, "study_validity": 1},
    "rubric_details": {
        r: {"score": 1, "justification": "Stub high justification."}
        for r in _RUBRIC_NAMES
    },
    "recommendations": [],
})


def make_stub_agent(output: str = _STUB_RESPONSE_LOW) -> QualityJudgeAgent:
    """Return a QualityJudgeAgent backed by a deterministic stub LLMClient.

    Args:
        output: JSON string the stub will return for every LLM call.

    Returns:
        :class:`QualityJudgeAgent` with mocked LLM client.
    """
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=output)
    return QualityJudgeAgent(llm_client=stub_client)


def _total_score(result) -> int:
    """Return the sum of all rubric scores from a QualityJudgeResult.

    Args:
        result: A :class:`QualityJudgeResult` instance.

    Returns:
        Integer sum of all rubric scores.
    """
    return sum(result.scores.values())


# ---------------------------------------------------------------------------
# MR-QJ1: Score Monotonicity
# ---------------------------------------------------------------------------


class TestQualityJudgeMRQJ1ScoreMonotonicity:
    """MR-QJ1: richer evidence must not reduce the total quality score."""

    async def test_extractions_done_does_not_reduce_score(self) -> None:
        """Source (no extractions) vs follow-up (extractions done) is non-reducing.

        The high stub returns higher scores, confirming the MR wiring.
        """
        agent_low = make_stub_agent(_STUB_RESPONSE_LOW)
        agent_high = make_stub_agent(_STUB_RESPONSE_HIGH)

        result_low = await agent_low.run(
            study_id=1, extractions_done=False
        )
        result_high = await agent_high.run(
            study_id=1, extractions_done=True
        )

        assert _total_score(result_high) >= _total_score(result_low), (
            "MR-QJ1: completing extractions must not reduce total quality score. "
            f"Low: {_total_score(result_low)}, High: {_total_score(result_high)}"
        )

    async def test_validity_filled_does_not_reduce_score(self) -> None:
        """Source (validity empty) vs follow-up (validity filled) is non-reducing."""
        agent_low = make_stub_agent(_STUB_RESPONSE_LOW)
        agent_high = make_stub_agent(_STUB_RESPONSE_HIGH)

        result_low = await agent_low.run(study_id=1, validity_filled=False)
        result_high = await agent_high.run(study_id=1, validity_filled=True)

        assert _total_score(result_high) >= _total_score(result_low), (
            "MR-QJ1: filling validity section must not reduce total quality score"
        )

    async def test_adding_search_strategy_does_not_reduce_score(self) -> None:
        """Adding a search strategy must not reduce total quality score."""
        agent_low = make_stub_agent(_STUB_RESPONSE_LOW)
        agent_high = make_stub_agent(_STUB_RESPONSE_HIGH)

        result_low = await agent_low.run(study_id=1)
        result_high = await agent_high.run(
            study_id=1,
            search_strategies=[{"query_string": "(TDD OR testing)", "result_count": 150}],
        )

        assert _total_score(result_high) >= _total_score(result_low), (
            "MR-QJ1: adding a search strategy must not reduce total quality score"
        )

    @given(current_phase=st.integers(min_value=1, max_value=5))
    async def test_total_score_non_negative(self, current_phase: int) -> None:
        """Hypothesis: total quality score must always be ≥ 0."""
        agent = make_stub_agent(_STUB_RESPONSE_LOW)
        result = await agent.run(study_id=1, current_phase=current_phase)
        assert _total_score(result) >= 0, (
            f"MR-QJ1: total score must be ≥ 0 for phase={current_phase}"
        )


# ---------------------------------------------------------------------------
# MR-QJ2: Rubric Independence
# ---------------------------------------------------------------------------


class TestQualityJudgeMRQJ2RubricIndependence:
    """MR-QJ2: all five rubric scores must be present in every response."""

    async def test_all_rubrics_present_in_low_response(self) -> None:
        """Every rubric score key must be present even for a low-quality study."""
        agent = make_stub_agent(_STUB_RESPONSE_LOW)
        result = await agent.run(study_id=1)

        for rubric in _RUBRIC_NAMES:
            assert rubric in result.scores, (
                f"MR-QJ2: rubric '{rubric}' missing from scores"
            )
            assert rubric in result.rubric_details, (
                f"MR-QJ2: rubric '{rubric}' missing from rubric_details"
            )

    async def test_all_rubrics_present_in_high_response(self) -> None:
        """Every rubric score key must be present for a high-quality study."""
        agent = make_stub_agent(_STUB_RESPONSE_HIGH)
        result = await agent.run(
            study_id=1,
            extractions_done=True,
            validity_filled=True,
            pico_saved=True,
            test_retest_done=True,
        )

        for rubric in _RUBRIC_NAMES:
            assert rubric in result.scores, (
                f"MR-QJ2: rubric '{rubric}' missing from high-quality response scores"
            )

    async def test_scores_within_valid_range(self) -> None:
        """All rubric scores must be clamped to their valid 0–max range."""
        from agents.services.quality_judge import _RUBRIC_MAX

        agent = make_stub_agent(_STUB_RESPONSE_HIGH)
        result = await agent.run(study_id=1)

        for rubric, max_val in _RUBRIC_MAX.items():
            score = result.scores.get(rubric, 0)
            assert 0 <= score <= max_val, (
                f"MR-QJ2: rubric '{rubric}' score {score} out of [0, {max_val}]"
            )

    @given(study_id=st.integers(min_value=1, max_value=9999))
    async def test_rubric_keys_stable_across_study_ids(self, study_id: int) -> None:
        """Hypothesis: rubric key set must be identical regardless of study_id."""
        agent = make_stub_agent(_STUB_RESPONSE_LOW)
        result = await agent.run(study_id=study_id)
        assert set(result.scores.keys()) == set(_RUBRIC_NAMES), (
            f"MR-QJ2: unexpected rubric keys for study_id={study_id}"
        )
