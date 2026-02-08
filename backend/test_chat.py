import requests
import json

url = "http://localhost:8000/api/v1/chat"
payload = {
    "message": "What is the price of RELIANCE?",
    "user_id": "test_user"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
