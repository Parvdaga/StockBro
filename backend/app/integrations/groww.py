"""
Groww API client for Indian stock market data.
Uses Groww web API for live prices, historical OHLCV, and search.
Features: TTL caching, connection pooling, exponential backoff retry.
"""
import httpx
import asyncio
import time
from typing import Optional, List, Dict

try:
    import yfinance as yf
    _YFINANCE_AVAILABLE = True
except ImportError:
    _YFINANCE_AVAILABLE = False
    print("⚠️  yfinance not installed — historical chart data disabled")

from app.schemas.stock import StockData
from app.config import settings
from app.integrations.cache import TTLCache
from app.integrations.retry import async_retry

# Try to import the SDK for instrument lookups
try:
    from growwapi import GrowwAPI
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False
    print("⚠️  growwapi SDK not installed — instrument search disabled")


# Groww web API base URLs (free, no auth needed)
GROWW_WEB_API = "https://groww.in/v1/api/stocks_data/v1"
GROWW_SEARCH_API = "https://groww.in/v1/api/search/v3/query/globalSuggestion/exchange/NSE_EQ"
GROWW_CHARTING_API = "https://groww.in/v1/api/charting_service/v2/chart/exchange"

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
_price_cache = TTLCache(max_size=200, default_ttl=30)      # 30s for live prices
_history_cache = TTLCache(max_size=50, default_ttl=300)     # 5min for historical
_search_cache = TTLCache(max_size=50, default_ttl=600)      # 10min for search

# Shared httpx client (connection pooling)
_http_client: Optional[httpx.AsyncClient] = None


