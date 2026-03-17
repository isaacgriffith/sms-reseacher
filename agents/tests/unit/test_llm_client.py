"""Tests for LLMClient: model string construction for each provider."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.core.config import AgentSettings
from agents.core.llm_client import LLMClient


def make_settings(provider: str = "anthropic", model: str = "claude-sonnet-4-6") -> AgentSettings:
    """Build a test :class:`AgentSettings` with explicit values."""
    return AgentSettings(
        llm_provider=provider,  # type: ignore[arg-type]
        llm_model=model,
        ollama_base_url="http://localhost:11434",
        anthropic_api_key="test-key",
        researcher_mcp_url="http://localhost:8002/sse",
    )


class TestModelString:
    """Verify correct LiteLLM model string construction."""

    def test_anthropic_model_string(self) -> None:
        """Anthropic provider produces 'anthropic/<model>'."""
        client = LLMClient(settings=make_settings("anthropic", "claude-sonnet-4-6"))
        assert client.model == "anthropic/claude-sonnet-4-6"

    def test_ollama_model_string(self) -> None:
        """Ollama provider produces 'ollama/<model>'."""
        client = LLMClient(settings=make_settings("ollama", "llama3.2:3b"))
        assert client.model == "ollama/llama3.2:3b"

    def test_anthropic_no_api_base(self) -> None:
        """Anthropic provider does not inject api_base into kwargs."""
        client = LLMClient(settings=make_settings("anthropic"))
        assert "api_base" not in client._extra_kwargs()

    def test_ollama_injects_api_base(self) -> None:
        """Ollama provider injects api_base pointing to local server."""
        client = LLMClient(settings=make_settings("ollama"))
        kwargs = client._extra_kwargs()
        assert "api_base" in kwargs
        assert kwargs["api_base"] == "http://localhost:11434"


class TestComplete:
    """Tests for LLMClient.complete() with mocked LiteLLM."""

    async def test_complete_calls_litellm(self) -> None:
        """complete() calls litellm.acompletion with correct model."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Decision: include\nReason: Relevant."

        with patch("agents.core.llm_client.litellm.acompletion", new=AsyncMock(return_value=mock_response)) as mock_call:
            client = LLMClient(settings=make_settings("anthropic", "claude-sonnet-4-6"))
            result = await client.complete([{"role": "user", "content": "Hello"}])

        mock_call.assert_called_once()
        call_kwargs = mock_call.call_args.kwargs
        assert call_kwargs["model"] == "anthropic/claude-sonnet-4-6"
        assert result == "Decision: include\nReason: Relevant."

    async def test_complete_passes_tools(self) -> None:
        """complete() forwards the tools list to litellm when provided."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""

        tools = [{"type": "function", "function": {"name": "search_papers"}}]

        with patch("agents.core.llm_client.litellm.acompletion", new=AsyncMock(return_value=mock_response)) as mock_call:
            client = LLMClient(settings=make_settings())
            await client.complete([{"role": "user", "content": "search"}], tools=tools)

        call_kwargs = mock_call.call_args.kwargs
        assert call_kwargs["tools"] == tools

    async def test_complete_ollama_includes_api_base(self) -> None:
        """Ollama provider passes api_base to litellm.acompletion."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"

        with patch("agents.core.llm_client.litellm.acompletion", new=AsyncMock(return_value=mock_response)) as mock_call:
            client = LLMClient(settings=make_settings("ollama", "llama3.2:3b"))
            await client.complete([{"role": "user", "content": "ping"}])

        call_kwargs = mock_call.call_args.kwargs
        assert call_kwargs.get("api_base") == "http://localhost:11434"


# ---------------------------------------------------------------------------
# T067: ProviderConfig Protocol + LLMClient overload tests
# ---------------------------------------------------------------------------


from dataclasses import dataclass  # noqa: E402
from agents.core.provider_config import ProviderConfig  # noqa: E402


@dataclass
class _StubConfig:
    """Concrete dataclass satisfying the ProviderConfig Protocol for testing."""

    model_string: str = "anthropic/claude-sonnet-4-6"
    api_base: str | None = None
    api_key: str | None = "sk-stub-key"


