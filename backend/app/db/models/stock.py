"""
Stock and price history models
"""
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from app.db.models.base import BaseModel


class Stock(BaseModel):
    """Stock master data"""
    __tablename__ = "stocks"
    
    symbol = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "NSE-RELIANCE"
    name = Column(String(255), nullable=False)
    exchange = Column(String(50))  # NSE, BSE, NASDAQ, etc.
    sector = Column(String(100))
    industry = Column(String(100))
    
    # Fundamental data (updated periodically)
    market_cap = Column(Float)
    pe_ratio = Column(Float)
    eps = Column(Float)
    dividend_yield = Column(Float)
    beta = Column(Float)
    week_52_high = Column(Float)
    week_52_low = Column(Float)
    
    # Additional data
    extra_data = Column(JSON)  # For flexible additional fields


class PriceHistory(BaseModel):
    """Historical price data for stocks"""
    __tablename__ = "price_history"
    
    symbol = Column(String(50), ForeignKey("stocks.symbol"), nullable=False, index=True)
    
    # OHLCV data
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer)
    
    # Additional metrics
    adjusted_close = Column(Float)
    
    __table_args__ = (
        Index('ix_price_history_symbol_created', 'symbol', 'created_at'),
    )
