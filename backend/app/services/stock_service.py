"""
Stock service for fetching and managing stock data
"""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.stock import Stock, PriceHistory
from app.schemas.stock import StockData, PricePoint, StockHistoryResponse
from app.integrations.groww import GrowwClient
from app.integrations.finnhub import FinnhubClient
from app.config import settings
import json


class StockService:
    """Service for stock data operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.groww_client = GrowwClient()
        self.finnhub_client = FinnhubClient()
    
    async def get_stock_price(self, symbol: str) -> Optional[StockData]:
        """
        Get real-time stock price
        Priority: GrowwAPI (Indian) -> Finnhub (Global)
        """
        # Try Indian stocks with Groww first
        if symbol.startswith(("NSE-", "BSE-")):
            data = await self.groww_client.get_stock_data(symbol)
            if data:
                return data
        
        # Fallback to Finnhub for global stocks
        data = await self.finnhub_client.get_stock_data(symbol)
        return data
    
    async def get_stock_details(self, symbol: str) -> Optional[Stock]:
        """Get stock details from database or fetch and store"""
        # Check database first
        result = await self.db.execute(
            select(Stock).where(Stock.symbol == symbol)
        )
        stock = result.scalar_one_or_none()
        
        if stock:
            return stock
        
        # Fetch from API and store
        data = await self.get_stock_price(symbol)
        if not data:
            return None
        
        # Create new stock entry
        stock = Stock(
            symbol=data.symbol,
            name=data.name,
            exchange=symbol.split("-")[0] if "-" in symbol else "UNKNOWN",
            market_cap=data.market_cap,
            pe_ratio=data.pe_ratio,
            eps=data.eps,
            dividend_yield=data.dividend_yield,
            week_52_high=data.week_52_high,
            week_52_low=data.week_52_low
        )
        
        self.db.add(stock)
        await self.db.commit()
        await self.db.refresh(stock)
        
        return stock
    
    async def get_price_history(
        self, 
        symbol: str, 
        days: int = 30
    ) -> StockHistoryResponse:
        """Get historical price data"""
        # Check database for recent data
        since_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(PriceHistory)
            .where(PriceHistory.symbol == symbol)
            .where(PriceHistory.created_at >= since_date)
            .order_by(PriceHistory.created_at)
        )
        history = result.scalars().all()
        
        # If we have enough data, return it
        if len(history) >= days * 0.8:  # 80% threshold
            price_points = [
                PricePoint(
                    timestamp=h.created_at,
                    open=h.open_price,
                    high=h.high_price,
                    low=h.low_price,
                    close=h.close_price,
                    volume=h.volume
                )
                for h in history
            ]
            return StockHistoryResponse(symbol=symbol, data=price_points)
        
        # Fetch from API
        history_data = await self.finnhub_client.get_price_history(symbol, days)
        
        # Store in database for future use
        for point in history_data:
            price_record = PriceHistory(
                symbol=symbol,
                open_price=point.open,
                high_price=point.high,
                low_price=point.low,
                close_price=point.close,
                volume=point.volume,
                created_at=point.timestamp
            )
            self.db.add(price_record)
        
        await self.db.commit()
        
        return StockHistoryResponse(symbol=symbol, data=history_data)
    
    async def search_stocks(self, query: str, limit: int = 10) -> List[Stock]:
        """Search for stocks by name or symbol"""
        result = await self.db.execute(
            select(Stock)
            .where(
                (Stock.symbol.ilike(f"%{query}%")) | 
                (Stock.name.ilike(f"%{query}%"))
            )
            .limit(limit)
        )
        return result.scalars().all()
