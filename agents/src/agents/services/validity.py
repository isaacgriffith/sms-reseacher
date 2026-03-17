"""Validity agent: generates pre-populated draft validity discussion text."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, field_validator

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader
from agents.core.provider_config import ProviderConfig

_VALIDITY_DIMS = (
    "descriptive",
    "theoretical",
    "generalizability_internal",
    "generalizability_external",
    "interpretive",
    "repeatability",
)


class ValidityResult(BaseModel):
    """Pre-populated draft text for all six validity discussion dimensions.

    All fields are non-empty strings after validation.
    """

    descriptive: str
    theoretical: str
    generalizability_internal: str
    generalizability_external: str
    interpretive: str
    repeatability: str

    @field_validator(
        "descriptive",
        "theoretical",
        "generalizability_internal",
        "generalizability_external",
        "interpretive",
        "repeatability",
    )
    @classmethod
    def require_non_empty(cls, v: str) -> str:
        """Ensure each validity dimension is a non-empty, non-whitespace string.

        Args:
            v: The raw dimension value from the LLM response.

        Returns:
            The stripped string value.

        Raises:
            ValueError: If the value is empty or whitespace-only.
        """
        stripped = (v or "").strip()
        if not stripped:
            raise ValueError("Validity dimension must not be empty.")
        return stripped


def _extract_json(raw: str) -> dict[str, Any]:
    """Strip markdown fences and parse JSON from the LLM response.

    Args:
        raw: The raw string returned by the LLM.

    Returns:
        The parsed JSON object.

    Raises:
        ValueError: If no valid JSON object can be found in the response.
    """
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"No valid JSON found in validity agent response: {raw[:200]!r}")


def _build_context(
    *,
    study_id: int,
    study_name: str | None,
    study_type: str | None,
    current_phase: int,
    pico_components: list[dict[str, Any]],
    search_strategies: list[dict[str, Any]],
    databases: str | None,
    test_retest_done: bool,
    reviewers: list[dict[str, Any]],
    inclusion_criteria: list[str],
    exclusion_criteria: list[str],
    extraction_summary: str | None,
) -> dict[str, Any]:
    """Build the Jinja2 template context dict from keyword arguments.

    Args:
        study_id: Study primary key.
        study_name: Human-readable study name.
        study_type: Study type enum value string.
        current_phase: Current SMS workflow phase (1–5).
        pico_components: List of PICO component dicts with ``type`` and ``content``.
        search_strategies: List of search string dicts with ``string_text`` and ``version``.
        databases: Comma-separated list of databases queried, or None.
        test_retest_done: Whether test-retest search validation was performed.
        reviewers: List of reviewer config dicts.
        inclusion_criteria: List of inclusion criterion description strings.
        exclusion_criteria: List of exclusion criterion description strings.
        extraction_summary: Human-readable summary of extraction results, or None.

    Returns:
        Context dict suitable for the Jinja2 prompt template.
    """
    return {
        "study_id": study_id,
        "study_name": study_name,
        "study_type": study_type,
        "current_phase": current_phase,
        "pico_components": pico_components,
        "search_strategies": search_strategies,
        "databases": databases,
        "test_retest_done": test_retest_done,
        "reviewers": reviewers,
        "inclusion_criteria": inclusion_criteria,
        "exclusion_criteria": exclusion_criteria,
        "extraction_summary": extraction_summary,
    }


class ValidityAgent:
    """Agent that generates pre-populated draft validity discussion text.

    Accepts a study snapshot containing PICO components, search strategy
    summary, criteria, reviewer configuration, and extraction summary.
    Returns a :class:`ValidityResult` with all six validity dimensions
    populated as draft text for researcher review.

    When ``provider_config`` is supplied, all LLM calls are routed through
    the database-backed model configuration rather than environment variables.

    Args:
        llm_client: Optional :class:`LLMClient` override for testing.
        provider_config: Optional :class:`ProviderConfig` for database-backed
            model routing.  When ``None``, falls back to environment settings.
    """

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        provider_config: ProviderConfig | None = None,
        system_message_override: str | None = None,
    ) -> None:
        """Initialise the validity agent.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.
            provider_config: Optional database-resolved provider configuration.
                Passed through to each :meth:`LLMClient.complete` call.
            system_message_override: Optional rendered system message to use
                instead of the default prompt-file system message.
        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("validity")
        self._provider_config = provider_config
        self._system_message_override = system_message_override

    async def run(
        self,
        *,
        study_id: int,
        study_name: str | None = None,
        study_type: str | None = None,
        current_phase: int = 1,
        pico_components: list[dict[str, Any]] | None = None,
        search_strategies: list[dict[str, Any]] | None = None,
        databases: str | None = None,
        test_retest_done: bool = False,
        reviewers: list[dict[str, Any]] | None = None,
        inclusion_criteria: list[str] | None = None,
        exclusion_criteria: list[str] | None = None,
        extraction_summary: str | None = None,
    ) -> ValidityResult:
        """Generate pre-populated draft validity discussion for all six dimensions.

        Args:
            study_id: Study primary key.
            study_name: Human-readable study name.
            study_type: Study type enum value string.
            current_phase: Current SMS workflow phase (1–5).
            pico_components: List of PICO component dicts with ``type`` and
                ``content`` keys.
            search_strategies: List of search string dicts with ``string_text``
                and ``version`` keys.
            databases: Comma-separated database names queried, or ``None``.
            test_retest_done: Whether test-retest search validation was performed.
            reviewers: List of reviewer config dicts.
            inclusion_criteria: List of inclusion criterion description strings.
            exclusion_criteria: List of exclusion criterion description strings.
            extraction_summary: Summary of data extraction results, or ``None``.

        Returns:
            A :class:`ValidityResult` with all six validity dimensions populated.

        Raises:
            ValueError: If the LLM response cannot be parsed, or if any
                dimension is empty in the parsed result.
        """
        context = _build_context(
            study_id=study_id,
            study_name=study_name,
            study_type=study_type,
            current_phase=current_phase,
            pico_components=pico_components or [],
            search_strategies=search_strategies or [],
            databases=databases,
            test_retest_done=test_retest_done,
            reviewers=reviewers or [],
            inclusion_criteria=inclusion_criteria or [],
            exclusion_criteria=exclusion_criteria or [],
            extraction_summary=extraction_summary,
        )
        messages = self._loader.load_messages(context)

        # Apply system message override if provided (Feature 005 / T063)
        if self._system_message_override is not None:
            messages = list(messages)
            for i, msg in enumerate(messages):
                if msg.get("role") == "system":
                    messages[i] = {"role": "system", "content": self._system_message_override}
                    break

        raw = await self._client.complete(
            messages, max_tokens=3000, provider_config=self._provider_config
        )
        data = _extract_json(raw)

        return ValidityResult(
            descriptive=data.get("descriptive", ""),
            theoretical=data.get("theoretical", ""),
            generalizability_internal=data.get("generalizability_internal", ""),
            generalizability_external=data.get("generalizability_external", ""),
            interpretive=data.get("interpretive", ""),
            repeatability=data.get("repeatability", ""),
        )
