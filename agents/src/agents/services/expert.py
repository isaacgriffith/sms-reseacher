"""Expert agent: identifies 10-20 high-confidence relevant papers."""

import json
from typing import Any

from pydantic import BaseModel

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader
from agents.core.provider_config import ProviderConfig


class ExpertPaper(BaseModel):
    """A paper identified by the Expert agent."""

    title: str
    authors: list[str]
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    rationale: str


class ExpertAgent:
    """Agent that identifies high-confidence relevant papers for a study.

    Uses the ``expert`` prompt templates with the configured LLM to
    produce a structured list of 10–20 highly relevant papers.

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
        """Initialise the expert agent.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.
            provider_config: Optional database-resolved provider configuration.
                Passed through to each :meth:`LLMClient.complete` call.
            system_message_override: Optional rendered system message to use
                instead of the default prompt-file system message.
        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("expert")
        self._provider_config = provider_config
        self._system_message_override = system_message_override

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
        objectives: list[str] | None = None,
        questions: list[str] | None = None,
    ) -> list[ExpertPaper]:
        """Identify relevant papers for the study.

        Args:
            topic: Brief topic description.
            variant: PICO variant name.
            population: PICO population component.
            intervention: PICO intervention component.
            comparison: PICO comparison component.
            outcome: PICO outcome component.
            context: PICO context component.
            objectives: Research objectives.
            questions: Research questions.

        Returns:
            A list of :class:`ExpertPaper` objects (10–20 papers).
        """
        template_context: dict[str, Any] = {
            "topic": topic,
            "variant": variant,
            "population": population,
            "intervention": intervention,
            "comparison": comparison,
            "outcome": outcome,
            "context": context,
            "objectives": objectives or [],
            "questions": questions or [],
        }
        messages = self._loader.load_messages(template_context)

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

        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:])
            cleaned = cleaned.rsplit("```", 1)[0].strip()

        data: list[dict[str, Any]] = json.loads(cleaned)
        return [ExpertPaper.model_validate(item) for item in data]
