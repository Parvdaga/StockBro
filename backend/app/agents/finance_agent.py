from phi.agent import Agent
from app.config import settings
from app.agents.shared_model import get_model
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
        
        # Initialize with auth token (GROWW_API_KEY from .env)
        groww = GrowwAPI(settings.GROWW_API_KEY)
        return groww
    except Exception as e:
        print(f"Groww Connection Error: {e}")
        return None

def get_stock_price(symbol: str):
    """
    Retrieves the current market price for a given stock symbol.
    Args:
        symbol (str): The stock symbol (e.g., 'RELIANCE', 'TCS')
    """
    groww = get_groww_session()
    if not groww:
        return "Error: Could not connect to Groww API."

    try:
        # Format symbol with exchange prefix (default to NSE)
        if not symbol.startswith(('NSE-', 'BSE-')):
            groww_symbol = f"NSE-{symbol.upper()}"
        else:
            groww_symbol = symbol.upper()
        
        # Get instrument data using the correct method
        response = groww.get_instrument_by_groww_symbol(groww_symbol=groww_symbol)
        
        if not response:
            return f"Error: Could not find data for symbol '{symbol}'."
        
        # DEBUG: Print full response to see structure
        print(f"DEBUG - Full Groww response for {symbol}:")
        print(f"Type: {type(response)}")
        print(f"Keys: {response.keys() if isinstance(response, dict) else 'N/A'}")
        print(f"Data: {response}")
        
        # Extract price from response
        # Try multiple possible field names
        price = (response.get('ltp') or response.get('close_price') or 
                response.get('current_price') or response.get('price') or
                response.get('lastPrice') or response.get('last_price'))
        
        company_name = (response.get('company_name') or response.get('name') or 
                       response.get('companyName') or response.get('symbol') or symbol)
        
        if price:
            return f"The current price of {company_name} is ₹{price}"
        else:
            # Return the full response so we can see what fields are available
            return f"Price field not found for {symbol}. Available fields: {list(response.keys()) if isinstance(response, dict) else response}"
        
    except Exception as e:
        return f"Error fetching stock price: {str(e)}"

# Create the Agent with explicit model to avoid OpenAI default
finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    model=get_model(),  # Use shared Groq/Gemini model
    tools=[get_stock_price],
    instructions=[
        "Use 'get_stock_price' to find the latest price of a stock.",
        "If the user asks for Nifty or Sensex, search for 'NIFTY 50' or 'SENSEX'."
        ],
    show_tool_calls=True,
    markdown=True,
)
