"""Unit tests for the exponential backoff retry utility."""
import asyncio
import pytest
from app.integrations.retry import async_retry


class TestAsyncRetry:
    def test_success_on_first_try(self):
        @async_retry(max_retries=3, base_delay=0.01)
        async def always_works():
            return "ok"

        result = asyncio.run(always_works())
        assert result == "ok"

    def test_retries_on_failure_then_succeeds(self):
        attempt = 0

        @async_retry(max_retries=3, base_delay=0.01, max_delay=0.05)
        async def fails_twice():
            nonlocal attempt
            attempt += 1
            if attempt < 3:
                raise ConnectionError("temporary failure")
            return "recovered"

        result = asyncio.run(fails_twice())
        assert result == "recovered"
        assert attempt == 3

    def test_gives_up_after_max_retries(self):
        @async_retry(max_retries=2, base_delay=0.01, max_delay=0.05)
        async def always_fails():
            raise TimeoutError("always timeout")

        with pytest.raises(TimeoutError):
            asyncio.run(always_fails())

    def test_non_retryable_exception_not_retried(self):
        attempt = 0

        @async_retry(
            max_retries=3,
            base_delay=0.01,
            retryable_exceptions=(ConnectionError,),
        )
        async def raises_value_error():
            nonlocal attempt
            attempt += 1
            raise ValueError("not retryable")

        with pytest.raises(ValueError):
            asyncio.run(raises_value_error())
        assert attempt == 1  # No retries for ValueError
