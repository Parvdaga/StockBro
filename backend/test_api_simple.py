"""
Simple API test script using Python requests
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ Health check passed")

def test_signup():
    """Test signup"""
    print("\n2. Testing signup...")
    data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"Response: {response.json()}")
        print("✅ Signup successful")
        return True
    elif response.status_code == 409:
        print("⚠️  User already exists (this is OK)")
        return False
    else:
        print(f"❌ Signup failed: {response.text}")
        return False

def test_login():
    """Test login"""
    print("\n3. Testing login...")
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Login successful")
        print(f"Access Token: {result['access_token'][:30]}...")
        return result['access_token']
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_create_watchlist(token):
    """Test creating watchlist"""
    print("\n4. Testing create watchlist (authenticated)...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "My Tech Stocks",
        "description": "Technology companies to watch"
    }
    response = requests.post(f"{BASE_URL}/api/v1/watchlists/", 
                            headers=headers, json=data)
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"✅ Watchlist created")
        print(f"Watchlist ID: {result['id']}")
        return result['id']
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_get_watchlists(token):
    """Test getting all watchlists"""
    print("\n5. Testing get watchlists...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/watchlists/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {len(result)} watchlist(s)")
        for w in result:
            print(f"  - {w['name']}: {w['description']}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_chat(token):
    """Test AI chat"""
    print("\n6. Testing AI chat...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": "What is the stock market?"}
    response = requests.post(f"{BASE_URL}/api/v1/chat/", 
                            headers=headers, json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Chat successful")
        print(f"AI Response: {result['answer'][:100]}...")
        return True
    else:
        print(f"⚠️  Chat failed (check GROQ_API_KEY): {response.text[:100]}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("StockBro API Test Suite")
    print("="*50)
    
    try:
        # Run tests
        test_health()
        test_signup()
        token = test_login()
        
        if token:
            test_create_watchlist(token)
            test_get_watchlists(token)
            test_chat(token)
        
        print("\n" + "="*50)
        print("✅ All tests completed!")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
