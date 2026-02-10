"""
Supabase client initialization and utilities
"""
import os
from supabase import create_client, Client
from typing import Optional
from functools import lru_cache

@lru_cache()
def get_supabase_client() -> Client:
    """
    Get Supabase client instance (singleton pattern)
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
    
    return create_client(url, key)


def get_user_from_token(token: str) -> Optional[dict]:
    """
    Verify JWT token and get user information
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User dict if valid, None otherwise
    """
    try:
        client = get_supabase_client()
        user = client.auth.get_user(token)
        return user.user if user else None
    except Exception as e:
        print(f"Token verification error: {e}")
        return None
