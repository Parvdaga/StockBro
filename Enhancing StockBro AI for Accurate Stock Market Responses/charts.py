"""
Chart data endpoints — serves historical OHLCV data for frontend charting.
Uses Groww charting API through the backend proxy.
"""
from fastapi import APIRouter, Query, HTTPException
from app.integrations.groww import GrowwClient
from app.schemas.stock import ChartDataResponse, ChartDataPoint
from typing import Optional

router = APIRouter(prefix="/charts", tags=["Charts"])

# Shared client
_groww = GrowwClient()

# Valid durations
VALID_DURATIONS = {"1d", "1w", "1M", "3M", "6M", "1y", "5y"}


@router.get("/{symbol}/history", response_model=ChartDataResponse)
async def get_chart_data(
    symbol: str,
    duration: str = Query("3M", description="Time period: 1d, 1w, 1M, 3M, 6M, 1y, 5y"),
):
    """
    Get historical OHLCV chart data for a stock.
    Data is cached for 5 minutes.

    Args:
        symbol: Stock symbol (e.g., RELIANCE, NSE-TCS)
        duration: Lookback period
    """
    if duration not in VALID_DURATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid duration '{duration}'. Must be one of: {', '.join(sorted(VALID_DURATIONS))}"
        )

    exchange, trading_symbol = GrowwClient._parse_symbol(symbol)
    data = await _groww.get_historical_data(trading_symbol, exchange, duration)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail=f"No chart data found for '{symbol}'. Ensure it's a valid NSE/BSE stock symbol."
        )

    return ChartDataResponse(
        symbol=f"{exchange}-{trading_symbol}",
        duration=duration,
        data=[ChartDataPoint(**point) for point in data],
    )
