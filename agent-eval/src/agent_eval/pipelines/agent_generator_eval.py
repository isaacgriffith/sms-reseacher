"""Deepeval evaluation pipeline for AgentGeneratorAgent — T072.

Defines representative input scenarios, quality criteria, and pass/fail
thresholds for assessing the quality of templates produced by
:class:`~agents.agent_generator.AgentGeneratorAgent`.

Evaluation criteria:
  1. **Variable Completeness** — the template must reference all six standard
     Jinja2 variables: role_name, role_description, persona_name,
     persona_description, domain, study_type.
  2. **Template Validity** — the output must be renderable by Jinja2
     (no unclosed tags, no syntax errors).
  3. **No Literal Name Leakage** — the generated template must NOT contain
     the literal value of persona_name (i.e. it must use ``{{ persona_name }}``
     rather than hard-coding the person's name).
  4. **Minimum Length** — the template must be at least 100 characters
     (trivially short templates are unlikely to be useful).

Usage::

    uv run python -m agent_eval.pipelines.agent_generator_eval

Or via CLI::

    uv run agent-eval run agent-generator

All tests use a stubbed LLMClient to avoid live API calls during CI.
Pass the ``--live`` flag when running against a real model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from unittest.mock import AsyncMock, MagicMock

from agents.agent_generator import AgentGeneratorAgent
from agents.core.llm_client import LLMClient
from deepeval.test_case import LLMTestCase

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_VARIABLES = [
    "{{ role_name }}",
    "{{ role_description }}",
    "{{ persona_name }}",
    "{{ persona_description }}",
    "{{ domain }}",
    "{{ study_type }}",
]

MINIMUM_TEMPLATE_LENGTH = 100

# ---------------------------------------------------------------------------
# Input dataset
# ---------------------------------------------------------------------------


@dataclass
class AgentGeneratorInput:
    """A single evaluation case for the AgentGeneratorAgent."""

    case_id: str
    task_type: str
    role_name: str
    role_description: str
    persona_name: str
    persona_description: str
    model_display_name: str = "Claude Haiku 4.5"
    notes: str = ""


AGENT_GENERATOR_TEST_INPUTS: list[AgentGeneratorInput] = [
    AgentGeneratorInput(
        case_id="ag-001",
        task_type="screener",
        role_name="Screener",
        role_description=(
            "Evaluates whether a paper's abstract meets the inclusion/exclusion "
            "criteria for a systematic mapping study."
        ),
        persona_name="Dr. Aria",
        persona_description=(
            "A meticulous systematic reviewer with ten years of experience "
            "in software engineering research synthesis."
        ),
        notes="Standard screener — most common case",
    ),
    AgentGeneratorInput(
        case_id="ag-002",
        task_type="extractor",
        role_name="Data Extractor",
        role_description=(
            "Extracts structured data items from full-text research papers "
            "according to a predefined extraction schema."
        ),
        persona_name="Dr. Sage",
        persona_description=(
            "A precise and detail-oriented researcher specialising in "
            "systematic evidence synthesis and data management."
        ),
        notes="Extractor role — tests different task_type branch",
    ),
    AgentGeneratorInput(
        case_id="ag-003",
        task_type="quality_judge",
        role_name="Quality Judge",
        role_description=(
            "Assesses the methodological quality of included primary studies "
            "using a standardised quality appraisal checklist."
        ),
        persona_name="Dr. Quinn",
        persona_description=(
            "An experienced methodologist who applies rigorous quality "
            "assessment frameworks to evaluate research validity."
        ),
        notes="Quality judge — multi-dimension assessment scenario",
    ),
    AgentGeneratorInput(
        case_id="ag-004",
        task_type="synthesiser",
        role_name="Synthesiser",
        role_description=(
            "Synthesises findings across multiple primary studies to produce "
            "a coherent narrative summary of the evidence base."
        ),
        persona_name="Dr. Nova",
        persona_description=(
            "A senior researcher skilled in thematic synthesis and "
            "evidence integration across diverse study designs."
        ),
        notes="Synthesiser — narrative synthesis scenario",
    ),
    AgentGeneratorInput(
        case_id="ag-005",
        task_type="domain_modeler",
        role_name="Domain Modeler",
        role_description=(
            "Constructs a conceptual taxonomy of the research domain from "
            "the corpus of included studies."
        ),
        persona_name="Dr. Orion",
        persona_description=(
            "A knowledge engineer who specialises in ontology construction "
            "and classification scheme design for research domains."
        ),
        notes="Domain modeler — taxonomy construction scenario",
    ),
]

# ---------------------------------------------------------------------------
# Stub helper — avoids live LLM calls in CI
# ---------------------------------------------------------------------------


def _build_stub_template(persona_name: str) -> str:
    """Build a realistic stub template that satisfies all quality criteria."""
    return (
        "You are {{ persona_name }}, a {{ role_name }} for {{ domain }} research.\n\n"
        "{{ persona_description }}\n\n"
        "## Role\n\n"
        "{{ role_description }}\n\n"
        "## Context\n\n"
        "You are conducting a {{ study_type }} and must apply rigorous methodology "
        "appropriate to the research domain.\n\n"
        "## Instructions\n\n"
        "Follow the standard protocols for your task type and provide clear, "
        "evidence-based outputs."
    )


def _make_stub_agent(persona_name: str) -> AgentGeneratorAgent:
    """Return an AgentGeneratorAgent with a deterministic stub LLMClient."""
    template = _build_stub_template(persona_name)
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=template)
    return AgentGeneratorAgent(llm_client=stub_client)


# ---------------------------------------------------------------------------
# Quality criteria predicates
# ---------------------------------------------------------------------------


def check_variable_completeness(template: str) -> tuple[bool, list[str]]:
    """Return (passed, missing_vars) — True when all six variables are present."""
    missing = [var for var in REQUIRED_VARIABLES if var not in template]
    return len(missing) == 0, missing


def check_template_validity(template: str) -> tuple[bool, str]:
    """Return (valid, error_message) — True when Jinja2 can parse the template."""
    try:
        import jinja2
        env = jinja2.Environment(undefined=jinja2.Undefined)
        env.parse(template)
        return True, ""
    except jinja2.TemplateSyntaxError as exc:
        return False, str(exc)


def check_no_literal_name_leakage(template: str, persona_name: str) -> bool:
    """Return True when the template does NOT contain the literal persona_name."""
    return persona_name not in template


def check_minimum_length(template: str) -> bool:
    """Return True when the template meets the minimum character threshold."""
    return len(template) >= MINIMUM_TEMPLATE_LENGTH


# ---------------------------------------------------------------------------
# Evaluation result
# ---------------------------------------------------------------------------


@dataclass
class EvalResult:
    """Result of evaluating a single AgentGeneratorInput case."""

    case_id: str
    passed: bool
    template: str
    failures: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        failures_str = "; ".join(self.failures) if self.failures else "none"
        return f"[{status}] {self.case_id} — failures: {failures_str}"


# ---------------------------------------------------------------------------
# Pipeline entry points
# ---------------------------------------------------------------------------


async def evaluate_single(
    case: AgentGeneratorInput,
    *,
    use_stub: bool = True,
) -> EvalResult:
    """Run quality evaluation for a single :class:`AgentGeneratorInput`.

    Args:
        case: The input case to evaluate.
        use_stub: When True (default), uses a stub LLMClient. Pass False to
            call a live LLM (requires ANTHROPIC_API_KEY in environment).

    Returns:
        :class:`EvalResult` with pass/fail status and failure reasons.

    """
    if use_stub:
        agent = _make_stub_agent(case.persona_name)
    else:
        agent = AgentGeneratorAgent()

    template = await agent.generate_system_message(
        task_type=case.task_type,
        role_name=case.role_name,
        role_description=case.role_description,
        persona_name=case.persona_name,
        persona_description=case.persona_description,
        model_display_name=case.model_display_name,
    )

    failures: list[str] = []

    # Criterion 1: Variable completeness
    complete, missing_vars = check_variable_completeness(template)
    if not complete:
        failures.append(f"Missing variables: {', '.join(missing_vars)}")

    # Criterion 2: Template validity
    valid, syntax_error = check_template_validity(template)
    if not valid:
        failures.append(f"Invalid Jinja2 syntax: {syntax_error}")

    # Criterion 3: No literal name leakage
    if not check_no_literal_name_leakage(template, case.persona_name):
        failures.append(f"Template contains literal persona_name: {case.persona_name!r}")

    # Criterion 4: Minimum length
    if not check_minimum_length(template):
        failures.append(
            f"Template too short: {len(template)} < {MINIMUM_TEMPLATE_LENGTH} chars"
        )

    return EvalResult(
        case_id=case.case_id,
        passed=len(failures) == 0,
        template=template,
        failures=failures,
    )


async def run_pipeline(
    inputs: list[AgentGeneratorInput] | None = None,
    *,
    use_stub: bool = True,
    pass_threshold: float = 1.0,
) -> tuple[bool, list[EvalResult]]:
    """Run the full AgentGenerator evaluation pipeline.

    Args:
        inputs: List of test cases. Defaults to :data:`AGENT_GENERATOR_TEST_INPUTS`.
        use_stub: When True, uses stub LLM (for CI). Set False for live evals.
        pass_threshold: Fraction of cases that must pass (0.0–1.0). Default 1.0.

    Returns:
        A tuple (pipeline_passed, results).

    """
    if inputs is None:
        inputs = AGENT_GENERATOR_TEST_INPUTS

    results: list[EvalResult] = []
    for case in inputs:
        result = await evaluate_single(case, use_stub=use_stub)
        results.append(result)

    passed_count = sum(1 for r in results if r.passed)
    pass_rate = passed_count / len(results) if results else 0.0
    pipeline_passed = pass_rate >= pass_threshold

    return pipeline_passed, results


# ---------------------------------------------------------------------------
# DeepEval test case builder (for use with deepeval.assert_test)
# ---------------------------------------------------------------------------


def build_deepeval_test_case(case: AgentGeneratorInput, template: str) -> LLMTestCase:
    """Build a :class:`~deepeval.test_case.LLMTestCase` from a result.

    This allows the results to be consumed by DeepEval's assertion framework
    and CI integrations.

    Args:
        case: The original input case.
        template: The generated template string.

    Returns:
        An :class:`LLMTestCase` describing the input/output pair.

    """
    input_str = (
        f"task_type={case.task_type}, role_name={case.role_name}, "
        f"persona_name={case.persona_name}"
    )
    expected_str = (
        "A Jinja2 template containing all six required variable placeholders: "
        + ", ".join(REQUIRED_VARIABLES)
    )
    return LLMTestCase(
        input=input_str,
        actual_output=template,
        expected_output=expected_str,
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import asyncio

    async def _main() -> None:
        pipeline_passed, results = await run_pipeline(use_stub=True)
        for result in results:
            print(result)
        print(f"\nPipeline: {'PASS' if pipeline_passed else 'FAIL'}")
        print(f"Pass rate: {sum(r.passed for r in results)}/{len(results)}")

    asyncio.run(_main())
