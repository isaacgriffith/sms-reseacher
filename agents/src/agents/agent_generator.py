"""AgentGeneratorAgent — produces optimised system message templates for other agents.

Feature 005: given a task type, role, and persona description, this agent uses
an LLM to generate a Jinja2 system message template that incorporates all
agent identity and context variables (role_name, role_description, persona_name,
persona_description, domain, study_type).
"""

from __future__ import annotations

from agents.core.llm_client import LLMClient
from agents.core.prompt_loader import PromptLoader
from agents.core.provider_config import ProviderConfig


class AgentGeneratorAgent:
    """Generates Jinja2 system-message templates for other research agents.

    Uses an LLM (routed through :class:`LLMClient`) to produce a well-formed
    template that references the six standard variable placeholders defined in
    Feature 005 (role_name, role_description, persona_name, persona_description,
    domain, study_type).

    Args:
        llm_client: Optional :class:`LLMClient` override.  When ``None``,
            a new client using the environment-based :class:`AgentSettings`
            is created.

    Examples::

        generator = AgentGeneratorAgent()
        template = await generator.generate_system_message(
            task_type="screener",
            role_name="Screener",
            role_description="Evaluates papers against inclusion/exclusion criteria.",
            persona_name="Dr. Aria",
            persona_description="A meticulous systematic reviewer.",
            model_display_name="Claude Sonnet 4.6",
            provider_config=my_config,
        )

    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        """Initialise the agent generator.

        Args:
            llm_client: LLM client to use; defaults to a new
                :class:`LLMClient` with environment-based settings.

        """
        self._client = llm_client or LLMClient()
        self._loader = PromptLoader("agent_generator")

    async def generate_system_message(
        self,
        *,
        task_type: str,
        role_name: str,
        role_description: str,
        persona_name: str,
        persona_description: str,
        model_display_name: str,
        provider_config: ProviderConfig | None = None,
    ) -> str:
        """Generate a Jinja2 system message template for the described agent.

        Builds a prompt from the static ``system.md`` and the rendered
        ``user.md.j2`` template, then calls the LLM and returns the raw
        generated template string.

        When ``provider_config`` is supplied, the LLM call is routed through
        the database-resolved model rather than the default environment settings.

        Args:
            task_type: The agent's task type (e.g. ``screener``, ``extractor``).
            role_name: Short functional role label (e.g. ``"Screener"``).
            role_description: Plain-text description of the role.
            persona_name: Human-readable persona name (e.g. ``"Dr. Aria"``).
            persona_description: Narrative persona background.
            model_display_name: Display name of the model used for context
                in the generated template (e.g. ``"Claude Sonnet 4.6"``).
            provider_config: Optional database-resolved :class:`ProviderConfig`.
                When provided, overrides environment-based model settings.

        Returns:
            The raw Jinja2 template string produced by the LLM.  The string
            should reference all six standard placeholders.

        Raises:
            litellm.exceptions.APIError: If the upstream LLM call fails.
            jinja2.exceptions.UndefinedError: If a required template variable
                is missing from the user prompt context.

        """
        context = {
            "task_type": task_type,
            "role_name": role_name,
            "role_description": role_description,
            "persona_name": persona_name,
            "persona_description": persona_description,
            "model_display_name": model_display_name,
        }
        messages = self._loader.load_messages(context)
        return await self._client.complete(
            messages,
            provider_config=provider_config,
            max_tokens=1024,
        )
