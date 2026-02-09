"""
Watchlist schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class WatchlistItemCreate(BaseModel):
    """Schema for adding stock to watchlist"""
    symbol: str = Field(..., description="Stock symbol (e.g., NSE-RELIANCE)")
    notes: Optional[str] = None


class WatchlistItemResponse(BaseModel):
    """Watchlist item response"""
    id: UUID
    symbol: str
    notes: Optional[str]
    added_at: datetime
    
    # Include real-time price data
    current_price: Optional[float] = None
    change_percent: Optional[float] = None
    
    class Config:
        from_attributes = True


class WatchlistCreate(BaseModel):
    """Schema for creating watchlist"""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None


class WatchlistUpdate(BaseModel):
    """Schema for updating watchlist"""
    name: Optional[str] = None
    description: Optional[str] = None


class WatchlistResponse(BaseModel):
    """Watchlist response with items"""
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    items: List[WatchlistItemResponse] = []
    
    class Config:
        from_attributes = True
