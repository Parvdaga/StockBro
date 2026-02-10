"""
Stock service for fetching stock data from external APIs
"""
from typing import Optional, List
from app.schemas.stock import StockData
from app.integrations.groww import GrowwClient
from app.config import settings


class StockService:
    """Service for stock data operations - API only, no database"""
    
    def __init__(self, db=None):
        # db parameter kept for compatibility but not used
        self.groww_client = GrowwClient()
    
    async def get_stock_price(self, symbol: str) -> Optional[StockData]:
        """
        Get real-time stock price from Groww API
        Supports Indian stocks (NSE-*, BSE-*)
        """
        # Only support Indian stocks via Groww
        if symbol.startswith(("NSE-", "BSE-")):
            data = await self.groww_client.get_stock_data(symbol)
            return data
        
        # For non-Indian stocks, return None
        # Could add other data providers here in the future
        return None
