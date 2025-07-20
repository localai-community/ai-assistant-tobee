"""
Pydantic schemas for database operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=1, max_length=50)
    email: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    """Schema for creating a user."""
    pass

class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class User(UserBase):
    """Schema for user responses."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    """Base message schema."""
    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")

class MessageCreate(MessageBase):
    """Schema for creating a message."""
    conversation_id: str
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None

class Message(MessageBase):
    """Schema for message responses."""
    id: str
    conversation_id: str
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    """Base conversation schema."""
    title: Optional[str] = Field(None, max_length=200)
    model: str = Field(default="llama3.2", max_length=50)

class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""
    user_id: Optional[str] = None

class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    title: Optional[str] = Field(None, max_length=200)
    model: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class Conversation(ConversationBase):
    """Schema for conversation responses."""
    id: str
    user_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []
    
    class Config:
        from_attributes = True 