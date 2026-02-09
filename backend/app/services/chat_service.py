"""
Chat service for managing conversations and messages
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models.chat import Conversation, Message
from app.schemas.chat import (
    ChatRequest, 
    ChatResponse, 
    ConversationResponse, 
    MessageResponse
)
from app.core.exceptions import NotFoundException, ForbiddenException
import json


class ChatService:
    """Service for chat operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_conversation(self, user_id: UUID) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(user_id=user_id)
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation
    
    async def get_conversation(
        self, 
        conversation_id: UUID, 
        user_id: UUID
    ) -> ConversationResponse:
        """Get conversation with message history"""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise NotFoundException("Conversation not found")
        
        if conversation.user_id != user_id:
            raise ForbiddenException("Access denied")
        
        return ConversationResponse.from_orm(conversation)
    
    async def get_user_conversations(self, user_id: UUID) -> List[ConversationResponse]:
        """Get all conversations for a user"""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .options(selectinload(Conversation.messages))
            .order_by(Conversation.updated_at.desc())
        )
        conversations = result.scalars().all()
        return [ConversationResponse.from_orm(c) for c in conversations]
    
    async def add_message(
        self,
        conversation_id: UUID,
        user_id: UUID,
        role: str,
        content: str,
        stocks: Optional[List[dict]] = None,
        news: Optional[List[dict]] = None,
        charts: Optional[dict] = None
    ) -> Message:
        """Add a message to conversation"""
        # Verify conversation ownership
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise NotFoundException("Conversation not found")
        
        if conversation.user_id != user_id:
            raise ForbiddenException("Access denied")
        
        # Create message
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            stocks=stocks,
            news=news,
            charts=charts
        )
        
        self.db.add(message)
        
        # Update conversation title from first message if not set
        if not conversation.title and role == "user":
            conversation.title = content[:50] + ("..." if len(content) > 50 else "")
        
        await self.db.commit()
        await self.db.refresh(message)
        
        return message
    
    async def delete_conversation(self, conversation_id: UUID, user_id: UUID) -> None:
        """Delete a conversation"""
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise NotFoundException("Conversation not found")
        
        if conversation.user_id != user_id:
            raise ForbiddenException("Access denied")
        
        await self.db.delete(conversation)
        await self.db.commit()
