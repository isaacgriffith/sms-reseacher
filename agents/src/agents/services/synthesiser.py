"""Synthesiser agent: synthesises findings from multiple papers."""

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader


class SynthesiserAgent:
    """Agent that synthesises findings across a set of included papers.

    Uses the ``synthesiser`` prompt templates to produce a coherent
    narrative answer to the research question from the provided
    paper summaries.

    Args:
        llm_client: Optional :class:`LLMClient` override for testing.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        """Initialise the synthesiser agent.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.
        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("synthesiser")

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
        return await self._client.complete(messages)
