"""FastAPI application factory for SMS Researcher backend."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.v1.router import api_router
from backend.core.config import configure_logging, get_logger, get_settings
from backend.core.logging import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown hooks.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control to FastAPI while the application is running.
    """
    settings = get_settings()
    configure_logging(json_logs=not settings.debug, log_level="DEBUG" if settings.debug else "INFO")
    logger = get_logger(__name__)
    logger.info("application_startup", app=settings.app_name, version=settings.app_version)
    yield
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        A fully configured :class:`FastAPI` instance ready to serve.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(api_router)

    return app


app = create_app()
