"""
Chat endpoints - Supabase version integrated with AI agents
"""
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.core.dependencies import get_supabase, get_current_user
from app.schemas.chat import ChatRequest, ChatResponse, ConversationResponse
from app.agents.master_agent import master_agent
from typing import List
from uuid import UUID

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Send message and get AI response"""
    
    # Get or create conversation
    if request.conversation_id:
        conversation = supabase.table("conversations")\
            .select("*")\
            .eq("id", str(request.conversation_id))\
            .eq("user_id", str(current_user.id))\
            .single()\
            .execute()
        
        if not conversation.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation_id = request.conversation_id
    else:
        # Create new conversation
        new_conv = supabase.table("conversations").insert({
            "user_id": str(current_user.id),
            "title": request.message[:50]  # Use first 50 chars as title
       }).execute()
        conversation_id = new_conv.data[0]["id"]
    
    # Add user message
    supabase.table("messages").insert({
        "conversation_id": str(conversation_id),
        "role": "user",
        "content": request.message
    }).execute()
    
    # Run AI agent
    response_stream = master_agent.run(request.message, stream=False)
    answer_text = response_stream.content
    
    # Parse structured data from agent response
    # TODO: Enhance agent to return JSON with stocks, news, charts
    stocks = []
    news = []
    charts = None
    
    # Add assistant message
    supabase.table("messages").insert({
        "conversation_id": str(conversation_id),
        "role": "assistant",
        "content": answer_text,
        "stocks": stocks,
        "news": news,
        "charts": charts
    }).execute()
    
    return ChatResponse(
        conversation_id=UUID(conversation_id),
        answer=answer_text,
        stocks=stocks,
        news=news,
        charts=charts
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
