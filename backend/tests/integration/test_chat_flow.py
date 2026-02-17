"""
Integration test for the full chat endpoint flow.

Sends a real request through POST /api/v1/chat/ and validates the
response structure (answer, stocks, news, charts). Requires a running
backend with valid API keys.
"""
import pytest
import httpx
import asyncio


# ── Configuration ──────────────────────────────
BACKEND_URL = "http://localhost:8000/api/v1"

# Test credentials — update with your Supabase test user
TEST_EMAIL = "test@test.com"
TEST_PASSWORD = "test1234"


@pytest.fixture(scope="module")
def auth_token():
    """Authenticate with the backend and return a bearer token."""
    try:
        resp = httpx.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=15.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("access_token") or data.get("token")
    except Exception as e:
        pytest.skip(f"Backend not running or auth failed: {e}")
    pytest.skip("Could not authenticate — check test credentials")


@pytest.fixture
def headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


class TestChatFlow:
    """End-to-end test: user asks about a stock → gets structured response."""

    def test_chat_returns_structured_response(self, headers):
        """POST /chat/ with a stock question should return answer + stocks + charts."""
        response = httpx.post(
            f"{BACKEND_URL}/chat/",
            json={"message": "How is Reliance doing today?"},
            headers=headers,
            timeout=60.0,
        )

        assert response.status_code == 200, f"Chat failed: {response.text}"
        data = response.json()

        # Required fields
        assert "answer" in data, "Response missing 'answer'"
        assert "conversation_id" in data, "Response missing 'conversation_id'"
        assert len(data["answer"]) > 50, "Answer too short — LLM may have failed"

        # At least one data attachment
        has_stocks = data.get("stocks") is not None and len(data["stocks"]) > 0
        has_charts = data.get("charts") is not None and len(data["charts"]) > 0
        assert has_stocks or has_charts, "Response should have stocks or charts"

    def test_chat_stocks_have_correct_shape(self, headers):
        """Stock data in response should have price, symbol, name."""
        response = httpx.post(
            f"{BACKEND_URL}/chat/",
            json={"message": "What is TCS stock price?"},
            headers=headers,
            timeout=60.0,
        )

        assert response.status_code == 200
        data = response.json()

        if data.get("stocks"):
            stock = data["stocks"][0]
            assert "symbol" in stock
            assert "current_price" in stock
            assert stock["current_price"] > 0

    def test_chat_charts_have_data_url(self, headers):
        """Chart configs should have symbol and data_url."""
        response = httpx.post(
            f"{BACKEND_URL}/chat/",
            json={"message": "Show me Infosys stock"},
            headers=headers,
            timeout=60.0,
        )

        assert response.status_code == 200
        data = response.json()

        if data.get("charts"):
            chart = data["charts"][0]
            assert "symbol" in chart
            assert "data_url" in chart
            assert "/api/v1/charts/" in chart["data_url"]

    def test_chart_endpoint_returns_ohlcv(self, headers):
        """GET /charts/RELIANCE/history should return OHLCV data."""
        response = httpx.get(
            f"{BACKEND_URL}/charts/RELIANCE/history?duration=1M",
            headers=headers,
            timeout=15.0,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "NSE-RELIANCE"
        assert data["duration"] == "1M"
        assert len(data["data"]) > 0

        point = data["data"][0]
        assert "timestamp" in point
        assert "open" in point
        assert "high" in point
        assert "low" in point
        assert "close" in point

    def test_news_search_returns_articles(self, headers):
        """GET /news/search should return formatted articles."""
        response = httpx.get(
            f"{BACKEND_URL}/news/search?q=Indian+stock+market",
            headers=headers,
            timeout=15.0,
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "count" in data

        if data["count"] > 0:
            article = data["results"][0]
            assert "title" in article
            assert "url" in article
            assert "source" in article

    def test_news_headlines(self, headers):
        """GET /news/headlines should return business headlines."""
        response = httpx.get(
            f"{BACKEND_URL}/news/headlines",
            headers=headers,
            timeout=15.0,
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
