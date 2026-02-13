"""
Watchlist endpoints - Supabase version
"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.core.dependencies import get_supabase, get_current_user
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
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Create a new watchlist"""
    data = {
        "user_id": str(current_user.id),
        "name": request.name,
        "description": request.description
    }
    response = await asyncio.to_thread(supabase.table("watchlists").insert(data).execute)
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create watchlist")
    return response.data[0]


@router.get("/", response_model=List[WatchlistResponse])
async def get_watchlists(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get all user watchlists with items"""
    response = await asyncio.to_thread(
        supabase.table("watchlists")
        .select("*, watchlist_items(*)")
        .eq("user_id", str(current_user.id))
        .execute
    )
    return response.data


@router.get("/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist(
    watchlist_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get specific watchlist"""
    response = await asyncio.to_thread(
        supabase.table("watchlists")
        .select("*, watchlist_items(*)")
        .eq("id", str(watchlist_id))
        .eq("user_id", str(current_user.id))
        .single()
        .execute
    )
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    return response.data


@router.patch("/{watchlist_id}", response_model=WatchlistResponse)
async def update_watchlist(
    watchlist_id: UUID,
    request: WatchlistUpdate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Update watchlist"""
    update_data = request.dict(exclude_unset=True)
    response = await asyncio.to_thread(
        supabase.table("watchlists")
        .update(update_data)
        .eq("id", str(watchlist_id))
        .eq("user_id", str(current_user.id))
        .execute
    )
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    return response.data[0]


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(
    watchlist_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Delete watchlist"""
    response = await asyncio.to_thread(
        supabase.table("watchlists")
        .delete()
        .eq("id", str(watchlist_id))
        .eq("user_id", str(current_user.id))
        .execute
    )
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Watchlist not found")


@router.post("/{watchlist_id}/items", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_stock_to_watchlist(
    watchlist_id: UUID,
    request: WatchlistItemCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Add stock to watchlist"""
    # Verify watchlist belongs to user
    watchlist = await asyncio.to_thread(
        supabase.table("watchlists")
        .select("id")
        .eq("id", str(watchlist_id))
        .eq("user_id", str(current_user.id))
        .single()
        .execute
    )
    
    if not watchlist.data:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    data = {
        "watchlist_id": str(watchlist_id),
        "symbol": request.symbol,
        "notes": request.notes
    }
    
    try:
        response = await asyncio.to_thread(supabase.table("watchlist_items").insert(data).execute)
        if not response.data:
             raise HTTPException(status_code=500, detail="Failed to add item")
        return response.data[0]
    except Exception as e:
        if "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Stock already in watchlist")
        raise


@router.delete("/{watchlist_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_stock_from_watchlist(
    watchlist_id: UUID,
    item_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Remove stock from watchlist"""
    # Verify watchlist belongs to user
    watchlist = await asyncio.to_thread(
        supabase.table("watchlists")
        .select("id")
        .eq("id", str(watchlist_id))
        .eq("user_id", str(current_user.id))
        .single()
        .execute
    )
    
    if not watchlist.data:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    response = await asyncio.to_thread(
        supabase.table("watchlist_items")
        .delete()
        .eq("id", str(item_id))
        .eq("watchlist_id", str(watchlist_id))
        .execute
    )
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Item not found")
