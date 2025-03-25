"""
Data models for the chatbot feature
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4

from shared.database import Base
from sqlalchemy import Column, String, DateTime, Integer, JSON, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship


class ChatSession(Base):
    """
    Model for storing chat sessions in the database
    """
    __tablename__ = 'chat_sessions'
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(50), nullable=False)
    language = Column(String(10), default='he')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship with documents (many-to-many)
    document_ids = Column(JSON, default=list)
    
    # Relationship with messages
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "language": self.language,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
            "document_ids": self.document_ids
        }


class ChatMessage(Base):
    """
    Model for storing chat messages in the database
    """
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), ForeignKey('chat_sessions.id'), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Document references
    document_references = Column(JSON, default=list)
    
    # Relationship with session
    session = relationship("ChatSession", back_populates="messages")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "document_references": self.document_references
        }
