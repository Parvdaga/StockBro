"""
News proxy endpoints — serves NewsData.io content through backend
to protect API keys and add caching/rate-limiting.
"""
from fastapi import APIRouter, Query
from app.integrations.newsdata import NewsDataClient
from typing import List, Dict

router = APIRouter(prefix="/news", tags=["News"])

# Shared client
_news_client = NewsDataClient()


@router.get("/search")
async def search_news(
    q: str = Query(..., min_length=1, description="Topic to search for"),
    max_results: int = Query(5, ge=1, le=10, description="Max articles to return"),
):
    """
    Search news by topic — backend proxies to NewsData.io.
    Results are cached for 10 minutes and rate-limited.
    """
    articles = await _news_client.search_news(q, max_results)
    return {"results": articles, "count": len(articles)}


@router.get("/headlines")
async def get_headlines(
    category: str = Query("business", description="News category"),
    max_results: int = Query(5, ge=1, le=10, description="Max headlines"),
):
    """
    Top business headlines — backend proxies to NewsData.io.
    Results are cached for 10 minutes and rate-limited.
    """
    headlines = await _news_client.get_top_headlines(category, max_results)
    return {"results": headlines, "count": len(headlines)}
