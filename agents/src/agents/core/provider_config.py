"""ProviderConfig Protocol — database-backed LLM provider configuration.

Feature 005: defines a structural interface that allows :class:`LLMClient`
to accept database-resolved provider credentials without depending on the
environment-variable-based :class:`AgentSettings`.

Any object that supplies ``model_string``, ``api_base``, and ``api_key``
satisfies the Protocol — no explicit inheritance is required.

Example::

    from dataclasses import dataclass
    from agents.core.provider_config import ProviderConfig

    @dataclass
    class DbProviderConfig:
        model_string: str = "anthropic/claude-sonnet-4-6"
        api_base: str | None = None
        api_key: str | None = "sk-..."

    config: ProviderConfig = DbProviderConfig()
    client = LLMClient()
    response = await client.complete(messages, provider_config=config)
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProviderConfig(Protocol):
    """Structural interface for database-resolved LLM provider configuration.

    Attributes:
        model_string: Fully-qualified LiteLLM model identifier, e.g.
            ``"anthropic/claude-sonnet-4-6"`` or ``"ollama/llama3"``.
        api_base: Optional base URL override.  Required for Ollama; ``None``
            for cloud providers (Anthropic, OpenAI).
        api_key: Plaintext API key for the provider.  ``None`` when no key
            is required (Ollama) or when the caller manages key injection
            via environment variables.
    """

    model_string: str
    api_base: str | None
    api_key: str | None
