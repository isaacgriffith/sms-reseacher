"""Domain Modeler agent: synthesises domain concepts and relationships from extracted data."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, field_validator

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader
from agents.core.provider_config import ProviderConfig


class Concept(BaseModel):
    """A domain concept identified across the body of papers."""

    name: str
    definition: str
    attributes: list[str] = []


class Relationship(BaseModel):
    """A directed relationship between two domain concepts."""

    from_: str
    to: str
    label: str
    type: str

    model_config = {"populate_by_name": True}


class DomainModelResult(BaseModel):
    """Structured output from the DomainModelAgent.

    Contains the full set of domain concepts and directed relationships
    synthesised from the study's extracted paper data.
    """

    concepts: list[Concept]
    relationships: list[Relationship]

    @field_validator("concepts")
    @classmethod
    def validate_unique_concept_names(cls, v: list[Concept]) -> list[Concept]:
        """Ensure concept names are unique (case-insensitive).

        Args:
            v: The list of concepts to validate.

        Returns:
            The validated list of concepts.

        Raises:
            ValueError: If duplicate concept names are detected.

        """
        seen: set[str] = set()
        for concept in v:
            key = concept.name.lower()
            if key in seen:
                raise ValueError(f"Duplicate concept name: {concept.name!r}")
            seen.add(key)
        return v


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
        raise ValueError(f"No valid JSON found in domain modeler response: {raw[:200]!r}") from None


class DomainModelAgent:
    """Agent that builds a domain model from aggregated extraction data.

    Synthesises open codings, keywords, and paper summaries from all accepted
    papers in a study into a typed :class:`DomainModelResult`.

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
        """Initialise the domain modeler agent.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.
            provider_config: Optional database-resolved provider configuration.
                Passed through to each :meth:`LLMClient.complete` call.
            system_message_override: Optional rendered system message to use
                instead of the default prompt-file system message.

        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("domain_modeler")
        self._provider_config = provider_config
        self._system_message_override = system_message_override

    async def run(
        self,
        *,
        topic: str,
        research_questions: list[str] | None = None,
        open_codings: list[dict[str, Any]] | None = None,
        keywords: list[str] | None = None,
        summaries: list[str] | None = None,
    ) -> DomainModelResult:
        """Build a domain model from aggregated extraction data.

        Args:
            topic: Brief topic description of the study.
            research_questions: List of research question strings for the study.
            open_codings: Aggregated list of open-coding dicts, each with
                ``code``, ``definition``, and optional ``evidence_quote`` keys.
            keywords: Deduplicated list of keywords across all papers.
            summaries: Per-paper summary strings (one per accepted paper).

        Returns:
            A :class:`DomainModelResult` with concepts and relationships.

        Raises:
            ValueError: If the LLM response cannot be parsed as valid JSON.

        """
        all_codings = open_codings or []
        all_keywords = keywords or []
        all_summaries = summaries or []
        context: dict[str, Any] = {
            "topic": topic,
            "research_questions": research_questions or [],
            "open_codings": all_codings,
            "keywords": all_keywords,
            "summaries": all_summaries,
            "paper_count": len(all_summaries),
        }
        messages = self._loader.load_messages(context)

        # Apply system message override if provided (Feature 005 / T063)
        if self._system_message_override is not None:
            messages = list(messages)
            for i, msg in enumerate(messages):
                if msg.get("role") == "system":
                    messages[i] = {"role": "system", "content": self._system_message_override}
                    break

        raw = await self._client.complete(
            messages, max_tokens=4096, provider_config=self._provider_config
        )
        data = _extract_json(raw)

        relationships = [
            Relationship(
                from_=rel.get("from", ""),
                to=rel.get("to", ""),
                label=rel.get("label", ""),
                type=rel.get("type", "other"),
            )
            for rel in (data.get("relationships") or [])
        ]

        return DomainModelResult(
            concepts=[Concept.model_validate(c) for c in (data.get("concepts") or [])],
            relationships=relationships,
        )
