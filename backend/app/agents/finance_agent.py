from phi.agent import Agent
from app.config import settings
import traceback

# specific import might usually be from growwapi import GrowwAPI or similar. 
# Since we don't have the docs, we will implement a robust connection handler.
# If the library follows standard practices:
try:
    from growwapi import GrowwAPI
except ImportError:
    # Fallback or placeholder if library structure differs
    print("GrowwAPI library not found or structure differs.")
    GrowwAPI = None

def get_groww_session():
    """Establishes a session with Groww API."""
    try:
        if not GrowwAPI:
            return None
        
        # Initialize with V2 API flow (assuming based on env vars available)
        groww = GrowwAPI(
            api_key=settings.GROWW_API_KEY,
            api_secret=settings.GROWW_API_SECRET
        )
        return groww
    except Exception as e:
        print(f"Groww Connection Error: {e}")
        return None

def get_stock_price(symbol: str):
    """
    Retrieves the current market price (LTP) for a given stock symbol.
    Args:
        symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS'). 
                      The agent should try to append 'NSE' if needed.
    """
    groww = get_groww_session()
    if not groww:
        return "Error: Could not connect to Groww API."

    try:
        # Fetch data (Pseudo-code matching typical SDK usage)
        # We might need to map symbol to a unique ID (ISIN or Groww Search ID)
        # Usually APIs have a search endpoint.
        
        # 1. Search for script
        search_results = groww.search(symbol)
        if not search_results or len(search_results) == 0:
             return f"Error: Could not find symbol '{symbol}'."
        
        target_script = search_results[0] # Best match
        script_id = target_script.get('id') or target_script.get('search_id')
        
        # 2. Get Live Data
        live_data = groww.get_live_data(script_id)
        
        price = live_data.get('ltp')
        return f"The current price of {target_script.get('title', symbol)} is ₹{price}"
        
    except Exception as e:
        return f"Error executing trade fetch: {str(e)}"

# Create the Agent
finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    tools=[get_stock_price],
    instructions=[
        "Use 'get_stock_price' to find the latest price of a stock.",
        "If the user asks for Nifty or Sensex, search for 'NIFTY 50' or 'SENSEX'."
        ],
    show_tool_calls=True,
    markdown=True,
)
