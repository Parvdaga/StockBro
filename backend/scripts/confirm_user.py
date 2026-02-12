import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path to import config if needed, or just load .env directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def confirm_user():
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    # MUST use Service Role Key to bypass email confirmation
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env file")
        return

    supabase: Client = create_client(url, key)

    print("\n--- Auto-Confirm User Email (Admin) ---")
    email = input("Enter email to confirm: ")
    
    try:
        # Get user ID by email (requires admin privileges)
        # Note: listing users is an admin operation
        users = supabase.auth.admin.list_users()
        user_id = None
        
        for user in users:
            if user.email == email:
                user_id = user.id
                break
        
        if not user_id:
            print(f"❌ User with email {email} not found.")
            return

        # Confirm the user
        res = supabase.auth.admin.update_user_by_id(
            user_id,
            {"email_confirm": True}
        )
        
        print(f"\n✅ User {email} confirmed successfully!")
        print("You can now login with scripts/get_access_token.py")
            
    except Exception as e:
        print(f"\n❌ Error confirming user: {e}")
        # Fallback: try to just delete the user so they can try again if they want
        print("Tip: If this fails, you might need to check the Supabase Dashboard manually.")

if __name__ == "__main__":
    confirm_user()
