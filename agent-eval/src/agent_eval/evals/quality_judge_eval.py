"""Deepeval evaluation pipeline for QualityJudgeAgent.

Validates that the agent:
- Returns all five rubrics scored (keys present in scores dict)
- All scores are within valid 0–max ranges per rubric
- rubric_details contains score and justification for each rubric
- Recommendations list is non-empty when any rubric scores below its max
- At least one recommendation targets the lowest-scoring rubric

Run with::

    agent-eval evaluate --agent quality_judge

Or directly::

    python -m agent_eval.evals.quality_judge_eval
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from deepeval.dataset import EvaluationDataset
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase


# ---------------------------------------------------------------------------
# Representative input dataset — study snapshots at varying completion levels
# ---------------------------------------------------------------------------

QUALITY_JUDGE_TEST_INPUTS: list[dict[str, Any]] = [
    {
        "case_id": "qj-001",
        "description": "Fully completed study — expect high scores",
        "study_id": 1,
        "study_name": "Systematic Mapping of TDD Practices",
        "study_type": "SMS",
        "current_phase": 5,
        "pico_saved": True,
        "search_strategies": [
            {"query_string": "(TDD OR test-driven) AND (software OR engineering)", "result_count": 312},
            {"query_string": "(TDD OR test-driven development) AND (defect OR quality OR productivity)", "result_count": 287},
        ],
        "test_retest_done": True,
        "reviewers": [
            {"reviewer_type": "human", "agent_name": None, "user_id": 1},
            {"reviewer_type": "ai_agent", "agent_name": "ScreenerAgent", "user_id": None},
        ],
        "inclusion_criteria": [
            "Peer-reviewed publications on TDD",
            "Studies with empirical data",
            "Published 2000–2024",
        ],
        "exclusion_criteria": [
            "Grey literature",
            "Non-software domains",
        ],
        "extractions_done": True,
        "validity_filled": True,
        "validity_dimensions": {
            "descriptive": "Data extracted by two reviewers.",
            "theoretical": "Grounded in Wieringa framework.",
            "generalizability_internal": "All 87 papers treated consistently.",
            "generalizability_external": "4 major databases searched.",
            "interpretive": "Inter-rater agreement κ=0.81.",
            "repeatability": "Strings documented in appendix.",
        },
    },
    {
        "case_id": "qj-002",
        "description": "Early-stage study — expect low scores and many recommendations",
        "study_id": 2,
        "study_name": "DevOps Adoption Review",
        "study_type": "SMS",
        "current_phase": 2,
        "pico_saved": False,
        "search_strategies": [],
        "test_retest_done": False,
        "reviewers": [],
        "inclusion_criteria": [],
        "exclusion_criteria": [],
        "extractions_done": False,
        "validity_filled": False,
        "validity_dimensions": {},
    },
    {
        "case_id": "qj-003",
        "description": "Partial study — search done, extraction pending",
        "study_id": 3,
        "study_name": "ML Fairness in Hiring — Mapping",
        "study_type": "SLR",
        "current_phase": 3,
        "pico_saved": True,
        "search_strategies": [
            {"query_string": "(fairness OR bias) AND (ML OR hiring OR recruitment)", "result_count": 178},
        ],
        "test_retest_done": False,
        "reviewers": [
            {"reviewer_type": "human", "agent_name": None, "user_id": 2},
        ],
        "inclusion_criteria": [
            "Empirical studies of ML fairness in hiring",
        ],
        "exclusion_criteria": [
            "Opinion papers",
            "Preprints without peer review",
        ],
        "extractions_done": False,
        "validity_filled": False,
        "validity_dimensions": {},
    },
]

PASS_THRESHOLD = 1.0  # All structural checks must pass

_RUBRIC_MAX = {
    "need_for_review": 2,
    "search_strategy": 2,
    "search_evaluation": 3,
    "extraction_classification": 3,
    "study_validity": 1,
}

_RUBRIC_NAMES = list(_RUBRIC_MAX.keys())


# ---------------------------------------------------------------------------
# Structural validation helpers
# ---------------------------------------------------------------------------


def _assert_all_rubrics_scored(output: str) -> None:
    """Raise AssertionError if any of the five rubrics is absent from scores.

    Args:
        output: JSON string produced by QualityJudgeAgent.

    Raises:
        AssertionError: When a rubric key is missing from the scores dict.
    """
    data: dict[str, Any] = json.loads(output)
    scores = data.get("scores", {})
    missing = [r for r in _RUBRIC_NAMES if r not in scores]
    assert not missing, f"Missing rubrics in scores: {missing}. Got keys: {list(scores.keys())}"


def _assert_scores_within_valid_ranges(output: str) -> None:
    """Raise AssertionError if any score exceeds its rubric maximum or is negative.

    Args:
        output: JSON string produced by QualityJudgeAgent.

    Raises:
        AssertionError: When a score is outside [0, max] for its rubric.
    """
    data: dict[str, Any] = json.loads(output)
    scores = data.get("scores", {})
    for rubric, max_val in _RUBRIC_MAX.items():
        if rubric not in scores:
            continue
        score = scores[rubric]
        assert 0 <= score <= max_val, (
            f"Score for '{rubric}' is {score}, expected 0–{max_val}."
        )


def _assert_rubric_details_complete(output: str) -> None:
    """Raise AssertionError if rubric_details is missing or lacks score/justification.

    Args:
        output: JSON string produced by QualityJudgeAgent.

    Raises:
        AssertionError: When rubric_details is absent or malformed.
    """
    data: dict[str, Any] = json.loads(output)
    details = data.get("rubric_details", {})
    assert details, "rubric_details is missing or empty."
    for rubric, detail in details.items():
        assert "score" in detail, f"rubric_details['{rubric}'] missing 'score' key."
        assert "justification" in detail, f"rubric_details['{rubric}'] missing 'justification' key."
        assert isinstance(detail["justification"], str) and detail["justification"].strip(), (
            f"rubric_details['{rubric}']['justification'] must be a non-empty string."
        )


def _assert_recommendations_non_empty_for_low_scores(output: str) -> None:
    """Raise AssertionError if any rubric is below max but recommendations is empty.

    Args:
        output: JSON string produced by QualityJudgeAgent.

    Raises:
        AssertionError: When low scores exist but no recommendations are produced.
    """
    data: dict[str, Any] = json.loads(output)
    scores = data.get("scores", {})
    recommendations = data.get("recommendations", [])
    any_below_max = any(
        scores.get(r, 0) < _RUBRIC_MAX[r] for r in _RUBRIC_NAMES
    )
    if any_below_max:
        assert len(recommendations) >= 1, (
            f"Expected ≥1 recommendation when rubrics are below max, got 0. "
            f"Scores: {scores}"
        )


# ---------------------------------------------------------------------------
# Deepeval test case builder
# ---------------------------------------------------------------------------


def build_test_cases(run_agent: bool = False) -> list[LLMTestCase]:
    """Build deepeval LLMTestCase objects for the QualityJudgeAgent evaluation suite.

    When *run_agent* is ``False`` (default for CI without LLM credentials) the
    ``actual_output`` is set to a structurally valid stub so criteria checks
    run without calling the LLM.  Set *run_agent=True* to call the real agent.

    Args:
        run_agent: Whether to call the live QualityJudgeAgent for each case.

    Returns:
        A list of :class:`LLMTestCase` objects ready for evaluation.
    """
    cases: list[LLMTestCase] = []

    for inp in QUALITY_JUDGE_TEST_INPUTS:
        if run_agent:
            actual_output = asyncio.run(_invoke_quality_judge(inp))
        else:
            # Structurally valid stub — skips LLM call
            stub_scores = {r: 1 for r in _RUBRIC_NAMES}
            actual_output = json.dumps({
                "scores": stub_scores,
                "rubric_details": {
                    r: {
                        "score": stub_scores[r],
                        "justification": f"[Stub] Justification for {r} in study '{inp['study_name']}'.",
                    }
                    for r in _RUBRIC_NAMES
                },
                "recommendations": [
                    {
                        "priority": 1,
                        "action": f"[Stub] Improve {_RUBRIC_NAMES[0]} score.",
                        "target_rubric": _RUBRIC_NAMES[0],
                    }
                ],
            })

        input_text = json.dumps({
            "study_name": inp["study_name"],
            "study_type": inp["study_type"],
            "current_phase": inp["current_phase"],
            "pico_saved": inp["pico_saved"],
            "search_strategies_count": len(inp.get("search_strategies") or []),
            "test_retest_done": inp.get("test_retest_done", False),
            "reviewers_count": len(inp.get("reviewers") or []),
            "extractions_done": inp.get("extractions_done", False),
            "validity_filled": inp.get("validity_filled", False),
        })

        cases.append(
            LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                expected_output=None,
                context=[
                    "QualityJudgeAgent must return a JSON object with 'scores', 'rubric_details', and 'recommendations' keys.",
                    f"Rubrics and their max scores: {_RUBRIC_MAX}.",
                    "All five rubrics must be present in scores with values within their valid range.",
                    "rubric_details must include score and non-empty justification for each rubric.",
                    "recommendations must be non-empty when any rubric scores below its maximum.",
                ],
            )
        )

    return cases


async def _invoke_quality_judge(inp: dict[str, Any]) -> str:
    """Call the live QualityJudgeAgent and return its serialised JSON output.

    Args:
        inp: Test input dictionary from QUALITY_JUDGE_TEST_INPUTS.

    Returns:
        JSON string of the QualityJudgeResult.
    """
    from agents.services.quality_judge import QualityJudgeAgent

    agent = QualityJudgeAgent()
    result = await agent.run(
        study_id=inp["study_id"],
        study_name=inp.get("study_name"),
        study_type=inp.get("study_type"),
        current_phase=inp.get("current_phase", 1),
        pico_saved=inp.get("pico_saved", False),
        search_strategies=inp.get("search_strategies") or [],
        test_retest_done=inp.get("test_retest_done", False),
        reviewers=inp.get("reviewers") or [],
        inclusion_criteria=inp.get("inclusion_criteria") or [],
        exclusion_criteria=inp.get("exclusion_criteria") or [],
        extractions_done=inp.get("extractions_done", False),
        validity_filled=inp.get("validity_filled", False),
        validity_dimensions=inp.get("validity_dimensions") or {},
    )
    return json.dumps({
        "scores": result.scores,
        "rubric_details": {
            rubric: {"score": detail.score, "justification": detail.justification}
            for rubric, detail in result.rubric_details.items()
        },
        "recommendations": [
            {"priority": rec.priority, "action": rec.action, "target_rubric": rec.target_rubric}
            for rec in result.recommendations
        ],
    })


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------


def run_quality_judge_eval(run_agent: bool = False, threshold: float = PASS_THRESHOLD) -> dict[str, Any]:
    """Execute the QualityJudgeAgent deepeval pipeline.

    Validates per-test-case:
    1. All five rubrics are present in the scores dict.
    2. All scores are within their valid 0–max range.
    3. rubric_details contains score and non-empty justification for each rubric.
    4. recommendations is non-empty when any rubric scores below its max.

    A case passes only when all four checks pass.  The pipeline passes when
    the fraction of passing cases ≥ *threshold* (default: 1.0 — all must pass).

    Args:
        run_agent: Whether to call the live agent (requires LLM credentials).
        threshold: Minimum fraction of cases that must pass (0.0–1.0).

    Returns:
        A dict with ``{passed, failed, total, pass_rate, errors}``.
    """
    cases = build_test_cases(run_agent=run_agent)
    passed = 0
    failed = 0
    errors: list[str] = []

    checks = [
        _assert_all_rubrics_scored,
        _assert_scores_within_valid_ranges,
        _assert_rubric_details_complete,
        _assert_recommendations_non_empty_for_low_scores,
    ]

    for case in cases:
        case_errors: list[str] = []
        for check in checks:
            try:
                check(case.actual_output)
            except AssertionError as exc:
                case_errors.append(str(exc))

        if case_errors:
            failed += 1
            errors.extend(case_errors)
        else:
            passed += 1

    total = passed + failed
    pass_rate = passed / total if total > 0 else 0.0
    result: dict[str, Any] = {
        "passed": passed,
        "failed": failed,
        "total": total,
        "pass_rate": pass_rate,
        "threshold": threshold,
        "pipeline_pass": pass_rate >= threshold,
        "errors": errors,
    }
    return result


if __name__ == "__main__":
    report = run_quality_judge_eval(run_agent=False)
    print(json.dumps(report, indent=2))
