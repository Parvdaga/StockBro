"""
Groww API client for Indian stock market data
"""
from typing import Optional
from app.schemas.stock import StockData
from app.config import settings
import asyncio


class GrowwClient:
    """Client for Groww API"""
    
    def __init__(self):
        self.api_key = settings.GROWW_API_KEY
        self.enabled = bool(self.api_key)
    
    async def get_stock_data(self, symbol: str) -> Optional[StockData]:
        """
        Get stock data from Groww API
        symbol format: NSE-RELIANCE, BSE-SENSEX
        """
        if not self.enabled:
            return None
        
        try:
            # Import here to avoid issues if library not installed
            from growwapi import GrowwAPI
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            def fetch_data():
                groww = GrowwAPI()
                response = groww.get_instrument_by_groww_symbol(groww_symbol=symbol)
                return response
            
            response = await loop.run_in_executor(None, fetch_data)
            
            if not response:
                return None
            
            # Extract price and company name
            price = (response.get('ltp') or response.get('close_price') or 
                    response.get('current_price') or response.get('price'))
            
            company_name = (response.get('company_name') or response.get('name') or 
                          response.get('companyName') or symbol)
            
            # Build StockData
            stock_data = StockData(
                symbol=symbol,
                name=company_name,
                current_price=float(price) if price else 0.0,
                change_percent=response.get('day_change_perc'),
                volume=response.get('volume'),
                market_cap=response.get('market_cap'),
                pe_ratio=response.get('pe_ratio') or response.get('pe'),
                eps=response.get('eps'),
                dividend_yield=response.get('dividend_yield'),
                week_52_high=response.get('52_week_high') or response.get('week_52_high'),
                week_52_low=response.get('52_week_low') or response.get('week_52_low')
            )
            
            return stock_data
            
        except Exception as e:
            print(f"Groww API error for {symbol}: {e}")
            return None
