"""Unit tests for Groww API client with mocked HTTP."""
import asyncio
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.integrations.groww import GrowwClient, _price_cache, _history_cache, _search_cache


@pytest.fixture(autouse=True)
def clear_caches():
    """Clear all Groww caches before each test."""
    _price_cache.clear()
    _history_cache.clear()
    _search_cache.clear()
    yield
    _price_cache.clear()
    _history_cache.clear()
    _search_cache.clear()


@pytest.fixture
def client():
    with patch("app.integrations.groww.settings") as mock_settings:
        mock_settings.GROWW_API_KEY = None  # No SDK needed for web API tests
        c = GrowwClient()
        return c


class TestParseSymbol:
    def test_simple_symbol(self):
        exchange, symbol = GrowwClient._parse_symbol("RELIANCE")
        assert exchange == "NSE"
        assert symbol == "RELIANCE"

    def test_nse_prefix(self):
        exchange, symbol = GrowwClient._parse_symbol("NSE-TCS")
        assert exchange == "NSE"
        assert symbol == "TCS"

    def test_bse_prefix(self):
        exchange, symbol = GrowwClient._parse_symbol("BSE-INFY")
        assert exchange == "BSE"
        assert symbol == "INFY"

    def test_lowercase_input(self):
        exchange, symbol = GrowwClient._parse_symbol("reliance")
        assert exchange == "NSE"
        assert symbol == "RELIANCE"

    def test_whitespace(self):
        exchange, symbol = GrowwClient._parse_symbol("  TCS  ")
        assert exchange == "NSE"
        assert symbol == "TCS"


class TestGetLivePrice:
    @patch("app.integrations.groww._rate_limiter.acquire", new_callable=AsyncMock, return_value=True)
    def test_success(self, mock_rate_limit, client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ltp": 2450.50,
            "dayChange": 25.30,
            "dayChangePerc": 1.04,
            "open": 2430.00,
            "high": 2460.00,
            "low": 2420.00,
            "close": 2425.20,
            "volume": 5000000,
        }

        async def mock_get(url, **kwargs):
            return mock_response

        with patch("app.integrations.groww._get_http_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = mock_get
            mock_get_client.return_value = mock_client

            result = asyncio.run(client.get_live_price("RELIANCE"))

        assert result is not None
        assert result["ltp"] == 2450.50
        assert result["volume"] == 5000000

    @patch("app.integrations.groww._rate_limiter.acquire", new_callable=AsyncMock, return_value=True)
    def test_not_found(self, mock_rate_limit, client):
        mock_response = MagicMock()
        mock_response.status_code = 404

        async def mock_get(url, **kwargs):
            return mock_response

        with patch("app.integrations.groww._get_http_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = mock_get
            mock_get_client.return_value = mock_client

            result = asyncio.run(client.get_live_price("INVALID_SYMBOL"))

        assert result is None


class TestGetHistoricalData:
    def test_success_with_yfinance(self, client):
        # Mock pandas DataFrame returned by yfinance
        mock_df = MagicMock()
        mock_df.empty = False
        
        # Create timestamps and rows
        import pandas as pd
        from datetime import datetime
        
        dates = pd.to_datetime([1700000000, 1700086400], unit='s')
        data = {
            "Open": [2400.0, 2430.0],
            "High": [2450.0, 2470.0],
            "Low": [2380.0, 2420.0],
            "Close": [2430.0, 2460.0],
            "Volume": [3000000, 2800000]
        }
        mock_df = pd.DataFrame(data, index=dates)

        with patch("app.integrations.groww.yf.Ticker") as MockTicker:
            mock_ticker_instance = MagicMock()
            mock_ticker_instance.history.return_value = mock_df
            MockTicker.return_value = mock_ticker_instance
            
            # We need to ensure _YFINANCE_AVAILABLE is True for the test
            with patch("app.integrations.groww._YFINANCE_AVAILABLE", True):
                result = asyncio.run(client.get_historical_data("RELIANCE", duration="1M"))

        assert result is not None
        assert len(result) == 2
        assert result[0]["open"] == 2400.0
        assert result[0]["volume"] == 3000000

    def test_api_failure(self, client):
        with patch("app.integrations.groww.yf.Ticker") as MockTicker:
            mock_ticker_instance = MagicMock()
            # Simulate failure by returning empty or raising exception
            mock_ticker_instance.history.side_effect = Exception("YFinance error")
            MockTicker.return_value = mock_ticker_instance
            
            with patch("app.integrations.groww._YFINANCE_AVAILABLE", True):
                result = asyncio.run(client.get_historical_data("RELIANCE", duration="1M"))

        assert result is None


class TestFormatCandles:
    def test_array_format(self):
        candles = [
            [1700000000, 100.0, 110.0, 95.0, 105.0, 1000],
        ]
        result = GrowwClient._format_candles(candles)
        assert len(result) == 1
        assert result[0]["open"] == 100.0
        assert result[0]["close"] == 105.0
        assert result[0]["volume"] == 1000

    def test_dict_format(self):
        candles = [
            {"t": 1700000000, "o": 100.0, "h": 110.0, "l": 95.0, "c": 105.0, "v": 1000},
        ]
        result = GrowwClient._format_candles(candles)
        assert len(result) == 1
        assert result[0]["open"] == 100.0

    def test_empty_candles(self):
        assert GrowwClient._format_candles([]) == []
