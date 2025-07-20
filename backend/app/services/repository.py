"""
Repository layer for database operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
import logging

from ..models.database import Conversation, Message, User
from ..models.schemas import ConversationCreate, MessageCreate, UserCreate

logger = logging.getLogger(__name__)

class ConversationRepository:
    """Repository for conversation operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_conversation(self, conversation: ConversationCreate) -> Conversation:
        """Create a new conversation."""
        db_conversation = Conversation(
            title=conversation.title,
            model=conversation.model,
            user_id=conversation.user_id
        )
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        return db_conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.is_active == True
        ).first()
    
    def get_conversations(self, user_id: Optional[str] = None, limit: int = 100) -> List[Conversation]:
        """Get conversations, optionally filtered by user."""
        query = self.db.query(Conversation).filter(Conversation.is_active == True)
        
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        
        return query.order_by(Conversation.updated_at.desc()).limit(limit).all()
    
    def update_conversation(self, conversation_id: str, **kwargs) -> Optional[Conversation]:
        """Update a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        for key, value in kwargs.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)
        
        conversation.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Soft delete a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        conversation.is_active = False
        self.db.commit()
        return True
    
    def clear_conversations(self, user_id: Optional[str] = None) -> int:
        """Clear all conversations for a user or all users."""
        query = self.db.query(Conversation).filter(Conversation.is_active == True)
        
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        
        count = query.count()
        query.update({"is_active": False})
        self.db.commit()
        return count

class MessageRepository:
    """Repository for message operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_message(self, message: MessageCreate) -> Message:
        """Create a new message."""
        db_message = Message(
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            tokens_used=message.tokens_used,
            model_used=message.model_used
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message
    
    def get_messages(self, conversation_id: str, limit: int = 100) -> List[Message]:
        """Get messages for a conversation."""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).limit(limit).all()
    
    def get_message(self, message_id: str) -> Optional[Message]:
        """Get a message by ID."""
        return self.db.query(Message).filter(Message.id == message_id).first()
    
    def delete_message(self, message_id: str) -> bool:
        """Delete a message."""
        message = self.get_message(message_id)
        if not message:
            return False
        
        self.db.delete(message)
        self.db.commit()
        return True

class UserRepository:
    """Repository for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user: UserCreate) -> User:
        """Create a new user."""
        db_user = User(
            username=user.username,
            email=user.email
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        return self.db.query(User).filter(
            User.id == user_id,
            User.is_active == True
        ).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self.db.query(User).filter(
            User.username == username,
            User.is_active == True
        ).first()
    
    def get_users(self, limit: int = 100) -> List[User]:
        """Get all active users."""
        return self.db.query(User).filter(
            User.is_active == True
        ).order_by(User.created_at.desc()).limit(limit).all() 