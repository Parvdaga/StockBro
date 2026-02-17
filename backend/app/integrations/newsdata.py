"""
NewsData.io API client for Indian stock market news.
Features: TTL caching, rate-limiting, exponential backoff retry.
"""
import asyncio
import time
import httpx
from typing import List, Dict, Optional

from app.config import settings
from app.integrations.cache import TTLCache
from app.integrations.retry import async_retry

# Base URL for NewsData.io v1
NEWSDATA_BASE_URL = "https://newsdata.io/api/1/latest"

# Module-level caches
_news_cache = TTLCache(max_size=100, default_ttl=600)  # 10 min TTL

# Rate limiter state (NewsData.io free plan ≈ 200 req/day → ~1 req / 7s)
_rate_limit_lock = asyncio.Lock()
_last_call_time: float = 0.0
_RATE_LIMIT_INTERVAL: float = 7.0  # seconds between API calls


async def _enforce_rate_limit():
    """Wait if needed to stay within NewsData.io rate limits."""
    global _last_call_time
    async with _rate_limit_lock:
        now = time.time()
        elapsed = now - _last_call_time
        if elapsed < _RATE_LIMIT_INTERVAL:
            wait = _RATE_LIMIT_INTERVAL - elapsed
            await asyncio.sleep(wait)
        _last_call_time = time.time()


class NewsDataClient:
    """Client for NewsData.io API — Indian stock market news with caching & retry."""

    def __init__(self):
        self.api_key = settings.NEWSDATA_API_KEY
        self.enabled = bool(self.api_key)

    @async_retry(max_retries=2, base_delay=1.0)
    async def search_news(
        self,
        query: str,
        max_results: int = 5,
        language: str = "en",
        country: str = "in",
    ) -> List[Dict]:
        """
        Search for news articles about a topic.
        Results are cached for 10 minutes and rate-limited.

        Args:
            query: Search query (e.g. "Reliance Industries")
            max_results: Maximum articles to return
            language: Language code (default: en)
            country: Country code (default: in)

        Returns:
            List of article dicts with title, description, url, source, published_at
        """
        if not self.enabled:
            print("NewsData API not enabled (key missing)")
            return []

        # Check cache
        cache_key = f"news_search:{query}:{language}:{country}"
        cached = _news_cache.get(cache_key)
        if cached is not None:
            return cached[:max_results]

        # Rate limit
        await _enforce_rate_limit()

        params = {
            "apikey": self.api_key,
            "q": query,
            "language": language,
            "country": country,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(NEWSDATA_BASE_URL, params=params)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    formatted = self._format_articles(results[:max_results])
                    _news_cache.set(cache_key, formatted)
                    return formatted
                elif response.status_code == 429:
                    print("[NewsData] Rate limit hit — will retry")
                    raise httpx.ReadError("Rate limited by NewsData.io")
                else:
                    print(f"NewsData API error: HTTP {response.status_code} - {response.text[:200]}")
                    return []
        except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError):
            raise  # Let retry decorator handle these
        except Exception as e:
            print(f"NewsData API error: {e}")
            return []

    @async_retry(max_retries=2, base_delay=1.0)
    async def get_top_headlines(
        self,
        category: str = "business",
        max_results: int = 5,
    ) -> List[Dict]:
        """Get top headlines for a category (e.g., business)."""
        if not self.enabled:
            return []

        # Check cache
        cache_key = f"news_headlines:{category}"
        cached = _news_cache.get(cache_key)
        if cached is not None:
            return cached[:max_results]

        # Rate limit
        await _enforce_rate_limit()

        params = {
            "apikey": self.api_key,
            "category": category,
            "language": "en",
            "country": "in",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(NEWSDATA_BASE_URL, params=params)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    formatted = self._format_articles(results[:max_results])
                    _news_cache.set(cache_key, formatted)
                    return formatted
                elif response.status_code == 429:
                    raise httpx.ReadError("Rate limited by NewsData.io")
                else:
                    print(f"NewsData headlines error: HTTP {response.status_code}")
                    return []
        except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError):
            raise
        except Exception as e:
            print(f"NewsData headlines error: {e}")
            return []

    @staticmethod
    def _format_articles(articles: List[Dict]) -> List[Dict]:
        """Format raw NewsData articles into consistent structure."""
        formatted = []
        for article in articles:
            description = article.get("description", "") or article.get("content", "") or ""
            formatted.append({
                "title": article.get("title", ""),
                "description": description[:200] if description else "",
                "url": article.get("link", ""),
                "image": article.get("image_url"),
                "published_at": article.get("pubDate", ""),
                "source": article.get("source_id", "Unknown"),
            })
        return formatted
