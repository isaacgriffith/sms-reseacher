"""Librarian agent: suggests seed papers and authors for a study."""

import json
from typing import Any

from pydantic import BaseModel

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader


class SuggestedPaper(BaseModel):
    """A paper suggested by the Librarian agent."""

    title: str
    authors: list[str]
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    rationale: str


class SuggestedAuthor(BaseModel):
    """An author suggested by the Librarian agent."""

    author_name: str
    institution: str | None = None
    profile_url: str | None = None
    rationale: str


class LibrarianResult(BaseModel):
    """Structured output from the Librarian agent."""

    papers: list[SuggestedPaper]
    authors: list[SuggestedAuthor]


class LibrarianAgent:
    """Agent that suggests seed papers and key authors for a systematic study.

    Uses the ``librarian`` prompt templates with the configured LLM to
    produce a structured list of relevant seed papers and authors.

    Args:
        llm_client: Optional :class:`LLMClient` override for testing.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        """Initialise the librarian agent.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.
        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("librarian")

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
        existing_seeds: list[str] | None = None,
    ) -> LibrarianResult:
        """Suggest seed papers and authors for the study.

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
            existing_seeds: Titles of papers already added as seeds.

        Returns:
            A :class:`LibrarianResult` with suggested papers and authors.
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
            "existing_seeds": existing_seeds or [],
        }
        messages = self._loader.load_messages(template_context)
        raw = await self._client.complete(messages)

        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:])
            cleaned = cleaned.rsplit("```", 1)[0].strip()

        data: dict[str, Any] = json.loads(cleaned)
        return LibrarianResult.model_validate(data)
