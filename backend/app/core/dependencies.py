"""
Dependency injection for Supabase client and authentication  
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase_client import get_supabase_client, get_user_from_token
from supabase import Client


# Supabase client dependency
def get_supabase() -> Client:
    """Get Supabase client instance"""
    return get_supabase_client()


# Security dependency
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
) -> dict:
    """
    Get current authenticated user from Supabase JWT token
    
    Returns:
        User dict with id, email, etc.
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    user = get_user_from_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# Optional auth - doesn't fail if no token
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    supabase: Client = Depends(get_supabase)
) -> Optional[dict]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    user = get_user_from_token(credentials.credentials)
    return user
