"""Request-scoped structured logging middleware for FastAPI."""

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.config import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that attaches a request-scoped structlog context.

    For every incoming HTTP request this middleware:

    1. Generates a unique ``request_id`` (UUID4).
    2. Binds ``method``, ``path``, and ``request_id`` into the
       ``structlog`` context-variable store so that all downstream
       log calls automatically include these fields.
    3. After the route handler completes, logs a single summary line
       containing ``method``, ``path``, ``status_code``, and
       ``duration_ms``.
    4. Clears the context-variable store on the way out.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Process a request, adding structured log context.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler.

        Returns:
            The HTTP response produced by the downstream handler.
        """
        request_id = str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        start = time.monotonic()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = round((time.monotonic() - start) * 1000, 2)
            status_code = response.status_code if response is not None else 500
            logger.info(
                "http_request",
                status_code=status_code,
                duration_ms=duration_ms,
            )
            structlog.contextvars.clear_contextvars()
