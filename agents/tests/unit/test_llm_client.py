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
