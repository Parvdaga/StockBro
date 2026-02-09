"""
Finnhub API client for global stock market data
"""
from typing import Optional, List
from datetime import datetime, timedelta
from app.schemas.stock import StockData, PricePoint
from app.config import settings
import asyncio
import httpx


class FinnhubClient:
    """Client for Finnhub API"""
    
    def __init__(self):
        self.api_key = settings.FINNHUB_API_KEY
        self.base_url = "https://finnhub.io/api/v1"
        self.enabled = bool(self.api_key)
    
    async def get_stock_data(self, symbol: str) -> Optional[StockData]:
        """
        Get real-time stock data from Finnhub
        symbol format: AAPL, TSLA, etc.
        """
        if not self.enabled:
            return None
        
        try:
            # Remove exchange prefix if present
            clean_symbol = symbol.split("-")[-1] if "-" in symbol else symbol
            
            async with httpx.AsyncClient() as client:
                # Get quote
                quote_response = await client.get(
                    f"{self.base_url}/quote",
                    params={"symbol": clean_symbol, "token": self.api_key}
                )
                quote = quote_response.json()
                
                # Get company profile
                profile_response = await client.get(
                    f"{self.base_url}/stock/profile2",
                    params={"symbol": clean_symbol, "token": self.api_key}
                )
                profile = profile_response.json()
                
                if not quote.get('c'):  # current price
                    return None
                
                # Build StockData
                stock_data = StockData(
                    symbol=clean_symbol,
                    name=profile.get('name', clean_symbol),
                    current_price=quote['c'],
                    change_percent=quote.get('dp'),  # delta percent
                    volume=None,  # Not in quote endpoint
                    market_cap=profile.get('marketCapitalization'),
                    pe_ratio=None,  # Need metrics endpoint (paid)
                    eps=None,
                    dividend_yield=None,
                    week_52_high=quote.get('h'),  # high price of the day
                    week_52_low=quote.get('l')   # low price of the day
                )
                
                return stock_data
                
        except Exception as e:
            print(f"Finnhub API error for {symbol}: {e}")
            return None
    
    async def get_price_history(
        self, 
        symbol: str, 
        days: int = 30
    ) -> List[PricePoint]:
        """Get historical candle data"""
        if not self.enabled:
            return []
        
        try:
            clean_symbol = symbol.split("-")[-1] if "-" in symbol else symbol
            
            # Calculate timestamps
            end_time = int(datetime.utcnow().timestamp())
            start_time = int((datetime.utcnow() - timedelta(days=days)).timestamp())
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/stock/candle",
                    params={
                        "symbol": clean_symbol,
                        "resolution": "D",  # Daily
                        "from": start_time,
                        "to": end_time,
                        "token": self.api_key
                    }
                )
                data = response.json()
                
                if data.get('s') != 'ok':
                    return []
                
                # Convert to PricePoint objects
                price_points = []
                for i in range(len(data['t'])):
                    price_points.append(PricePoint(
                        timestamp=datetime.fromtimestamp(data['t'][i]),
                        open=data['o'][i],
                        high=data['h'][i],
                        low=data['l'][i],
                        close=data['c'][i],
                        volume=data['v'][i] if 'v' in data else None
                    ))
                
                return price_points
                
        except Exception as e:
            print(f"Finnhub history error for {symbol}: {e}")
            return []
