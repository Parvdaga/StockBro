"""
Unit tests for QueryRouter — intent parsing and entity extraction.
"""
import pytest
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.agents.query_router import QueryRouter, route_query, ParsedQuery


@pytest.fixture
def router():
    return QueryRouter()


# ──────────────────────────────────────────────
# Intent classification
# ──────────────────────────────────────────────

class TestIntentClassification:

    def test_price_intent_with_symbol(self, router):
        result = router.parse("What is the price of RELIANCE?")
        assert result.intent == "PRICE_QUOTE"
        assert "RELIANCE" in result.symbols

    def test_price_intent_ltp(self, router):
        result = router.parse("Show me LTP of TCS")
        assert result.intent == "PRICE_QUOTE"
        assert "TCS" in result.symbols

    def test_news_intent(self, router):
        result = router.parse("Latest news about Indian stock market")
        assert result.intent == "NEWS"

    def test_chart_intent(self, router):
        result = router.parse("Show me RELIANCE chart for 1 year")
        assert result.intent == "CHART"
        assert "RELIANCE" in result.symbols

    def test_options_intent(self, router):
        result = router.parse("Explain call options for NIFTY")
        assert result.intent == "OPTIONS"

    def test_ipo_intent(self, router):
        result = router.parse("Upcoming IPO this week")
        assert result.intent == "IPO"

    def test_intraday_intent(self, router):
        result = router.parse("Intraday plan for RELIANCE")
        assert result.intent == "INTRADAY"
        assert "RELIANCE" in result.symbols

    def test_long_term_intent(self, router):
        result = router.parse("Should I invest in TCS for long term?")
        assert result.intent == "LONG_TERM"
        assert "TCS" in result.symbols

    def test_search_intent(self, router):
        result = router.parse("Find Tata Motors stock symbol")
        assert result.intent == "SEARCH"

    def test_general_intent(self, router):
        result = router.parse("Hello, how are you?")
        assert result.intent == "GENERAL"

    def test_symbol_only_is_price(self, router):
        """A bare symbol with no other keywords defaults to PRICE_QUOTE."""
        result = router.parse("INFY")
        assert result.intent == "PRICE_QUOTE"
        assert "INFY" in result.symbols


# ──────────────────────────────────────────────
# Symbol extraction
# ──────────────────────────────────────────────

class TestSymbolExtraction:

    def test_single_symbol(self, router):
        result = router.parse("Price of HDFCBANK")
        assert result.symbols == ["HDFCBANK"]

    def test_multiple_symbols(self, router):
        result = router.parse("Compare RELIANCE and TCS")
        assert "RELIANCE" in result.symbols
        assert "TCS" in result.symbols

    def test_exchange_prefix(self, router):
        result = router.parse("Get NSE-RELIANCE price")
        assert "RELIANCE" in result.symbols

    def test_no_symbols(self, router):
        result = router.parse("How is the market today?")
        assert result.symbols == []


# ──────────────────────────────────────────────
# Timeframe extraction
# ──────────────────────────────────────────────

class TestTimeframeExtraction:

    def test_one_month(self, router):
        result = router.parse("Show 1 month chart of RELIANCE")
        assert result.timeframe == "1M"

    def test_three_months(self, router):
        result = router.parse("RELIANCE performance over 3 months")
        assert result.timeframe == "3M"

    def test_one_year(self, router):
        result = router.parse("TCS 1 year trend")
        assert result.timeframe == "1y"

    def test_today(self, router):
        result = router.parse("What happened today?")
        assert result.timeframe == "1d"

    def test_no_timeframe(self, router):
        result = router.parse("Price of RELIANCE")
        assert result.timeframe is None


# ──────────────────────────────────────────────
# Convenience function
# ──────────────────────────────────────────────

class TestRouteQuery:

    def test_convenience_function(self):
        result = route_query("What is the price of RELIANCE?")
        assert isinstance(result, ParsedQuery)
        assert result.intent == "PRICE_QUOTE"
        assert "RELIANCE" in result.symbols

    def test_returns_parsed_query(self):
        result = route_query("Hello")
        assert isinstance(result, ParsedQuery)
        assert result.query_text == "Hello"