class TestProviderConfigProtocol:
    """Verify ProviderConfig Protocol compliance and LLMClient overload."""

    def test_stub_config_satisfies_protocol(self) -> None:
        """_StubConfig satisfies the ProviderConfig Protocol at runtime."""
        cfg = _StubConfig()
        assert isinstance(cfg, ProviderConfig)

    def test_model_string_attribute(self) -> None:
        """ProviderConfig instance exposes model_string attribute."""
        cfg = _StubConfig(model_string="openai/gpt-4")
        assert cfg.model_string == "openai/gpt-4"

    def test_api_base_can_be_none(self) -> None:
        """ProviderConfig api_base can be None (cloud providers)."""
        cfg = _StubConfig(api_base=None)
        assert cfg.api_base is None

    def test_api_key_can_be_none(self) -> None:
        """ProviderConfig api_key can be None (Ollama / env-key providers)."""
        cfg = _StubConfig(api_key=None)
        assert cfg.api_key is None


class TestLLMClientWithProviderConfig:
    """LLMClient.complete() uses provider_config when provided."""

    async def test_uses_provider_config_model_string(self) -> None:
        """complete() uses provider_config.model_string when config is not None."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "answer"

        cfg = _StubConfig(model_string="anthropic/claude-opus-4-5", api_key="sk-test")

        with patch("agents.core.llm_client.litellm.acompletion", new=AsyncMock(return_value=mock_response)) as mock_call:
            client = LLMClient(settings=make_settings("anthropic", "claude-haiku"))
            await client.complete([{"role": "user", "content": "hi"}], provider_config=cfg)

        call_kwargs = mock_call.call_args.kwargs
        assert call_kwargs["model"] == "anthropic/claude-opus-4-5"

    async def test_uses_provider_config_api_key(self) -> None:
        """complete() injects api_key from provider_config when not None."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"

        cfg = _StubConfig(model_string="openai/gpt-4", api_key="sk-from-db")

        with patch("agents.core.llm_client.litellm.acompletion", new=AsyncMock(return_value=mock_response)) as mock_call:
            client = LLMClient(settings=make_settings())
            await client.complete([{"role": "user", "content": "x"}], provider_config=cfg)

        call_kwargs = mock_call.call_args.kwargs
        assert call_kwargs.get("api_key") == "sk-from-db"

    async def test_uses_provider_config_api_base(self) -> None:
        """complete() injects api_base from provider_config when not None."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"

        cfg = _StubConfig(
            model_string="ollama/llama3",
            api_base="http://custom-ollama:11434",
            api_key=None,
        )

        with patch("agents.core.llm_client.litellm.acompletion", new=AsyncMock(return_value=mock_response)) as mock_call:
            client = LLMClient(settings=make_settings())
            await client.complete([{"role": "user", "content": "x"}], provider_config=cfg)

        call_kwargs = mock_call.call_args.kwargs
        assert call_kwargs.get("api_base") == "http://custom-ollama:11434"

    async def test_falls_back_to_agent_settings_when_config_none(self) -> None:
        """complete() uses AgentSettings model string when provider_config is None."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"

        with patch("agents.core.llm_client.litellm.acompletion", new=AsyncMock(return_value=mock_response)) as mock_call:
            client = LLMClient(settings=make_settings("anthropic", "claude-haiku-test"))
            await client.complete([{"role": "user", "content": "x"}], provider_config=None)

        call_kwargs = mock_call.call_args.kwargs
        assert call_kwargs["model"] == "anthropic/claude-haiku-test"

    async def test_no_api_key_in_kwargs_when_config_key_is_none(self) -> None:
        """complete() does not inject api_key when provider_config.api_key is None."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"

        cfg = _StubConfig(model_string="ollama/llama3", api_key=None, api_base=None)

        with patch("agents.core.llm_client.litellm.acompletion", new=AsyncMock(return_value=mock_response)) as mock_call:
            client = LLMClient(settings=make_settings())
            await client.complete([{"role": "user", "content": "x"}], provider_config=cfg)

        call_kwargs = mock_call.call_args.kwargs
        assert "api_key" not in call_kwargs
