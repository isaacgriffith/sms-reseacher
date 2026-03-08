"""Agent settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Settings for the agents sub-project.

    All LLM and MCP connection parameters are fully configurable
    via environment variables so providers can be swapped without
    code changes (FR-022, FR-023).
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM provider
    llm_provider: Literal["anthropic", "ollama"] = "anthropic"
    llm_model: str = "claude-sonnet-4-6"
    ollama_base_url: str = "http://localhost:11434"
    anthropic_api_key: str = ""

    # researcher-mcp connection
    researcher_mcp_url: str = "http://localhost:8002/sse"


@lru_cache
def get_agent_settings() -> AgentSettings:
    """Return a cached :class:`AgentSettings` instance."""
    return AgentSettings()
