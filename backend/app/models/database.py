"""
SQLAlchemy database models for LocalAI Community.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    """Generate a UUID for primary keys."""
    return str(uuid.uuid4())

class User(Base):
    """User model for authentication and session management."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class Conversation(Base):
    """Conversation model for chat sessions."""
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=True)
    model = Column(String(50), nullable=False, default="llama3:latest")
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}', model='{self.model}')>"

class Message(Base):
    """Message model for individual chat messages."""
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, nullable=True)
    model_used = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', conversation_id='{self.conversation_id}')>"

class ChatDocument(Base):
    """Chat document model for conversation-scoped document storage."""
    __tablename__ = "chat_documents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    summary_text = Column(Text, nullable=True)
    summary_type = Column(String(50), nullable=True)
    processing_status = Column(String(50), default="uploaded", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", backref="documents")
    user = relationship("User", backref="documents")
    
    def __repr__(self):
        return f"<ChatDocument(id={self.id}, filename='{self.filename}', conversation_id='{self.conversation_id}')>"

class DocumentChunk(Base):
    """Document chunk model for storing document segments with embeddings."""
    __tablename__ = "document_chunks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("chat_documents.id"), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding_id = Column(String(100), nullable=True)  # Reference to vector store
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    document = relationship("ChatDocument", backref="chunks")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id='{self.document_id}', chunk_index={self.chunk_index})>"

class UserSession(Base):
    """User session model for storing current user state."""
    __tablename__ = "user_sessions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_key = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "default_session"
    current_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="sessions")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, session_key='{self.session_key}', current_user_id='{self.current_user_id}')>" 