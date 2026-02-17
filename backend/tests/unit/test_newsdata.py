"""Unit tests for NewsData.io client with mocked HTTP."""
import asyncio
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from app.integrations.newsdata import NewsDataClient, _news_cache


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear news cache before each test."""
    _news_cache.clear()
    yield
    _news_cache.clear()


@pytest.fixture
def client():
    with patch("app.integrations.newsdata.settings") as mock_settings:
        mock_settings.NEWSDATA_API_KEY = "test_key_123"
        c = NewsDataClient()
        c.enabled = True
        return c


class TestNewsDataClient:
    def test_disabled_without_key(self):
        with patch("app.integrations.newsdata.settings") as mock_settings:
            mock_settings.NEWSDATA_API_KEY = None
            c = NewsDataClient()
            assert c.enabled is False
            result = asyncio.run(c.search_news("test"))
            assert result == []

    @patch("app.integrations.newsdata._rate_limiter.acquire", new_callable=AsyncMock, return_value=True)
    def test_search_news_success(self, mock_rate_limit, client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Reliance Q3 Results",
                    "description": "Strong earnings reported",
                    "link": "https://example.com/article",
                    "pubDate": "2026-02-16 10:00:00",
                    "source_id": "moneycontrol",
                    "image_url": None,
                }
            ]
        }

        async def mock_get(url, params=None, **kwargs):
            return mock_response

        with patch("httpx.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = mock_get
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client_instance

            result = asyncio.run(client.search_news("Reliance", max_results=5))

        assert len(result) == 1
        assert result[0]["title"] == "Reliance Q3 Results"
        assert result[0]["source"] == "moneycontrol"

    @patch("app.integrations.newsdata._rate_limiter.acquire", new_callable=AsyncMock, return_value=True)
    def test_search_news_http_error(self, mock_rate_limit, client):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        async def mock_get(url, params=None, **kwargs):
            return mock_response

        with patch("httpx.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = mock_get
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client_instance

            result = asyncio.run(client.search_news("test"))

        assert result == []

    def test_format_articles(self):
        raw = [
            {
                "title": "Test Article",
                "description": "A description",
                "link": "https://example.com",
                "pubDate": "2026-02-16",
                "source_id": "reuters",
                "image_url": "https://img.example.com/1.jpg",
            }
        ]
        formatted = NewsDataClient._format_articles(raw)
        assert len(formatted) == 1
        assert formatted[0]["title"] == "Test Article"
        assert formatted[0]["url"] == "https://example.com"
        assert formatted[0]["source"] == "reuters"
        assert formatted[0]["image"] == "https://img.example.com/1.jpg"
