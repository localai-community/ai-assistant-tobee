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

class ChatDocumentBase(BaseModel):
    """Base chat document schema."""
    filename: str = Field(..., max_length=255)
    file_type: str = Field(..., max_length=50)
    file_size: int
    file_path: str = Field(..., max_length=500)

class ChatDocumentCreate(ChatDocumentBase):
    """Schema for creating a chat document."""
    conversation_id: str
    user_id: Optional[str] = None

class ChatDocumentUpdate(BaseModel):
    """Schema for updating a chat document."""
    summary_text: Optional[str] = None
    summary_type: Optional[str] = Field(None, max_length=50)
    processing_status: Optional[str] = Field(None, max_length=50)

class ChatDocument(ChatDocumentBase):
    """Schema for chat document responses."""
    id: str
    conversation_id: str
    user_id: Optional[str] = None
    upload_timestamp: datetime
    summary_text: Optional[str] = None
    summary_type: Optional[str] = None
    processing_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DocumentChunkBase(BaseModel):
    """Base document chunk schema."""
    chunk_text: str
    chunk_index: int

class DocumentChunkCreate(DocumentChunkBase):
    """Schema for creating a document chunk."""
    document_id: str
    embedding_id: Optional[str] = None

class DocumentChunk(DocumentChunkBase):
    """Schema for document chunk responses."""
    id: str
    document_id: str
    embedding_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# User Settings Schemas
class UserSettingsBase(BaseModel):
    user_id: str
    enable_context_awareness: bool = True
    include_memory: bool = False
    context_strategy: str = "conversation_only"
    selected_model: str = "deepseek-r1:8b"
    use_streaming: bool = True
    use_rag: bool = False
    use_advanced_rag: bool = False
    use_phase2_reasoning: bool = False
    use_reasoning_chat: bool = False
    use_phase3_reasoning: bool = False
    selected_phase2_engine: str = "auto"
    selected_phase3_strategy: str = "auto"
    temperature: float = 0.7

class UserSettingsCreate(UserSettingsBase):
    pass

class UserSettingsUpdate(BaseModel):
    enable_context_awareness: Optional[bool] = None
    include_memory: Optional[bool] = None
    context_strategy: Optional[str] = None
    selected_model: Optional[str] = None
    use_streaming: Optional[bool] = None
    use_rag: Optional[bool] = None
    use_advanced_rag: Optional[bool] = None
    use_phase2_reasoning: Optional[bool] = None
    use_reasoning_chat: Optional[bool] = None
    use_phase3_reasoning: Optional[bool] = None
    selected_phase2_engine: Optional[str] = None
    selected_phase3_strategy: Optional[str] = None
    temperature: Optional[float] = None

class UserSettingsResponse(UserSettingsBase):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True