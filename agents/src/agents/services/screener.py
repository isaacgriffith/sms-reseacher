"""Screener agent: decides whether a paper meets inclusion criteria."""

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader


class ScreenerAgent:
    """Agent that screens papers against inclusion/exclusion criteria.

    Uses the ``screener`` prompt templates in
    ``agents/prompts/screener/`` to construct messages and the
    configured LLM to produce an inclusion decision.

    Args:
        llm_client: Optional :class:`LLMClient` override for testing.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        """Initialise the screener agent.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.
        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("screener")

    async def run(
        self,
        inclusion_criteria: str,
        exclusion_criteria: str,
        abstract: str,
    ) -> str:
        """Screen a paper abstract against the given criteria.

        Args:
            inclusion_criteria: Natural-language inclusion criteria
                for the systematic study.
            exclusion_criteria: Natural-language exclusion criteria.
            abstract: The paper's abstract text to screen.

        Returns:
            The LLM's screening decision as a raw string
            (e.g. ``"include"`` or ``"exclude"`` with optional
            justification).
        """
        context = {
            "inclusion_criteria": inclusion_criteria,
            "exclusion_criteria": exclusion_criteria,
            "abstract": abstract,
        }
        messages = self._loader.load_messages(context)
        return await self._client.complete(messages)
