"""Deepeval evaluation pipeline for ProtocolReviewerAgent.

Defines a representative input dataset of SLR protocol drafts with known
methodological issues, output criteria (structured JSON with issues and
overall_assessment), and pass/fail thresholds.

Run with::

    python -m agent_eval.evals.protocol_reviewer_eval
"""

from __future__ import annotations

import json
from typing import Any

from deepeval.test_case import LLMTestCase

# ---------------------------------------------------------------------------
# Representative input dataset
# ---------------------------------------------------------------------------

PROTOCOL_TEST_INPUTS: list[dict[str, Any]] = [
    {
        "case_id": "pr-001",
        "description": "Well-formed meta-analysis protocol",
        "protocol": {
            "background": "This review investigates the effect of test-driven development (TDD) on software defect density across agile projects.",
            "rationale": "Despite widespread TDD adoption, no meta-analysis synthesises its effect on defect density across controlled studies.",
            "research_questions": [
                "RQ1: What is the effect of TDD on defect density compared with non-TDD development?",
                "RQ2: What contextual factors moderate the TDD–defect density relationship?",
            ],
            "pico_population": "Software development teams in industrial or academic settings",
            "pico_intervention": "Test-driven development (TDD)",
            "pico_comparison": "Traditional (test-last) development",
            "pico_outcome": "Defect density (defects per KLOC or equivalent)",
            "pico_context": "Agile or iterative development environments",
            "search_strategy": "(TDD OR 'test-driven development') AND ('defect density' OR 'code quality' OR 'software quality') AND (experiment OR study OR trial)",
            "inclusion_criteria": [
                "Empirical studies (controlled experiments, quasi-experiments, case studies)",
                "Reports quantitative defect metrics",
                "Published in peer-reviewed venues",
                "Published 2000–2026",
            ],
            "exclusion_criteria": [
                "Grey literature (blog posts, technical reports without review)",
                "Non-English publications",
                "Studies without a comparison group",
            ],
            "data_extraction_strategy": "Extract: sample size, effect size (Cohen's d or equivalent), confidence interval, team experience level, language, domain.",
            "synthesis_approach": "meta_analysis",
            "dissemination_strategy": "Submit to IEEE Transactions on Software Engineering; present at ICSE 2027.",
            "timetable": "Q1 2026: search; Q2 2026: screening; Q3 2026: extraction; Q4 2026: synthesis and writing",
        },
        "expected_issue_count": 0,  # well-formed protocol
        "known_issues": [],
    },
    {
        "case_id": "pr-002",
        "description": "Missing search strategy — critical flaw",
        "protocol": {
            "background": "Review of code review practices in open-source projects.",
            "rationale": "Code review effectiveness is poorly understood in OSS contexts.",
            "research_questions": ["RQ1: How effective is code review in OSS projects?"],
            "pico_population": "Open-source project contributors",
            "pico_intervention": "Formal code review",
            "pico_comparison": "No formal code review",
            "pico_outcome": "Bug discovery rate",
            "pico_context": None,
            "search_strategy": "",
            "inclusion_criteria": ["Empirical studies", "OSS projects"],
            "exclusion_criteria": ["Non-English"],
            "data_extraction_strategy": "Extract bug counts and review coverage.",
            "synthesis_approach": "descriptive",
            "dissemination_strategy": "Blog post.",
            "timetable": "January 2026 to June 2026",
        },
        "expected_issue_count": 1,
        "known_issues": ["search_strategy"],
    },
    {
        "case_id": "pr-003",
        "description": "Meta-analysis approach but no effect size extraction planned",
        "protocol": {
            "background": "Investigating whether pair programming improves code quality.",
            "rationale": "Multiple RCTs exist but have not been meta-analysed.",
            "research_questions": ["RQ1: Does pair programming improve code quality?"],
            "pico_population": "Software developers",
            "pico_intervention": "Pair programming",
            "pico_comparison": "Solo programming",
            "pico_outcome": "Code quality",
            "pico_context": None,
            "search_strategy": "('pair programming') AND ('code quality' OR defects)",
            "inclusion_criteria": ["RCTs and quasi-experiments", "Peer-reviewed"],
            "exclusion_criteria": ["Opinion pieces"],
            "data_extraction_strategy": "Extract author, year, setting, and qualitative findings.",
            "synthesis_approach": "meta_analysis",
            "dissemination_strategy": "Conference paper.",
            "timetable": "2026 Q1–Q3",
        },
        "expected_issue_count": 1,
        "known_issues": ["data_extraction_strategy"],
    },
    {
        "case_id": "pr-004",
        "description": "Vague and empty mandatory fields",
        "protocol": {
            "background": "Software.",
            "rationale": "",
            "research_questions": [],
            "pico_population": "",
            "pico_intervention": "Something",
            "pico_comparison": "",
            "pico_outcome": "",
            "pico_context": None,
            "search_strategy": "software",
            "inclusion_criteria": [],
            "exclusion_criteria": [],
            "data_extraction_strategy": "",
            "synthesis_approach": "qualitative",
            "dissemination_strategy": "",
            "timetable": "",
        },
        "expected_issue_count": 3,  # multiple critical/major issues
        "known_issues": ["rationale", "research_questions", "pico_population"],
    },
    {
        "case_id": "pr-005",
        "description": "Contradictory inclusion/exclusion criteria",
        "protocol": {
            "background": "Investigating agile adoption in safety-critical systems.",
            "rationale": "Little evidence on agile in safety-critical domains.",
            "research_questions": ["RQ1: Can agile methods be applied in safety-critical software?"],
            "pico_population": "Safety-critical software teams",
            "pico_intervention": "Agile methods (Scrum, Kanban)",
            "pico_comparison": "Waterfall development",
            "pico_outcome": "Safety incident rate",
            "pico_context": None,
            "search_strategy": "(agile OR scrum OR kanban) AND ('safety-critical' OR embedded)",
            "inclusion_criteria": ["Studies in safety-critical domains", "Empirical studies"],
            "exclusion_criteria": ["Studies in safety-critical domains"],
            "data_extraction_strategy": "Extract incident rates and compliance measures.",
            "synthesis_approach": "descriptive",
            "dissemination_strategy": "Journal submission.",
            "timetable": "Q1–Q4 2026",
        },
        "expected_issue_count": 1,
        "known_issues": ["exclusion_criteria"],
    },
    {
        "case_id": "pr-006",
        "description": "Minor issues only — timetable vague",
        "protocol": {
            "background": "Survey of static analysis tool adoption in Python projects.",
            "rationale": "Static analysis tool usage is anecdotally increasing but data are scarce.",
            "research_questions": ["RQ1: How widely are static analysis tools adopted in Python OSS?"],
            "pico_population": "Python open-source project maintainers",
            "pico_intervention": "Static analysis tool adoption",
            "pico_comparison": "Projects without static analysis",
            "pico_outcome": "Bug density, contributor satisfaction",
            "pico_context": None,
            "search_strategy": "('static analysis' OR linting) AND Python AND ('open source' OR OSS)",
            "inclusion_criteria": ["Empirical studies or surveys", "Python projects"],
            "exclusion_criteria": ["Commercial closed-source projects"],
            "data_extraction_strategy": "Extract tool names, adoption rates, and quality outcomes.",
            "synthesis_approach": "descriptive",
            "dissemination_strategy": "ICSE 2027 submission.",
            "timetable": "Sometime next year",
        },
        "expected_issue_count": 1,
        "known_issues": ["timetable"],
    },
]


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------


