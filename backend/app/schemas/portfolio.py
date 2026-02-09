"""
Portfolio schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    """Transaction types"""
    BUY = "buy"
    SELL = "sell"


class TransactionCreate(BaseModel):
    """Create transaction"""
    symbol: str
    transaction_type: TransactionType
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    fees: Optional[float] = Field(0.0, ge=0)
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    """Transaction response"""
    id: UUID
    symbol: str
    transaction_type: TransactionType
    quantity: int
    price: float
    fees: float
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class HoldingResponse(BaseModel):
    """Current holding"""
    id: UUID
    symbol: str
    quantity: int
    average_price: float
    
    # Calculated fields
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    
    class Config:
        from_attributes = True


class PortfolioCreate(BaseModel):
    """Create portfolio"""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None


class PortfolioResponse(BaseModel):
    """Portfolio with holdings"""
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    holdings: List[HoldingResponse] = []
    
    # Aggregated metrics
    total_value: Optional[float] = None
    total_pnl: Optional[float] = None
    total_pnl_percent: Optional[float] = None
    
    class Config:
        from_attributes = True
