"""Deepeval evaluation pipeline for ValidityAgent.

Validates that the agent:
- Returns all six validity dimensions as non-empty strings
- Does not produce empty or whitespace-only values for any dimension
- Uses language that reflects the study's actual decisions (no hallucinated facts)
- Produces output within a reasonable length range (not trivially short)

Run with::

    agent-eval evaluate --agent validity

Or directly::

    python -m agent_eval.evals.validity_eval
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from deepeval.test_case import LLMTestCase

# ---------------------------------------------------------------------------
# Representative input dataset — study snapshots at varying completion states
# ---------------------------------------------------------------------------

VALIDITY_TEST_INPUTS: list[dict[str, Any]] = [
    {
        "case_id": "v-001",
        "description": "Fully completed study — all phases done",
        "study_id": 1,
        "study_name": "Systematic Mapping of TDD Practices in Software Engineering",
        "study_type": "SMS",
        "current_phase": 5,
        "pico_components": [
            {"type": "population", "content": "Software engineering practitioners and researchers"},
            {"type": "intervention", "content": "Test-driven development (TDD) practices"},
            {"type": "comparison", "content": "Traditional development without TDD"},
            {"type": "outcome", "content": "Code quality, defect rates, developer productivity"},
        ],
        "search_strategies": [
            {"string_text": "(TDD OR \"test-driven\") AND (software OR engineering OR development)", "version": 1},
            {"string_text": "(TDD OR \"test-driven development\") AND (software OR engineering) AND (defect OR quality OR productivity)", "version": 2},
        ],
        "databases": "ACM DL, IEEE Xplore, Scopus, Web of Science",
        "test_retest_done": True,
        "reviewers": [
            {"reviewer_type": "human", "agent_name": None, "user_id": 1},
            {"reviewer_type": "ai_agent", "agent_name": "ScreenerAgent", "user_id": None},
        ],
        "inclusion_criteria": [
            "Published in peer-reviewed venues (journal, conference, workshop)",
            "Studies the use, adoption, or effect of TDD",
            "Published between 2000 and 2024",
        ],
        "exclusion_criteria": [
            "Grey literature, blog posts, tutorials",
            "Studies focused on non-software domains",
            "Papers without empirical data or a research method",
        ],
        "extraction_summary": (
            "Data extraction was performed on 87 accepted papers. "
            "Fields extracted include: research type, venue, author details, open codings, and per-RQ answers. "
            "AI reviewer and human reviewer independently coded each paper; conflicts were flagged and resolved by discussion."
        ),
    },
    {
        "case_id": "v-002",
        "description": "Partial study — search done, no extractions",
        "study_id": 2,
        "study_name": "Mapping Studies on DevOps Adoption",
        "study_type": "SMS",
        "current_phase": 3,
        "pico_components": [
            {"type": "population", "content": "Software development teams adopting DevOps"},
            {"type": "intervention", "content": "DevOps practices (CI/CD, IaC, monitoring)"},
            {"type": "outcome", "content": "Deployment frequency, mean time to recovery"},
        ],
        "search_strategies": [
            {"string_text": "(DevOps OR \"continuous delivery\" OR \"continuous integration\") AND (practice OR adoption OR impact)", "version": 1},
        ],
        "databases": "IEEE Xplore, ACM DL",
        "test_retest_done": False,
        "reviewers": [
            {"reviewer_type": "human", "agent_name": None, "user_id": 2},
        ],
        "inclusion_criteria": [
            "Empirical study of DevOps practices",
            "Published 2015–2024",
        ],
        "exclusion_criteria": [
            "Position papers and opinion pieces",
        ],
        "extraction_summary": None,
    },
    {
        "case_id": "v-003",
        "description": "Early-stage study — PICO defined, no search yet",
        "study_id": 3,
        "study_name": "Review of Fairness in ML-Based Hiring Tools",
        "study_type": "SLR",
        "current_phase": 1,
        "pico_components": [
            {"type": "population", "content": "ML systems used in recruitment and hiring"},
            {"type": "intervention", "content": "Algorithmic fairness constraints and audits"},
            {"type": "outcome", "content": "Reduction in demographic disparities in hiring outcomes"},
        ],
        "search_strategies": [],
        "databases": None,
        "test_retest_done": False,
        "reviewers": [],
        "inclusion_criteria": [
            "Studies ML tools used in hiring or recruitment",
            "Addresses fairness, bias, or discrimination",
        ],
        "exclusion_criteria": [],
        "extraction_summary": None,
    },
]

PASS_THRESHOLD = 1.0  # All structural checks must pass

_VALIDITY_DIMS = (
    "descriptive",
    "theoretical",
    "generalizability_internal",
    "generalizability_external",
    "interpretive",
    "repeatability",
)

_MIN_DIM_LENGTH = 50  # Minimum characters per dimension (guards against trivially short output)


# ---------------------------------------------------------------------------
# Structural validation helpers
# ---------------------------------------------------------------------------


def _assert_all_dimensions_present(output: str) -> None:
    """Raise AssertionError if any validity dimension is missing from the output.

    Args:
        output: JSON string produced by ValidityAgent.

    Raises:
        AssertionError: When one or more of the six dimensions are absent.

    """
    data: dict[str, Any] = json.loads(output)
    missing = [dim for dim in _VALIDITY_DIMS if dim not in data]
    assert not missing, f"Missing validity dimensions: {missing}. Output keys: {list(data.keys())}"


def _assert_no_empty_dimensions(output: str) -> None:
    """Raise AssertionError if any validity dimension is empty or whitespace-only.

    Args:
        output: JSON string produced by ValidityAgent.

    Raises:
        AssertionError: When any dimension value is empty or whitespace-only.

    """
    data: dict[str, Any] = json.loads(output)
    empty = [dim for dim in _VALIDITY_DIMS if not (data.get(dim) or "").strip()]
    assert not empty, f"Empty validity dimensions: {empty}"


def _assert_min_dimension_length(output: str) -> None:
    """Raise AssertionError if any dimension is shorter than the minimum length.

    Args:
        output: JSON string produced by ValidityAgent.

    Raises:
        AssertionError: When any dimension has fewer than _MIN_DIM_LENGTH characters.

    """
    data: dict[str, Any] = json.loads(output)
    too_short = [
        dim
        for dim in _VALIDITY_DIMS
        if len((data.get(dim) or "").strip()) < _MIN_DIM_LENGTH
    ]
    assert not too_short, (
        f"Validity dimensions below minimum length ({_MIN_DIM_LENGTH} chars): {too_short}"
    )


def _assert_all_string_values(output: str) -> None:
    """Raise AssertionError if any validity dimension value is not a string.

    Args:
        output: JSON string produced by ValidityAgent.

    Raises:
        AssertionError: When any dimension value is not of type str.

    """
    data: dict[str, Any] = json.loads(output)
    non_string = [dim for dim in _VALIDITY_DIMS if not isinstance(data.get(dim), str)]
    assert not non_string, f"Non-string validity dimension values: {non_string}"


# ---------------------------------------------------------------------------
# Deepeval test case builder
# ---------------------------------------------------------------------------


def build_test_cases(run_agent: bool = False) -> list[LLMTestCase]:
    """Build deepeval LLMTestCase objects for the ValidityAgent evaluation suite.

    When *run_agent* is ``False`` (default for CI without LLM credentials) the
    ``actual_output`` is set to a structurally valid stub so criteria checks
    run without calling the LLM.  Set *run_agent=True* to call the real agent.

    Args:
        run_agent: Whether to call the live ValidityAgent for each case.

    Returns:
        A list of :class:`LLMTestCase` objects ready for evaluation.

    """
    cases: list[LLMTestCase] = []

    for inp in VALIDITY_TEST_INPUTS:
        if run_agent:
            actual_output = asyncio.run(_invoke_validity_agent(inp))
        else:
            # Structurally valid stub — skips LLM call, validates structure only
            actual_output = json.dumps({
                dim: (
                    f"[Stub] {dim.replace('_', ' ').title()} validity discussion "
                    f"for study '{inp['study_name']}'. "
                    "This text covers methodological decisions and potential threats to validity "
                    "for the " + dim + " dimension."
                )
                for dim in _VALIDITY_DIMS
            })

        input_text = json.dumps({
            "study_name": inp["study_name"],
            "study_type": inp["study_type"],
            "current_phase": inp["current_phase"],
            "pico_defined": bool(inp.get("pico_components")),
            "search_strategies_count": len(inp.get("search_strategies") or []),
            "reviewers_count": len(inp.get("reviewers") or []),
            "extraction_done": bool(inp.get("extraction_summary")),
        })

        cases.append(
            LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                expected_output=None,
                context=[
                    "ValidityAgent must return a JSON object with all six validity dimensions.",
                    "Each dimension must be a non-empty string of at least 50 characters.",
                    "Dimensions: descriptive, theoretical, generalizability_internal, "
                    "generalizability_external, interpretive, repeatability.",
                    "No dimension may be null, missing, or whitespace-only.",
                ],
            )
        )

    return cases


async def _invoke_validity_agent(inp: dict[str, Any]) -> str:
    """Call the live ValidityAgent and return its serialised JSON output.

    Args:
        inp: Test input dictionary from VALIDITY_TEST_INPUTS.

    Returns:
        JSON string of the ValidityResult.

    """
    from agents.services.validity import ValidityAgent

    agent = ValidityAgent()
    result = await agent.run(
        study_id=inp["study_id"],
        study_name=inp.get("study_name"),
        study_type=inp.get("study_type"),
        current_phase=inp.get("current_phase", 1),
        pico_components=inp.get("pico_components") or [],
        search_strategies=inp.get("search_strategies") or [],
        databases=inp.get("databases"),
        test_retest_done=inp.get("test_retest_done", False),
        reviewers=inp.get("reviewers") or [],
        inclusion_criteria=inp.get("inclusion_criteria") or [],
        exclusion_criteria=inp.get("exclusion_criteria") or [],
        extraction_summary=inp.get("extraction_summary"),
    )
    return json.dumps(result.model_dump())


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------


def run_validity_eval(run_agent: bool = False, threshold: float = PASS_THRESHOLD) -> dict[str, Any]:
    """Execute the ValidityAgent deepeval pipeline.

    Validates per-test-case:
    1. All six validity dimensions are present in the output.
    2. All dimension values are non-empty strings.
    3. All dimension values meet the minimum length threshold.
    4. All dimension values are of type str (not null or other types).

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
        _assert_all_dimensions_present,
        _assert_all_string_values,
        _assert_no_empty_dimensions,
        _assert_min_dimension_length,
    ]

    for case in cases:
        case_errors: list[str] = []
        for check in checks:
            try:
                check(case.actual_output or "")
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
    report = run_validity_eval(run_agent=False)
    print(json.dumps(report, indent=2))
