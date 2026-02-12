
import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd()))

from app.config import settings
from app.integrations.groww import GrowwClient

async def test_groww():
    print(f"Testing Groww Client...")
    print(f"API Key present: {bool(settings.GROWW_API_KEY)}")
    
    try:
        import growwapi
        print("growwapi library is installed.")
    except ImportError:
        print("ERROR: growwapi library is NOT installed.")
        return

    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    symbol = "NSE-RELIANCE"
    def fetch_data():
        from growwapi import GrowwAPI
        groww = GrowwAPI(settings.GROWW_API_KEY)
        response = groww.get_instrument_by_groww_symbol(groww_symbol=symbol)
        return response
    
    print(f"Fetching raw data for {symbol} directly...")
    raw_response = await loop.run_in_executor(None, fetch_data)
    print("RAW RESPONSE:", raw_response)
    
    data = await client.get_stock_data(symbol)
    
    if data:
        print("SUCCESS! Data received:")
        print(data)
    else:
        print("FAILURE: No data received.")

if __name__ == "__main__":
    asyncio.run(test_groww())
