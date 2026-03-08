"""Settings for the researcher-mcp server."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class ResearcherSettings(BaseSettings):
    """Environment-driven configuration for researcher-mcp.

    All settings can be overridden via environment variables with the same
    name (case-insensitive).
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    semantic_scholar_rpm: int = 100
    open_alex_rpm: int = 300
    scihub_enabled: bool = False
    scihub_url: str = "https://sci-hub.se"
    unpaywall_email: str = "researcher@example.com"


def get_settings() -> ResearcherSettings:
    """Return a cached settings instance."""
    return ResearcherSettings()
