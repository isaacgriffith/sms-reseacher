"""Application settings and structured logging configuration."""

import logging
import sys
from functools import lru_cache
from typing import Literal

import structlog
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings loaded from environment variables.

    All values have safe defaults suitable for local development.
    Override by setting the corresponding environment variable or
    creating a ``.env`` file at the repository root.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    app_name: str = "SMS Researcher API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./dev.db"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # LLM
    llm_provider: Literal["anthropic", "ollama"] = "anthropic"
    llm_model: str = "claude-sonnet-4-6"
    ollama_base_url: str = "http://localhost:11434"
    anthropic_api_key: str = ""

    # researcher-mcp
    researcher_mcp_url: str = "http://localhost:8002/sse"


@lru_cache
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance.

    Uses ``lru_cache`` so the settings object is only constructed once
    per process, even in async contexts.
    """
    return Settings()


def configure_logging(*, json_logs: bool = True, log_level: str = "INFO") -> None:
    """Configure ``structlog`` for structured JSON output.

    Should be called once at application startup (e.g., in ``main.py``
    lifespan or at module level in production entry points).

    Args:
        json_logs: When ``True`` (default), emit JSON log lines suitable
            for log aggregation.  Set to ``False`` in development for
            human-readable console output.
        log_level: Standard log level name (``"DEBUG"``, ``"INFO"``, etc.).
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level.upper())


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound ``structlog`` logger.

    Args:
        name: Optional logger name; defaults to the calling module's name.

    Returns:
        A bound logger that emits structured JSON in production.
    """
    return structlog.get_logger(name)
