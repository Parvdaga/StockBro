"""
Quick test script to verify Groq API integration and Groww API
"""
from app.agents.master_agent import master_agent
from app.config import settings

print("=" * 60)
print("Testing StockBro with Groq API")
print("=" * 60)

# Check configuration
print(f"\n[OK] Groq API Key: {'SET' if settings.GROQ_API_KEY else 'NOT SET'}")
print(f"[OK] Groww API Key: {'SET' if settings.GROWW_API_KEY else 'NOT SET'}")
print(f"[OK] Google API Key: {'SET' if settings.GOOGLE_API_KEY else 'NOT SET'}")

# Test 1: Simple non-tool query
print("\n" + "=" * 60)
print("TEST 1: Simple greeting (no tools)")
print("=" * 60)
try:
    response = master_agent.run("Hello, who are you?", stream=False)
    print(f"[SUCCESS] Response: {response.content[:200]}...")
except Exception as e:
    print(f"[ERROR] Error: {e}")

# Test 2: Stock price query (requires Groww API)
print("\n" + "=" * 60)
print("TEST 2: Stock price query (with Groww API)")
print("=" * 60)
try:
    response = master_agent.run("What is the price of RELIANCE?", stream=False)
    print(f"[SUCCESS] Response: {response.content}")
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
