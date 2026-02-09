"""
Watchlist service for managing user stock watchlists
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models.watchlist import Watchlist, WatchlistItem
from app.schemas.watchlist import (
    WatchlistCreate, 
    WatchlistUpdate, 
    WatchlistResponse, 
    WatchlistItemCreate,
    WatchlistItemResponse
)
from app.core.exceptions import NotFoundException, ForbiddenException, ConflictException
from app.services.stock_service import StockService


class WatchlistService:
    """Service for watchlist operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.stock_service = StockService(db)
    
    async def create_watchlist(
        self, 
        user_id: UUID, 
        request: WatchlistCreate
    ) -> WatchlistResponse:
        """Create a new watchlist"""
        watchlist = Watchlist(
            user_id=user_id,
            name=request.name,
            description=request.description
        )
        
        self.db.add(watchlist)
        await self.db.commit()
        await self.db.refresh(watchlist)
        
        return WatchlistResponse.from_orm(watchlist)
    
    async def get_user_watchlists(self, user_id: UUID) -> List[WatchlistResponse]:
        """Get all watchlists for a user"""
        result = await self.db.execute(
            select(Watchlist)
            .where(Watchlist.user_id == user_id)
            .options(selectinload(Watchlist.items))
        )
        watchlists = result.scalars().all()
        
        # Enrich with real-time prices
        responses = []
        for watchlist in watchlists:
            items_with_prices = []
            for item in watchlist.items:
                price_data = await self.stock_service.get_stock_price(item.symbol)
                item_response = WatchlistItemResponse.from_orm(item)
                if price_data:
                    item_response.current_price = price_data.current_price
                    item_response.change_percent = price_data.change_percent
                items_with_prices.append(item_response)
            
            watchlist_response = WatchlistResponse.from_orm(watchlist)
            watchlist_response.items = items_with_prices
            responses.append(watchlist_response)
        
        return responses
    
    async def get_watchlist(
        self, 
        watchlist_id: UUID, 
        user_id: UUID
    ) -> WatchlistResponse:
        """Get a specific watchlist"""
        result = await self.db.execute(
            select(Watchlist)
            .where(Watchlist.id == watchlist_id)
            .options(selectinload(Watchlist.items))
        )
        watchlist = result.scalar_one_or_none()
        
        if not watchlist:
            raise NotFoundException("Watchlist not found")
        
        if watchlist.user_id != user_id:
            raise ForbiddenException("Access denied")
        
        # Enrich with real-time prices
        items_with_prices = []
        for item in watchlist.items:
            price_data = await self.stock_service.get_stock_price(item.symbol)
            item_response = WatchlistItemResponse.from_orm(item)
            if price_data:
                item_response.current_price = price_data.current_price
                item_response.change_percent = price_data.change_percent
            items_with_prices.append(item_response)
        
        watchlist_response = WatchlistResponse.from_orm(watchlist)
        watchlist_response.items = items_with_prices
        return watchlist_response
    
    async def update_watchlist(
        self,
        watchlist_id: UUID,
        user_id: UUID,
        request: WatchlistUpdate
    ) -> WatchlistResponse:
        """Update watchlist details"""
        result = await self.db.execute(
            select(Watchlist).where(Watchlist.id == watchlist_id)
        )
        watchlist = result.scalar_one_or_none()
        
        if not watchlist:
            raise NotFoundException("Watchlist not found")
        
        if watchlist.user_id != user_id:
            raise ForbiddenException("Access denied")
        
        if request.name:
            watchlist.name = request.name
        if request.description is not None:
            watchlist.description = request.description
        
        await self.db.commit()
        await self.db.refresh(watchlist)
        
        return WatchlistResponse.from_orm(watchlist)
    
    async def delete_watchlist(self, watchlist_id: UUID, user_id: UUID) -> None:
        """Delete a watchlist"""
        result = await self.db.execute(
            select(Watchlist).where(Watchlist.id == watchlist_id)
        )
        watchlist = result.scalar_one_or_none()
        
        if not watchlist:
            raise NotFoundException("Watchlist not found")
        
        if watchlist.user_id != user_id:
            raise ForbiddenException("Access denied")
        
        await self.db.delete(watchlist)
        await self.db.commit()
    
    async def add_stock(
        self,
        watchlist_id: UUID,
        user_id: UUID,
        request: WatchlistItemCreate
    ) -> WatchlistItemResponse:
        """Add a stock to watchlist"""
        # Verify watchlist ownership
        result = await self.db.execute(
            select(Watchlist).where(Watchlist.id == watchlist_id)
        )
        watchlist = result.scalar_one_or_none()
        
        if not watchlist:
            raise NotFoundException("Watchlist not found")
        
        if watchlist.user_id != user_id:
            raise ForbiddenException("Access denied")
        
        # Check if stock already exists in watchlist
        result = await self.db.execute(
            select(WatchlistItem)
            .where(WatchlistItem.watchlist_id == watchlist_id)
            .where(WatchlistItem.symbol == request.symbol)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise ConflictException("Stock already in watchlist")
        
        # Add stock
        item = WatchlistItem(
            watchlist_id=watchlist_id,
            symbol=request.symbol,
            notes=request.notes
        )
        
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        
        # Enrich with price data
        price_data = await self.stock_service.get_stock_price(request.symbol)
        item_response = WatchlistItemResponse.from_orm(item)
        if price_data:
            item_response.current_price = price_data.current_price
            item_response.change_percent = price_data.change_percent
        
        return item_response
    
    async def remove_stock(
        self,
        watchlist_id: UUID,
        item_id: UUID,
        user_id: UUID
    ) -> None:
        """Remove a stock from watchlist"""
        # Verify watchlist ownership
        result = await self.db.execute(
            select(Watchlist).where(Watchlist.id == watchlist_id)
        )
        watchlist = result.scalar_one_or_none()
        
        if not watchlist:
            raise NotFoundException("Watchlist not found")
        
        if watchlist.user_id != user_id:
            raise ForbiddenException("Access denied")
        
        # Find and delete item
        result = await self.db.execute(
            select(WatchlistItem)
            .where(WatchlistItem.id == item_id)
            .where(WatchlistItem.watchlist_id == watchlist_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise NotFoundException("Stock not found in watchlist")
        
        await self.db.delete(item)
        await self.db.commit()
