"""
Chat endpoints — integrates Groww stock data, GNews news, and LLM via agents
"""
import re
import asyncio
import traceback
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.core.dependencies import get_supabase, get_current_user
from app.schemas.chat import ChatRequest, ChatResponse, ConversationResponse, NewsItem, ChartConfig
from app.schemas.stock import StockData
from app.agents.master_agent import master_agent
from app.integrations.groww import GrowwClient
from app.integrations.newsdata import NewsDataClient
from typing import List
from uuid import UUID

router = APIRouter(prefix="/chat", tags=["Chat"])

# Shared clients
_groww = GrowwClient()
_news_client = NewsDataClient()

# Common Indian stock symbols for detection
KNOWN_SYMBOLS = {
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC",
    "BHARTIARTL", "HINDUNILVR", "KOTAKBANK", "LT", "AXISBANK", "BAJFINANCE",
    "MARUTI", "TITAN", "WIPRO", "ADANIENT", "ADANIPORTS", "ASIANPAINT",
    "BAJAJFINSV", "COALINDIA", "DRREDDY", "EICHERMOT", "GRASIM",
    "HCLTECH", "HEROMOTOCO", "HINDALCO", "INDUSINDBK", "JSWSTEEL",
    "M&M", "NESTLEIND", "NTPC", "ONGC", "POWERGRID", "SUNPHARMA",
    "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TECHM", "ULTRACEMCO",
    "UNITDSPR", "CIPLA", "DIVISLAB", "VEDL", "ZOMATO", "PAYTM",
    "NIFTY", "SENSEX",
}


def _extract_stock_symbols(text: str) -> List[str]:
    """Extract potential stock symbols from text using word-boundary matching."""
    found = set()
    upper = text.upper()

    # Check known symbols with word-boundary to avoid false positives
    # e.g. "LT" should not match inside "RESULT" or "ALTERNATIVELY"
    for sym in KNOWN_SYMBOLS:
        # Escape special chars like & for regex
        escaped = re.escape(sym)
        if re.search(rf'\b{escaped}\b', upper):
            found.add(sym)

    # Check NSE-XXX or BSE-XXX patterns
    pattern = re.findall(r'\b(NSE|BSE)-([A-Z&]+)\b', upper)
    for exchange, sym in pattern:
        found.add(sym)

    return list(found)


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Send message and get AI response with integrated stock data and news"""

    # Get or create conversation
    conversation_id = None
    
    if request.conversation_id:
        try:
            # Try to fetch existing conversation
            # Using .execute() instead of .single() to avoid exception if not found
            conversation = await asyncio.to_thread(
                supabase.table("conversations")
                .select("*")
                .eq("id", str(request.conversation_id))
                .eq("user_id", str(current_user.id))
                .execute
            )

            if conversation.data:
                conversation_id = str(request.conversation_id)
            else:
                print(f"Conversation {request.conversation_id} not found. Creating new conversation.")
        
        except Exception as e:
            print(f"Error fetching conversation {request.conversation_id}: {e}")
            # Logic will fall through to creating new conversation
    
    # Create new conversation if ID wasn't provided OR wasn't found
    if not conversation_id:
        try:
            new_conv = await asyncio.to_thread(
                supabase.table("conversations").insert({
                    "user_id": str(current_user.id),
                    "title": request.message[:50]
                }).execute
            )
            conversation_id = new_conv.data[0]["id"]
        except Exception as e:
            print(f"Error creating conversation: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")

    # Save user message
    await asyncio.to_thread(
        supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "role": "user",
            "content": request.message
        }).execute
    )

    # ── Run AI Agent (LLM + Groww + NewsData via tool calls) ──
    try:
        response_obj = master_agent.run(request.message, stream=False)
        answer_text = response_obj.content or "I couldn't process your request. Please try again."
    except Exception as e:
        print(f"Agent error: {e}")
        traceback.print_exc()
        answer_text = "I encountered an issue processing your request. Please try again."

    # ── Extract structured data from the conversation ──
    combined_text = request.message  # Only extract from user message, not LLM output
    symbols = _extract_stock_symbols(combined_text)

    # Fetch live stock data for mentioned symbols
    stocks_data = []
    for sym in symbols[:5]:  # Limit to 5 stocks
        try:
            stock = await _groww.get_stock_data(sym)
            if stock:
                stocks_data.append(stock.model_dump())
        except Exception as e:
            print(f"Error fetching stock {sym}: {e}")

    # Fetch relevant news
    news_data = []
    try:
        # Build a news query from the message
        news_query = request.message
        if symbols:
            # If we found stock symbols, search for the first one
            news_query = f"{symbols[0]} stock India"
        articles = await _news_client.search_news(news_query, max_results=3)
        for article in articles:
            news_data.append({
                "title": article["title"],
                "url": article["url"],
                "source": article.get("source", "Unknown"),
                "published_at": article.get("published_at", ""),
                "sentiment": None,
                "sentiment_score": None,
            })
    except Exception as e:
        print(f"Error fetching news: {e}")

    # Save assistant message with structured data
    await asyncio.to_thread(
        supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": answer_text,
            "stocks": stocks_data if stocks_data else None,
            "news": news_data if news_data else None,
            "charts": None
        }).execute
    )

    # Build chart configs for detected stocks
    chart_configs = []
    for sym in symbols[:3]:  # Charts for up to 3 stocks
        chart_configs.append(ChartConfig(
            symbol=sym,
            chart_type="candlestick",
            data_url=f"/api/v1/charts/{sym}/history?duration=3M"
        ))

    return ChatResponse(
        conversation_id=UUID(conversation_id),
        answer=answer_text,
        stocks=[StockData(**d) for d in stocks_data] if stocks_data else None,
        news=[NewsItem(**n) for n in news_data] if news_data else None,
        charts=chart_configs if chart_configs else None
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get user's conversation history"""
    response = await asyncio.to_thread(
        supabase.table("conversations")
        .select("*, messages(*)")
        .eq("user_id", str(current_user.id))
        .order("created_at", desc=True)
        .execute
    )

    return response.data


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get specific conversation with messages"""
    response = await asyncio.to_thread(
        supabase.table("conversations")
        .select("*, messages(*)")
        .eq("id", str(conversation_id))
        .eq("user_id", str(current_user.id))
        .single()
        .execute
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return response.data


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Delete a conversation"""
    response = await asyncio.to_thread(
        supabase.table("conversations")
        .delete()
        .eq("id", str(conversation_id))
        .eq("user_id", str(current_user.id))
        .execute
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Conversation not found")