def _assert_valid_structure(output: str) -> None:
    """Raise AssertionError if output is not a valid ProtocolReviewResult JSON.

    Args:
        output: JSON string produced by ProtocolReviewerAgent.

    Raises:
        AssertionError: When the output lacks required fields.

    """
    data: dict[str, Any] = json.loads(output)
    assert "issues" in data, "Missing 'issues' key in output"
    assert "overall_assessment" in data, "Missing 'overall_assessment' key"
    assert isinstance(data["issues"], list), "'issues' must be a list"
    assert isinstance(data["overall_assessment"], str), "'overall_assessment' must be a string"
    assert len(data["overall_assessment"]) > 0, "'overall_assessment' must be non-empty"

    for issue in data["issues"]:
        assert "section" in issue, f"Issue missing 'section': {issue}"
        assert "severity" in issue, f"Issue missing 'severity': {issue}"
        assert issue["severity"] in {"critical", "major", "minor"}, (
            f"severity must be critical|major|minor, got {issue['severity']!r}"
        )
        assert "description" in issue, f"Issue missing 'description': {issue}"
        assert "suggestion" in issue, f"Issue missing 'suggestion': {issue}"


def _assert_faithfulness(output: str, test_input: dict[str, Any]) -> None:
    """Raise AssertionError if known critical sections are not flagged in issues.

    Args:
        output: JSON string from ProtocolReviewerAgent.
        test_input: The test input dict with ``known_issues`` field.

    Raises:
        AssertionError: When a known issue section is not present in output.

    """
    known = test_input.get("known_issues", [])
    if not known:
        return

    data: dict[str, Any] = json.loads(output)
    flagged_sections = {issue["section"] for issue in data.get("issues", [])}

    for section in known:
        assert section in flagged_sections, (
            f"Expected issue in section {section!r} but only got: {flagged_sections}"
        )


