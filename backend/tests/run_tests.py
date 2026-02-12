
import asyncio
import os
import sys
import json
import requests
from app.integrations.groww import GrowwClient
from app.integrations.gnews import GNewsClient
from app.agents.finance_agent import FinanceAgent
from app.agents.news_agent import NewsAgent
from app.agents.master_agent import MasterAgent
from app.config importsettings

# Override verify_ssl to avoid issues in test env if needed
# But requests should handle verify=True by default.

async def test_groww():
    print("\n[TEST] Testing Groww Integration...")
    client = GrowwClient()
    # 1. Search
    print("  > Searching 'RELIANCE'...")
    results = await client.search_instruments("RELIANCE")
    if results:
        print(f"    Pass: Found {len(results)} results.")
        symbol = results[0]['groww_symbol']
        print(f"    Top result: {symbol} ({results[0]['name']})")
        
        # 2. Live Price
        print(f"  > Fetching live price for {symbol}...")
        price = await client.get_stock_price(symbol)
        if price:
            print(f"    Pass: Price is {price}")
        else:
            print("    FAIL: Price is None")
    else:
        print("    FAIL: No search results found.")

async def test_gnews():
    print("\n[TEST] Testing GNews Integration...")
    client = GNewsClient()
    # 1. Search
    print("  > Searching news for 'TATA MOTORS'...")
    articles = await client.get_news("TATA MOTORS")
    if articles:
        print(f"    Pass: Found {len(articles)} articles.")
        print(f"    Title: {articles[0]['title']}")
    else:
        print("    FAIL: No articles found.")

async def test_agents():
    print("\n[TEST] Testing Agents...")
    
    # Finance Agent
    print("  > Finance Agent: search_stock('INFY')...")
    res = FinanceAgent().search_stock("INFY")
    print(f"    Result: {res[:100]}...") # Truncate
    
    # News Agent
    print("  > News Agent: get_stock_news('INFY')...")
    res = NewsAgent().get_stock_news("INFY")
    print(f"    Result: {res[:100]}...")

    # Master Agent (Chat)
    print("  > Master Agent: 'What is the price of SBI?'...")
    # Mock user_id
    agent = MasterAgent(user_id="test-user")
    # We can't easily await the implementation_plan generator here in a simple script if it returns a generator 
    # but the phi Agent.run() usually returns an iterator or string.
    # The `chat` method in `chat.py` uses `agent.run(message, stream=True)`.
    # Let's try verify basic run
    try:
        response = agent.run("What is the current price of SBI?", stream=False)
        # response might be a RunResponse object or string depending on version
        # If it's an object, it has .content
        content = getattr(response, 'content', str(response))
        print(f"    Pass: Agent Response: {content[:100]}...")
    except Exception as e:
        print(f"    FAIL: Agent run failed: {e}")

def test_api_endpoints():
    print("\n[TEST] Testing Public API Endpoints...")
    base_url = "http://localhost:8000/api/v1"
    
    # 1. Health
    try:
        r = requests.get("http://localhost:8000/health")
        print(f"  > GET /health: {r.status_code}")
    except Exception as e:
        print(f"  > GET /health FAIL: {e}")
        return

    # 2. Stock Price
    try:
        r = requests.get(f"{base_url}/stocks/RELIANCE")
        print(f"  > GET /stocks/RELIANCE: {r.status_code}")
        if r.status_code == 200:
            print(f"    Data: {r.json().get('current_price')}")
    except Exception as e:
        print(f"  > GET /stocks/RELIANCE FAIL: {e}")

    # 3. Search
    try:
        r = requests.get(f"{base_url}/stocks/search?q=WIPRO")
        print(f"  > GET /stocks/search?q=WIPRO: {r.status_code}")
        if r.status_code == 200:
            print(f"    Results: {len(r.json().get('results', []))}")
    except Exception as e:
        print(f"  > GET /stocks/search FAIL: {e}")

    # 4. Trending
    try:
        r = requests.get(f"{base_url}/stocks/trending")
        print(f"  > GET /stocks/trending: {r.status_code}")
        if r.status_code == 200:
            print(f"    Count: {len(r.json())}")
    except Exception as e:
        print(f"  > GET /stocks/trending FAIL: {e}")

if __name__ == "__main__":
    # Add project root to path
    sys.path.append(os.getcwd())
    
    print("=== STOCKBRO BACKEND VERIFICATION REPORT ===")
    
    # Run Async Tests
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_groww())
    loop.run_until_complete(test_gnews())
    
    # Run Agent Tests (might be synchronous or async depending on implementation, 
    # but phi agents are usually sync wrapping async or sync. 
    # Wait, `FinanceAgent` methods are sync strings? 
    # Let's check `finance_agent.py`: `search_stock` is sync.
    # `MasterAgent` inheriting from `Agent` is usually sync `run()`.
    test_agents()
    
    # Run API Tests
    test_api_endpoints()
    
    print("\n=== END REPORT ===")
