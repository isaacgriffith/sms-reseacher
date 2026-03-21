"""LiteLLM-backed LLM client supporting Anthropic, OpenAI, and Ollama providers.

Feature 005 update: :meth:`LLMClient.complete` now accepts an optional
``provider_config`` parameter of type :class:`~agents.core.provider_config.ProviderConfig`.
When supplied, the database-resolved model string, API base URL, and API key
override the environment-variable-based :class:`AgentSettings` for that call,
enabling per-agent model configuration without restarting the service.
"""

from typing import Any

import litellm

from agents.core.config import AgentSettings, get_agent_settings
from agents.core.provider_config import ProviderConfig


class LLMClient:
    """Thin wrapper around :func:`litellm.acompletion`.

    Constructs the correct model string and API base for the configured
    provider so callers never need to know which backend is in use.

    When ``provider_config`` is passed to :meth:`complete`, it overrides the
    environment-based :class:`AgentSettings` for that individual call, allowing
    different agents to use different models and providers at runtime.

    Examples::

        # Environment-based (legacy / default)
        client = LLMClient()
        response = await client.complete([{"role": "user", "content": "Hello"}])

        # Database-backed override (Feature 005)
        from agents.core.provider_config import ProviderConfig
        from dataclasses import dataclass

        @dataclass
        class MyConfig:
            model_string: str = "anthropic/claude-sonnet-4-6"
            api_base: str | None = None
            api_key: str | None = "sk-..."

        response = await client.complete(messages, provider_config=MyConfig())
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
        """Return the fully-qualified LiteLLM model string from settings.

        - Anthropic: ``anthropic/<model>`` (e.g. ``anthropic/claude-sonnet-4-6``)
        - Ollama:    ``ollama/<model>``    (e.g. ``ollama/llama3.2:3b``)
        """
        s = self._settings
        if s.llm_provider == "ollama":
            return f"ollama/{s.llm_model}"
        return f"anthropic/{s.llm_model}"

    def _extra_kwargs(self) -> dict[str, Any]:
        """Return provider-specific keyword arguments for LiteLLM from settings.

        For Ollama, injects ``api_base`` so requests route to the local
        Ollama server rather than the Anthropic cloud endpoint.
        """
        if self._settings.llm_provider == "ollama":
            return {"api_base": self._settings.ollama_base_url}
        return {}

    def _kwargs_from_provider_config(self, provider_config: ProviderConfig) -> dict[str, Any]:
        """Build LiteLLM keyword arguments from a database-resolved ProviderConfig.

        Args:
            provider_config: A :class:`ProviderConfig` instance with
                ``model_string``, ``api_base``, and ``api_key``.

        Returns:
            A dict containing ``model`` and, conditionally, ``api_base`` and
            ``api_key`` overrides ready for :func:`litellm.acompletion`.

        """
        kwargs: dict[str, Any] = {"model": provider_config.model_string}
        if provider_config.api_base is not None:
            kwargs["api_base"] = provider_config.api_base
        if provider_config.api_key is not None:
            kwargs["api_key"] = provider_config.api_key
        return kwargs

    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        provider_config: ProviderConfig | None = None,
    ) -> str:
        """Send a chat completion request and return the response text.

        When ``provider_config`` is supplied, model routing is determined by
        the config's ``model_string``, ``api_base``, and ``api_key`` rather
        than the :class:`AgentSettings` this client was initialised with.

        Args:
            messages: OpenAI-format message list
                (e.g. ``[{"role": "user", "content": "..."}]``).
            tools: Optional LiteLLM-format tool definitions (function
                schemas) — used when MCP tools are injected.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.
            provider_config: Optional database-resolved provider configuration.
                When not ``None``, overrides the environment-based settings
                for this call only.

        Returns:
            The text content of the first choice in the response.

        Raises:
            litellm.exceptions.APIError: If the upstream LLM call fails.

        """
        if provider_config is not None:
            base_kwargs = self._kwargs_from_provider_config(provider_config)
        else:
            base_kwargs = {"model": self.model, **self._extra_kwargs()}

        kwargs: dict[str, Any] = {
            **base_kwargs,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools

        response = await litellm.acompletion(**kwargs)
        content: str = response.choices[0].message.content or ""
        return content
