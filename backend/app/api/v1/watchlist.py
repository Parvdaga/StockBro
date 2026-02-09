"""
Watchlist endpoints
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.services.watchlist_service import WatchlistService
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistUpdate,
    WatchlistResponse,
    WatchlistItemCreate,
    WatchlistItemResponse
)
from typing import List
from uuid import UUID

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])


@router.post("/", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def create_watchlist(
    request: WatchlistCreate,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new watchlist"""
    watchlist_service = WatchlistService(db)
    return await watchlist_service.create_watchlist(user_id, request)


@router.get("/", response_model=List[WatchlistResponse])
async def get_watchlists(
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all user watchlists"""
    watchlist_service = WatchlistService(db)
    return await watchlist_service.get_user_watchlists(user_id)


@router.get("/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist(
    watchlist_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific watchlist"""
    watchlist_service = WatchlistService(db)
    return await watchlist_service.get_watchlist(watchlist_id, user_id)


@router.patch("/{watchlist_id}", response_model=WatchlistResponse)
async def update_watchlist(
    watchlist_id: UUID,
    request: WatchlistUpdate,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update watchlist"""
    watchlist_service = WatchlistService(db)
    return await watchlist_service.update_watchlist(watchlist_id, user_id, request)


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(
    watchlist_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete watchlist"""
    watchlist_service = WatchlistService(db)
    await watchlist_service.delete_watchlist(watchlist_id, user_id)


@router.post("/{watchlist_id}/items", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_stock_to_watchlist(
    watchlist_id: UUID,
    request: WatchlistItemCreate,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add stock to watchlist"""
    watchlist_service = WatchlistService(db)
    return await watchlist_service.add_stock(watchlist_id, user_id, request)


@router.delete("/{watchlist_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_stock_from_watchlist(
    watchlist_id: UUID,
    item_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove stock from watchlist"""
    watchlist_service = WatchlistService(db)
    await watchlist_service.remove_stock(watchlist_id, item_id, user_id)
