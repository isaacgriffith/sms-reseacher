"""Unit tests for QualityJudgeAgent.

Mocks LLMClient to verify:
- QualityJudgeResult is returned with all required fields
- Scores are within valid ranges per rubric (clamped)
- Recommendations list is non-empty when low scores present
- JSON parsing works with and without markdown fences
- Scores default to 0 for missing rubrics in LLM response
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.services.quality_judge import (
    QualityJudgeAgent,
    QualityJudgeResult,
    Recommendation,
    RubricDetail,
    _RUBRIC_MAX,
)

_RUBRIC_NAMES = list(_RUBRIC_MAX.keys())

_SNAPSHOT_KWARGS = {
    "study_id": 1,
    "study_name": "TDD Study",
    "study_type": "SMS",
    "current_phase": 3,
    "pico_saved": True,
    "search_strategies": [{"query_string": "TDD AND quality", "result_count": 150}],
    "test_retest_done": False,
    "reviewers": [{"reviewer_type": "human", "agent_name": None, "user_id": 1}],
    "inclusion_criteria": ["Empirical studies of TDD"],
    "exclusion_criteria": ["Grey literature"],
    "extractions_done": True,
    "validity_filled": False,
    "validity_dimensions": {"descriptive": "filled", "theoretical": ""},
}


def _make_client(response: str) -> MagicMock:
    """Return a mock LLMClient whose complete() coroutine returns *response*."""
    client = MagicMock()
    client.complete = AsyncMock(return_value=response)
    return client


def _json_response(
    scores: dict | None = None,
    rubric_details: dict | None = None,
    recommendations: list | None = None,
) -> str:
    """Return a minimal valid QualityJudge JSON string."""
    default_scores = {r: 1 for r in _RUBRIC_NAMES}
    if scores:
        default_scores.update(scores)

    default_details = {
        r: {"score": default_scores[r], "justification": f"Justification for {r}."}
        for r in _RUBRIC_NAMES
    }
    if rubric_details:
        default_details.update(rubric_details)

    default_recs = [
        {"priority": 1, "action": "Perform test-retest validation.", "target_rubric": "search_strategy"}
    ]

    return json.dumps({
        "scores": default_scores,
        "rubric_details": default_details,
        "recommendations": recommendations if recommendations is not None else default_recs,
    })


class TestQualityJudgeResultShape:
    """Verify QualityJudgeResult structure from mocked LLM output."""

    @pytest.mark.asyncio
    async def test_returns_quality_judge_result_type(self) -> None:
        """run() returns a QualityJudgeResult instance."""
        agent = QualityJudgeAgent(llm_client=_make_client(_json_response()))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert isinstance(result, QualityJudgeResult)

    @pytest.mark.asyncio
    async def test_has_scores_dict(self) -> None:
        """QualityJudgeResult.scores is a dict."""
        agent = QualityJudgeAgent(llm_client=_make_client(_json_response()))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert isinstance(result.scores, dict)

    @pytest.mark.asyncio
    async def test_has_rubric_details_dict(self) -> None:
        """QualityJudgeResult.rubric_details is a dict of RubricDetail objects."""
        agent = QualityJudgeAgent(llm_client=_make_client(_json_response()))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert isinstance(result.rubric_details, dict)
        for rubric, detail in result.rubric_details.items():
            assert isinstance(detail, RubricDetail)

    @pytest.mark.asyncio
    async def test_has_recommendations_list(self) -> None:
        """QualityJudgeResult.recommendations is a list."""
        agent = QualityJudgeAgent(llm_client=_make_client(_json_response()))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert isinstance(result.recommendations, list)

    @pytest.mark.asyncio
    async def test_recommendations_non_empty_for_low_scores(self) -> None:
        """Recommendations list is non-empty when low scores are present."""
        low_scores = {r: 0 for r in _RUBRIC_NAMES}
        recs = [
            {"priority": i + 1, "action": f"Fix {r}.", "target_rubric": r}
            for i, r in enumerate(_RUBRIC_NAMES)
        ]
        agent = QualityJudgeAgent(
            llm_client=_make_client(_json_response(scores=low_scores, recommendations=recs))
        )
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert len(result.recommendations) > 0


class TestScoreValidation:
    """Scores are clamped to the valid range for each rubric."""

    @pytest.mark.asyncio
    async def test_need_for_review_max_is_2(self) -> None:
        """score for need_for_review is clamped to 0–2."""
        over_scores = {"need_for_review": 99}
        agent = QualityJudgeAgent(llm_client=_make_client(_json_response(scores=over_scores)))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert result.scores.get("need_for_review", 0) <= 2

    @pytest.mark.asyncio
    async def test_search_strategy_max_is_2(self) -> None:
        """score for search_strategy is clamped to 0–2."""
        over_scores = {"search_strategy": 99}
        agent = QualityJudgeAgent(llm_client=_make_client(_json_response(scores=over_scores)))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert result.scores.get("search_strategy", 0) <= 2

    @pytest.mark.asyncio
    async def test_search_evaluation_max_is_3(self) -> None:
        """score for search_evaluation is clamped to 0–3."""
        over_scores = {"search_evaluation": 99}
        agent = QualityJudgeAgent(llm_client=_make_client(_json_response(scores=over_scores)))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert result.scores.get("search_evaluation", 0) <= 3

    @pytest.mark.asyncio
    async def test_extraction_classification_max_is_3(self) -> None:
        """score for extraction_classification is clamped to 0–3."""
        over_scores = {"extraction_classification": 99}
        agent = QualityJudgeAgent(llm_client=_make_client(_json_response(scores=over_scores)))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert result.scores.get("extraction_classification", 0) <= 3

    @pytest.mark.asyncio
    async def test_study_validity_max_is_1(self) -> None:
        """score for study_validity is clamped to 0–1."""
        over_scores = {"study_validity": 99}
        agent = QualityJudgeAgent(llm_client=_make_client(_json_response(scores=over_scores)))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert result.scores.get("study_validity", 0) <= 1

    @pytest.mark.asyncio
    async def test_scores_are_non_negative(self) -> None:
        """Negative scores from LLM are clamped to 0."""
        neg_scores = {r: -5 for r in _RUBRIC_NAMES}
        agent = QualityJudgeAgent(llm_client=_make_client(_json_response(scores=neg_scores)))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        for score in result.scores.values():
            assert score >= 0


class TestMarkdownFenceStripping:
    """JSON wrapped in markdown code fences is stripped before parsing."""

    @pytest.mark.asyncio
    async def test_strips_json_code_fence(self) -> None:
        """```json ... ``` fences are stripped and the payload parsed."""
        payload = _json_response()
        fenced = f"```json\n{payload}\n```"
        agent = QualityJudgeAgent(llm_client=_make_client(fenced))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert isinstance(result, QualityJudgeResult)

    @pytest.mark.asyncio
    async def test_strips_generic_code_fence(self) -> None:
        """Generic ``` fences without language tag are also stripped."""
        payload = _json_response()
        fenced = f"```\n{payload}\n```"
        agent = QualityJudgeAgent(llm_client=_make_client(fenced))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        assert isinstance(result, QualityJudgeResult)


class TestRubricDetails:
    """rubric_details contains score and justification for each rubric."""

    @pytest.mark.asyncio
    async def test_rubric_detail_has_score_and_justification(self) -> None:
        """Each rubric detail has a numeric score and non-empty justification."""
        agent = QualityJudgeAgent(llm_client=_make_client(_json_response()))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        for rubric, detail in result.rubric_details.items():
            assert isinstance(detail.score, int)
            assert isinstance(detail.justification, str)

    @pytest.mark.asyncio
    async def test_recommendation_has_required_fields(self) -> None:
        """Each recommendation has priority (int), action (str), and target_rubric (str)."""
        agent = QualityJudgeAgent(llm_client=_make_client(_json_response()))
        result = await agent.run(**_SNAPSHOT_KWARGS)
        for rec in result.recommendations:
            assert isinstance(rec, Recommendation)
            assert isinstance(rec.priority, int)
            assert isinstance(rec.action, str)
            assert isinstance(rec.target_rubric, str)
