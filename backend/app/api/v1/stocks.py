"""
Stock data endpoints
"""
from fastapi import APIRouter, Query, HTTPException
from app.services.stock_service import StockService
from app.schemas.stock import StockData
from typing import List

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get("/{symbol}", response_model=StockData)
async def get_stock(
    symbol: str
):
    """Get real-time stock data (Indian stocks: NSE-*, BSE-*)"""
    stock_service = StockService()
    data = await stock_service.get_stock_price(symbol)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Stock {symbol} not found or unsupported exchange"
        )
    
    return data
