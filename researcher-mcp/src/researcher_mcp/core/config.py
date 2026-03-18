"""Settings for the researcher-mcp server."""

from __future__ import annotations

import functools

from pydantic_settings import BaseSettings, SettingsConfigDict


class ResearcherSettings(BaseSettings):
    """Environment-driven configuration for researcher-mcp.

    All settings can be overridden via environment variables with the same
    name (case-insensitive).

    Attributes:
        semantic_scholar_rpm: Semantic Scholar API requests per minute.
        open_alex_rpm: OpenAlex API requests per minute.
        scihub_enabled: Master switch — SciHub retrieval is disabled unless
            explicitly set to True by the server operator.
        scihub_url: Base URL for SciHub requests.
        unpaywall_email: Institutional email sent with Unpaywall API requests
            per Unpaywall's terms of service.
        ieee_xplore_api_key: IEEE Xplore REST API key.
        elsevier_api_key: Elsevier API key (shared by Scopus, ScienceDirect,
            and Inspec / Engineering Village).
        elsevier_inst_token: Elsevier institutional token for expanded access.
        wos_api_key: Clarivate Web of Science Starter API key.
        springer_api_key: Springer Nature Metadata API key.
        semantic_scholar_api_key: Semantic Scholar API key (optional; raises
            per-key rate limit above the shared unauthenticated pool).
        scholarly_proxy_url: HTTP(S) proxy URL for Google Scholar requests via
            ``scholarly``.  Strongly recommended in production to avoid CAPTCHA
            blocks.
        markitdown_ocr_model: LLM model identifier passed to MarkItDown when
            ``enable_ocr=True`` is requested (e.g. ``claude-haiku-4-5-20251001``).

    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Legacy / existing settings
    semantic_scholar_rpm: int = 100
    open_alex_rpm: int = 300
    scihub_enabled: bool = False
    scihub_url: str = "https://sci-hub.se"
    unpaywall_email: str = "researcher@example.com"

    # Feature 006: academic database API credentials
    ieee_xplore_api_key: str = ""
    elsevier_api_key: str = ""
    elsevier_inst_token: str = ""
    wos_api_key: str = ""
    springer_api_key: str = ""
    semantic_scholar_api_key: str = ""
    scholarly_proxy_url: str = ""
    markitdown_ocr_model: str = ""


@functools.lru_cache(maxsize=1)
def get_settings() -> ResearcherSettings:
    """Return a cached settings singleton.

    Returns:
        The module-level :class:`ResearcherSettings` instance, constructed
        once and reused for the lifetime of the process.

    """
    return ResearcherSettings()
