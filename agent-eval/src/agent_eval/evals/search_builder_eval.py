"""Deepeval evaluation pipeline for SearchStringBuilderAgent.

Defines a representative input dataset, output criteria (valid boolean syntax,
non-empty terms_used, synonym expansion evidence), and pass/fail thresholds.

Run with::

    agent-eval evaluate --agent search_builder --suite <path-to-suite.jsonl>

Or directly::

    python -m agent_eval.evals.search_builder_eval
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from deepeval.test_case import LLMTestCase

# ---------------------------------------------------------------------------
# Representative input dataset
# ---------------------------------------------------------------------------

SEARCH_BUILDER_TEST_INPUTS: list[dict[str, Any]] = [
    {
        "case_id": "sb-001",
        "topic": "Test-Driven Development in software engineering",
        "variant": "PICO",
        "population": "software engineers",
        "intervention": "test-driven development",
        "comparison": "non-TDD development",
        "outcome": "code quality and defect rate",
        "objectives": ["Identify empirical TDD studies"],
        "questions": ["Does TDD reduce defect rate?"],
        "seed_keywords": ["TDD", "unit testing", "test-first"],
        "inclusion_criteria": ["empirical studies only"],
        "exclusion_criteria": ["grey literature excluded"],
    },
    {
        "case_id": "sb-002",
        "topic": "Machine learning in healthcare diagnostics",
        "variant": "PICOS",
        "population": "radiology patients",
        "intervention": "ML-based image analysis",
        "comparison": "expert radiologist reading",
        "outcome": "diagnostic accuracy",
        "objectives": ["Compare ML vs human accuracy in radiology"],
        "questions": ["Can ML match radiologist accuracy?"],
        "seed_keywords": ["deep learning", "CNN", "medical imaging"],
        "inclusion_criteria": ["peer-reviewed", "published after 2015"],
        "exclusion_criteria": ["non-medical AI applications"],
    },
    {
        "case_id": "sb-003",
        "topic": "Agile methods in distributed software teams",
        "variant": "SPIDER",
        "population": "distributed software development teams",
        "intervention": "agile ceremonies (Scrum, Kanban)",
        "comparison": None,
        "outcome": "team velocity and communication quality",
        "objectives": ["Understand agile adoption patterns in remote work"],
        "questions": ["How do agile practices adapt to distributed settings?"],
        "seed_keywords": ["Scrum", "Kanban", "remote teams", "distributed agile"],
        "inclusion_criteria": ["primary studies", "software development context"],
        "exclusion_criteria": ["non-software projects"],
    },
]


# ---------------------------------------------------------------------------
# Output assertion helpers
# ---------------------------------------------------------------------------


def _assert_non_empty_search_string(output: str) -> None:
    """Raise AssertionError if search_string field is absent or empty.

    Args:
        output: JSON string produced by SearchStringBuilderAgent.

    Raises:
        AssertionError: When search_string is missing or empty.

    """
    data: dict[str, Any] = json.loads(output)
    search_string = data.get("search_string", "")
    assert search_string and len(search_string.strip()) > 0, (
        f"Expected non-empty search_string, got: {search_string!r}. Full output: {output}"
    )


def _assert_valid_boolean_syntax(output: str) -> None:
    """Check that the search string contains at least one Boolean operator.

    Validates that the generated string uses Boolean logic (AND, OR, NOT).
    This is a structural check — full query parsing is out of scope.

    Args:
        output: JSON string produced by SearchStringBuilderAgent.

    Raises:
        AssertionError: When no Boolean operator is found.

    """
    data: dict[str, Any] = json.loads(output)
    search_string: str = data.get("search_string", "")
    upper = search_string.upper()
    has_boolean = any(
        bool(re.search(rf"\b{op}\b", upper)) for op in ("AND", "OR", "NOT")
    )
    assert has_boolean, (
        f"search_string contains no Boolean operators (AND/OR/NOT): {search_string!r}"
    )


def _assert_terms_used_non_empty(output: str) -> None:
    """Raise AssertionError if terms_used is absent or empty.

    Args:
        output: JSON string produced by SearchStringBuilderAgent.

    Raises:
        AssertionError: When terms_used list is missing or empty.

    """
    data: dict[str, Any] = json.loads(output)
    terms_used: list[Any] = data.get("terms_used", [])
    assert len(terms_used) > 0, (
        f"Expected at least one TermGroup in terms_used, got 0. Output: {output}"
    )


def _assert_synonym_expansion_evidence(output: str) -> None:
    """Check that expansion_notes is present and non-empty.

    Synonym expansion evidence is captured in the ``expansion_notes`` field.

    Args:
        output: JSON string produced by SearchStringBuilderAgent.

    Raises:
        AssertionError: When expansion_notes is absent or blank.

    """
    data: dict[str, Any] = json.loads(output)
    notes: str = data.get("expansion_notes", "")
    assert notes and len(notes.strip()) > 0, (
        f"Expected non-empty expansion_notes (synonym expansion evidence), got: {notes!r}"
    )


# ---------------------------------------------------------------------------
# Deepeval test cases
# ---------------------------------------------------------------------------


def build_test_cases(run_agent: bool = False) -> list[LLMTestCase]:
    """Build deepeval LLMTestCase objects for the search builder evaluation suite.

    When *run_agent* is False (default for CI without LLM credentials) the
    ``actual_output`` is set to a stub JSON string so structural metrics can
    still be evaluated. Set *run_agent=True* to invoke the real agent.

    Args:
        run_agent: Whether to call the live SearchStringBuilderAgent for each case.

    Returns:
        A list of :class:`LLMTestCase` objects ready for deepeval assertion.

    """
    cases: list[LLMTestCase] = []

    for inp in SEARCH_BUILDER_TEST_INPUTS:
        if run_agent:
            actual_output = asyncio.run(_invoke_search_builder(inp))
        else:
            # Stub output: structurally valid, skips LLM call
            actual_output = json.dumps({
                "search_string": (
                    f'("{inp["intervention"]}" OR "{inp["seed_keywords"][0]}") '
                    f'AND ("{inp["outcome"]}")'
                    if inp.get("intervention") and inp.get("seed_keywords")
                    else f'("{inp["topic"]}") AND (quality OR effectiveness)'
                ),
                "terms_used": [
                    {
                        "component": "intervention",
                        "terms": inp.get("seed_keywords", ["stub-term"]),
                    }
                ],
                "expansion_notes": (
                    f"Stub expansion for {inp['topic']}. "
                    "Synonyms sourced from IEEE Thesaurus and MeSH."
                ),
            })

        input_text = json.dumps({k: v for k, v in inp.items() if k != "case_id"})

        cases.append(
            LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                expected_output=None,
                context=[
                    "SearchStringBuilderAgent must return a JSON object with keys: "
                    "search_string, terms_used, expansion_notes.",
                    "search_string must be a non-empty Boolean expression using AND/OR/NOT.",
                    "terms_used must be a non-empty list of {component, terms} objects.",
                    "expansion_notes must describe synonym expansion evidence.",
                ],
            )
        )

    return cases


async def _invoke_search_builder(inp: dict[str, Any]) -> str:
    """Call the real SearchStringBuilderAgent and return its raw JSON output string.

    Args:
        inp: Test input dictionary with topic, variant, PICO fields, etc.

    Returns:
        JSON string of the SearchStringResult.

    """
    from agents.services.search_builder import SearchStringBuilderAgent

    agent = SearchStringBuilderAgent()
    result = await agent.run(
        topic=inp["topic"],
        variant=inp["variant"],
        population=inp.get("population"),
        intervention=inp.get("intervention"),
        comparison=inp.get("comparison"),
        outcome=inp.get("outcome"),
        seed_keywords=inp.get("seed_keywords", []),
        objectives=inp.get("objectives", []),
        questions=inp.get("questions", []),
        inclusion_criteria=inp.get("inclusion_criteria", []),
        exclusion_criteria=inp.get("exclusion_criteria", []),
    )
    return json.dumps({
        "search_string": result.search_string,
        "terms_used": [tg.model_dump() for tg in result.terms_used],
        "expansion_notes": result.expansion_notes,
    })


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------


def run_search_builder_eval(
    run_agent: bool = False,
    threshold: float = 0.7,
) -> dict[str, Any]:
    """Execute the SearchStringBuilderAgent deepeval pipeline.

    Validates:
    1. search_string is non-empty (structural check).
    2. search_string contains at least one Boolean operator (AND/OR/NOT).
    3. terms_used list is non-empty (synonym expansion present).
    4. expansion_notes is non-empty (synonym expansion evidence).

    Args:
        run_agent: Whether to call the live agent (requires LLM credentials).
        threshold: Pass/fail threshold ratio (0.0–1.0); pipeline fails if
            ``passed / total < threshold``.

    Returns:
        A dict with ``{passed, failed, total, errors, pass_rate}`` fields.

    """
    cases = build_test_cases(run_agent=run_agent)
    passed = 0
    failed = 0
    errors: list[str] = []

    assertion_checks = [
        _assert_non_empty_search_string,
        _assert_valid_boolean_syntax,
        _assert_terms_used_non_empty,
        _assert_synonym_expansion_evidence,
    ]

    for case in cases:
        case_passed = True
        for check in assertion_checks:
            try:
                check(case.actual_output or "")
            except AssertionError as exc:
                case_passed = False
                errors.append(str(exc))
        if case_passed:
            passed += 1
        else:
            failed += 1

    total = passed + failed
    pass_rate = passed / total if total > 0 else 0.0
    result: dict[str, Any] = {
        "passed": passed,
        "failed": failed,
        "total": total,
        "pass_rate": pass_rate,
        "threshold": threshold,
        "pipeline_passed": pass_rate >= threshold,
        "errors": errors,
    }
    return result


if __name__ == "__main__":
    report = run_search_builder_eval(run_agent=False)
    print(json.dumps(report, indent=2))
