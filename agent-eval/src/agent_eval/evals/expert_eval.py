"""Deepeval evaluation pipeline for ExpertAgent.

Defines a representative input dataset, output criteria (non-empty paper list,
no hallucinated DOIs), and pass/fail thresholds.

Run with::

    python -m agent_eval.evals.expert_eval
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from deepeval.test_case import LLMTestCase


# ---------------------------------------------------------------------------
# Representative input dataset
# ---------------------------------------------------------------------------

EXPERT_TEST_INPUTS: list[dict[str, Any]] = [
    {
        "case_id": "exp-001",
        "topic": "Test-Driven Development in software engineering",
        "variant": "PICO",
        "population": "software engineers",
        "intervention": "TDD",
        "comparison": "non-TDD development",
        "outcome": "code quality and defect density",
        "objectives": ["Survey empirical TDD evidence"],
        "questions": ["What is the impact of TDD on code quality?"],
    },
    {
        "case_id": "exp-002",
        "topic": "Code review effectiveness in open-source projects",
        "variant": "PICO",
        "population": "open-source contributors",
        "intervention": "structured code review process",
        "comparison": "ad-hoc review or no review",
        "outcome": "defect detection rate and review throughput",
        "objectives": ["Identify best practices for OSS code review"],
        "questions": ["Does formal code review improve OSS quality?"],
    },
    {
        "case_id": "exp-003",
        "topic": "Continuous integration in agile projects",
        "variant": "PICOS",
        "population": "agile development teams",
        "intervention": "CI/CD pipeline adoption",
        "comparison": "manual integration",
        "outcome": "deployment frequency and rollback rate",
        "objectives": ["Quantify CI/CD adoption benefits"],
        "questions": ["How does CI adoption affect deployment stability?"],
    },
]


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------


def _assert_non_empty_papers(output: str) -> None:
    """Raise AssertionError if the output list contains no papers.

    Args:
        output: JSON array string produced by ExpertAgent.

    Raises:
        AssertionError: When the list is empty.
    """
    data: list[dict[str, Any]] = json.loads(output)
    assert isinstance(data, list), f"Expected JSON array, got {type(data)}"
    assert len(data) > 0, f"Expected at least one paper suggestion, got 0. Output: {output}"


def _assert_no_obviously_hallucinated_dois(output: str) -> None:
    """Check that returned DOIs follow the ``10.`` prefix convention.

    Args:
        output: JSON array string produced by ExpertAgent.
    """
    data: list[dict[str, Any]] = json.loads(output)
    for paper in data:
        doi = paper.get("doi")
        if doi is not None:
            assert doi.startswith("10."), (
                f"Paper DOI '{doi}' does not start with '10.' — likely hallucinated."
            )


def _assert_rationale_present(output: str) -> None:
    """Check that every returned paper has a non-empty rationale field.

    Args:
        output: JSON array string produced by ExpertAgent.

    Raises:
        AssertionError: When any paper is missing a rationale.
    """
    data: list[dict[str, Any]] = json.loads(output)
    for paper in data:
        rationale = paper.get("rationale", "")
        assert rationale, f"Paper '{paper.get('title')}' is missing a rationale."


# ---------------------------------------------------------------------------
# Deepeval test cases
# ---------------------------------------------------------------------------


def build_test_cases(run_agent: bool = False) -> list[LLMTestCase]:
    """Build deepeval LLMTestCase objects for the expert evaluation suite.

    When *run_agent* is False (default) a stub output is used so CI can run
    structural checks without LLM credentials.

    Args:
        run_agent: Whether to call the live ExpertAgent for each case.

    Returns:
        A list of :class:`LLMTestCase` objects ready for assertion.
    """
    cases: list[LLMTestCase] = []

    for inp in EXPERT_TEST_INPUTS:
        if run_agent:
            actual_output = asyncio.run(_invoke_expert(inp))
        else:
            actual_output = json.dumps([
                {
                    "title": "Stub Paper for " + inp["topic"],
                    "authors": ["Stub Author"],
                    "year": 2024,
                    "venue": "Stub Venue",
                    "doi": "10.0000/stub",
                    "rationale": "Stub rationale: directly relevant to the study topic.",
                }
            ])

        input_text = json.dumps({k: v for k, v in inp.items() if k != "case_id"})

        cases.append(
            LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                expected_output=None,
                context=[
                    "ExpertAgent must return a JSON array of paper objects.",
                    "Each paper must have title, authors, rationale.",
                    "DOIs, when present, must start with '10.'.",
                    "Every paper must have a non-empty rationale explaining its relevance.",
                ],
            )
        )

    return cases


async def _invoke_expert(inp: dict[str, Any]) -> str:
    """Call the real ExpertAgent and return its raw JSON output string.

    Args:
        inp: Test input dictionary with topic, variant, PICO fields, etc.

    Returns:
        JSON array string of ExpertPaper objects.
    """
    from agents.services.expert import ExpertAgent

    agent = ExpertAgent()
    papers = await agent.run(
        topic=inp["topic"],
        variant=inp["variant"],
        population=inp.get("population"),
        intervention=inp.get("intervention"),
        comparison=inp.get("comparison"),
        outcome=inp.get("outcome"),
        objectives=inp.get("objectives", []),
        questions=inp.get("questions", []),
    )
    return json.dumps([p.model_dump() for p in papers])


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------


def run_expert_eval(run_agent: bool = False, threshold: float = 0.7) -> dict[str, Any]:
    """Execute the ExpertAgent deepeval pipeline.

    Validates:
    1. Output contains ≥1 paper (non-empty papers check).
    2. All DOIs follow the ``10.`` prefix convention.
    3. Every paper has a non-empty rationale field.

    Args:
        run_agent: Whether to call the live agent (requires LLM credentials).
        threshold: Reserved for future deepeval metric thresholds.

    Returns:
        A dict with ``{passed, failed, total, errors}`` counts.
    """
    cases = build_test_cases(run_agent=run_agent)
    passed = 0
    failed = 0
    errors: list[str] = []

    for case in cases:
        try:
            _assert_non_empty_papers(case.actual_output)
            _assert_no_obviously_hallucinated_dois(case.actual_output)
            _assert_rationale_present(case.actual_output)
            passed += 1
        except AssertionError as exc:
            failed += 1
            errors.append(str(exc))

    total = passed + failed
    result = {"passed": passed, "failed": failed, "total": total, "errors": errors}
    return result


if __name__ == "__main__":
    report = run_expert_eval(run_agent=False)
    print(json.dumps(report, indent=2))
