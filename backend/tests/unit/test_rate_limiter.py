"""
Unit tests for TokenBucketLimiter — rate limiting for API compliance.
"""
import pytest
import asyncio
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.integrations.rate_limiter import TokenBucketLimiter, get_limiter


# ──────────────────────────────────────────────
# Basic acquire/release
# ──────────────────────────────────────────────

class TestTokenBucketBasics:

    @pytest.mark.asyncio
    async def test_acquire_within_limits(self):
        limiter = TokenBucketLimiter(max_calls_per_day=10, max_calls_per_hour=5, name="test")
        assert await limiter.acquire() is True

    @pytest.mark.asyncio
    async def test_hourly_limit_exhaustion(self):
        limiter = TokenBucketLimiter(max_calls_per_day=100, max_calls_per_hour=3, name="test_hourly")
        assert await limiter.acquire() is True   # 1
        assert await limiter.acquire() is True   # 2
        assert await limiter.acquire() is True   # 3
        assert await limiter.acquire() is False  # 4th blocked by hourly

    @pytest.mark.asyncio
    async def test_daily_limit_exhaustion(self):
        limiter = TokenBucketLimiter(max_calls_per_day=3, max_calls_per_hour=100, name="test_daily")
        assert await limiter.acquire() is True   # 1
        assert await limiter.acquire() is True   # 2
        assert await limiter.acquire() is True   # 3
        assert await limiter.acquire() is False  # 4th blocked by daily


# ──────────────────────────────────────────────
# Status reporting
# ──────────────────────────────────────────────

class TestLimiterStatus:

    @pytest.mark.asyncio
    async def test_status_after_acquire(self):
        limiter = TokenBucketLimiter(max_calls_per_day=10, max_calls_per_hour=5, name="status_test")
        await limiter.acquire()
        await limiter.acquire()

        status = limiter.status
        assert status["daily_used"] == 2
        assert status["hourly_used"] == 2
        assert status["daily_remaining"] == 8
        assert status["hourly_remaining"] == 3
        assert status["name"] == "status_test"


# ──────────────────────────────────────────────
# get_limiter singleton
# ──────────────────────────────────────────────

class TestGetLimiter:

    def test_returns_same_instance(self):
        limiter1 = get_limiter("test_singleton")
        limiter2 = get_limiter("test_singleton")
        assert limiter1 is limiter2

    def test_different_names_different_instances(self):
        limiter_a = get_limiter("service_a")
        limiter_b = get_limiter("service_b")
        assert limiter_a is not limiter_b

    def test_known_service_limits(self):
        """Check that pre-configured services have correct limits."""
        groww = get_limiter("groww")
        assert groww.max_daily == 500
        assert groww.max_hourly == 100

        newsdata = get_limiter("newsdata")
        assert newsdata.max_daily == 180
        assert newsdata.max_hourly == 30
