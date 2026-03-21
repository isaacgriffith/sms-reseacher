"""Screener agent: decides whether a paper meets inclusion criteria."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader
from agents.core.provider_config import ProviderConfig


class CriterionRef(BaseModel):
    """Reference to a criterion that influenced the screening decision."""

    criterion_id: int | None = None
    criterion_type: str  # "inclusion" or "exclusion"
    text: str


class ScreeningResult(BaseModel):
    """Structured output from the ScreenerAgent."""

    decision: str  # "accepted", "rejected", or "duplicate"
    reasons: list[CriterionRef] = []


class ScreenerAgent:
    """Agent that screens papers against inclusion/exclusion criteria.

    Supports both the legacy string-based interface and a structured
    interface accepting lists of :class:`CriterionRef` objects, returning
    a :class:`ScreeningResult` Pydantic model.

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
        """Initialise the screener agent.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.
            provider_config: Optional database-resolved provider configuration.
                Passed through to each :meth:`LLMClient.complete` call.
            system_message_override: Optional rendered system message to use
                instead of the default prompt-file system message.

        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("screener")
        self._provider_config = provider_config
        self._system_message_override = system_message_override

    async def run(
        self,
        inclusion_criteria: str | list[dict[str, Any]],
        exclusion_criteria: str | list[dict[str, Any]],
        abstract: str,
        title: str = "",
    ) -> str | ScreeningResult:
        """Screen a paper abstract against the given criteria.

        Accepts either legacy string-based criteria (returns raw string) or
        structured criterion lists (returns :class:`ScreeningResult`).

        Args:
            inclusion_criteria: Natural-language inclusion criteria string, or
                a list of ``{id, description}`` criterion dicts.
            exclusion_criteria: Natural-language exclusion criteria string, or
                a list of ``{id, description}`` criterion dicts.
            abstract: The paper's abstract text to screen.
            title: Optional paper title to include for context.

        Returns:
            Raw string decision when criteria are strings (legacy mode), or a
            :class:`ScreeningResult` when criteria are structured lists.

        """
        structured_mode = isinstance(inclusion_criteria, list)

        if structured_mode:
            # Format structured criteria for the prompt
            inc_text = "\n".join(
                f"[IC{c.get('id', i + 1)}] {c.get('description', c)}"
                for i, c in enumerate(inclusion_criteria)  # type: ignore[arg-type]
            )
            exc_text = "\n".join(
                f"[EC{c.get('id', i + 1)}] {c.get('description', c)}"
                for i, c in enumerate(exclusion_criteria)  # type: ignore[arg-type]
            )
            inc_arg = inc_text or "No inclusion criteria specified."
            exc_arg = exc_text or "No exclusion criteria specified."
        else:
            inc_arg = inclusion_criteria  # type: ignore[assignment]
            exc_arg = exclusion_criteria  # type: ignore[assignment]

        context = {
            "inclusion_criteria": inc_arg,
            "exclusion_criteria": exc_arg,
            "abstract": abstract,
            "title": title,
            "structured_output": structured_mode,
        }
        messages = self._loader.load_messages(context)

        # Apply system message override if provided (Feature 005 / T061)
        if self._system_message_override is not None:
            messages = list(messages)
            for i, msg in enumerate(messages):
                if msg.get("role") == "system":
                    messages[i] = {"role": "system", "content": self._system_message_override}
                    break

        raw = await self._client.complete(messages, provider_config=self._provider_config)

        if not structured_mode:
            return raw

        # Parse structured JSON response
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:])
            cleaned = cleaned.rsplit("```", 1)[0].strip()

        try:
            data: dict[str, Any] = json.loads(cleaned)
            return ScreeningResult.model_validate(data)
        except json.JSONDecodeError, Exception:
            # Fallback: infer decision from plain text
            lower = cleaned.lower()
            if "accept" in lower:
                decision = "accepted"
            elif "duplicate" in lower:
                decision = "duplicate"
            else:
                decision = "rejected"
            return ScreeningResult(decision=decision, reasons=[])
