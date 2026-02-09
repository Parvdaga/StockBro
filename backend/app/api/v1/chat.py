"""
Chat endpoints - integrated with AI agents
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest, ChatResponse, ConversationResponse
from app.agents.master_agent import master_agent
from typing import List
from uuid import UUID
import json

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send message and get AI response"""
    chat_service = ChatService(db)
    
    # Get or create conversation
    if request.conversation_id:
        conversation = await chat_service.get_conversation(request.conversation_id, user_id)
        conversation_id = request.conversation_id
    else:
        conversation = await chat_service.create_conversation(user_id)
        conversation_id = conversation.id
    
    # Add user message
    await chat_service.add_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=request.message
    )
    
    # Run AI agent
    response_stream = master_agent.run(request.message, stream=False)
    answer_text = response_stream.content
    
    # Parse structured data from agent response
    # TODO: Enhance agent to return JSON with stocks, news, charts
    stocks = []
    news = []
    charts = None
    
    # Add assistant message
    await chat_service.add_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=answer_text,
        stocks=stocks,
        news=news,
        charts=charts
    )
    
    return ChatResponse(
        conversation_id=conversation_id,
        answer=answer_text,
        stocks=stocks,
        news=news,
        charts=charts
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's conversation history"""
    chat_service = ChatService(db)
    return await chat_service.get_user_conversations(user_id)


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific conversation with messages"""
    chat_service = ChatService(db)
    return await chat_service.get_conversation(conversation_id, user_id)


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation"""
    chat_service = ChatService(db)
    await chat_service.delete_conversation(conversation_id, user_id)
