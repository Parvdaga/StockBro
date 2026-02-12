"""
Chat endpoints — integrates Groww stock data, GNews news, and LLM via agents
"""
import re
import traceback
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.core.dependencies import get_supabase, get_current_user
from app.schemas.chat import ChatRequest, ChatResponse, ConversationResponse, NewsItem
from app.schemas.stock import StockData
from app.agents.master_agent import master_agent
from app.integrations.groww import GrowwClient
from app.integrations.gnews import GNewsClient
from typing import List
from uuid import UUID

router = APIRouter(prefix="/chat", tags=["Chat"])

# Shared clients
_groww = GrowwClient()
_gnews = GNewsClient()

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
    """Extract potential stock symbols from text (user message + agent response)"""
    found = set()
    upper = text.upper()

    # Check known symbols
    for sym in KNOWN_SYMBOLS:
        if sym in upper:
            found.add(sym)

    # Check NSE-XXX or BSE-XXX patterns
    pattern = re.findall(r'\b(NSE|BSE)-([A-Z&]+)\b', upper)
    for exchange, sym in pattern:
        found.add(sym)

    # Check ₹ followed by a number (indicates price was mentioned, symbol likely nearby)
    # Also look for stock-like uppercase words
    words = re.findall(r'\b([A-Z][A-Z0-9&]{2,15})\b', upper)
    for w in words:
        if w in KNOWN_SYMBOLS:
            found.add(w)

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
            conversation = supabase.table("conversations")\
                .select("*")\
                .eq("id", str(request.conversation_id))\
                .eq("user_id", str(current_user.id))\
                .execute()

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
            new_conv = supabase.table("conversations").insert({
                "user_id": str(current_user.id),
                "title": request.message[:50]
            }).execute()
            conversation_id = new_conv.data[0]["id"]
        except Exception as e:
            print(f"Error creating conversation: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")

    # Save user message
    supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "role": "user",
        "content": request.message
    }).execute()

    # ── Run AI Agent (LLM + Groww + GNews via tool calls) ──
    try:
        response_obj = master_agent.run(request.message, stream=False)
        answer_text = response_obj.content or "I couldn't process your request. Please try again."
    except Exception as e:
        print(f"Agent error: {e}")
        traceback.print_exc()
        answer_text = "I encountered an issue processing your request. Please try again."

    # ── Extract structured data from the conversation ──
    combined_text = f"{request.message} {answer_text}"
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
        articles = await _gnews.search_news(news_query, max_results=3)
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
    supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": answer_text,
        "stocks": stocks_data if stocks_data else None,
        "news": news_data if news_data else None,
        "charts": None
    }).execute()

    return ChatResponse(
        conversation_id=UUID(conversation_id),
        answer=answer_text,
        stocks=[StockData(**d) for d in stocks_data] if stocks_data else None,
        news=[NewsItem(**n) for n in news_data] if news_data else None,
        charts=None
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get user's conversation history"""
    response = supabase.table("conversations")\
        .select("*, messages(*)")\
        .eq("user_id", str(current_user.id))\
        .order("created_at", desc=True)\
        .execute()

    return response.data


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get specific conversation with messages"""
    response = supabase.table("conversations")\
        .select("*, messages(*)")\
        .eq("id", str(conversation_id))\
        .eq("user_id", str(current_user.id))\
        .single()\
        .execute()

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
    response = supabase.table("conversations")\
        .delete()\
        .eq("id", str(conversation_id))\
        .eq("user_id", str(current_user.id))\
        .execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Conversation not found")
