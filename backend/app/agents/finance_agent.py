"""
Finance Agent — fetches Indian stock data via Groww API
"""
from phi.agent import Agent
from app.config import settings
from app.agents.shared_model import get_model
import asyncio

# Import Groww client
try:
    from growwapi import GrowwAPI
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False
    GrowwAPI = None

# HTTP-based price fetcher (Groww web API — free, no auth)
import requests

GROWW_WEB_API = "https://groww.in/v1/api/stocks_data/v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

# Module-level cache for equity instruments DataFrame
_cached_equity_df = None


def _parse_symbol(symbol: str) -> tuple:
    """Parse symbol like 'RELIANCE', 'NSE-RELIANCE' → (exchange, trading_symbol)"""
    symbol = symbol.strip().upper()
    if "-" in symbol:
        parts = symbol.split("-", 1)
        exchange = parts[0] if parts[0] in ("NSE", "BSE") else "NSE"
        trading_symbol = parts[1]
    else:
        exchange = "NSE"
        trading_symbol = symbol
    return exchange, trading_symbol


def _get_instrument_name(groww_symbol: str) -> str:
    """Get company name from SDK instrument lookup"""
    if not _SDK_AVAILABLE or not settings.GROWW_API_KEY:
        return groww_symbol.split("-")[-1]
    try:
        groww = GrowwAPI(settings.GROWW_API_KEY)
        info = groww.get_instrument_by_groww_symbol(groww_symbol=groww_symbol)
        return info.get("name", groww_symbol.split("-")[-1]) if info else groww_symbol.split("-")[-1]
    except Exception:
        return groww_symbol.split("-")[-1]


def get_stock_price(symbol: str) -> str:
    """
    Get the current stock price and market data for an Indian stock.
    
    Args:
        symbol (str): Stock symbol like 'RELIANCE', 'TCS', 'INFY', 'HDFCBANK',
                      or with exchange prefix like 'NSE-RELIANCE', 'BSE-TCS'.
                      For NIFTY index, use 'NIFTY 50'. For SENSEX, use 'SENSEX'.
    
    Returns:
        str: Stock data summary in text format.
    """
    try:
        exchange, trading_symbol = _parse_symbol(symbol)
        groww_symbol = f"{exchange}-{trading_symbol}"

        # Fetch live price from Groww web API
        url = f"{GROWW_WEB_API}/accord_points/exchange/{exchange}/segment/CASH/latest_prices_ohlc/{trading_symbol}"
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return f"Stock not found: {symbol}"

        data = response.json()
        ltp = data.get("ltp", "N/A")
        day_change = data.get("dayChange", 0)
        day_change_perc = data.get("dayChangePerc", 0)
        open_price = data.get("open", "N/A")
        high = data.get("high", "N/A")
        low = data.get("low", "N/A")
        close = data.get("close", "N/A")
        volume = data.get("volume", "N/A")
        year_high = data.get("yearHighPrice", "N/A")
        year_low = data.get("yearLowPrice", "N/A")

        # Get company name
        company_name = _get_instrument_name(groww_symbol)

        # Return structured text data for the LLM to format
        return (
            f"Stock: {company_name} ({groww_symbol})\n"
            f"Current Price: ₹{ltp}\n"
            f"Day Change: ₹{day_change} ({day_change_perc}%)\n"
            f"Open: ₹{open_price} | High: ₹{high} | Low: ₹{low} | Prev Close: ₹{close}\n"
            f"Volume: {volume}\n"
            f"52-Week High: ₹{year_high} | 52-Week Low: ₹{year_low}"
        )

    except Exception as e:
        return f"Error fetching stock price for '{symbol}': {str(e)}"


def search_stock(query: str) -> str:
    """
    Search for Indian stocks by company name or symbol.
    
    Args:
        query (str): Company name or stock symbol to search for
                     (e.g., 'Reliance', 'Tata', 'Banking')
    
    Returns:
        str: List of matching stock symbols and names.
    """
    if not _SDK_AVAILABLE or not settings.GROWW_API_KEY:
        return "Stock search is not available (SDK not installed)."

    try:
        global _cached_equity_df
        if _cached_equity_df is None:
            groww = GrowwAPI(settings.GROWW_API_KEY)
            all_inst = groww.get_all_instruments()
            _cached_equity_df = all_inst[
                (all_inst["segment"] == "CASH") &
                (all_inst["exchange"] == "NSE") &
                (all_inst["instrument_type"] == "EQ")
            ].copy()

        q = query.upper()
        matches = _cached_equity_df[
            _cached_equity_df["trading_symbol"].str.contains(q, na=False) |
            _cached_equity_df["name"].str.contains(q, case=False, na=False)
        ].head(10)

        if matches.empty:
            return f"No Indian stocks found matching '{query}'."

        lines = [f"Stocks matching '{query}':\n"]
        for _, row in matches.iterrows():
            lines.append(f"- {row['name']} -- {row['trading_symbol']} ({row['exchange']})")

        return "\n".join(lines)

    except Exception as e:
        return f"Error searching stocks: {str(e)}"


# Create the Finance Agent
finance_agent = Agent(
    name="Finance Agent",
    role="Indian Stock Market Data Specialist",
    model=get_model(),
    tools=[get_stock_price, search_stock],
    instructions=[
        "You are a specialist in Indian stock market data.",
        "Use 'get_stock_price' to fetch the latest price of any Indian stock (NSE/BSE).",
        "Use 'search_stock' if the user asks about a company and you need the stock symbol.",
        "Always use the stock SYMBOL (like RELIANCE, TCS, INFY, HDFCBANK) when calling get_stock_price.",
        "For NIFTY 50, use 'NIFTY 50'. For SENSEX, use 'SENSEX'.",
        "Common Indian stock symbols: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, SBIN, ITC, BHARTIARTL, HINDUNILVR, KOTAKBANK, LT, BAJFINANCE, MARUTI, TITAN, AXISBANK.",
        "All prices are in Indian Rupees (₹).",
    ],
    show_tool_calls=True,
    markdown=True,
)
