"""
Finance Agent — fetches Indian stock data via Groww API
"""
from phi.agent import Agent
from app.core.config import settings
from app.agents.shared_model import get_model
from app.integrations.groww import GrowwClient
import asyncio
import concurrent.futures

# Shared Groww client with caching + retry + pooling
_groww_client = GrowwClient()

# Thread pool for running async code from sync context (phi-agent tools are sync)
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

def _run_async(coro):
    """Run an async coroutine from a sync context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    
    if loop and loop.is_running():
        def _thread_run():
            return asyncio.run(coro)
        future = _executor.submit(_thread_run)
        return future.result(timeout=15)
    else:
        return asyncio.run(coro)


def get_stock_price(symbol: str) -> str:
    """
    Get the current stock price and market data for an Indian stock.
    
    Args:
        symbol (str): Stock symbol like 'RELIANCE', 'TCS', 'INFY', 'HDFCBANK',
                     or with exchange prefix like 'NSE-RELIANCE', 'BSE-TCS'.
    
    Returns:
        str: Stock data summary in text format with timestamp.
    """
    try:
        # Use centralized GrowwClient with caching + retry
        stock_data = _run_async(_groww_client.get_stock_data(symbol))
        
        if not stock_data:
            return f"❌ Stock not found: {symbol}. Try using 'search_stock' first."
        
        # Get live price for freshness
        exchange, trading_symbol = _groww_client._parse_symbol(symbol)
        live_data = _run_async(_groww_client.get_live_price(trading_symbol, exchange))
        
        if not live_data:
            return f"❌ Unable to fetch live price for {symbol}"
        
        ltp = live_data.get("ltp", "N/A")
        day_change = live_data.get("dayChange", 0)
        day_change_perc = live_data.get("dayChangePerc", 0)
        open_price = live_data.get("open", "N/A")
        high = live_data.get("high", "N/A")
        low = live_data.get("low", "N/A")
        close = live_data.get("close", "N/A")
        volume = live_data.get("volume", "N/A")
        year_high = live_data.get("yearHighPrice", "N/A")
        year_low = live_data.get("yearLowPrice", "N/A")
        
        # Include data source timestamp
        import time
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S IST")
        
        return (
            f"📊 **Stock Data** (as of {timestamp})\n"
            f"**Symbol:** {stock_data.symbol} | **Name:** {stock_data.name}\n"
            f"**Current Price:** ₹{ltp}\n"
            f"**Day Change:** ₹{day_change} ({day_change_perc:+.2f}%)\n"
            f"**Today's Range:** ₹{low} - ₹{high}\n"
            f"**Open:** ₹{open_price} | **Prev Close:** ₹{close}\n"
            f"**Volume:** {volume:,}\n"
            f"**52-Week Range:** ₹{year_low} - ₹{year_high}\n"
            f"_Source: Groww (cached 30s)_"
        )
        
    except Exception as e:
        return f"❌ Error fetching stock price for '{symbol}': {str(e)}"


def search_stock(query: str) -> str:
    """
    Search for Indian stocks by company name or symbol.
    
    Args:
        query (str): Company name or stock symbol to search for
                    (e.g., 'Reliance', 'Tata', 'Banking')
    
    Returns:
        str: List of matching stock symbols and names.
    """
    try:
        results = _run_async(_groww_client.search_stocks(query, max_results=10))
        
        if not results:
            return f"❌ No Indian stocks found matching '{query}'."
        
        lines = [f"🔍 **Stocks matching '{query}':**\n"]
        for i, stock in enumerate(results, 1):
            symbol = stock.get("symbol", "")
            name = stock.get("name", "")
            exchange = stock.get("exchange", "NSE")
            lines.append(f"{i}. **{name}** — `{symbol}` ({exchange})")
        
        lines.append("\n_Use the symbol (e.g., 'RELIANCE') with get_stock_price._")
        return "\n".join(lines)
        
    except Exception as e:
        return f"❌ Error searching stocks: {str(e)}"


# Create the Finance Agent
finance_agent = Agent(
    name="Finance Agent",
    role="Indian Stock Market Data Specialist",
    model=get_model(),
    tools=[get_stock_price, search_stock],
    instructions=[
        "You are a specialist in Indian stock market data (NSE/BSE).",
        "ALWAYS use 'get_stock_price' to fetch live prices — it returns timestamped data.",
        "Use 'search_stock' if the user asks about a company name and you need the symbol.",
        "Common symbols: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, SBIN, ITC, BHARTIARTL.",
        "All prices are in Indian Rupees (₹). Data is cached for 30 seconds.",
        "Include the 'as of' timestamp in your final response to show data freshness.",
    ],
    show_tool_calls=True,
    markdown=True,
)
