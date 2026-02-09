"""
Authentication service for user management
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user import User
from app.schemas.auth import UserSignupRequest, UserLoginRequest, TokenResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.exceptions import UnauthorizedException, ConflictException
from datetime import timedelta


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def signup(self, request: UserSignupRequest) -> UserResponse:
        """Register a new user"""
        # Check if user already exists
        result = await self.db.execute(
            select(User).where(User.email == request.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ConflictException("User with this email already exists")
        
        # Create new user
        hashed_pwd = hash_password(request.password)
        user = User(
            email=request.email,
            hashed_password=hashed_pwd,
            full_name=request.full_name,
            is_active=True
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return UserResponse.model_validate(user)
    
    async def login(self, request: UserLoginRequest) -> TokenResponse:
        """Authenticate user and return tokens"""
        # Find user
        result = await self.db.execute(
            select(User).where(User.email == request.email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(request.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        
        if not user.is_active:
            raise UnauthorizedException("User account is disabled")
        
        # Create tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def refresh_access_token(self, user_id: str) -> str:
        """Generate new access token"""
        user = await self.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("Invalid or inactive user")
        
        return create_access_token({"sub": str(user.id)})
