"""
Chat conversation schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime
from app.schemas.stock import StockData


class NewsItem(BaseModel):
    """News article with sentiment"""
    title: str
    url: str
    source: Optional[str] = None
    published_at: Optional[str] = None
    sentiment: Optional[str] = Field(None, description="positive, negative, or neutral")
    sentiment_score: Optional[float] = None


class ChatRequest(BaseModel):
    """User chat message"""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = None


class ChartConfig(BaseModel):
    """Chart configuration embedded in chat response"""
    symbol: str
    chart_type: str = "candlestick"  # candlestick | line | volume
    data_url: str  # /api/v1/charts/{symbol}/history?duration=3M


class ChatResponse(BaseModel):
    """AI response with structured data"""
    conversation_id: UUID
    answer: str = Field(..., description="Natural language response")
    stocks: Optional[List[StockData]] = Field(None, description="Relevant stock data")
    news: Optional[List[NewsItem]] = Field(None, description="Relevant news articles")
    charts: Optional[List[ChartConfig]] = Field(None, description="Chart configs for frontend rendering")


class MessageResponse(BaseModel):
    """Single message in conversation"""
    id: UUID
    role: str  # "user" or "assistant"
    content: str
    stocks: Optional[Any] = None
    news: Optional[Any] = None
    charts: Optional[Any] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation with message history"""
    id: UUID
    title: Optional[str]
    created_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True
