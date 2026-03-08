"""Extractor agent: pulls structured data fields from paper text."""

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader


class ExtractorAgent:
    """Agent that extracts structured data fields from paper full text.

    Uses the ``extractor`` prompt templates to instruct the LLM to
    identify and return specific data fields from the paper content.

    Args:
        llm_client: Optional :class:`LLMClient` override for testing.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        """Initialise the extractor agent.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.
        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("extractor")

    async def run(self, data_fields: str, paper_text: str) -> str:
        """Extract data fields from the given paper text.

        Args:
            data_fields: A description or list of fields to extract
                (e.g. ``"research method, sample size, threat to validity"``).
            paper_text: The paper's full text or relevant sections.

        Returns:
            The LLM's extraction result as a raw string, typically
            structured JSON or a Markdown table.
        """
        context = {"data_fields": data_fields, "paper_text": paper_text}
        messages = self._loader.load_messages(context)
        return await self._client.complete(messages)
