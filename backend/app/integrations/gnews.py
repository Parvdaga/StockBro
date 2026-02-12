"""
GNews API client for Indian stock market news
Uses gnews.io API for searching and fetching news articles
"""
import httpx
from typing import List, Optional, Dict
from app.config import settings


GNEWS_SEARCH_URL = "https://gnews.io/api/v4/search"
GNEWS_HEADLINES_URL = "https://gnews.io/api/v4/top-headlines"


class GNewsClient:
    """Client for GNews API — Indian stock market news"""

    def __init__(self):
        self.api_key = settings.GNEWS_API_KEY
        self.enabled = bool(self.api_key)

    async def search_news(
        self,
        query: str,
        max_results: int = 5,
        lang: str = "en",
        country: str = "in",
    ) -> List[Dict]:
        """
        Search for news articles about a topic.

        Args:
            query: Search query (e.g. "Reliance Industries stock")
            max_results: Maximum articles to return (1-100)
            lang: Language code
            country: Country code (default: India)

        Returns:
            List of article dicts with title, description, url, source, publishedAt
        """
        if not self.enabled:
            return []

        params = {
            "q": query,
            "lang": lang,
            "country": country,
            "max": min(max_results, 10),
            "token": self.api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(GNEWS_SEARCH_URL, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return self._format_articles(data.get("articles", []))
                else:
                    print(f"GNews API error: HTTP {response.status_code} - {response.text[:200]}")
                    return []
        except Exception as e:
            print(f"GNews API error: {e}")
            return []

    async def get_top_headlines(
        self,
        category: str = "business",
        max_results: int = 5,
        query: Optional[str] = None,
    ) -> List[Dict]:
        """
        Get top headlines for a category.

        Args:
            category: News category (business, technology, etc.)
            max_results: Maximum articles to return
            query: Optional additional keyword filter

        Returns:
            List of article dicts
        """
        if not self.enabled:
            return []

        params = {
            "category": category,
            "lang": "en",
            "country": "in",
            "max": min(max_results, 10),
            "token": self.api_key,
        }
        if query:
            params["q"] = query

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(GNEWS_HEADLINES_URL, params=params)
                if response.status_code == 200:
                    data = response.json()
                    return self._format_articles(data.get("articles", []))
                else:
                    print(f"GNews headlines error: HTTP {response.status_code}")
                    return []
        except Exception as e:
            print(f"GNews headlines error: {e}")
            return []

    @staticmethod
    def _format_articles(articles: List[Dict]) -> List[Dict]:
        """Format raw GNews articles into consistent structure"""
        formatted = []
        for article in articles:
            formatted.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "image": article.get("image"),
                "published_at": article.get("publishedAt", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
            })
        return formatted
