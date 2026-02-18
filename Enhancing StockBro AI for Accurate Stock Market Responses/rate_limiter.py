"""
Token-bucket rate limiter for free-tier API compliance.
Supports daily + hourly budgets with async-safe locking.
"""
import asyncio
import time
from typing import Dict, Optional


class TokenBucketLimiter:
    """
    Rate limiter using token-bucket algorithm.
    Enforces both hourly and daily limits for API calls.

    Usage:
        limiter = TokenBucketLimiter(max_calls_per_day=180, max_calls_per_hour=30)

        if await limiter.acquire():
            # OK to make API call
        else:
            # Rate limited — use cached/stale data
    """

    def __init__(
        self,
        max_calls_per_day: int = 200,
        max_calls_per_hour: int = 50,
        name: str = "default",
    ):
        self.name = name
        self.max_daily = max_calls_per_day
        self.max_hourly = max_calls_per_hour

        self._daily_count = 0
        self._hourly_count = 0
        self._daily_reset: float = self._next_day_reset()
        self._hourly_reset: float = time.time() + 3600
        self._lock = asyncio.Lock()

    @staticmethod
    def _next_day_reset() -> float:
        """Get timestamp for next midnight UTC."""
        now = time.time()
        # Reset at next midnight UTC
        seconds_in_day = 86400
        return now - (now % seconds_in_day) + seconds_in_day

    def _maybe_reset(self) -> None:
        """Reset counters if time windows have elapsed."""
        now = time.time()

        if now >= self._daily_reset:
            self._daily_count = 0
            self._daily_reset = self._next_day_reset()

        if now >= self._hourly_reset:
            self._hourly_count = 0
            self._hourly_reset = now + 3600

    async def acquire(self) -> bool:
        """
        Try to acquire a token. Returns True if allowed, False if rate-limited.
        Thread-safe via asyncio lock.
        """
        async with self._lock:
            self._maybe_reset()

            if self._daily_count >= self.max_daily:
                print(
                    f"[RATE-LIMIT] {self.name}: daily limit reached "
                    f"({self._daily_count}/{self.max_daily})"
                )
                return False

            if self._hourly_count >= self.max_hourly:
                print(
                    f"[RATE-LIMIT] {self.name}: hourly limit reached "
                    f"({self._hourly_count}/{self.max_hourly})"
                )
                return False

            self._daily_count += 1
            self._hourly_count += 1
            return True

    @property
    def status(self) -> Dict:
        """Get current limiter status for monitoring."""
        self._maybe_reset()
        return {
            "name": self.name,
            "daily_used": self._daily_count,
            "daily_limit": self.max_daily,
            "daily_remaining": max(0, self.max_daily - self._daily_count),
            "hourly_used": self._hourly_count,
            "hourly_limit": self.max_hourly,
            "hourly_remaining": max(0, self.max_hourly - self._hourly_count),
        }


# ──────────────────────────────────────────────
# Pre-configured limiters for each API
# ──────────────────────────────────────────────
_limiters: Dict[str, TokenBucketLimiter] = {}

# Default budgets per service (conservative for free tiers)
_DEFAULT_LIMITS = {
    "groww": {"max_calls_per_day": 500, "max_calls_per_hour": 100},
    "newsdata": {"max_calls_per_day": 180, "max_calls_per_hour": 30},
}


def get_limiter(service_name: str) -> TokenBucketLimiter:
    """
    Get or create a rate limiter for a named service.

    Args:
        service_name: One of 'groww', 'newsdata', or custom name

    Returns:
        TokenBucketLimiter instance (singleton per service name)
    """
    if service_name not in _limiters:
        limits = _DEFAULT_LIMITS.get(service_name, {"max_calls_per_day": 200, "max_calls_per_hour": 50})
        _limiters[service_name] = TokenBucketLimiter(
            name=service_name,
            **limits,
        )
    return _limiters[service_name]
