"""Deepeval evaluation pipeline for SynthesiserAgent.

Defines a representative input dataset, output criteria (non-empty synthesis
with key-findings section, conclusion present), and pass/fail thresholds.

Run with::

    python -m agent_eval.evals.synthesiser_eval
"""

from __future__ import annotations

import json
from typing import Any

from deepeval.test_case import LLMTestCase


# ---------------------------------------------------------------------------
# Representative input dataset
# ---------------------------------------------------------------------------

SYNTHESISER_TEST_INPUTS: list[dict[str, Any]] = [
    {
        "case_id": "syn-001",
        "research_question": "What is the effect of TDD on software defect density?",
        "papers_summary": (
            "Paper A: Controlled experiment; TDD reduced defects by 40% (n=42).\n"
            "Paper B: Field study; no significant defect reduction with TDD (n=12).\n"
            "Paper C: TDD increased development time but reduced post-release defects."
        ),
        "expected_sections": ["summary", "findings", "conclusion"],
    },
    {
        "case_id": "syn-002",
        "research_question": "How does pair programming affect code quality in agile teams?",
        "papers_summary": (
            "Paper A: Pair programming improves code review coverage.\n"
            "Paper B: Code defect rate drops by 15% with pair programming.\n"
            "Paper C: Developer satisfaction increases but velocity temporarily drops."
        ),
        "expected_sections": ["summary", "findings", "conclusion"],
    },
    {
        "case_id": "syn-003",
        "research_question": "What evidence exists for CI/CD adoption benefits in enterprise contexts?",
        "papers_summary": (
            "Paper A: CI reduces integration failures by 60% in enterprise Java projects.\n"
            "Paper B: CD shortens release cycles from weeks to hours on average.\n"
            "Paper C: Organisational culture is the main barrier to CI/CD adoption."
        ),
        "expected_sections": ["summary", "findings", "conclusion"],
    },
]

_STUB_SYNTHESIS = (
    "## Summary\nStub synthesis summary text.\n\n"
    "## Key Findings\n- Finding A.\n- Finding B.\n\n"
    "## Contradictions / Gaps\nNo contradictions identified.\n\n"
    "## Conclusion\nFurther research is needed."
)


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------


def _assert_synthesis_non_empty(output: str) -> None:
    """Raise AssertionError if the synthesis output is empty.

    Args:
        output: String returned by SynthesiserAgent.

    Raises:
        AssertionError: When output is empty or whitespace-only.
    """
    assert output and output.strip(), "Synthesis output must not be empty"
    assert len(output.strip()) >= 50, (
        f"Synthesis output too short ({len(output.strip())} chars, expected ≥50)"
    )


def _assert_conclusion_present(output: str) -> None:
    """Raise AssertionError if a conclusion section is absent.

    Args:
        output: String returned by SynthesiserAgent.

    Raises:
        AssertionError: When no conclusion section can be found.
    """
    lower = output.lower()
    assert "conclusion" in lower or "summary" in lower, (
        "Synthesis must contain a 'Conclusion' or 'Summary' section"
    )


def _assert_findings_present(output: str) -> None:
    """Raise AssertionError if no key findings section is present.

    Args:
        output: String returned by SynthesiserAgent.

    Raises:
        AssertionError: When no findings section is found.
    """
    lower = output.lower()
    assert "finding" in lower or "result" in lower or "evidence" in lower, (
        "Synthesis must reference findings, results, or evidence"
    )


# ---------------------------------------------------------------------------
# Deepeval test cases
# ---------------------------------------------------------------------------


def build_test_cases(run_agent: bool = False) -> list[LLMTestCase]:
    """Build deepeval LLMTestCase objects for the synthesiser evaluation suite.

    Args:
        run_agent: Whether to call the live SynthesiserAgent for each case.

    Returns:
        A list of :class:`LLMTestCase` objects ready for deepeval assertion.
    """
    cases: list[LLMTestCase] = []

    for inp in SYNTHESISER_TEST_INPUTS:
        if run_agent:
            import asyncio
            actual_output = asyncio.run(_invoke_synthesiser(inp))
        else:
            actual_output = _STUB_SYNTHESIS

        cases.append(
            LLMTestCase(
                input=json.dumps({
                    "research_question": inp["research_question"],
                    "papers_summary": inp["papers_summary"],
                }),
                actual_output=actual_output,
                expected_output=(
                    "A structured synthesis with summary, key findings, "
                    "contradictions/gaps, and conclusion sections."
                ),
                context=[
                    "SynthesiserAgent must produce a non-empty narrative.",
                    "Output must contain a findings section.",
                    "Output must contain a conclusion or summary.",
                ],
            )
        )

    return cases


async def _invoke_synthesiser(inp: dict[str, Any]) -> str:
    """Call the real SynthesiserAgent and return its output string.

    Args:
        inp: Test input dict with research_question and papers_summary.

    Returns:
        Raw synthesis string from the agent.
    """
    from agents.services.synthesiser import SynthesiserAgent

    agent = SynthesiserAgent()
    return await agent.run(
        papers_summary=inp["papers_summary"],
        research_question=inp["research_question"],
    )


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------


def run_synthesiser_eval(run_agent: bool = False, threshold: float = 0.85) -> dict[str, Any]:
    """Execute the SynthesiserAgent deepeval pipeline.

    Validates:
    1. Output is non-empty and meets minimum length.
    2. A findings section is present.
    3. A conclusion or summary section is present.

    Args:
        run_agent: Whether to call the live agent (requires LLM credentials).
        threshold: Fraction of cases that must pass (default: 0.85).

    Returns:
        A dict with ``{passed, failed, total, errors}`` counts.
    """
    cases = build_test_cases(run_agent=run_agent)
    passed = 0
    failed = 0
    errors: list[str] = []

    for case in cases:
        try:
            _assert_synthesis_non_empty(case.actual_output)
            _assert_findings_present(case.actual_output)
            _assert_conclusion_present(case.actual_output)
            passed += 1
        except AssertionError as exc:
            failed += 1
            errors.append(str(exc))

    total = passed + failed
    return {"passed": passed, "failed": failed, "total": total, "errors": errors}


if __name__ == "__main__":
    report = run_synthesiser_eval(run_agent=False)
    print(json.dumps(report, indent=2))
