"""Search String Builder agent: generates Boolean search strings from PICO/C."""

import json
from typing import Any

from pydantic import BaseModel

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader


class TermGroup(BaseModel):
    """A group of search terms for one PICO/C component."""

    component: str
    terms: list[str]


class SearchStringResult(BaseModel):
    """Structured output from the SearchStringBuilderAgent."""

    search_string: str
    terms_used: list[TermGroup]
    expansion_notes: str


class SearchStringBuilderAgent:
    """Agent that generates Boolean search strings for systematic mapping studies.

    Accepts PICO/C component text, seed keywords, and inclusion/exclusion
    criteria, then produces an expanded Boolean search string with term
    explanations.

    Args:
        llm_client: Optional :class:`LLMClient` override for testing.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        """Initialise the search string builder agent.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.
        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("search_builder")

    async def run(
        self,
        topic: str,
        variant: str,
        *,
        population: str | None = None,
        intervention: str | None = None,
        comparison: str | None = None,
        outcome: str | None = None,
        context: str | None = None,
        extra_fields: dict[str, Any] | None = None,
        objectives: list[str] | None = None,
        questions: list[str] | None = None,
        seed_keywords: list[str] | None = None,
        inclusion_criteria: list[str] | None = None,
        exclusion_criteria: list[str] | None = None,
    ) -> SearchStringResult:
        """Generate a Boolean search string for the study.

        Args:
            topic: Brief topic description of the study.
            variant: PICO variant name (e.g. ``"PICO"``, ``"SPIDER"``).
            population: PICO population component text.
            intervention: PICO intervention component text.
            comparison: PICO comparison component text.
            outcome: PICO outcome component text.
            context: PICO context component text.
            extra_fields: Variant-specific additional fields.
            objectives: List of research objective strings.
            questions: List of research question strings.
            seed_keywords: Keywords extracted from seed papers.
            inclusion_criteria: Textual inclusion criterion descriptions.
            exclusion_criteria: Textual exclusion criterion descriptions.

        Returns:
            A :class:`SearchStringResult` with the Boolean string and term details.
        """
        template_context: dict[str, Any] = {
            "topic": topic,
            "variant": variant,
            "population": population,
            "intervention": intervention,
            "comparison": comparison,
            "outcome": outcome,
            "context": context,
            "extra_fields": extra_fields,
            "objectives": objectives or [],
            "questions": questions or [],
            "seed_keywords": seed_keywords or [],
            "inclusion_criteria": inclusion_criteria or [],
            "exclusion_criteria": exclusion_criteria or [],
        }
        messages = self._loader.load_messages(template_context)
        raw = await self._client.complete(messages, max_tokens=2048)

        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:])
            cleaned = cleaned.rsplit("```", 1)[0].strip()

        data: dict[str, Any] = json.loads(cleaned)
        return SearchStringResult.model_validate(data)
