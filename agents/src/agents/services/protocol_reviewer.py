"""Protocol reviewer agent: evaluates SLR draft protocols for methodological soundness."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader
from agents.core.provider_config import ProviderConfig


class ProtocolIssue(BaseModel):
    """A single methodological issue identified in a review protocol.

    Attributes:
        section: The protocol section containing the issue.
        severity: One of ``"critical"``, ``"major"``, or ``"minor"``.
        description: Human-readable explanation of the problem.
        suggestion: Actionable recommendation for how to fix it.

    """

    section: str
    severity: str
    description: str
    suggestion: str


class ProtocolReviewResult(BaseModel):
    """Structured output from the :class:`ProtocolReviewerAgent`.

    Attributes:
        issues: List of methodological issues found in the protocol.
        overall_assessment: One-paragraph summary of protocol quality and readiness.

    """

    issues: list[ProtocolIssue] = []
    overall_assessment: str = ""


class ProtocolReviewerAgent:
    """Agent that reviews SLR protocols for methodological soundness.

    Evaluates draft protocols against SLR best practices (Kitchenham & Charters
    guidelines, PRISMA) and returns structured feedback identifying critical,
    major, and minor issues.

    When ``provider_config`` is supplied, all LLM calls are routed through
    the database-backed model configuration rather than environment variables.

    When ``system_message_override`` is supplied, the rendered study-context
    system message replaces the default prompt-file system message.

    Args:
        llm_client: Optional :class:`LLMClient` override for testing.
        provider_config: Optional :class:`ProviderConfig` for database-backed
            model routing. When ``None``, falls back to environment settings.
        system_message_override: Optional rendered system message string that
            replaces the first system message loaded from prompt files.

    """

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        provider_config: ProviderConfig | None = None,
        system_message_override: str | None = None,
    ) -> None:
        """Initialise the protocol reviewer agent.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.
            provider_config: Optional database-resolved provider configuration.
                Passed through to each :meth:`LLMClient.complete` call.
            system_message_override: Optional rendered system message to use
                instead of the default prompt-file system message.

        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("protocol_reviewer")
        self._provider_config = provider_config
        self._system_message_override = system_message_override

    async def review(self, protocol_data: dict[str, Any]) -> ProtocolReviewResult:
        """Review a draft SLR protocol and return structured feedback.

        Renders all protocol fields into the user prompt template, sends them
        to the LLM, and parses the structured JSON response into a
        :class:`ProtocolReviewResult`.

        Args:
            protocol_data: Dictionary of protocol fields. Recognised keys match
                the :class:`db.models.slr.ReviewProtocol` columns:
                ``background``, ``rationale``, ``research_questions``,
                ``pico_population``, ``pico_intervention``, ``pico_comparison``,
                ``pico_outcome``, ``pico_context``, ``search_strategy``,
                ``inclusion_criteria``, ``exclusion_criteria``,
                ``data_extraction_strategy``, ``synthesis_approach``,
                ``dissemination_strategy``, ``timetable``.

        Returns:
            A :class:`ProtocolReviewResult` containing ``issues`` and
            ``overall_assessment``.

        Raises:
            ValueError: If the LLM response cannot be parsed as JSON and no
                fallback is possible.

        """
        messages = self._loader.load_messages(protocol_data)

        if self._system_message_override is not None:
            messages = list(messages)
            for i, msg in enumerate(messages):
                if msg.get("role") == "system":
                    messages[i] = {"role": "system", "content": self._system_message_override}
                    break

        raw = await self._client.complete(messages, provider_config=self._provider_config)

        return self._parse_response(raw)

    def _parse_response(self, raw: str) -> ProtocolReviewResult:
        """Parse the LLM response string into a :class:`ProtocolReviewResult`.

        Strips optional markdown code fences before JSON parsing. Falls back
        to a minimal result with the raw text as the overall assessment if
        parsing fails.

        Args:
            raw: Raw string response from the LLM.

        Returns:
            A :class:`ProtocolReviewResult` instance.

        """
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Drop first line (```json or ```) and last closing ```
            cleaned = "\n".join(lines[1:])
            cleaned = cleaned.rsplit("```", 1)[0].strip()

        try:
            data: dict[str, Any] = json.loads(cleaned)
            return ProtocolReviewResult.model_validate(data)
        except json.JSONDecodeError, Exception:
            # Graceful fallback: preserve raw text as the assessment
            return ProtocolReviewResult(
                issues=[],
                overall_assessment=raw.strip(),
            )
