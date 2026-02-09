"""
Stock data schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StockData(BaseModel):
    """Real-time stock data"""
    symbol: str = Field(..., description="Stock symbol (e.g., NSE-RELIANCE)")
    name: str
    current_price: float
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None


class PricePoint(BaseModel):
    """Single price point for charts"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[int] = None


class StockHistoryResponse(BaseModel):
    """Historical price data"""
    symbol: str
    data: List[PricePoint]
    

class StockDetailResponse(BaseModel):
    """Detailed stock information"""
    symbol: str
    name: str
    exchange: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    current_price: float
    change_percent: Optional[float] = None
    fundamentals: StockData
