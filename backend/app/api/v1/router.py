"""
API v1 router - aggregates all endpoint routers
"""
from fastapi import APIRouter
from app.api.v1 import auth, stocks, watchlist, chat, news, charts

router = APIRouter()

# Include all sub-routers
router.include_router(auth.router)
router.include_router(stocks.router)
router.include_router(watchlist.router)
router.include_router(chat.router)
router.include_router(news.router)
router.include_router(charts.router)
