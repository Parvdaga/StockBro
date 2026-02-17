"""
Exponential backoff retry utility for async HTTP calls.
"""
import asyncio
import random
from functools import wraps
from typing import Tuple, Type

import httpx


# Default retryable exceptions
DEFAULT_RETRYABLE = (
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.ReadError,
    ConnectionError,
    TimeoutError,
)


def async_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = DEFAULT_RETRYABLE,
):
    """
    Decorator: retry an async function with exponential backoff + jitter.

    Args:
        max_retries: Maximum number of retry attempts (total calls = max_retries + 1)
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
        retryable_exceptions: Tuple of exception classes to retry on
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        # Exponential backoff with jitter
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        jitter = random.uniform(0, delay * 0.5)
                        wait_time = delay + jitter
                        print(
                            f"[RETRY] {func.__name__} attempt {attempt + 1}/{max_retries} "
                            f"failed ({type(e).__name__}), retrying in {wait_time:.1f}s..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        print(
                            f"[RETRY] {func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
            raise last_exception
        return wrapper
    return decorator
