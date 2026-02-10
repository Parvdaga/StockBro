import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path to import config if needed, or just load .env directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_token():
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
        return

    supabase: Client = create_client(url, key)

    print("\n--- Get Supabase Access Token ---")
    email = input("Enter email: ")
    password = input("Enter password: ")

    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        print("\n✅ Login Successful!")
        print("\nHere is your ACCESS TOKEN (Bearer Token):")
        print("-" * 50)
        print(res.session.access_token)
        print("-" * 50)
        print("\nCopy the token above and use it in Swagger UI 'Authorize' button.")
        
    except Exception as e:
        print(f"\n❌ Login Failed: {e}")

if __name__ == "__main__":
    get_token()
