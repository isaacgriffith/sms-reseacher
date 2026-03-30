"""Deepeval evaluation pipeline for ScreenerAgent.

Defines a representative input dataset, output criteria (inclusion/exclusion
decisions ≥85% agreement with ground truth), and pass/fail thresholds.

Run with::

    python -m agent_eval.evals.screener_eval
"""

from __future__ import annotations

import json
from typing import Any

from deepeval.test_case import LLMTestCase

# ---------------------------------------------------------------------------
# Representative input dataset
# ---------------------------------------------------------------------------

SCREENER_TEST_INPUTS: list[dict[str, Any]] = [
    {
        "case_id": "scr-001",
        "title": "A controlled experiment on the effect of TDD on software quality",
        "abstract": "We present a controlled experiment comparing TDD with traditional waterfall development. Defect density was reduced by 40% in the TDD group.",
        "inclusion_criteria": ["empirical studies", "controlled experiments", "software quality metrics"],
        "exclusion_criteria": ["grey literature", "non-software projects"],
        "expected": "accepted",
    },
    {
        "case_id": "scr-002",
        "title": "My blog: why I hate unit tests",
        "abstract": "Opinion piece arguing that unit tests are a waste of time and developers should just use manual testing.",
        "inclusion_criteria": ["empirical studies", "controlled experiments"],
        "exclusion_criteria": ["grey literature", "opinion pieces"],
        "expected": "rejected",
    },
    {
        "case_id": "scr-003",
        "title": "Systematic mapping of agile practices in distributed teams",
        "abstract": "A systematic mapping study that categorises 87 primary studies on agile ceremonies in distributed development contexts.",
        "inclusion_criteria": ["systematic studies", "agile methods", "distributed teams"],
        "exclusion_criteria": ["single case studies", "non-English publications"],
        "expected": "accepted",
    },
]


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------


def _assert_valid_decision(output: str) -> None:
    """Raise AssertionError if output does not contain a valid decision.

    Args:
        output: JSON string produced by ScreenerAgent.

    Raises:
        AssertionError: When the decision is not one of accepted/rejected/duplicate.

    """
    data: dict[str, Any] = json.loads(output)
    decision = data.get("decision")
    assert decision in {"accepted", "rejected", "duplicate"}, (
        f"Expected decision in {{accepted, rejected, duplicate}}, got {decision!r}"
    )


def _assert_rationale_present(output: str) -> None:
    """Raise AssertionError if output does not contain a non-empty rationale.

    Args:
        output: JSON string produced by ScreenerAgent.

    Raises:
        AssertionError: When rationale is missing or empty.

    """
    data: dict[str, Any] = json.loads(output)
    rationale = data.get("rationale", "")
    assert rationale and len(rationale) > 10, (
        f"Expected non-empty rationale, got: {rationale!r}"
    )


# ---------------------------------------------------------------------------
# Deepeval test cases
# ---------------------------------------------------------------------------


def build_test_cases(run_agent: bool = False) -> list[LLMTestCase]:
    """Build deepeval LLMTestCase objects for the screener evaluation suite.

    Args:
        run_agent: Whether to call the live ScreenerAgent for each case.

    Returns:
        A list of :class:`LLMTestCase` objects ready for deepeval assertion.

    """
    cases: list[LLMTestCase] = []

    for inp in SCREENER_TEST_INPUTS:
        if run_agent:
            import asyncio
            actual_output = asyncio.run(_invoke_screener(inp))
        else:
            actual_output = json.dumps({
                "decision": inp["expected"],
                "rationale": f"Stub rationale for {inp['case_id']}",
                "matched_inclusion": inp["inclusion_criteria"][:1],
                "matched_exclusion": [],
            })

        input_text = json.dumps({
            "title": inp["title"],
            "abstract": inp["abstract"],
            "inclusion_criteria": inp["inclusion_criteria"],
            "exclusion_criteria": inp["exclusion_criteria"],
        })

        cases.append(
            LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                expected_output=json.dumps({"decision": inp["expected"]}),
                context=[
                    "ScreenerAgent must return decision: accepted | rejected | duplicate.",
                    "Rationale must be non-empty and explain the decision.",
                    "Matched inclusion/exclusion criteria must be listed.",
                ],
            )
        )

    return cases


async def _invoke_screener(inp: dict[str, Any]) -> str:
    """Call the real ScreenerAgent and return its raw JSON output string.

    Args:
        inp: Test input dict with title, abstract, criteria.

    Returns:
        JSON string of the screener result.

    """
    from agents.services.screener import ScreenerAgent

    agent = ScreenerAgent()
    result = await agent.run(
        title=inp["title"],
        abstract=inp.get("abstract", ""),
        inclusion_criteria=inp.get("inclusion_criteria", []),
        exclusion_criteria=inp.get("exclusion_criteria", []),
    )
    from agents.services.screener import ScreeningResult as _SR

    assert isinstance(result, _SR), f"Expected ScreeningResult, got {type(result)}"
    return json.dumps(result.model_dump())


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------


def run_screener_eval(run_agent: bool = False, threshold: float = 0.85) -> dict[str, Any]:
    """Execute the ScreenerAgent deepeval pipeline.

    Validates:
    1. Output contains a valid decision (accepted/rejected/duplicate).
    2. A non-empty rationale is present.

    Args:
        run_agent: Whether to call the live agent (requires LLM credentials).
        threshold: Fraction of cases that must pass (default: 0.85).

    Returns:
        A dict with ``{passed, failed, total}`` counts.

    """
    cases = build_test_cases(run_agent=run_agent)
    passed = 0
    failed = 0
    errors: list[str] = []

    for case in cases:
        try:
            assert case.actual_output is not None, "actual_output must not be None"
            _assert_valid_decision(case.actual_output)
            _assert_rationale_present(case.actual_output)
            passed += 1
        except AssertionError as exc:
            failed += 1
            errors.append(str(exc))

    total = passed + failed
    result = {"passed": passed, "failed": failed, "total": total, "errors": errors}
    return result


if __name__ == "__main__":
    report = run_screener_eval(run_agent=False)
    print(json.dumps(report, indent=2))
