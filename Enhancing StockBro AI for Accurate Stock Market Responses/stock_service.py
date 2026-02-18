"""
Stock service for fetching Indian stock data from Groww API
"""
from typing import Optional, List, Dict
from app.schemas.stock import StockData
from app.integrations.groww import GrowwClient


class StockService:
    """Service for Indian stock data via Groww"""

    def __init__(self):
        self.groww_client = GrowwClient()

    async def get_stock_price(self, symbol: str) -> Optional[StockData]:
        """
        Get real-time stock price from Groww.
        Accepts: 'RELIANCE', 'NSE-RELIANCE', 'TCS', etc.
        Auto-defaults to NSE exchange if no prefix given.
        """
        return await self.groww_client.get_stock_data(symbol)

    async def search_stocks(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for Indian stocks by name or symbol.
        """
        return await self.groww_client.search_stocks(query, max_results)

    async def get_trending_stocks(self) -> List[StockData]:
        """
        Get trending/popular Indian stocks with live prices
        """
        return await self.groww_client.get_trending_stocks()
