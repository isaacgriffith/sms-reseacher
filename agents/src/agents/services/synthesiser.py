"""Synthesiser agent: synthesises findings from multiple papers."""

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader
from agents.core.provider_config import ProviderConfig


class SynthesiserAgent:
    """Agent that synthesises findings across a set of included papers.

    Uses the ``synthesiser`` prompt templates to produce a coherent
    narrative answer to the research question from the provided
    paper summaries.

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
        """Initialise the synthesiser agent.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.
            provider_config: Optional database-resolved provider configuration.
                Passed through to each :meth:`LLMClient.complete` call.
            system_message_override: Optional rendered system message to use
                instead of the default prompt-file system message.

        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("synthesiser")
        self._provider_config = provider_config
        self._system_message_override = system_message_override

    async def run(self, papers_summary: str, research_question: str) -> str:
        """Synthesise findings from paper summaries.

        Args:
            papers_summary: A combined summary or structured list of
                findings from included papers.
            research_question: The primary research question the
                synthesis should answer.

        Returns:
            The LLM's synthesised narrative as a raw string.

        """
        context = {"papers_summary": papers_summary, "research_question": research_question}
        messages = self._loader.load_messages(context)

        # Apply system message override if provided (Feature 005 / T063)
        if self._system_message_override is not None:
            messages = list(messages)
            for i, msg in enumerate(messages):
                if msg.get("role") == "system":
                    messages[i] = {"role": "system", "content": self._system_message_override}
                    break

        return await self._client.complete(messages, provider_config=self._provider_config)
