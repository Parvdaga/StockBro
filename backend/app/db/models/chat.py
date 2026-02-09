"""
Chat conversation and message models
"""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from app.db.models.base import BaseModel


class Conversation(BaseModel):
    """Chat conversation container"""
    __tablename__ = "conversations"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255))  # Auto-generated from first message
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(BaseModel):
    """Individual message in a conversation"""
    __tablename__ = "messages"
    
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    
    # Structured data attached to message
    stocks = Column(JSON)  # List of StockData
    news = Column(JSON)  # List of NewsItem
    charts = Column(JSON)  # Chart configurations
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
