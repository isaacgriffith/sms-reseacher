"""Extractor agent: pulls structured data fields from paper text."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, field_validator

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader
from agents.core.provider_config import ProviderConfig

_VALID_RESEARCH_TYPES = frozenset(
    {
        "evaluation",
        "solution_proposal",
        "validation",
        "philosophical",
        "opinion",
        "personal_experience",
        "unknown",
    }
)


class ExtractionResult(BaseModel):
    """Structured extraction output for one paper.

    All fields correspond 1-to-1 with the DataExtraction DB model columns.
    """

    research_type: str
    venue_type: str
    venue_name: str | None
    author_details: list[dict[str, Any]]
    summary: str | None
    open_codings: list[dict[str, Any]]
    keywords: list[str]
    question_data: dict[str, Any]

    @field_validator("research_type")
    @classmethod
    def validate_research_type(cls, v: str) -> str:
        """Ensure research_type is one of the R1–R6 enum values.

        Args:
            v: The raw research_type string from the LLM response.

        Returns:
            The validated research_type string.

        Raises:
            ValueError: If the value is not a recognised research type.
        """
        if v not in _VALID_RESEARCH_TYPES:
            return "unknown"
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
        raise ValueError(f"No valid JSON found in extractor response: {raw[:200]!r}")


class ExtractorAgent:
    """Agent that extracts structured data fields from paper full text.

    Applies R1–R6 research-type classification rules and returns a
    typed :class:`ExtractionResult` for each paper processed.

    When ``provider_config`` is supplied, all LLM calls are routed through
    the database-backed model configuration rather than environment variables.

    When ``system_message_override`` is supplied, the rendered study-context
    system message replaces the default prompt-file system message.

    Args:
        llm_client: Optional :class:`LLMClient` override for testing.
        provider_config: Optional :class:`ProviderConfig` for database-backed
            model routing.  When ``None``, falls back to environment settings.
        system_message_override: Optional rendered system message string that
            replaces the first system message loaded from prompt files.
    """

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        provider_config: ProviderConfig | None = None,
        system_message_override: str | None = None,
    ) -> None:
        """Initialise the extractor agent.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.
            provider_config: Optional database-resolved provider configuration.
                Passed through to each :meth:`LLMClient.complete` call.
            system_message_override: Optional rendered system message to use
                instead of the default prompt-file system message.
        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("extractor")
        self._provider_config = provider_config
        self._system_message_override = system_message_override

    async def run(
        self,
        *,
        paper_text: str,
        title: str,
        authors: list[dict[str, Any]] | None = None,
        year: int | None = None,
        venue: str | None = None,
        doi: str | None = None,
        research_questions: list[dict[str, str]] | None = None,
    ) -> ExtractionResult:
        """Extract structured data from a paper.

        Args:
            paper_text: The paper's full text or abstract.
            title: Paper title from metadata.
            authors: Author list from metadata (each a dict with ``name``,
                ``institution``, ``locale`` keys).
            year: Publication year, or ``None`` if unknown.
            venue: Journal or conference name, or ``None``.
            doi: Digital object identifier, or ``None``.
            research_questions: List of ``{id, text}`` dicts representing the
                study's research questions to answer from the paper.

        Returns:
            An :class:`ExtractionResult` with all fields populated.

        Raises:
            ValueError: If the LLM response cannot be parsed as valid JSON.
        """
        context = {
            "title": title,
            "authors": authors or [],
            "year": year,
            "venue": venue,
            "doi": doi,
            "paper_text": paper_text,
            "research_questions": research_questions or [],
        }
        messages = self._loader.load_messages(context)

        # Apply system message override if provided (Feature 005 / T062)
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

        return ExtractionResult(
            research_type=data.get("research_type", "unknown"),
            venue_type=data.get("venue_type", "other") or "other",
            venue_name=data.get("venue_name"),
            author_details=data.get("author_details") or [],
            summary=data.get("summary"),
            open_codings=data.get("open_codings") or [],
            keywords=data.get("keywords") or [],
            question_data=data.get("question_data") or {},
        )
