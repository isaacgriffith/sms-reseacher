"""LiteLLM-backed judge implementing DeepEval's LLM interface."""

from __future__ import annotations

import os
from typing import Any

import litellm
from deepeval.models.base_model import DeepEvalBaseLLM


class LiteLLMJudge(DeepEvalBaseLLM):
    """Wraps litellm.completion to act as a DeepEval judge model.

    Provider and model are resolved from environment variables or constructor
    arguments, matching the same convention used by ``agents/core/llm_client.py``.
    """

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        ollama_url: str | None = None,
    ) -> None:
        """Initialise the judge.

        Args:
            provider: ``"anthropic"`` or ``"ollama"``. Falls back to
                ``LLM_PROVIDER`` env var then ``"anthropic"``.
            model: Base model identifier. Falls back to ``LLM_MODEL`` env var.
            ollama_url: Ollama server URL. Falls back to ``OLLAMA_BASE_URL`` env
                var then ``"http://localhost:11434"``.

        """
        self._provider = provider or os.environ.get("LLM_PROVIDER", "anthropic")
        self._model_name = model or os.environ.get("LLM_MODEL", "claude-sonnet-4-6")
        self._ollama_url = ollama_url or os.environ.get(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        )

    def _build_model_string(self) -> str:
        """Return the litellm model string for the configured provider."""
        if self._provider == "ollama":
            return f"ollama/{self._model_name}"
        return f"anthropic/{self._model_name}"

    def get_model_name(self) -> str:
        """Return a human-readable model name."""
        return self._build_model_string()

    def load_model(self) -> LiteLLMJudge:
        """Return self (no lazy loading required for litellm)."""
        return self

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a response synchronously via litellm.

        Args:
            prompt: The prompt string to evaluate.
            **kwargs: Additional kwargs forwarded to litellm.

        Returns:
            The model response content as a string.

        """
        extra: dict[str, Any] = {}
        if self._provider == "ollama":
            extra["api_base"] = self._ollama_url

        response = litellm.completion(
            model=self._build_model_string(),
            messages=[{"role": "user", "content": prompt}],
            **extra,
            **kwargs,
        )
        content: str = response.choices[0].message.content or ""
        return content

    async def a_generate(self, prompt: str, **kwargs: Any) -> str:
        """Async generation via litellm.

        Args:
            prompt: The prompt string to evaluate.
            **kwargs: Additional kwargs forwarded to litellm.

        Returns:
            The model response content as a string.

        """
        extra: dict[str, Any] = {}
        if self._provider == "ollama":
            extra["api_base"] = self._ollama_url

        response = await litellm.acompletion(
            model=self._build_model_string(),
            messages=[{"role": "user", "content": prompt}],
            **extra,
            **kwargs,
        )
        content: str = response.choices[0].message.content or ""
        return content
