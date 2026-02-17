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
    """Simple in-memory cache with per-key TTL, max size eviction, and stale-while-revalidate."""

    def __init__(self, max_size: int = 200, default_ttl: int = 300, stale_window: int = 0):
        """
        Args:
            max_size: Maximum number of items in cache (oldest evicted first)
            default_ttl: Default time-to-live in seconds
            stale_window: Extra seconds after TTL where stale data is still returned
                          (0 = disabled, data is simply expired)
        """
        self._cache: OrderedDict = OrderedDict()
        self._expiry: dict[str, float] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._stale_window = stale_window
        self._lock = asyncio.Lock()

    def get(self, key: str, allow_stale: bool = False) -> Optional[Any]:
        """
        Get a value from cache. Returns None if missing or expired.

        Args:
            allow_stale: If True and stale_window is set, return expired-but-stale data.
                         The returned dict will have '_stale': True added if it's a dict.
        """
        if key not in self._cache:
            return None

        now = time.time()
        expiry_time = self._expiry.get(key, 0)

        if now <= expiry_time:
            # Fresh — move to end (most recently used) and return
            self._cache.move_to_end(key)
            return self._cache[key]

        # Data is expired — check stale window
        if allow_stale and self._stale_window > 0 and now <= (expiry_time + self._stale_window):
            # Stale but usable — return with marker
            value = self._cache[key]
            if isinstance(value, dict):
                stale_copy = {**value, "_stale": True}
                return stale_copy
            return value

        # Fully expired — remove
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
        return None

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
