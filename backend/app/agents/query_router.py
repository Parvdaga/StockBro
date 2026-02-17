"""
Query router — parse user intent before calling tools.
Ensures consistent, deterministic tool selection.
"""
from typing import Literal, Optional, List
from pydantic import BaseModel, Field
import re

# Intent types
IntentType = Literal[
    "PRICE_QUOTE",      # Get current price
    "CHART",            # Historical chart
    "NEWS",             # News search
    "SEARCH",           # Search for symbol
    "FUNDAMENTALS",     # P/E, market cap (future)
    "IPO",              # IPO info (future)
    "OPTIONS",          # F&O explainer
    "INTRADAY",         # Intraday plan
    "LONG_TERM",        # Long-term thesis
    "GENERAL",          # General query
]


class ParsedQuery(BaseModel):
    """Structured representation of user query."""
    intent: IntentType
    symbols: List[str] = Field(default_factory=list, description="Stock symbols mentioned")
    timeframe: Optional[str] = Field(None, description="Time period (1d, 1w, 1M, 3M, 1y)")
    query_text: str = Field(..., description="Original query")
    search_term: Optional[str] = Field(None, description="Company name for search")


class QueryRouter:
    """Parse user queries into structured intent + entities."""

    # Common Indian stock symbols
    KNOWN_SYMBOLS = {
        "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC",
        "BHARTIARTL", "HINDUNILVR", "KOTAKBANK", "LT", "BAJFINANCE", "MARUTI",
        "TITAN", "AXISBANK", "WIPRO", "ADANIPORTS", "ASIANPAINT", "ULTRACEMCO",
        "NIFTY", "SENSEX", "TATAMOTORS", "SUNPHARMA", "ONGC", "NTPC",
        "POWERGRID", "NESTLEIND", "JSWSTEEL", "TATASTEEL", "TECHM", "HCLTECH",
        "BAJAJFINSV", "DIVISLAB", "DRREDDY", "CIPLA", "EICHERMOT", "HEROMOTOCO",
        "M&M", "COALINDIA", "GRASIM", "APOLLOHOSP", "BRITANNIA", "SBILIFE",
        "HDFC", "BPCL", "HINDALCO", "INDUSINDBK", "UPL", "TATACONSUM",
    }

    # Intent keywords
    PRICE_KEYWORDS = {"price", "current", "trading", "ltp", "quote", "value", "worth", "what is", "how much"}
    CHART_KEYWORDS = {"chart", "graph", "candlestick", "historical", "trend", "performance", "movement"}
    NEWS_KEYWORDS = {"news", "headlines", "latest", "updates", "sentiment", "articles", "market buzz"}
    SEARCH_KEYWORDS = {"find", "search", "lookup", "which stock", "symbol for", "ticker"}
    OPTIONS_KEYWORDS = {"option", "options", "call option", "put option", "f&o", "futures", "derivatives", "strike", "premium", "expiry"}
    INTRADAY_KEYWORDS = {"intraday", "day trade", "scalping", "short term", "today", "swing trade"}
    LONG_TERM_KEYWORDS = {"invest", "long term", "hold", "portfolio", "fundamentals", "value investing", "dividend"}
    IPO_KEYWORDS = {"ipo", "upcoming ipo", "listing", "subscription", "allotment"}

    def parse(self, query: str) -> ParsedQuery:
        """
        Parse user query into structured intent + entities.

        Returns:
            ParsedQuery with intent, symbols, timeframe, etc.
        """
        query_lower = query.lower()
        query_upper = query.upper()

        # Extract symbols (known symbols in uppercase)
        symbols = []
        for word in query_upper.split():
            clean_word = re.sub(r'[^A-Z0-9&]', '', word)
            if clean_word in self.KNOWN_SYMBOLS:
                symbols.append(clean_word)

        # Also check for NSE-XXX or BSE-XXX format
        exchange_pattern = r'\b(NSE|BSE)-([A-Z]+)\b'
        for match in re.finditer(exchange_pattern, query_upper):
            sym = match.group(2)
            if sym not in symbols:
                symbols.append(sym)

        # Extract timeframe
        timeframe = self._extract_timeframe(query_lower)

        # Determine intent (order matters — most specific first)
        intent = self._determine_intent(query_lower, symbols)

        # Extract search term (for company names)
        search_term = None
        if intent == "SEARCH":
            search_term = self._extract_search_term(query, symbols)

        return ParsedQuery(
            intent=intent,
            symbols=symbols,
            timeframe=timeframe,
            query_text=query,
            search_term=search_term,
        )

    def _determine_intent(self, query_lower: str, symbols: List[str]) -> IntentType:
        """Determine primary intent from query."""

        # Options/F&O (check first as it's very specific)
        if any(kw in query_lower for kw in self.OPTIONS_KEYWORDS):
            return "OPTIONS"

        # IPO
        if any(kw in query_lower for kw in self.IPO_KEYWORDS):
            return "IPO"

        # Chart (check before price as "chart price" should be chart)
        if any(kw in query_lower for kw in self.CHART_KEYWORDS):
            return "CHART"

        # News
        if any(kw in query_lower for kw in self.NEWS_KEYWORDS):
            return "NEWS"

        # Search (no symbol mentioned + search keywords)
        if not symbols and any(kw in query_lower for kw in self.SEARCH_KEYWORDS):
            return "SEARCH"

        # Intraday
        if any(kw in query_lower for kw in self.INTRADAY_KEYWORDS):
            return "INTRADAY"

        # Long term
        if any(kw in query_lower for kw in self.LONG_TERM_KEYWORDS):
            return "LONG_TERM"

        # Price (if symbol mentioned or price keywords)
        if symbols or any(kw in query_lower for kw in self.PRICE_KEYWORDS):
            return "PRICE_QUOTE"

        # Default
        return "GENERAL"

    def _extract_timeframe(self, query: str) -> Optional[str]:
        """Extract time period from query."""
        timeframe_patterns = {
            r'\b(1|one)\s*day\b': '1d',
            r'\btoday\b': '1d',
            r'\b(1|one)\s*week\b': '1w',
            r'\b(1|one)\s*month\b': '1M',
            r'\b(3|three)\s*month': '3M',
            r'\b(6|six)\s*month': '6M',
            r'\b(1|one)\s*year\b': '1y',
            r'\b(5|five)\s*year': '5y',
        }

        for pattern, value in timeframe_patterns.items():
            if re.search(pattern, query):
                return value

        return None

    def _extract_search_term(self, query: str, symbols: List[str]) -> Optional[str]:
        """Extract company name for search queries."""
        # Remove known symbols from query
        cleaned = query
        for sym in symbols:
            cleaned = re.sub(rf'\b{sym}\b', '', cleaned, flags=re.IGNORECASE)

        # Remove common keywords
        for kw in ["find", "search", "stock", "symbol", "for", "what", "is", "the", "lookup"]:
            cleaned = re.sub(rf'\b{kw}\b', '', cleaned, flags=re.IGNORECASE)

        # Clean whitespace and return
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned if cleaned else None


# Global router instance
router = QueryRouter()


def route_query(text: str) -> ParsedQuery:
    """
    Convenience function: parse a user query into structured intent.

    Args:
        text: Raw user query string

    Returns:
        ParsedQuery with intent, symbols, timeframe, etc.
    """
    return router.parse(text)
