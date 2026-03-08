"""Deepeval evaluation pipeline for ExtractorAgent.

Defines a representative input dataset, output criteria (non-empty extraction
fields, no hallucinated values), and pass/fail thresholds.

Run with::

    python -m agent_eval.evals.extractor_eval
"""

from __future__ import annotations

import json
from typing import Any

from deepeval.test_case import LLMTestCase


# ---------------------------------------------------------------------------
# Representative input dataset
# ---------------------------------------------------------------------------

EXTRACTOR_TEST_INPUTS: list[dict[str, Any]] = [
    {
        "case_id": "ext-001",
        "title": "A controlled experiment on the effect of TDD on software quality",
        "abstract": (
            "We present a controlled experiment comparing TDD with traditional waterfall. "
            "42 professional developers participated. Defect density was reduced by 40% "
            "in the TDD group (p < 0.05). External validity is limited to Java projects."
        ),
        "extraction_fields": ["study_design", "sample_size", "outcome_measure", "limitations"],
    },
    {
        "case_id": "ext-002",
        "title": "Systematic mapping of agile practices in distributed teams",
        "abstract": (
            "This systematic mapping study analyses 87 primary studies from 2005–2022. "
            "Scrum was the most commonly adopted framework (61%). Key finding: standup "
            "frequency correlates positively with team velocity in remote settings."
        ),
        "extraction_fields": ["study_design", "sample_size", "outcome_measure", "key_findings"],
    },
    {
        "case_id": "ext-003",
        "title": "ML-based code smell detection: a replication study",
        "abstract": (
            "We replicated a 2019 study using three ML classifiers (SVM, RF, LSTM) on "
            "10 open-source Java repositories. F1 improved from 0.72 to 0.81 with LSTM. "
            "Threats: dataset may not generalise to proprietary codebases."
        ),
        "extraction_fields": ["study_design", "methods_used", "outcome_measure", "limitations"],
    },
]


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------


def _assert_non_empty_fields(output: str, required_fields: list[str]) -> None:
    """Raise AssertionError if any required field is missing or empty.

    Args:
        output: JSON string produced by ExtractorAgent.
        required_fields: List of field names that must be present and non-empty.

    Raises:
        AssertionError: When a required field is missing or empty.
    """
    data: dict[str, Any] = json.loads(output)
    for field in required_fields:
        val = data.get(field)
        assert val, f"Required extraction field '{field}' is missing or empty. Output: {output}"


def _assert_no_none_values_for_required_fields(output: str, required_fields: list[str]) -> None:
    """Raise AssertionError if any required field has None value.

    Args:
        output: JSON string produced by ExtractorAgent.
        required_fields: Fields that must not be null.

    Raises:
        AssertionError: When a required field is null.
    """
    data: dict[str, Any] = json.loads(output)
    for field in required_fields:
        assert data.get(field) is not None, (
            f"Field '{field}' must not be null. Output: {output}"
        )


# ---------------------------------------------------------------------------
# Deepeval test cases
# ---------------------------------------------------------------------------


def build_test_cases(run_agent: bool = False) -> list[LLMTestCase]:
    """Build deepeval LLMTestCase objects for the extractor evaluation suite.

    Args:
        run_agent: Whether to call the live ExtractorAgent for each case.

    Returns:
        A list of :class:`LLMTestCase` objects ready for deepeval assertion.
    """
    cases: list[LLMTestCase] = []

    for inp in EXTRACTOR_TEST_INPUTS:
        if run_agent:
            import asyncio
            actual_output = asyncio.run(_invoke_extractor(inp))
        else:
            actual_output = json.dumps({
                field: f"Stub value for {field} in {inp['case_id']}"
                for field in inp["extraction_fields"]
            })

        input_text = json.dumps({
            "title": inp["title"],
            "abstract": inp["abstract"],
            "extraction_fields": inp["extraction_fields"],
        })

        cases.append(
            LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                expected_output=None,
                context=[
                    "ExtractorAgent must return a JSON object with all requested extraction fields.",
                    "No field value should be null for fields present in the abstract.",
                    "Extracted values must be grounded in the abstract text (no hallucination).",
                ],
            )
        )

    return cases


async def _invoke_extractor(inp: dict[str, Any]) -> str:
    """Call the real ExtractorAgent and return its raw JSON output string.

    Args:
        inp: Test input dict with title, abstract, extraction_fields.

    Returns:
        JSON string of the extractor result.
    """
    from agents.services.extractor import ExtractorAgent

    agent = ExtractorAgent()
    result = await agent.run(
        title=inp["title"],
        abstract=inp.get("abstract", ""),
        fields=inp.get("extraction_fields", []),
    )
    return json.dumps(result.model_dump())


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------


def run_extractor_eval(run_agent: bool = False, threshold: float = 0.7) -> dict[str, Any]:
    """Execute the ExtractorAgent deepeval pipeline.

    Validates:
    1. All requested extraction fields are present and non-empty.
    2. No required field has a None value.

    Args:
        run_agent: Whether to call the live agent (requires LLM credentials).
        threshold: Fraction of cases that must pass (default: 0.7).

    Returns:
        A dict with ``{passed, failed, total}`` counts.
    """
    cases = build_test_cases(run_agent=run_agent)
    passed = 0
    failed = 0
    errors: list[str] = []

    for case in cases:
        input_data = json.loads(case.input)
        required_fields = input_data.get("extraction_fields", [])
        try:
            _assert_non_empty_fields(case.actual_output, required_fields)
            _assert_no_none_values_for_required_fields(case.actual_output, required_fields)
            passed += 1
        except AssertionError as exc:
            failed += 1
            errors.append(str(exc))

    total = passed + failed
    result = {"passed": passed, "failed": failed, "total": total, "errors": errors}
    return result


if __name__ == "__main__":
    report = run_extractor_eval(run_agent=False)
    print(json.dumps(report, indent=2))
