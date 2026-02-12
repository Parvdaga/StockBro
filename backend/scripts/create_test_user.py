import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path to import config if needed, or just load .env directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_user():
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
        return

    supabase: Client = create_client(url, key)

    print("\n--- Create New Supabase User ---")
    email = input("Enter email for new user: ")
    password = input("Enter password (min 6 chars): ")
    
    confirm = input(f"Create user {email}? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return

    try:
        # Sign up the user
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if res.user:
            print(f"\n✅ User created successfully! ID: {res.user.id}")
            if res.session:
                print("Session active (Auto-confirmed).")
            else:
                print("⚠️  Check your email for a confirmation link (if email confirmations are enabled).")
                print("   If you are creating a test user on localhost/dev, you might need to manually confirm in Supabase Dashboard")
                print("   OR disable 'Confirm email' in Supabase Authentication -> Providers -> Email.")
        else:
            print("\n❌ User creation failed (User might already exist or strict validation).")
            
    except Exception as e:
        print(f"\n❌ Error creating user: {e}")

if __name__ == "__main__":
    create_user()
