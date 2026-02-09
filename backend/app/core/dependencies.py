"""
Dependency injection for services and database sessions
"""
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app.core.security import verify_token
from app.core.exceptions import UnauthorizedException
from uuid import UUID


# Database dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Security dependency
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """Get current authenticated user ID from JWT token"""
    token = credentials.credentials
    user_id = verify_token(token)
    
    if not user_id:
        raise UnauthorizedException("Invalid or expired token")
    
    return UUID(user_id)


# Optional auth - doesn't fail if no token
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> Optional[UUID]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    user_id = verify_token(credentials.credentials)
    return UUID(user_id) if user_id else None
