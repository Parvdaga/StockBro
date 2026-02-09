"""
Watchlist models for tracking favorite stocks
"""
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.models.base import BaseModel


class Watchlist(BaseModel):
    """User's watchlist container"""
    __tablename__ = "watchlists"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    
    # Relationships
    user = relationship("User", back_populates="watchlists")
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")


class WatchlistItem(BaseModel):
    """Individual stock in a watchlist"""
    __tablename__ = "watchlist_items"
    
    watchlist_id = Column(UUID(as_uuid=True), ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(50), nullable=False)  # e.g., "NSE-RELIANCE"
    notes = Column(String(500))
    
    # Relationships
    watchlist = relationship("Watchlist", back_populates="items")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('watchlist_id', 'symbol', name='unique_watchlist_symbol'),
    )
