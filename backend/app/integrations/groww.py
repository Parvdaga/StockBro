"""
Groww API client for Indian stock market data
Uses Groww web API for live prices + SDK for instrument metadata
"""
import httpx
import asyncio
from typing import Optional, List, Dict
from app.schemas.stock import StockData
from app.config import settings

# Try to import the SDK for instrument lookups
try:
    from growwapi import GrowwAPI
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False
    print("⚠️  growwapi SDK not installed — instrument search disabled")


# Groww web API base URL (free, no auth needed)
GROWW_WEB_API = "https://groww.in/v1/api/stocks_data/v1"
GROWW_SEARCH_API = "https://groww.in/v1/api/search/v3/query/globalSuggestion/exchange/NSE_EQ"
GROWW_COMPANY_API = "https://groww.in/v1/api/stocks_data/v1/company/search/groww_contract"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}


class GrowwClient:
    """Client for Indian stock market data via Groww"""

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
        """Get cached NSE equity instruments DataFrame (loaded once)"""
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
    async def get_live_price(self, trading_symbol: str, exchange: str = "NSE") -> Optional[Dict]:
        """
        Get live price data from Groww web API.
        Returns dict with: ltp, open, high, low, close, volume, dayChange, dayChangePerc,
                           yearHighPrice, yearLowPrice, etc.
        """
        url = f"{GROWW_WEB_API}/accord_points/exchange/{exchange}/segment/CASH/latest_prices_ohlc/{trading_symbol}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=HEADERS)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Groww web API error for {trading_symbol}: HTTP {response.status_code}")
                    return None
        except Exception as e:
            print(f"Groww web API error for {trading_symbol}: {e}")
            return None

    # ──────────────────────────────────────────────
    # Instrument metadata via SDK
    # ──────────────────────────────────────────────
    def get_instrument_info(self, groww_symbol: str) -> Optional[Dict]:
        """
        Get instrument metadata from SDK.
        groww_symbol format: NSE-RELIANCE, BSE-TCS
        """
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
        Accepts: 'RELIANCE', 'NSE-RELIANCE', 'BSE-RELIANCE', 'TCS', etc.
        """
        # Parse symbol
        exchange, trading_symbol = self._parse_symbol(symbol)

        # Fetch live price (primary data source)
        live_data = await self.get_live_price(trading_symbol, exchange)
        if not live_data:
            return None

        # Try to get instrument name from SDK
        groww_symbol = f"{exchange}-{trading_symbol}"
        instrument = self.get_instrument_info(groww_symbol)
        company_name = (instrument or {}).get("name", trading_symbol)

        # Build StockData
        return StockData(
            symbol=groww_symbol,
            name=company_name,
            current_price=float(live_data.get("ltp", 0)),
            change_percent=live_data.get("dayChangePerc"),
            volume=live_data.get("volume"),
            market_cap=None,  # Not available from this endpoint
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
        """
        Search for Indian stocks by name or symbol.
        Uses SDK instrument list (reliable) with web API as fallback.
        """
        # Primary: SDK-based search (always works)
        results = await self._search_instruments_sdk(query, max_results)
        if results:
            return results

        # Fallback: Groww web search API
        try:
            url = GROWW_SEARCH_API
            params = {"q": query, "size": max_results, "page": 0}
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=HEADERS)
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
                    return results
        except Exception as e:
            print(f"Groww search error: {e}")

        return []

    async def _search_instruments_sdk(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search using cached SDK instrument list"""
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
        """Get trending/popular Indian stocks with live prices"""
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
        """Parse symbol into (exchange, trading_symbol)"""
        symbol = symbol.strip().upper()
        if "-" in symbol:
            parts = symbol.split("-", 1)
            exchange = parts[0] if parts[0] in ("NSE", "BSE") else "NSE"
            trading_symbol = parts[1]
        else:
            exchange = "NSE"
            trading_symbol = symbol
        return exchange, trading_symbol
