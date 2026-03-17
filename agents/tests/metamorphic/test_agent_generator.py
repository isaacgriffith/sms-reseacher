"""Metamorphic tests for AgentGeneratorAgent — T071.

Metamorphic Relations:
  MR-AG1: Persona Rename Neutrality
    Changing persona_name does not change whether the output template contains
    the ``{{ persona_name }}`` placeholder (the variable reference, not the
    literal name). The template must always include the six standard variables.

  MR-AG2: Role Description Elaboration
    Adding extra detail to role_description does not remove any of the six
    required Jinja2 variable placeholders from the generated template.

  MR-AG3: Task Type Invariance for Required Variables
    Regardless of the task_type value, the generated template must contain
    all six standard variables.

Because tests must not make live LLM calls, the LLMClient is stubbed with a
deterministic response that contains all six required placeholders.
"""

from __future__ import annotations

import re
from unittest.mock import AsyncMock, MagicMock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from agents.agent_generator import AgentGeneratorAgent
from agents.core.llm_client import LLMClient

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

VALID_TASK_TYPES = [
    "screener",
    "extractor",
    "librarian",
    "expert",
    "quality_judge",
    "domain_modeler",
    "synthesiser",
    "validity_assessor",
]

# Deterministic stub template — always contains all six required variables
_STUB_TEMPLATE = (
    "You are {{ persona_name }}, a {{ role_name }} for {{ domain }} research.\n\n"
    "{{ persona_description }}\n\n"
    "{{ role_description }}\n\n"
    "You specialise in {{ study_type }} workflows."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_stub_agent(response: str = _STUB_TEMPLATE) -> AgentGeneratorAgent:
    """Return an AgentGeneratorAgent backed by a stub LLMClient."""
    stub_client = MagicMock(spec=LLMClient)
    stub_client.complete = AsyncMock(return_value=response)
    return AgentGeneratorAgent(llm_client=stub_client)


def _has_all_variables(template: str) -> bool:
    """Return True iff *template* contains all six required Jinja2 variables."""
    return all(var in template for var in REQUIRED_VARIABLES)


def _count_variables(template: str) -> dict[str, int]:
    """Return a count of occurrences of each required variable in template."""
    return {var: template.count(var) for var in REQUIRED_VARIABLES}


# ---------------------------------------------------------------------------
# MR-AG1: Persona Rename Neutrality
# ---------------------------------------------------------------------------


class TestPersonaRenameNeutrality:
    """MR-AG1: persona_name change does not affect required placeholder presence."""

    @given(
        persona_name_1=st.text(min_size=2, max_size=30, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs"))).filter(str.strip),
        persona_name_2=st.text(min_size=2, max_size=30, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs"))).filter(str.strip),
    )
    @settings(max_examples=20)
    async def test_persona_rename_preserves_variable_placeholders(
        self, persona_name_1: str, persona_name_2: str
    ) -> None:
        """Both persona names produce a template with all required placeholders."""
        agent = _make_stub_agent()

        result_1 = await agent.generate_system_message(
            task_type="screener",
            role_name="Screener",
            role_description="Evaluates abstracts against inclusion criteria.",
            persona_name=persona_name_1.strip() or "Dr. Alpha",
            persona_description="A meticulous reviewer.",
            model_display_name="Claude Haiku",
        )

        result_2 = await agent.generate_system_message(
            task_type="screener",
            role_name="Screener",
            role_description="Evaluates abstracts against inclusion criteria.",
            persona_name=persona_name_2.strip() or "Dr. Beta",
            persona_description="A meticulous reviewer.",
            model_display_name="Claude Haiku",
        )

        # MR-AG1: Both results must contain all required placeholders
        assert _has_all_variables(result_1), (
            f"Result with persona_name={persona_name_1!r} missing variables:\n{result_1}"
        )
        assert _has_all_variables(result_2), (
            f"Result with persona_name={persona_name_2!r} missing variables:\n{result_2}"
        )


# ---------------------------------------------------------------------------
# MR-AG2: Role Description Elaboration
# ---------------------------------------------------------------------------


class TestRoleDescriptionElaboration:
    """MR-AG2: Adding detail to role_description does not remove required vars."""

    @given(
        base_description=st.text(
            min_size=5, max_size=80,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs", "Po")),
        ),
        extra_detail=st.text(
            min_size=5, max_size=80,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs", "Po")),
        ),
    )
    @settings(max_examples=20)
    async def test_elaborated_description_preserves_required_vars(
        self, base_description: str, extra_detail: str
    ) -> None:
        """Elaborating role_description does not drop any required Jinja2 variable."""
        agent = _make_stub_agent()

        base_result = await agent.generate_system_message(
            task_type="extractor",
            role_name="Extractor",
            role_description=base_description or "Extracts data from papers.",
            persona_name="Dr. Extract",
            persona_description="A precise data extractor.",
            model_display_name="Claude Haiku",
        )

        elaborated_result = await agent.generate_system_message(
            task_type="extractor",
            role_name="Extractor",
            role_description=(base_description or "Extracts data from papers.") + " " + (extra_detail or "With high accuracy."),
            persona_name="Dr. Extract",
            persona_description="A precise data extractor.",
            model_display_name="Claude Haiku",
        )

        # MR-AG2: Both must contain all required variables
        assert _has_all_variables(base_result), (
            f"Base result missing variables:\n{base_result}"
        )
        assert _has_all_variables(elaborated_result), (
            f"Elaborated result missing variables:\n{elaborated_result}"
        )


# ---------------------------------------------------------------------------
# MR-AG3: Task Type Invariance for Required Variables
# ---------------------------------------------------------------------------


class TestTaskTypeInvariance:
    """MR-AG3: Required variables appear regardless of task_type."""

    @pytest.mark.parametrize("task_type", VALID_TASK_TYPES)
    async def test_all_task_types_include_required_variables(
        self, task_type: str
    ) -> None:
        """Every task_type produces a template with all six required placeholders."""
        agent = _make_stub_agent()

        result = await agent.generate_system_message(
            task_type=task_type,
            role_name=f"{task_type.title()} Agent",
            role_description=f"Performs {task_type} tasks for research studies.",
            persona_name="Dr. Generic",
            persona_description="An expert research assistant.",
            model_display_name="Claude Haiku",
        )

        assert _has_all_variables(result), (
            f"task_type={task_type!r} produced template missing required vars:\n{result}"
        )

    async def test_two_different_task_types_both_have_all_variables(self) -> None:
        """Both screener and extractor task types produce complete templates."""
        agent = _make_stub_agent()

        screener_result = await agent.generate_system_message(
            task_type="screener",
            role_name="Screener",
            role_description="Screens papers against inclusion/exclusion criteria.",
            persona_name="Dr. Screen",
            persona_description="A meticulous abstract reviewer.",
            model_display_name="Claude Haiku",
        )

        extractor_result = await agent.generate_system_message(
            task_type="extractor",
            role_name="Extractor",
            role_description="Extracts structured data from full-text papers.",
            persona_name="Dr. Extract",
            persona_description="A precise data extraction specialist.",
            model_display_name="Claude Haiku",
        )

        assert _has_all_variables(screener_result), f"Screener template missing vars:\n{screener_result}"
        assert _has_all_variables(extractor_result), f"Extractor template missing vars:\n{extractor_result}"


# ---------------------------------------------------------------------------
# Additional sanity: stub always returns the template we configured
# ---------------------------------------------------------------------------


class TestStubBehavior:
    """Sanity checks for the test stub itself."""

    async def test_stub_returns_configured_template(self) -> None:
        """The stub LLMClient returns the configured response verbatim."""
        custom_template = "Hello {{ role_name }} — {{ persona_name }} — {{ domain }} — {{ study_type }} — {{ role_description }} — {{ persona_description }}"
        agent = _make_stub_agent(response=custom_template)

        result = await agent.generate_system_message(
            task_type="screener",
            role_name="Screener",
            role_description="Screens papers.",
            persona_name="Dr. Test",
            persona_description="Test persona.",
            model_display_name="Test Model",
        )

        assert result == custom_template

    async def test_stub_returns_string(self) -> None:
        """generate_system_message returns a str."""
        agent = _make_stub_agent()

        result = await agent.generate_system_message(
            task_type="screener",
            role_name="R",
            role_description="D",
            persona_name="P",
            persona_description="Pd",
            model_display_name="M",
        )

        assert isinstance(result, str)
