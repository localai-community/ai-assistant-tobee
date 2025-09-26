"""
Repository layer for database operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
import logging

from ..models.database import Conversation, Message, User, ChatDocument, DocumentChunk
from ..models.schemas import ConversationCreate, MessageCreate, UserCreate, ChatDocumentCreate, DocumentChunkCreate

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

class ChatDocumentRepository:
    """Repository for chat document operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_document(self, document_data: ChatDocumentCreate) -> ChatDocument:
        """Create a new chat document."""
        try:
            document = ChatDocument(**document_data.dict())
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            logger.info(f"Created chat document: {document.id}")
            return document
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating chat document: {e}")
            raise
    
    def get_document(self, document_id: str) -> Optional[ChatDocument]:
        """Get a chat document by ID."""
        return self.db.query(ChatDocument).filter(ChatDocument.id == document_id).first()
    
    def get_conversation_documents(self, conversation_id: str) -> List[ChatDocument]:
        """Get all documents for a conversation."""
        return self.db.query(ChatDocument).filter(
            ChatDocument.conversation_id == conversation_id
        ).order_by(ChatDocument.upload_timestamp.desc()).all()
    
    def get_user_documents(self, user_id: str, limit: int = 100) -> List[ChatDocument]:
        """Get all documents for a user."""
        return self.db.query(ChatDocument).filter(
            ChatDocument.user_id == user_id
        ).order_by(ChatDocument.upload_timestamp.desc()).limit(limit).all()
    
    def update_document(self, document_id: str, update_data: dict) -> Optional[ChatDocument]:
        """Update a chat document."""
        try:
            document = self.get_document(document_id)
            if not document:
                return None
            
            for key, value in update_data.items():
                if hasattr(document, key):
                    setattr(document, key, value)
            
            document.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(document)
            logger.info(f"Updated chat document: {document_id}")
            return document
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating chat document: {e}")
            raise
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a chat document."""
        try:
            document = self.get_document(document_id)
            if not document:
                return False
            
            self.db.delete(document)
            self.db.commit()
            logger.info(f"Deleted chat document: {document_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting chat document: {e}")
            raise
    
    def cleanup_conversation_documents(self, conversation_id: str) -> int:
        """Clean up all documents for a conversation."""
        try:
            deleted_count = self.db.query(ChatDocument).filter(
                ChatDocument.conversation_id == conversation_id
            ).delete()
            self.db.commit()
            logger.info(f"Cleaned up {deleted_count} documents for conversation: {conversation_id}")
            return deleted_count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cleaning up conversation documents: {e}")
            raise

class DocumentChunkRepository:
    """Repository for document chunk operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_chunk(self, chunk_data: DocumentChunkCreate) -> DocumentChunk:
        """Create a new document chunk."""
        try:
            chunk = DocumentChunk(**chunk_data.dict())
            self.db.add(chunk)
            self.db.commit()
            self.db.refresh(chunk)
            logger.info(f"Created document chunk: {chunk.id}")
            return chunk
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating document chunk: {e}")
            raise
    
    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        """Get all chunks for a document."""
        return self.db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index).all()
    
    def delete_document_chunks(self, document_id: str) -> int:
        """Delete all chunks for a document."""
        try:
            deleted_count = self.db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).delete()
            self.db.commit()
            logger.info(f"Deleted {deleted_count} chunks for document: {document_id}")
            return deleted_count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting document chunks: {e}")
            raise 