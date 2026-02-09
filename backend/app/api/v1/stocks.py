"""
Stock data endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.services.stock_service import StockService
from app.schemas.stock import StockData, StockHistoryResponse
from typing import List

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get("/{symbol}", response_model=StockData)
async def get_stock(
    symbol: str,
    db: AsyncSession = Depends(get_db)
):
    """Get real-time stock data"""
    stock_service = StockService(db)
    data = await stock_service.get_stock_price(symbol)
    
    if not data:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Stock {symbol} not found")
    
    return data


@router.get("/{symbol}/history", response_model=StockHistoryResponse)
async def get_stock_history(
    symbol: str,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get historical price data"""
    stock_service = StockService(db)
    return await stock_service.get_price_history(symbol, days)


@router.get("/search/", response_model=List[dict])
async def search_stocks(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Search stocks by name or symbol"""
    stock_service = StockService(db)
    stocks = await stock_service.search_stocks(q, limit)
    
    return [
        {
            "symbol": s.symbol,
            "name": s.name,
            "exchange": s.exchange
        }
        for s in stocks
    ]
