"""
Query router — parse user intent before calling tools.
Ensures consistent, deterministic tool selection.
"""
from typing import Literal, Optional, List, Dict
from pydantic import BaseModel, Field
import re

# Intent types
IntentType = Literal[
    "PRICE_QUOTE",      # Get current price
    "CHART",            # Historical chart
    "NEWS",             # News search
    "SEARCH",           # Search for symbol
    "FUNDAMENTALS",     # P/E, market cap (future)
    "IPO",              # IPO info
    "OPTIONS",          # F&O explainer
    "INTRADAY",         # Intraday plan
    "LONG_TERM",        # Long-term thesis
    "GENERAL",          # General query
    "EDUCATIONAL",      # Learning about terms
]


class ParsedQuery(BaseModel):
    """Structured representation of user query."""
    intent: IntentType
    symbols: List[str] = Field(default_factory=list, description="Stock symbols mentioned")
    timeframe: Optional[str] = Field(None, description="Time period (1d, 1w, 1M, 3M, 1y)")
    query_text: str = Field(..., description="Original query")
    search_term: Optional[str] = Field(None, description="Company name for search")
    is_complex: bool = Field(False, description="Whether the query requires multiple tools")


class QueryRouter:
    """Parse user queries into structured intent + entities."""

    # Common Indian stock symbols and their common names/nicknames
    NICKNAMES = {
        "RELIANCE": ["reliance", "ril", "mukesh ambani"],
        "TCS": ["tcs", "tata consultancy"],
        "INFY": ["infosys", "infy"],
        "HDFCBANK": ["hdfc bank", "hdfc", "hdfcb"],
        "ICICIBANK": ["icici bank", "icici"],
        "SBIN": ["sbi", "state bank", "sbin"],
        "ITC": ["itc"],
        "BHARTIARTL": ["airtel", "bharti airtel"],
        "TATAMOTORS": ["tata motors", "tamotors"],
        "ZOMATO": ["zomato"],
        "PAYTM": ["paytm", "one97"],
        "NIFTY": ["nifty", "nifty 50", "index"],
        "SENSEX": ["sensex", "bse index"],
    }

    # Reverse mapping for quick lookup
    SYMBOL_MAP: Dict[str, str] = {}
    for sym, names in NICKNAMES.items():
        for name in names:
            SYMBOL_MAP[name] = sym

    # Intent keywords
    PRICE_KEYWORDS = {"price", "current", "trading", "ltp", "quote", "value", "worth", "how much", "rate"}
    CHART_KEYWORDS = {"chart", "graph", "candlestick", "historical", "trend", "performance", "movement", "show me"}
    NEWS_KEYWORDS = {"news", "headlines", "latest", "updates", "sentiment", "articles", "market buzz", "happening"}
    SEARCH_KEYWORDS = {"find", "search", "lookup", "which stock", "symbol for", "ticker", "suggest"}
    OPTIONS_KEYWORDS = {"call option", "put option", "f&o", "futures", "derivatives", "strike", "premium", "expiry"}
    INTRADAY_KEYWORDS = {"intraday", "day trade", "scalping", "short term", "today", "swing trade", "entry", "exit"}
    LONG_TERM_KEYWORDS = {"invest", "long term", "hold", "portfolio", "fundamentals", "value investing", "dividend", "multibagger"}
    IPO_KEYWORDS = {"ipo", "upcoming ipo", "listing", "subscription", "allotment", "gmp", "grey market"}
    EDUCATIONAL_KEYWORDS = {"what is", "define", "explain", "how does", "meaning of", "learn"}

    def parse(self, query: str) -> ParsedQuery:
        """
        Parse user query into structured intent + entities.
        """
        query_lower = query.lower()
        
        # Extract symbols using nicknames and direct matches
        symbols = self._extract_symbols(query_lower)

        # Extract timeframe
        timeframe = self._extract_timeframe(query_lower)

        # Determine intent (order matters — most specific first)
        intent = self._determine_intent(query_lower, symbols)

        # Extract search term (for company names)
        search_term = None
        if intent == "SEARCH" or (not symbols and intent == "PRICE_QUOTE"):
            search_term = self._extract_search_term(query, symbols)

        # Check if query is complex (e.g., news AND price)
        is_complex = self._is_complex_query(query_lower)

        return ParsedQuery(
            intent=intent,
            symbols=symbols,
            timeframe=timeframe,
            query_text=query,
            search_term=search_term,
            is_complex=is_complex,
        )

    def _extract_symbols(self, query_lower: str) -> List[str]:
        """Extract stock symbols using fuzzy and nickname matching."""
        found = set()
        
        # 1. Check for nicknames/common names
        for name, sym in self.SYMBOL_MAP.items():
            if re.search(rf'\b{re.escape(name)}\b', query_lower):
                found.add(sym)
        
        # 2. Check for NSE-XXX or BSE-XXX format
        exchange_pattern = r'\b(nse|bse)-([a-z0-9&]+)\b'
        for match in re.finditer(exchange_pattern, query_lower):
            found.add(match.group(2).upper())
            
        # 3. Check for standalone uppercase words that might be symbols (if 3+ chars)
        # (This is more risky, so we keep it conservative)
        potential_syms = re.findall(r'\b[A-Z]{3,10}\b', query_lower.upper())
        for sym in potential_syms:
            # We could validate against a master list here
            if sym in ["NIFTY", "SENSEX", "RELIANCE", "TCS", "INFY"]:
                found.add(sym)

        return list(found)

    def _determine_intent(self, query_lower: str, symbols: List[str]) -> IntentType:
        """Determine primary intent from query."""
        
        # Price (if symbol mentioned + price keyword, prioritize price)
        if symbols and any(kw in query_lower for kw in self.PRICE_KEYWORDS):
            return "PRICE_QUOTE"

        # Specific domains
        if any(kw in query_lower for kw in self.OPTIONS_KEYWORDS):
            return "OPTIONS"
        if any(kw in query_lower for kw in self.IPO_KEYWORDS):
            return "IPO"
        if any(kw in query_lower for kw in self.INTRADAY_KEYWORDS):
            return "INTRADAY"
        if any(kw in query_lower for kw in self.LONG_TERM_KEYWORDS):
            return "LONG_TERM"
            
        # Functional intents
        if any(kw in query_lower for kw in self.CHART_KEYWORDS):
            return "CHART"
        if any(kw in query_lower for kw in self.NEWS_KEYWORDS):
            return "NEWS"
        if any(kw in query_lower for kw in self.EDUCATIONAL_KEYWORDS):
            return "EDUCATIONAL"
            
        # Search/Lookup
        if not symbols and any(kw in query_lower for kw in self.SEARCH_KEYWORDS):
            return "SEARCH"
            
        # Price (default if symbol mentioned)
        if symbols or any(kw in query_lower for kw in self.PRICE_KEYWORDS):
            return "PRICE_QUOTE"

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
        cleaned = query.lower()
        # Remove known symbols and common words
        for sym in symbols:
            cleaned = re.sub(rf'\b{sym.lower()}\b', '', cleaned)
        
        stop_words = ["find", "search", "stock", "symbol", "for", "what", "is", "the", "lookup", "price", "of"]
        for kw in stop_words:
            cleaned = re.sub(rf'\b{kw}\b', '', cleaned)

        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned if cleaned else None

    def _is_complex_query(self, query_lower: str) -> bool:
        """Check if query mentions multiple domains (e.g., price AND news)."""
        counts = 0
        if any(kw in query_lower for kw in self.PRICE_KEYWORDS): counts += 1
        if any(kw in query_lower for kw in self.NEWS_KEYWORDS): counts += 1
        if any(kw in query_lower for kw in self.CHART_KEYWORDS): counts += 1
        return counts > 1


# Global router instance
router = QueryRouter()

def route_query(text: str) -> ParsedQuery:
    """Convenience function: parse a user query into structured intent."""
    return router.parse(text)
