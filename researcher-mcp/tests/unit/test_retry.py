"""Unit test: tenacity retry on timeout — retries 3 times total."""

from __future__ import annotations

from unittest.mock import AsyncMock, call, patch

import httpx
import pytest

from researcher_mcp.core.http_client import with_retry


class TestRetry:
    """Tests for tenacity retry behaviour in with_retry."""

    async def test_retries_on_timeout_then_succeeds(self) -> None:
        """Function that times out twice then succeeds retries 3 times total."""
        call_count = 0

        async def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.TimeoutException("timeout")
            return "success"

        result = await with_retry(flaky)
        assert result == "success"
        assert call_count == 3

    async def test_raises_after_all_attempts_fail(self) -> None:
        """with_retry raises after 3 failed attempts."""
        call_count = 0

        async def always_fail() -> str:
            nonlocal call_count
            call_count += 1
            raise httpx.TimeoutException("timeout")

        with pytest.raises(httpx.TimeoutException):
            await with_retry(always_fail)
        assert call_count == 3
