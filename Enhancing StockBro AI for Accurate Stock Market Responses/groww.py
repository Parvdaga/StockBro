"""
Groww API client for Indian stock market data.
Uses Groww web API for live prices, historical OHLCV, and search.
Features: TTL caching, connection pooling, exponential backoff retry.
"""
import httpx
import asyncio
import time
from typing import Optional, List, Dict, Any

try:
    import yfinance as yf
    _YFINANCE_AVAILABLE = True
except ImportError:
    _YFINANCE_AVAILABLE = False
    print("⚠️  yfinance not installed — historical chart data disabled")

from app.schemas.stock import StockData
from app.core.config import settings
from app.integrations.cache import TTLCache
from app.integrations.retry import async_retry
from app.integrations.rate_limiter import get_limiter

# Groww web API base URLs (free, no auth needed)
GROWW_WEB_API = "https://groww.in/v1/api/stocks_data/v1"
GROWW_SEARCH_API = "https://groww.in/v1/api/search/v3/query/globalSuggestion/exchange/NSE_EQ"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

# Duration presets → yfinance (period, interval)
DURATION_MAP_YF = {
    "1d": ("1d", "5m"),
    "1w": ("5d", "15m"),
    "1M": ("1mo", "1d"),
    "3M": ("3mo", "1d"),
    "6M": ("6mo", "1d"),
    "1y": ("1y", "1wk"),
    "5y": ("5y", "1mo"),
}

# Module-level caches
_price_cache = TTLCache(max_size=200, default_ttl=30, stale_window=300)   # 30s TTL + 5min stale
_history_cache = TTLCache(max_size=50, default_ttl=300)     # 5min for historical
_search_cache = TTLCache(max_size=50, default_ttl=600)      # 10min for search

# Rate limiter for Groww API
_rate_limiter = get_limiter("groww")

# Shared httpx client (connection pooling)
_http_client: Optional[httpx.AsyncClient] = None


class RequestCoalescer:
    """Coalesce concurrent requests for the same resource into a single upstream call."""

    def __init__(self):
        self._pending: Dict[str, asyncio.Future] = {}
        self._lock = asyncio.Lock()

    async def coalesce(self, key: str, fetch_fn):
        """
        If multiple concurrent calls request the same key, only one fetch happens.
        """
        async with self._lock:
            if key in self._pending:
                # Another request is already fetching this — wait for it
                return await self._pending[key]

            # Create a new future for this fetch
            future = asyncio.Future()
            self._pending[key] = future

        try:
            result = await fetch_fn()
            future.set_result(result)
            return result
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            async with self._lock:
                self._pending.pop(key, None)


# Module-level coalescer
_coalescer = RequestCoalescer()