def _get_http_client() -> httpx.AsyncClient:
    """Get or create the shared async HTTP client."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=10.0, headers=HEADERS)
    return _http_client


class GrowwClient:
    """Client for Indian stock market data via Groww — with caching & retry."""

    _instruments_df = None  # Class-level cache for instruments

    def __init__(self):
        self.api_key = settings.GROWW_API_KEY
        self._sdk = None
        if _SDK_AVAILABLE and self.api_key:
            try:
                self._sdk = GrowwAPI(self.api_key)
            except Exception as e:
                print(f"[WARN] Groww SDK init failed: {e}")

    def _get_equity_instruments(self):
        """Get cached NSE equity instruments DataFrame (loaded once)."""
        if GrowwClient._instruments_df is None and self._sdk:
            try:
                all_inst = self._sdk.get_all_instruments()
                GrowwClient._instruments_df = all_inst[
                    (all_inst["segment"] == "CASH") &
                    (all_inst["exchange"] == "NSE") &
                    (all_inst["instrument_type"] == "EQ")
                ].copy()
                print(f"[GROWW] Cached {len(GrowwClient._instruments_df)} NSE equity instruments")
            except Exception as e:
                print(f"[WARN] Failed to load instruments: {e}")
                return None
        return GrowwClient._instruments_df

    # ──────────────────────────────────────────────
    # Live price data via Groww web API
    # ──────────────────────────────────────────────
    @async_retry(max_retries=2, base_delay=0.5)
    async def get_live_price(self, trading_symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """
        Get live price data from Groww web API (cached for 30s).
        Returns dict with: ltp, open, high, low, close, volume, dayChange, dayChangePerc, etc.
        """
        cache_key = f"price:{exchange}:{trading_symbol}"
        cached = _price_cache.get(cache_key)
        if cached is not None:
            return cached

        url = f"{GROWW_WEB_API}/accord_points/exchange/{exchange}/segment/CASH/latest_prices_ohlc/{trading_symbol}"
        try:
            client = _get_http_client()
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                _price_cache.set(cache_key, data)
                return data
            else:
                print(f"Groww web API error for {trading_symbol}: HTTP {response.status_code}")
                return None
        except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError):
            raise  # Let retry handle
        except Exception as e:
            print(f"Groww web API error for {trading_symbol}: {e}")
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
        Uses yfinance with .NS (NSE) or .BO (BSE) suffix.

        Args:
            trading_symbol: NSE symbol (e.g. RELIANCE)
            exchange: NSE or BSE
            duration: One of 1d, 1w, 1M, 3M, 6M, 1y, 5y

        Returns:
            List of dicts with timestamp, open, high, low, close, volume
        """
        if not _YFINANCE_AVAILABLE:
            print("[CHART] yfinance not installed")
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
                """Fetch with retry for transient yfinance errors."""
                last_err = None
                for attempt in range(3):
                    try:
                        ticker = yf.Ticker(yf_symbol)
                        df = ticker.history(period=yf_period, interval=yf_interval)
                        if df is not None and not df.empty:
                            return df
                    except Exception as e:
                        last_err = e
                        import time as _time
                        _time.sleep(1)
                if last_err:
                    print(f"[CHART] yfinance {yf_symbol} failed after 3 tries: {last_err}")
                return None

            df = await loop.run_in_executor(None, _fetch)

            if df is None or df.empty:
                print(f"[CHART] No data from yfinance for {yf_symbol}")
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

    @staticmethod
    def _format_candles(candles: list) -> List[Dict]:
        """Convert Groww candle array to chart-ready dicts."""
        formatted = []
        for c in candles:
            # Groww candle format: [timestamp, open, high, low, close, volume]
            if isinstance(c, (list, tuple)) and len(c) >= 5:
                formatted.append({
                    "timestamp": int(c[0]),
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4]),
                    "volume": int(c[5]) if len(c) > 5 else None,
                })
            elif isinstance(c, dict):
                formatted.append({
                    "timestamp": c.get("timestamp", c.get("t", 0)),
                    "open": float(c.get("open", c.get("o", 0))),
                    "high": float(c.get("high", c.get("h", 0))),
                    "low": float(c.get("low", c.get("l", 0))),
                    "close": float(c.get("close", c.get("c", 0))),
                    "volume": c.get("volume", c.get("v")),
                })
        return formatted

    # ──────────────────────────────────────────────
    # Instrument metadata via SDK
    # ──────────────────────────────────────────────
    def get_instrument_info(self, groww_symbol: str) -> Optional[Dict]:
        """Get instrument metadata from SDK."""
        if not self._sdk:
            return None
        try:
            return self._sdk.get_instrument_by_groww_symbol(groww_symbol=groww_symbol)
        except Exception as e:
            print(f"Groww SDK instrument lookup failed for {groww_symbol}: {e}")
            return None

    # ──────────────────────────────────────────────
    # Combined: full stock data
    # ──────────────────────────────────────────────
    async def get_stock_data(self, symbol: str) -> Optional[StockData]:
        """
        Get complete stock data combining live prices + instrument metadata.
        Accepts: 'RELIANCE', 'NSE-RELIANCE', 'BSE-RELIANCE', etc.
        """
        exchange, trading_symbol = self._parse_symbol(symbol)

        # Fetch live price (primary data source)
        live_data = await self.get_live_price(trading_symbol, exchange)
        if not live_data:
            return None

        # Try to get instrument name from SDK
        groww_symbol = f"{exchange}-{trading_symbol}"
        instrument = self.get_instrument_info(groww_symbol)
        company_name = (instrument or {}).get("name", trading_symbol)

        return StockData(
            symbol=groww_symbol,
            name=company_name,
            current_price=float(live_data.get("ltp", 0)),
            change_percent=live_data.get("dayChangePerc"),
            volume=live_data.get("volume"),
            market_cap=None,
            pe_ratio=None,
            eps=None,
            dividend_yield=None,
            week_52_high=live_data.get("yearHighPrice"),
            week_52_low=live_data.get("yearLowPrice"),
        )

    # ──────────────────────────────────────────────
    # Search stocks
    # ──────────────────────────────────────────────
    async def search_stocks(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for Indian stocks by name or symbol (cached for 10min)."""
        cache_key = f"search:{query.upper()}"
        cached = _search_cache.get(cache_key)
        if cached is not None:
            return cached[:max_results]

        # Primary: SDK-based search
        results = await self._search_instruments_sdk(query, max_results)
        if results:
            _search_cache.set(cache_key, results)
            return results

        # Fallback: Groww web search API
        try:
            params = {"q": query, "size": max_results, "page": 0}
            client = _get_http_client()
            response = await client.get(GROWW_SEARCH_API, params=params)
            if response.status_code == 200:
                data = response.json()
                results = []
                content = data.get("data", {}).get("content", []) or data.get("content", [])
                for item in content:
                    entity = item.get("entity_data", item)
                    results.append({
                        "symbol": entity.get("nse_scrip_code") or entity.get("bse_scrip_code") or "",
                        "name": entity.get("company_name") or entity.get("title") or "",
                        "exchange": "NSE",
                        "groww_symbol": f"NSE-{entity.get('nse_scrip_code', '')}",
                    })
                if results:
                    _search_cache.set(cache_key, results)
                return results
        except Exception as e:
            print(f"Groww search error: {e}")

        return []

    async def _search_instruments_sdk(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search using cached SDK instrument list."""
        if not self._sdk:
            return []
        try:
            loop = asyncio.get_event_loop()

            def _search():
                df = self._get_equity_instruments()
                if df is None or df.empty:
                    return []
                q = query.upper()
                matches = df[
                    df["trading_symbol"].str.contains(q, na=False) |
                    df["name"].str.contains(q, case=False, na=False)
                ]
                return matches.head(max_results).to_dict("records")

            results = await loop.run_in_executor(None, _search)
            return [
                {
                    "symbol": r.get("trading_symbol", ""),
                    "name": r.get("name", ""),
                    "exchange": r.get("exchange", "NSE"),
                    "groww_symbol": r.get("groww_symbol", ""),
                }
                for r in results
            ]
        except Exception as e:
            print(f"SDK search error: {e}")
            return []

    # ──────────────────────────────────────────────
    # Trending / popular stocks
    # ──────────────────────────────────────────────
    async def get_trending_stocks(self) -> List[Dict]:
        """Get trending/popular Indian stocks with live prices."""
        popular_symbols = [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
            "HINDUNILVR", "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK",
            "LT", "AXISBANK", "BAJFINANCE", "MARUTI", "TITAN",
        ]
        results = []
        for sym in popular_symbols[:10]:
            data = await self.get_stock_data(sym)
            if data:
                results.append(data)
        return results

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────
    @staticmethod
    def _parse_symbol(symbol: str) -> tuple:
        """Parse symbol into (exchange, trading_symbol)."""
        symbol = symbol.strip().upper()
        if "-" in symbol:
            parts = symbol.split("-", 1)
            exchange = parts[0] if parts[0] in ("NSE", "BSE") else "NSE"
            trading_symbol = parts[1]
        else:
            exchange = "NSE"
            trading_symbol = symbol
        return exchange, trading_symbol
