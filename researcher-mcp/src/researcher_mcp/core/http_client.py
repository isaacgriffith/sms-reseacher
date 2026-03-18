"""HTTP client factory with tenacity retry and token-bucket rate limiting."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)


def _is_retryable(exc: BaseException) -> bool:
    """Return True for HTTP 5xx errors and transport-level failures."""
    if isinstance(exc, httpx.TimeoutException | httpx.NetworkError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500
    return False


class TokenBucket:
    """Simple async token-bucket rate limiter."""

    def __init__(self, rpm: int) -> None:
        """Initialise bucket for *rpm* requests per minute."""
        self._rate = rpm / 60.0  # tokens per second
        self._tokens = float(rpm)
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Block until a token is available."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last
            self._last = now
            self._tokens = min(float(self._rate * 60), self._tokens + elapsed * self._rate)
            if self._tokens >= 1:
                self._tokens -= 1
                return
            wait = (1 - self._tokens) / self._rate
        await asyncio.sleep(wait)
        async with self._lock:
            self._tokens = max(0.0, self._tokens - 1)


def make_retry_client(timeout: float = 10.0) -> httpx.AsyncClient:
    """Return an ``httpx.AsyncClient`` configured for use in source classes.

    The client itself does not retry; callers should wrap individual requests
    with :func:`with_retry` to get tenacity behaviour.

    Args:
        timeout: Default request timeout in seconds.

    Returns:
        A new :class:`httpx.AsyncClient` instance.

    """
    return httpx.AsyncClient(timeout=timeout)


async def with_retry(coro_fn: Callable[[], Any]) -> Any:
    """Execute *coro_fn* with tenacity retry (max 3 attempts, exp backoff + full jitter).

    Retries on HTTP 5xx, :class:`httpx.TimeoutException`, and
    :class:`httpx.NetworkError`.

    Args:
        coro_fn: A zero-argument async callable to retry.

    Returns:
        The result of *coro_fn* on first success.

    Raises:
        The last exception if all attempts fail.

    """
    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(multiplier=1, min=0.5, max=10),
        retry=retry_if_exception(_is_retryable),
        reraise=True,
    ):
        with attempt:
            return await coro_fn()