def _get_http_client() -> httpx.AsyncClient:
    """Get or create the shared async HTTP client."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=10.0, headers=HEADERS)
    return _http_client


class GrowwClient:
    """Client for Indian stock market data via Groww — with caching & retry."""

    def __init__(self):
        self.api_key = settings.GROWW_API_KEY

    @staticmethod
    def _parse_symbol(symbol: str) -> (str, str):
        """Parse 'NSE-RELIANCE' or 'RELIANCE' into (exchange, symbol)."""
        if "-" in symbol:
            parts = symbol.split("-")
            return parts[0].upper(), parts[1].upper()
        return "NSE", symbol.upper()

    # ──────────────────────────────────────────────
    # Live price data via Groww web API
    # ──────────────────────────────────────────────
    @async_retry(max_retries=2, base_delay=0.5)
    async def get_live_price(self, trading_symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """
        Get live price data from Groww web API (cached for 30s, coalesced).
        """
        cache_key = f"price:{exchange}:{trading_symbol}"
        cached = _price_cache.get(cache_key)
        if cached is not None:
            return cached

        # Coalesce concurrent requests — only 1 upstream call per symbol
        async def _fetch():
            # Check rate limit; if exhausted, try stale data
            if not await _rate_limiter.acquire():
                stale = _price_cache.get(cache_key, allow_stale=True)
                if stale:
                    print(f"[GROWW] Rate-limited, serving stale data for {trading_symbol}")
                    return stale
                return None

            url = f"{GROWW_WEB_API}/accord_points/exchange/{exchange}/segment/CASH/latest_prices_ohlc/{trading_symbol}"
            try:
                client = _get_http_client()
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    _price_cache.set(cache_key, data)
                    return data
                elif response.status_code == 429:
                    # Fallback to stale if rate limited by upstream
                    stale = _price_cache.get(cache_key, allow_stale=True)
                    if stale:
                        return stale
                    return None
                else:
                    print(f"Groww web API error for {trading_symbol}: HTTP {response.status_code}")
                    return None
            except Exception as e:
                print(f"Groww web API error for {trading_symbol}: {e}")
                # Fallback to stale on network error
                stale = _price_cache.get(cache_key, allow_stale=True)
                return stale

        return await _coalescer.coalesce(cache_key, _fetch)

    async def get_stock_data(self, symbol: str) -> Optional[StockData]:
        """Convenience method to get formatted StockData."""
        raw = await self.get_live_price(symbol)
        if not raw:
            return None
            
        try:
            return StockData(
                symbol=symbol,
                name=raw.get("displayName", symbol),
                current_price=raw.get("ltp", 0),
                open_price=raw.get("open", 0),
                high_price=raw.get("high", 0),
                low_price=raw.get("low", 0),
                prev_close=raw.get("close", 0),
                change=raw.get("dayChange", 0),
                change_percent=raw.get("dayChangePerc", 0),
                volume=raw.get("volume", 0),
                last_updated=int(time.time())
            )
        except Exception as e:
            print(f"Error formatting stock data for {symbol}: {e}")
            return None

    # ──────────────────────────────────────────────
    # Historical OHLCV data for charts (via yfinance)
    # ──────────────────────────────────────────────
    async def get_historical_data(
        self,
        trading_symbol: str,
        exchange: str = "NSE",
        duration: str = "3M",
    ) -> Optional[List[Dict]]:
        """
        Get historical OHLCV candle data for charting (cached for 5min).
        """
        if not _YFINANCE_AVAILABLE:
            return None

        cache_key = f"history:{exchange}:{trading_symbol}:{duration}"
        cached = _history_cache.get(cache_key)
        if cached is not None:
            return cached

        yf_period, yf_interval = DURATION_MAP_YF.get(duration, ("3mo", "1d"))
        suffix = ".NS" if exchange == "NSE" else ".BO"
        yf_symbol = f"{trading_symbol}{suffix}"

        try:
            loop = asyncio.get_event_loop()

            def _fetch():
                ticker = yf.Ticker(yf_symbol)
                df = ticker.history(period=yf_period, interval=yf_interval)
                return df

            df = await loop.run_in_executor(None, _fetch)

            if df is None or df.empty:
                return None

            formatted = []
            for idx, row in df.iterrows():
                ts = int(idx.timestamp())
                formatted.append({
                    "timestamp": ts,
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]) if row["Volume"] else None,
                })

            if formatted:
                _history_cache.set(cache_key, formatted)
            return formatted

        except Exception as e:
            print(f"[CHART] yfinance error for {yf_symbol}: {e}")
            return None

    # ──────────────────────────────────────────────
    # Search for instruments
    # ──────────────────────────────────────────────
    async def search_stocks(self, query: str, size: int = 10) -> List[Dict]:
        """Search for stocks on Groww."""
        cache_key = f"search:{query}:{size}"
        cached = _search_cache.get(cache_key)
        if cached:
            return cached

        params = {"query": query, "size": size}
        try:
            client = _get_http_client()
            response = await client.get(GROWW_SEARCH_API, params=params)
            if response.status_code == 200:
                data = response.json()
                results = data.get("data", [])
                # Filter for stocks
                stocks = [r for r in results if r.get("entity_type") == "STOCKS"]
                _search_cache.set(cache_key, stocks)
                return stocks
            return []
        except Exception as e:
            print(f"Groww search error: {e}")
            return []

    async def get_trending_stocks(self) -> List[StockData]:
        """Get trending/popular Indian stocks with live prices."""
        # Use a default list of high-volume NIFTY 50 stocks as trending
        trending_symbols = ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "SBIN", "ITC", "BHARTIARTL"]
        tasks = [self.get_stock_data(sym) for sym in trending_symbols]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]
