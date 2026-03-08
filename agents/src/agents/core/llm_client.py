"""LiteLLM-backed LLM client supporting Anthropic and Ollama providers."""

from typing import Any

import litellm

from agents.core.config import AgentSettings, get_agent_settings


class LLMClient:
    """Thin wrapper around :func:`litellm.acompletion`.

    Constructs the correct model string and API base for the configured
    provider so callers never need to know which backend is in use.

    Examples::

        client = LLMClient()
        response = await client.complete([{"role": "user", "content": "Hello"}])
    """

    def __init__(self, settings: AgentSettings | None = None) -> None:
        """Initialise the client.

        Args:
            settings: Optional :class:`AgentSettings` override.  When
                ``None``, the cached settings from
                :func:`get_agent_settings` are used.
        """
        self._settings = settings or get_agent_settings()

    @property
    def model(self) -> str:
        """Return the fully-qualified LiteLLM model string.

        - Anthropic: ``anthropic/<model>`` (e.g. ``anthropic/claude-sonnet-4-6``)
        - Ollama:    ``ollama/<model>``    (e.g. ``ollama/llama3.2:3b``)
        """
        s = self._settings
        if s.llm_provider == "ollama":
            return f"ollama/{s.llm_model}"
        return f"anthropic/{s.llm_model}"

    def _extra_kwargs(self) -> dict[str, Any]:
        """Return provider-specific keyword arguments for LiteLLM.

        For Ollama, injects ``api_base`` so requests route to the local
        Ollama server rather than the Anthropic cloud endpoint.
        """
        if self._settings.llm_provider == "ollama":
            return {"api_base": self._settings.ollama_base_url}
        return {}

    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> str:
        """Send a chat completion request and return the response text.

        Args:
            messages: OpenAI-format message list
                (e.g. ``[{"role": "user", "content": "..."}]``).
            tools: Optional LiteLLM-format tool definitions (function
                schemas) — used when MCP tools are injected.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.

        Returns:
            The text content of the first choice in the response.

        Raises:
            litellm.exceptions.APIError: If the upstream LLM call fails.
        """
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **self._extra_kwargs(),
        }
        if tools:
            kwargs["tools"] = tools

        response = await litellm.acompletion(**kwargs)
        content: str = response.choices[0].message.content or ""
        return content
