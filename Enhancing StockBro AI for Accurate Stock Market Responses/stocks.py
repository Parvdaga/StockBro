"""
Stock data endpoints — Indian stocks via Groww API
"""
from fastapi import APIRouter, Query, HTTPException
from app.services.stock_service import StockService
from app.schemas.stock import StockData
from typing import List, Optional

router = APIRouter(prefix="/stocks", tags=["Stocks"])
stock_service = StockService()


@router.get("/search")
async def search_stocks(
    q: str = Query(..., min_length=1, description="Stock name or symbol to search"),
    max_results: int = Query(10, ge=1, le=50, description="Max results to return"),
):
    """Search for Indian stocks by name or symbol"""
    results = await stock_service.search_stocks(q, max_results)
    if not results:
        return {"results": [], "message": f"No stocks found matching '{q}'"}
    return {"results": results}


@router.get("/trending", response_model=List[StockData])
async def get_trending_stocks():
    """Get trending/popular Indian stocks with live prices"""
    stocks = await stock_service.get_trending_stocks()
    return stocks


@router.get("/{symbol}", response_model=StockData)
async def get_stock(symbol: str):
    """
    Get real-time stock data for an Indian stock.
    
    Accepts: RELIANCE, NSE-RELIANCE, TCS, BSE-TCS, etc.
    Defaults to NSE exchange if no prefix provided.
    """
    data = await stock_service.get_stock_price(symbol)

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Stock '{symbol}' not found. Make sure it's a valid NSE/BSE listed Indian stock symbol (e.g., RELIANCE, TCS, INFY, HDFCBANK)."
        )

    return data
