"""NarrativeSynthesiserAgent — generates practitioner-friendly narrative paragraphs.

Feature 008: Given a research question and a list of included papers, the agent
produces a concise 3–5 sentence narrative suitable for an Evidence Briefing.
"""

from __future__ import annotations

from dataclasses import dataclass

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader
from agents.core.provider_config import ProviderConfig


@dataclass
class PaperSummary:
    """Lightweight paper summary passed to the synthesiser.

    Attributes:
        title: Paper title string.
        abstract: Paper abstract text, or ``None`` if unavailable.

    """

    title: str
    abstract: str | None


class NarrativeSynthesiserAgent:
    """Generates a practitioner-friendly narrative paragraph for a research question.

    Uses an LLM (routed through :class:`LLMClient`) to produce a 3–5 sentence
    plain-language summary of the evidence provided by the included papers.

    The agent is stateless; each call to :meth:`draft_section` is independent.

    Args:
        llm_client: Optional :class:`LLMClient` override.  When ``None``,
            a new client using the environment-based :class:`AgentSettings`
            is created.

    Examples::

        agent = NarrativeSynthesiserAgent()
        text = await agent.draft_section(
            study_id=42,
            rq_index=0,
            rq_text="What strategies exist to reduce onboarding time?",
            papers=[PaperSummary(title="Fast Onboarding Study", abstract="...")],
        )

    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        """Initialise the narrative synthesiser.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.

        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("narrative_synthesiser")

    async def draft_section(
        self,
        *,
        study_id: int,
        rq_index: int,
        rq_text: str,
        papers: list[PaperSummary],
        provider_config: ProviderConfig | None = None,
    ) -> str:
        """Generate a practitioner-friendly narrative draft for one synthesis section.

        Renders the ``user.md.j2`` template with the research question and paper
        list, then calls the LLM and returns the generated paragraph text.

        Args:
            study_id: The Rapid Review study ID (used for logging context).
            rq_index: Zero-based index of the research question within the
                protocol's ``research_questions`` list.
            rq_text: The research question text to synthesise.
            papers: List of :class:`PaperSummary` objects for included papers.
            provider_config: Optional database-resolved :class:`ProviderConfig`.
                When provided, overrides environment-based model settings.

        Returns:
            The raw narrative paragraph text produced by the LLM.

        Raises:
            litellm.exceptions.APIError: If the upstream LLM call fails.
            jinja2.exceptions.UndefinedError: If a required template variable
                is missing from the rendered user prompt.

        """
        context = {
            "research_question": rq_text,
            "papers": [{"title": p.title, "abstract": p.abstract} for p in papers],
        }
        messages = self._loader.load_messages(context)
        return await self._client.complete(
            messages,
            provider_config=provider_config,
            max_tokens=512,
        )