# ---------------------------------------------------------------------------
# Deepeval test cases
# ---------------------------------------------------------------------------


def build_test_cases(run_agent: bool = False) -> list[LLMTestCase]:
    """Build deepeval LLMTestCase objects for the protocol reviewer evaluation suite.

    Args:
        run_agent: Whether to call the live ProtocolReviewerAgent for each case.

    Returns:
        A list of :class:`LLMTestCase` objects ready for deepeval assertion.

    """
    cases: list[LLMTestCase] = []

    for inp in PROTOCOL_TEST_INPUTS:
        if run_agent:
            import asyncio
            actual_output = asyncio.run(_invoke_reviewer(inp))
        else:
            # Stub: produce the ideal output based on known_issues
            stub_issues = [
                {
                    "section": section,
                    "severity": "major",
                    "description": f"Known issue in {section}.",
                    "suggestion": f"Fix the {section} section.",
                }
                for section in inp.get("known_issues", [])
            ]
            actual_output = json.dumps({
                "issues": stub_issues,
                "overall_assessment": f"Stub assessment for {inp['case_id']}.",
            })

        input_text = json.dumps({
            "case_id": inp["case_id"],
            "description": inp["description"],
            "protocol": inp["protocol"],
        })

        cases.append(
            LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                expected_output=json.dumps({
                    "expected_issue_count": inp["expected_issue_count"],
                    "known_issues": inp.get("known_issues", []),
                }),
                context=[
                    "ProtocolReviewerAgent must return JSON with 'issues' and 'overall_assessment'.",
                    "Each issue must have section, severity, description, and suggestion.",
                    "severity must be critical, major, or minor.",
                    "Known problematic sections must be flagged.",
                ],
            )
        )

    return cases


async def _invoke_reviewer(inp: dict[str, Any]) -> str:
    """Call the real ProtocolReviewerAgent and return its JSON output string.

    Args:
        inp: Test input dict with a ``protocol`` key.

    Returns:
        JSON string of the review result.

    """
    from agents.services.protocol_reviewer import ProtocolReviewerAgent

    agent = ProtocolReviewerAgent()
    result = await agent.review(inp["protocol"])
    return json.dumps(result.model_dump())


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------


def run_protocol_reviewer_eval(
    run_agent: bool = False, threshold: float = 0.7
) -> dict[str, Any]:
    """Execute the ProtocolReviewerAgent deepeval pipeline.

    Validates:
    1. Output has valid JSON structure with required fields.
    2. Known problematic sections are flagged in the issues list.

    Args:
        run_agent: Whether to call the live agent (requires LLM credentials).
        threshold: Fraction of cases that must pass (default: 0.7).

    Returns:
        A dict with ``{passed, failed, total, pass_rate, errors}``.

    """
    cases = build_test_cases(run_agent=run_agent)
    inputs = PROTOCOL_TEST_INPUTS
    passed = 0
    failed = 0
    errors: list[str] = []

    for case, inp in zip(cases, inputs, strict=True):
        try:
            _assert_valid_structure(case.actual_output or "")
            _assert_faithfulness(case.actual_output or "", inp)
            passed += 1
        except AssertionError as exc:
            failed += 1
            errors.append(f"[{inp['case_id']}] {exc}")

    total = passed + failed
    pass_rate = passed / total if total > 0 else 0.0
    result = {
        "passed": passed,
        "failed": failed,
        "total": total,
        "pass_rate": pass_rate,
        "threshold": threshold,
        "threshold_met": pass_rate >= threshold,
        "errors": errors,
    }
    return result


if __name__ == "__main__":
    report = run_protocol_reviewer_eval(run_agent=False)
    print(json.dumps(report, indent=2))
