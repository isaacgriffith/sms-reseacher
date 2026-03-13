"""Deepeval evaluation pipeline for DomainModelAgent.

Validates that the agent:
- Returns ≥1 concept and ≥1 relationship (non-empty output)
- Produces no duplicate concept names (case-insensitive)
- Relationship ``from`` and ``to`` fields reference names present in the
  concepts list (valid relationship direction)

Run with::

    agent-eval evaluate --agent domain_modeler

Or directly::

    python -m agent_eval.evals.domain_modeler_eval
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from deepeval.dataset import EvaluationDataset
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase


# ---------------------------------------------------------------------------
# Representative input dataset
# ---------------------------------------------------------------------------

DOMAIN_MODELER_TEST_INPUTS: list[dict[str, Any]] = [
    {
        "case_id": "dm-001",
        "topic": "Test-Driven Development in software engineering",
        "research_questions": [
            "What approaches to TDD have been proposed in the literature?",
            "What are the reported benefits and drawbacks of TDD?",
        ],
        "open_codings": [
            {"code": "Test-First", "definition": "Writing tests before production code", "evidence_quote": "tests were written before any production code"},
            {"code": "Refactoring", "definition": "Improving code structure without changing behaviour", "evidence_quote": "code was continuously refactored"},
            {"code": "Defect Reduction", "definition": "Lower defect density in TDD projects", "evidence_quote": "30% fewer defects were reported"},
            {"code": "Developer Productivity", "definition": "Impact on coding speed", "evidence_quote": "initial overhead with long-term gains"},
            {"code": "Code Coverage", "definition": "Percentage of code exercised by tests", "evidence_quote": "test coverage exceeded 90%"},
        ],
        "keywords": ["TDD", "unit testing", "agile", "refactoring", "code quality", "defects"],
        "summaries": [
            "An empirical study of TDD adoption in industrial settings found a 30% reduction in post-release defects.",
            "A controlled experiment compared TDD to waterfall-style development, measuring code coverage and defect rates.",
        ],
    },
    {
        "case_id": "dm-002",
        "topic": "Machine learning fairness in hiring decisions",
        "research_questions": [
            "How is algorithmic bias defined and measured in hiring tools?",
            "What mitigation strategies exist for reducing bias?",
        ],
        "open_codings": [
            {"code": "Algorithmic Bias", "definition": "Systematic unfairness in ML predictions", "evidence_quote": "protected attributes leaked through proxies"},
            {"code": "Fairness Metrics", "definition": "Quantitative measures of fairness", "evidence_quote": "equalised odds and demographic parity were compared"},
            {"code": "Bias Mitigation", "definition": "Techniques to reduce unfair outcomes", "evidence_quote": "reweighting the training set reduced disparity"},
            {"code": "Explainability", "definition": "Making model decisions interpretable", "evidence_quote": "SHAP values highlighted biased features"},
        ],
        "keywords": ["fairness", "bias", "hiring", "machine learning", "discrimination", "explainability"],
        "summaries": [
            "A survey of 15 hiring AI tools found that most lacked transparency about fairness criteria.",
            "A technical study proposed a post-processing step that equalised false positive rates across demographic groups.",
        ],
    },
    {
        "case_id": "dm-003",
        "topic": "DevOps practices and continuous delivery",
        "research_questions": [
            "What DevOps practices are most commonly reported in industry?",
            "How does CI/CD adoption affect deployment frequency and failure rate?",
        ],
        "open_codings": [
            {"code": "CI/CD Pipelines", "definition": "Automated build, test, and deploy workflows", "evidence_quote": "all changes triggered a full pipeline run"},
            {"code": "Infrastructure-as-Code", "definition": "Managing infrastructure through version-controlled scripts", "evidence_quote": "Terraform configs were stored in the same repo"},
            {"code": "Monitoring", "definition": "Real-time observability of production systems", "evidence_quote": "dashboards tracked error rates and latency"},
            {"code": "Deployment Frequency", "definition": "How often code is deployed to production", "evidence_quote": "teams deployed multiple times per day"},
            {"code": "Mean Time to Recovery", "definition": "Average time to restore after a failure", "evidence_quote": "MTTR dropped from hours to minutes after DevOps adoption"},
        ],
        "keywords": ["DevOps", "CI/CD", "continuous delivery", "deployment", "monitoring", "infrastructure"],
        "summaries": [
            "An industry survey reported that teams using CI/CD deploy 30× more frequently than those without.",
            "A case study at a large enterprise showed DevOps reduced MTTR by 70%.",
        ],
    },
]

PASS_THRESHOLD = 1.0  # All structural checks must pass


# ---------------------------------------------------------------------------
# Structural validation helpers
# ---------------------------------------------------------------------------


def _assert_min_concepts(output: str) -> None:
    """Raise AssertionError if the output has fewer than 1 concept.

    Args:
        output: JSON string produced by DomainModelAgent.

    Raises:
        AssertionError: When the concepts list is empty.
    """
    data: dict[str, Any] = json.loads(output)
    concepts = data.get("concepts", [])
    assert len(concepts) >= 1, f"Expected ≥1 concept, got {len(concepts)}. Output: {output[:300]}"


def _assert_min_relationships(output: str) -> None:
    """Raise AssertionError if the output has fewer than 1 relationship.

    Args:
        output: JSON string produced by DomainModelAgent.

    Raises:
        AssertionError: When the relationships list is empty.
    """
    data: dict[str, Any] = json.loads(output)
    relationships = data.get("relationships", [])
    assert len(relationships) >= 1, (
        f"Expected ≥1 relationship, got {len(relationships)}. Output: {output[:300]}"
    )


def _assert_no_duplicate_concept_names(output: str) -> None:
    """Raise AssertionError if concept names are not unique (case-insensitive).

    Args:
        output: JSON string produced by DomainModelAgent.

    Raises:
        AssertionError: When duplicate concept names are detected.
    """
    data: dict[str, Any] = json.loads(output)
    names = [c.get("name", "").lower() for c in data.get("concepts", [])]
    seen: set[str] = set()
    for name in names:
        assert name not in seen, (
            f"Duplicate concept name '{name}' detected in domain model output."
        )
        seen.add(name)


def _assert_valid_relationship_directions(output: str) -> None:
    """Raise AssertionError if any relationship references an undefined concept.

    Args:
        output: JSON string produced by DomainModelAgent.

    Raises:
        AssertionError: When a relationship ``from`` or ``to`` does not match
            a concept name in the output.
    """
    data: dict[str, Any] = json.loads(output)
    concept_names = {c.get("name", "").lower() for c in data.get("concepts", [])}
    for rel in data.get("relationships", []):
        from_name = rel.get("from", "").lower()
        to_name = rel.get("to", "").lower()
        assert from_name in concept_names, (
            f"Relationship 'from' value '{rel.get('from')}' is not in the concepts list."
        )
        assert to_name in concept_names, (
            f"Relationship 'to' value '{rel.get('to')}' is not in the concepts list."
        )


# ---------------------------------------------------------------------------
# Deepeval test case builder
# ---------------------------------------------------------------------------


def build_test_cases(run_agent: bool = False) -> list[LLMTestCase]:
    """Build deepeval LLMTestCase objects for the domain-modeler evaluation suite.

    When *run_agent* is ``False`` (default for CI without LLM credentials) the
    ``actual_output`` is set to a structurally valid stub so criteria checks
    run without calling the LLM.  Set *run_agent=True* to call the real agent.

    Args:
        run_agent: Whether to call the live DomainModelAgent for each case.

    Returns:
        A list of :class:`LLMTestCase` objects ready for evaluation.
    """
    cases: list[LLMTestCase] = []

    for inp in DOMAIN_MODELER_TEST_INPUTS:
        if run_agent:
            actual_output = asyncio.run(_invoke_domain_modeler(inp))
        else:
            # Structurally valid stub — skips LLM call
            actual_output = json.dumps({
                "concepts": [
                    {
                        "name": "Stub Concept A",
                        "definition": "A stub concept for " + inp["topic"],
                        "attributes": ["attribute-1"],
                    },
                    {
                        "name": "Stub Concept B",
                        "definition": "A second stub concept.",
                        "attributes": [],
                    },
                ],
                "relationships": [
                    {
                        "from": "Stub Concept A",
                        "to": "Stub Concept B",
                        "label": "supports",
                        "type": "supports",
                    }
                ],
            })

        input_text = json.dumps({
            "topic": inp["topic"],
            "research_questions": inp["research_questions"],
            "open_codings_count": len(inp["open_codings"]),
            "keywords": inp["keywords"],
        })

        cases.append(
            LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                expected_output=None,
                context=[
                    "DomainModelAgent must return a JSON object with 'concepts' and 'relationships' keys.",
                    "Concepts must have unique names (case-insensitive).",
                    "Relationships must reference concept names present in the concepts list.",
                    "Output must contain ≥1 concept and ≥1 relationship.",
                ],
            )
        )

    return cases


async def _invoke_domain_modeler(inp: dict[str, Any]) -> str:
    """Call the live DomainModelAgent and return its serialised JSON output.

    Args:
        inp: Test input dictionary from DOMAIN_MODELER_TEST_INPUTS.

    Returns:
        JSON string of the DomainModelResult.
    """
    from agents.services.domain_modeler import DomainModelAgent

    agent = DomainModelAgent()
    result = await agent.run(
        topic=inp["topic"],
        research_questions=inp.get("research_questions", []),
        open_codings=inp.get("open_codings", []),
        keywords=inp.get("keywords", []),
        summaries=inp.get("summaries", []),
    )
    return json.dumps({
        "concepts": [c.model_dump() for c in result.concepts],
        "relationships": [
            {"from": r.from_, "to": r.to, "label": r.label, "type": r.type}
            for r in result.relationships
        ],
    })


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------


def run_domain_modeler_eval(run_agent: bool = False, threshold: float = PASS_THRESHOLD) -> dict[str, Any]:
    """Execute the DomainModelAgent deepeval pipeline.

    Validates per-test-case:
    1. Output contains ≥1 concept.
    2. Output contains ≥1 relationship.
    3. Concept names are unique (case-insensitive).
    4. All relationship ``from``/``to`` values reference defined concepts.

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
        _assert_min_concepts,
        _assert_min_relationships,
        _assert_no_duplicate_concept_names,
        _assert_valid_relationship_directions,
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
    report = run_domain_modeler_eval(run_agent=False)
    print(json.dumps(report, indent=2))
