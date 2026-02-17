"""Unit tests for the TTL cache utility."""
import time
import asyncio
import pytest
from app.integrations.cache import TTLCache, cached


class TestTTLCache:
    def test_set_and_get(self):
        cache = TTLCache(max_size=10, default_ttl=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_key(self):
        cache = TTLCache(max_size=10, default_ttl=60)
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        cache = TTLCache(max_size=10, default_ttl=1)
        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_max_size_eviction(self):
        cache = TTLCache(max_size=3, default_ttl=60)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)  # Should evict "a"
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("d") == 4
        assert cache.size == 3

    def test_invalidate(self):
        cache = TTLCache(max_size=10, default_ttl=60)
        cache.set("key1", "value1")
        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_clear(self):
        cache = TTLCache(max_size=10, default_ttl=60)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.size == 0
        assert cache.get("a") is None

    def test_overwrite_moves_to_end(self):
        cache = TTLCache(max_size=3, default_ttl=60)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("a", 10)  # Overwrite "a", moves to end
        cache.set("d", 4)   # Should evict "b" (oldest non-recently-used)
        assert cache.get("a") == 10
        assert cache.get("b") is None  # evicted
        assert cache.get("d") == 4


class TestCachedDecorator:
    def test_caches_result(self):
        cache = TTLCache(max_size=10, default_ttl=60)
        call_count = 0

        @cached(cache, key_fn=lambda x: f"test:{x}")
        async def fetch(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = asyncio.run(fetch(5))
        result2 = asyncio.run(fetch(5))
        assert result1 == 10
        assert result2 == 10
        assert call_count == 1  # Second call used cache

    def test_does_not_cache_none(self):
        cache = TTLCache(max_size=10, default_ttl=60)
        call_count = 0

        @cached(cache, key_fn=lambda: "test_none")
        async def fetch_none():
            nonlocal call_count
            call_count += 1
            return None

        asyncio.run(fetch_none())
        asyncio.run(fetch_none())
        assert call_count == 2  # None is not cached
