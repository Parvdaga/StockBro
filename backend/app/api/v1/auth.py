"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends
from supabase import Client
from app.core.dependencies import get_supabase, get_current_user
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Get current authenticated user profile
    
    Note: Authentication (signup/login) is handled client-side via Supabase Auth.
    This endpoint retrieves the user's profile from the database.
    """
    # Get user profile from database
    response = supabase.table("profiles").select("*").eq("id", current_user.id).single().execute()
    
    if not response.data:
        # If no profile exists, create one
        profile_data = {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.user_metadata.get("full_name") if current_user.user_metadata else None,
            "is_active": True
        }
        response = supabase.table("profiles").insert(profile_data).execute()
        return response.data[0]
    
    return response.data
