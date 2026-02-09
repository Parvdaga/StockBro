"""
Complete Integration Demo - Groq LLM + Groww API + News
Tests all three components working together
"""
import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1/chat"

def test_query(message, description):
    """Test a query and display results"""
    print("\n" + "=" * 70)
    print(f"TEST: {description}")
    print("=" * 70)
    print(f"Query: {message}")
    print("-" * 70)
    
    try:
        response = requests.post(
            API_URL,
            json={"message": message, "user_id": "guest"},
            timeout=60  # Longer timeout for tool use
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ SUCCESS (Status: {response.status_code})")
            print(f"\nAnswer:\n{data['answer']}")
            
            if data.get('stocks'):
                print(f"\nStocks Data: {data['stocks']}")
            if data.get('news'):
                print(f"\nNews Data: {data['news']}")
        else:
            print(f"\n✗ ERROR (Status: {response.status_code})")
            print(f"Error: {response.json().get('detail', 'Unknown')[:200]}")
    
    except requests.exceptions.Timeout:
        print("\n✗ TIMEOUT - Query took too long (>60s)")
    except Exception as e:
        print(f"\n✗ ERROR: {type(e).__name__}: {str(e)[:100]}")

print("="  * 70)
print("STOCKBRO COMPLETE INTEGRATION DEMO")
print("Testing: Groq LLM + Groww Stock API + DuckDuckGo News")
print("=" * 70)

# Test 1: Pure LLM (no tools)
test_query(
    "Hello! What can you help me with?",
    "LLM Intelligence Test (No Tools)"
)

# Test 2: News search
test_query(
    "What's the latest news about Tesla?",
    "News Integration Test (DuckDuckGo)"
)

# Test 3: Stock price (Groww API)  
test_query(
    "What is the current price of RELIANCE?",
    "Stock Data Test (Groww API)"
)

# Test 4: Combined query
test_query(
    "Tell me about TCS stock and any recent news about it",
    "Combined Test (Stock + News)"
)

print("\n" + "=" * 70)
print("INTEGRATION DEMO COMPLETE!")
print("=" * 70)
