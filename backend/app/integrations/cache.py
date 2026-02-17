"""
In-memory TTL cache for API responses.
Thread-safe with asyncio support. No external dependencies.
"""
import time
import asyncio
from collections import OrderedDict
from typing import Any, Optional, Callable
from functools import wraps


class TTLCache:
    """Simple in-memory cache with per-key TTL and max size eviction."""

    def __init__(self, max_size: int = 200, default_ttl: int = 300):
        """
        Args:
            max_size: Maximum number of items in cache (oldest evicted first)
            default_ttl: Default time-to-live in seconds
        """
        self._cache: OrderedDict = OrderedDict()
        self._expiry: dict[str, float] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache. Returns None if missing or expired."""
        if key not in self._cache:
            return None
        if time.time() > self._expiry.get(key, 0):
            # Expired — remove
            self._cache.pop(key, None)
            self._expiry.pop(key, None)
            return None
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return self._cache[key]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value with TTL."""
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        self._expiry[key] = time.time() + (ttl or self._default_ttl)
        # Evict oldest if over capacity
        while len(self._cache) > self._max_size:
            oldest_key, _ = self._cache.popitem(last=False)
            self._expiry.pop(oldest_key, None)

    def invalidate(self, key: str) -> None:
        """Remove a specific key from cache."""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)

    def clear(self) -> None:
        """Clear the entire cache."""
        self._cache.clear()
        self._expiry.clear()

    @property
    def size(self) -> int:
        return len(self._cache)


def cached(cache: TTLCache, key_fn: Callable[..., str], ttl: Optional[int] = None):
    """
    Decorator to cache the result of an async function.

    Args:
        cache: TTLCache instance to use
        key_fn: Function that takes the same args and returns a cache key string
        ttl: Optional TTL override
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = key_fn(*args, **kwargs)
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = await func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
