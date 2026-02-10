"""
Authentication and user schemas
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


# User profile response (from Supabase)
class UserResponse(BaseModel):
    """User profile information"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime


# For updating user profile
class UserUpdateRequest(BaseModel):
    """Request to update user profile"""
    full_name: Optional[str] = None
