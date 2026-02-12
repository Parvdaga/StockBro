import os
import sys
import requests
import json
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

BASE_URL = "http://localhost:8000/api/v1"
ROOT_URL = "http://localhost:8000"

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_pass(msg):
    print(f"{Colors.OKGREEN}[PASS]{Colors.ENDC} {msg}")

def print_fail(msg):
    print(f"{Colors.FAIL}[FAIL]{Colors.ENDC} {msg}")

def print_info(msg):
    print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} {msg}")

def print_header(msg):
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {msg} ==={Colors.ENDC}")

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        # Test User Credentials (load from env or use defaults/prompt)
        # For this script we will try to sign up a test user or sign in if exists
        self.email = f"test_user_{int(time.time())}@example.com"
        self.password = "TestPass123!"

    def log_result(self, test_name: str, success: bool, message: str = ""):
        if success:
            self.results["passed"] += 1
            print_pass(f"{test_name}: {message}")
        else:
            self.results["failed"] += 1
            print_fail(f"{test_name}: {message}")
        
        self.results["details"].append({
            "test": test_name,
            "status": "PASS" if success else "FAIL",
            "message": message,
            "timestamp": time.strftime("%H:%M:%S")
        })

    def authenticate(self):
        print_header("Authentication Setup")
        try:
            from supabase import create_client, Client
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            
            if not url or not key:
                print_fail("Supabase credentials missing in .env")
                return False

            # Use Service Role Key to allow admin actions (like creating confirmed users)
            supabase: Client = create_client(url, key)
            
            print_info(f"Attempting to create/get test user: {self.email}")
            
            try:
                # Try to create user with admin privileges (auto-confirm email)
                # Note: supabase-py admin usage might vary by version. 
                # Newer versions use supabase.auth.admin.create_user
                attributes = {
                    "email": self.email,
                    "password": self.password,
                    "email_confirm": True,
                    "user_metadata": {"full_name": "Test User"}
                }
                # Check if we can use admin
                if hasattr(supabase.auth, 'admin'):
                    try:
                        user = supabase.auth.admin.create_user(attributes)
                        print_pass("Created auto-confirmed user via Admin API.")
                    except Exception as e:
                        # User might already exist
                        if "already registered" in str(e) or "already exists" in str(e):
                             print_info("User already exists.")
                        else:
                             print_info(f"Admin create failed: {e}")
                else:
                    # Fallback to signup
                     supabase.auth.sign_up({
                        "email": self.email,
                        "password": self.password,
                    })

                # Now Sign In to get the session/token
                res = supabase.auth.sign_in_with_password({
                    "email": self.email,
                    "password": self.password
                })
                
                if res.session:
                     self.token = res.session.access_token
                     self.user_id = res.user.id
                     print_pass("Logged in successfully.")
                     return True
                else:
                     print_fail("Login failed: No session returned.")
                     
            except Exception as e:
                print_fail(f"Authentication failed: {e}")

            # Fallback: Try 'test@example.com' just in case
            print_info("Attempting fallback login with test@example.com...")
            try:
                res = supabase.auth.sign_in_with_password({
                    "email": "test@example.com",
                    "password": "password"
                })
                if res.session:
                    self.token = res.session.access_token
                    self.user_id = res.user.id
                    self.email = "test@example.com"
                    print_pass(f"Logged in as test@example.com")
                    return True
            except:
                pass

            return False
                
        except ImportError:
            print_fail("supabase python package not installed. Authenticated tests will fail.")
            return False
        except Exception as e:
            print_fail(f"Authentication setup error: {e}")
            return False

    def get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def test_public_endpoints(self):
        print_header("Testing Public Endpoints")
        
        # 1. Root
        try:
            r = self.session.get(ROOT_URL + "/")
            self.log_result("GET /", r.status_code == 200, f"Status: {r.status_code}")
        except Exception as e:
            self.log_result("GET /", False, str(e))

        # 2. Health
        try:
            r = self.session.get(ROOT_URL + "/health")
            self.log_result("GET /health", r.status_code == 200, f"Status: {r.status_code}")
        except Exception as e:
            self.log_result("GET /health", False, str(e))

    def test_stocks_endpoints(self):
        print_header("Testing Stock Data Endpoints")
        
        # 1. Search
        try:
            r = self.session.get(f"{BASE_URL}/stocks/search?q=RELIANCE")
            success = r.status_code == 200 and len(r.json().get('results', [])) > 0
            self.log_result("GET /stocks/search", success, f"Status: {r.status_code}, Results: {len(r.json().get('results', []))}")
        except Exception as e:
            self.log_result("GET /stocks/search", False, str(e))

        # 2. Trending
        try:
            r = self.session.get(f"{BASE_URL}/stocks/trending")
            success = r.status_code == 200 and isinstance(r.json(), list)
            self.log_result("GET /stocks/trending", success, f"Status: {r.status_code}, items: {len(r.json()) if success else 0}")
        except Exception as e:
            self.log_result("GET /stocks/trending", False, str(e))

        # 3. Get Stock Details
        try:
            r = self.session.get(f"{BASE_URL}/stocks/RELIANCE")
            success = r.status_code == 200 and r.json().get('symbol') == 'RELIANCE'
            self.log_result("GET /stocks/RELIANCE", success, f"Status: {r.status_code}, Price: {r.json().get('current_price')}")
        except Exception as e:
            self.log_result("GET /stocks/RELIANCE", False, str(e))

    def test_authenticated_endpoints(self):
        if not self.token:
            print_header("Skipping Authenticated Endpoints (No Token)")
            return

        print_header("Testing Authenticated Endpoints")
        headers = self.get_headers()

        # 1. Auth Me
        try:
            r = self.session.get(f"{BASE_URL}/auth/me", headers=headers)
            self.log_result("GET /auth/me", r.status_code == 200, f"User: {r.json().get('email')}")
        except Exception as e:
            self.log_result("GET /auth/me", False, str(e))

        # 2. Watchlists
        watchlist_id = None
        # Create
        try:
            payload = {"name": f"Test List {int(time.time())}", "description": "Automated test list"}
            r = self.session.post(f"{BASE_URL}/watchlists/", json=payload, headers=headers)
            success = r.status_code == 201
            if success:
                watchlist_id = r.json().get("id")
            self.log_result("POST /watchlists/", success, f"ID: {watchlist_id}")
        except Exception as e:
            self.log_result("POST /watchlists/", False, str(e))

        if watchlist_id:
            # Add Item
            item_id = None
            try:
                payload = {"symbol": "TATASTEEL", "notes": "Buy on dip"}
                r = self.session.post(f"{BASE_URL}/watchlists/{watchlist_id}/items", json=payload, headers=headers)
                success = r.status_code == 201
                if success:
                    item_id = r.json().get("id")
                self.log_result("POST /watchlists/items", success, f"Item ID: {item_id}")
            except Exception as e:
                self.log_result("POST /watchlists/items", False, str(e))

            # Delete Item
            if item_id:
                try:
                    r = self.session.delete(f"{BASE_URL}/watchlists/{watchlist_id}/items/{item_id}", headers=headers)
                    self.log_result("DELETE /watchlists/items", r.status_code == 204, "")
                except Exception as e:
                    self.log_result("DELETE /watchlists/items", False, str(e))
            
            # Delete Watchlist
            try:
                r = self.session.delete(f"{BASE_URL}/watchlists/{watchlist_id}", headers=headers)
                self.log_result("DELETE /watchlists/{id}", r.status_code == 204, "")
            except Exception as e:
                self.log_result("DELETE /watchlists/{id}", False, str(e))

        # 3. Chat
        conversation_id = None
        try:
            payload = {"message": "What is the price of RELIANCE?", "conversation_id": None}
            print_info("Sending chat message (this might take a few seconds)...")
            r = self.session.post(f"{BASE_URL}/chat/", json=payload, headers=headers)
            success = r.status_code == 200
            if success:
                data = r.json()
                conversation_id = data.get("conversation_id")
                answer = data.get("answer", "")
                print_info(f"AI Answer: {answer[:100]}...")
            self.log_result("POST /chat/", success, f"Conv ID: {conversation_id}")
        except Exception as e:
            self.log_result("POST /chat/", False, str(e))

        if conversation_id:
            # Get History
            try:
                r = self.session.get(f"{BASE_URL}/chat/conversations/{conversation_id}", headers=headers)
                self.log_result("GET /chat/conversations/{id}", r.status_code == 200, "")
            except Exception as e:
                self.log_result("GET /chat/conversations/{id}", False, str(e))

            # Delete Conversation
            try:
                r = self.session.delete(f"{BASE_URL}/chat/conversations/{conversation_id}", headers=headers)
                self.log_result("DELETE /chat/conversations/{id}", r.status_code == 204, "")
            except Exception as e:
                self.log_result("DELETE /chat/conversations/{id}", False, str(e))

    def run(self):
        print_header("STARTING BACKEND VERIFICATION")
        self.test_public_endpoints()
        self.test_stocks_endpoints()
        
        # Auth attempts
        if self.authenticate():
            self.test_authenticated_endpoints()
        else:
            print_fail("Skipping authenticated tests due to login failure.")
            self.results["details"].append({"test": "Authentication", "status": "FAIL", "message": "Could not sign in"})

        print_header("VERIFICATION COMPLETE")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        
        # Save report
        with open("backend_test_report.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print_info("Report saved to backend_test_report.json")

if __name__ == "__main__":
    tester = BackendTester()
    tester.run()
