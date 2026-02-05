from pydantic import BaseModel, Field
from typing import List, Optional

class StockData(BaseModel):
    """Model for Stock Data (Chart/Table)"""
    ticker: str = Field(..., description="Stock Ticker Symbol (e.g., AAPL)")
    current_price: float = Field(..., description="Current trading price")
    change_percent: Optional[float] = Field(None, description="Percentage change")
    volume: Optional[int] = Field(None, description="Trading volume")
    # For historical charts, we might need list of points, but keeping it simple for now
    
class NewsItem(BaseModel):
    """Model for News Items"""
    title: str
    url: str
    source: Optional[str] = None
    published_at: Optional[str] = None
    sentiment: Optional[str] = Field(None, description="Positive, Negative, or Neutral")

class AgentResponse(BaseModel):
    """
    Standardized response from the Master Agent.
    Includes the natural language text and structured data for UI rendering.
    """
    answer: str = Field(..., description="The natural language response to the user query.")
    stocks: Optional[List[StockData]] = Field(None, description="List of relevant stock data found.")
    news: Optional[List[NewsItem]] = Field(None, description="List of relevant news articles found.")
