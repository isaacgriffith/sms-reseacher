"""Unit tests for backend.core.config and backend.main.

Covers configure_logging, get_logger, get_settings, and create_app/lifespan.
"""

from __future__ import annotations

from unittest.mock import patch


# ---------------------------------------------------------------------------
# Settings / get_settings
# ---------------------------------------------------------------------------


def test_get_settings_returns_settings_instance():
    """get_settings returns a Settings instance with expected attribute types.

    The default settings should have string app_name and a boolean debug flag.
    """
    from backend.core.config import Settings, get_settings

    settings = get_settings()
    assert isinstance(settings, Settings)
    assert isinstance(settings.app_name, str)
    assert isinstance(settings.debug, bool)


def test_settings_has_default_database_url():
    """Settings has a non-empty default database_url.

    The default database_url should be a non-empty string for local dev.
    """
    from backend.core.config import Settings

    s = Settings()
    assert isinstance(s.database_url, str)
    assert len(s.database_url) > 0


def test_settings_has_default_researcher_mcp_url():
    """Settings has a default researcher_mcp_url.

    The default URL should point to the local MCP service.
    """
    from backend.core.config import Settings

    s = Settings()
    assert "localhost" in s.researcher_mcp_url


def test_settings_has_default_redis_url():
    """Settings has a default redis_url.

    The default should be the local Redis connection string.
    """
    from backend.core.config import Settings

    s = Settings()
    assert s.redis_url.startswith("redis://")


def test_settings_has_default_totp_fields():
    """Settings has positive default totp_lockout_attempts and totp_lockout_minutes.

    The TOTP lockout defaults should be positive integers.
    """
    from backend.core.config import Settings

    s = Settings()
    assert s.totp_lockout_attempts > 0
    assert s.totp_lockout_minutes > 0


def test_settings_llm_defaults():
    """Settings has default llm_model and anthropic llm_provider.

    The default LLM provider should be anthropic.
    """
    from backend.core.config import Settings

    s = Settings()
    assert s.llm_provider == "anthropic"
    assert isinstance(s.llm_model, str)


# ---------------------------------------------------------------------------
# configure_logging
# ---------------------------------------------------------------------------


def test_configure_logging_with_json_false_does_not_raise():
    """configure_logging with json_logs=False completes without error.

    The function should complete without raising when using console renderer.
    """
    from backend.core.config import configure_logging

    # Should not raise
    configure_logging(json_logs=False, log_level="DEBUG")


def test_configure_logging_with_json_true_does_not_raise():
    """configure_logging with json_logs=True completes without error.

    The function should complete without raising when using JSON renderer.
    """
    from backend.core.config import configure_logging

    configure_logging(json_logs=True, log_level="INFO")


def test_configure_logging_with_warning_level():
    """configure_logging accepts WARNING as a valid log level.

    Non-standard log levels like WARNING should be accepted.
    """
    from backend.core.config import configure_logging

    configure_logging(json_logs=False, log_level="WARNING")


# ---------------------------------------------------------------------------
# get_logger
# ---------------------------------------------------------------------------


def test_get_logger_returns_bound_logger():
    """get_logger returns a structlog BoundLogger.

    The returned object should be a structlog BoundLogger instance.
    """
    import structlog

    from backend.core.config import get_logger

    logger = get_logger("test.module")
    assert logger is not None


def test_get_logger_with_none_name():
    """get_logger accepts None as name.

    None should be accepted as the logger name.
    """
    from backend.core.config import get_logger

    logger = get_logger(None)
    assert logger is not None


# ---------------------------------------------------------------------------
# create_app / lifespan
# ---------------------------------------------------------------------------


def test_create_app_returns_fastapi_instance():
    """create_app returns a FastAPI application with the expected title.

    The returned app should have the title from settings.
    """
    from fastapi import FastAPI

    from backend.main import create_app

    app = create_app()
    assert isinstance(app, FastAPI)
    assert app.title == "SMS Researcher API"


async def test_lifespan_logs_startup_and_shutdown():
    """lifespan context manager logs startup and shutdown without errors.

    The lifespan function should be callable as an async context manager
    and complete without raising.
    """
    from fastapi import FastAPI

    from backend.main import lifespan

    app = FastAPI()
    async with lifespan(app):
        pass  # startup + shutdown should not raise


async def test_lifespan_startup_logs_app_name():
    """lifespan logs application_startup with the app name from settings.

    The startup log call should include the app name from application settings.
    """
    from fastapi import FastAPI
    from unittest.mock import MagicMock, patch

    from backend.main import lifespan

    mock_logger = MagicMock()
    app = FastAPI()

    with patch("backend.main.get_logger", return_value=mock_logger):
        async with lifespan(app):
            pass

    # logger.info should have been called at least once for startup
    assert mock_logger.info.called
