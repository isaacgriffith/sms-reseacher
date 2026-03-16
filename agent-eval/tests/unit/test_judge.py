"""Unit tests for agent_eval.judge.litellm_judge.LiteLLMJudge.

All external litellm calls are mocked so no real LLM API calls are made.
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent_eval.judge.litellm_judge import LiteLLMJudge


class TestLiteLLMJudgeInit:
    """Tests for LiteLLMJudge initialisation and configuration."""

    def test_default_provider_anthropic(self) -> None:
        """Without env override, provider defaults to anthropic."""
        env = {"LLM_PROVIDER": "", "LLM_MODEL": "", "OLLAMA_BASE_URL": ""}
        with patch.dict(os.environ, env, clear=False):
            judge = LiteLLMJudge(provider="anthropic", model="claude-test")
        assert judge._provider == "anthropic"

    def test_ollama_provider_stored(self) -> None:
        """Provider=ollama is stored correctly."""
        judge = LiteLLMJudge(provider="ollama", model="llama3")
        assert judge._provider == "ollama"

    def test_env_var_fallback_for_provider(self) -> None:
        """LLM_PROVIDER env var is used when provider arg is None."""
        with patch.dict(os.environ, {"LLM_PROVIDER": "ollama"}):
            judge = LiteLLMJudge()
        assert judge._provider == "ollama"

    def test_env_var_fallback_for_model(self) -> None:
        """LLM_MODEL env var is used when model arg is None."""
        with patch.dict(os.environ, {"LLM_MODEL": "my-model"}):
            judge = LiteLLMJudge()
        assert judge._model_name == "my-model"

    def test_ollama_url_default(self) -> None:
        """Default Ollama URL is localhost:11434."""
        judge = LiteLLMJudge(provider="anthropic")
        assert "11434" in judge._ollama_url

    def test_ollama_url_env_fallback(self) -> None:
        """OLLAMA_BASE_URL env var is used when arg is None."""
        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://myserver:9999"}):
            judge = LiteLLMJudge()
        assert "9999" in judge._ollama_url


class TestLiteLLMJudgeMethods:
    """Tests for LiteLLMJudge model name and build_model_string."""

    def test_get_model_name_anthropic(self) -> None:
        """get_model_name returns anthropic/<model> for anthropic provider."""
        judge = LiteLLMJudge(provider="anthropic", model="claude-test")
        assert judge.get_model_name() == "anthropic/claude-test"

    def test_get_model_name_ollama(self) -> None:
        """get_model_name returns ollama/<model> for ollama provider."""
        judge = LiteLLMJudge(provider="ollama", model="llama3")
        assert judge.get_model_name() == "ollama/llama3"

    def test_load_model_returns_self(self) -> None:
        """load_model returns the judge instance itself."""
        judge = LiteLLMJudge(provider="anthropic", model="claude-test")
        assert judge.load_model() is judge

    def test_build_model_string_anthropic(self) -> None:
        """_build_model_string returns anthropic/<model> string."""
        judge = LiteLLMJudge(provider="anthropic", model="claude-3")
        assert judge._build_model_string() == "anthropic/claude-3"

    def test_build_model_string_ollama(self) -> None:
        """_build_model_string returns ollama/<model> string."""
        judge = LiteLLMJudge(provider="ollama", model="llama3")
        assert judge._build_model_string() == "ollama/llama3"


class TestLiteLLMJudgeGenerate:
    """Tests for LiteLLMJudge.generate and a_generate with mocked litellm."""

    def test_generate_returns_content(self) -> None:
        """generate returns message content from litellm response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Judge response text"

        with patch("agent_eval.judge.litellm_judge.litellm.completion", return_value=mock_response):
            judge = LiteLLMJudge(provider="anthropic", model="claude-test")
            result = judge.generate("Is this a good paper?")

        assert result == "Judge response text"

    def test_generate_ollama_includes_api_base(self) -> None:
        """generate passes api_base for ollama provider."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"

        with patch("agent_eval.judge.litellm_judge.litellm.completion", return_value=mock_response) as mock_completion:
            judge = LiteLLMJudge(provider="ollama", model="llama3", ollama_url="http://custom:1111")
            judge.generate("test prompt")

        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs.get("api_base") == "http://custom:1111"

    def test_generate_empty_content_returns_empty_string(self) -> None:
        """generate returns empty string when content is None."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None

        with patch("agent_eval.judge.litellm_judge.litellm.completion", return_value=mock_response):
            judge = LiteLLMJudge(provider="anthropic", model="claude-test")
            result = judge.generate("prompt")

        assert result == ""

    async def test_a_generate_returns_content(self) -> None:
        """a_generate returns message content from async litellm response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "async response"

        with patch("agent_eval.judge.litellm_judge.litellm.acompletion", new=AsyncMock(return_value=mock_response)):
            judge = LiteLLMJudge(provider="anthropic", model="claude-test")
            result = await judge.a_generate("Is this paper relevant?")

        assert result == "async response"

    async def test_a_generate_ollama_includes_api_base(self) -> None:
        """a_generate passes api_base for ollama provider."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"

        with patch("agent_eval.judge.litellm_judge.litellm.acompletion", new=AsyncMock(return_value=mock_response)) as mock_comp:
            judge = LiteLLMJudge(provider="ollama", model="llama3", ollama_url="http://ollama:9999")
            await judge.a_generate("test")

        call_kwargs = mock_comp.call_args[1]
        assert call_kwargs.get("api_base") == "http://ollama:9999"
