"""
Repository layer for database operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
import logging

from ..models.database import Conversation, Message, User, ChatDocument, DocumentChunk, UserSession, UserQuestion, AIPrompt, ContextAwarenessData
from ..models.schemas import ConversationCreate, MessageCreate, UserCreate, ChatDocumentCreate, DocumentChunkCreate, UserSessionCreate, UserSessionUpdate, UserQuestionCreate, AIPromptCreate, ContextAwarenessDataCreate

logger = logging.getLogger(__name__)

class ConversationRepository:
    """Repository for conversation operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_conversation(self, conversation: ConversationCreate, conversation_id: Optional[str] = None) -> Conversation:
        """Create a new conversation."""
        # Don't create conversations for guest users
        if conversation.user_id == "00000000-0000-0000-0000-000000000001":
            raise ValueError("Cannot create conversations for guest users")
        
        db_conversation = Conversation(
            id=conversation_id,  # Use provided ID or let database generate one
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
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user and all related data (cascade delete)."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Due to cascade="all, delete-orphan" in the User model,
            # deleting the user will automatically delete all related:
            # - conversations
            # - messages (through conversations)
            # - chat_documents (through conversations)
            # - document_chunks (through chat_documents)
            # - user_settings (if any)
            self.db.delete(user)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            self.db.rollback()
            return False
    
    def delete_user_by_username(self, username: str) -> bool:
        """Delete a user by username and all related data."""
        try:
            user = self.db.query(User).filter(User.username == username).first()
            if not user:
                return False
            
            user_id = user.id
            self.db.delete(user)
            self.db.commit()
            logger.info(f"Deleted user '{username}' (ID: {user_id}) and all related data")
            return True
        except Exception as e:
            logger.error(f"Failed to delete user '{username}': {e}")
            self.db.rollback()
            return False

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

class UserSessionRepository:
    """Repository for user session operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, session: UserSessionCreate) -> UserSession:
        """Create a new user session."""
        db_session = UserSession(
            session_key=session.session_key,
            current_user_id=session.current_user_id
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        return db_session
    
    def get_session(self, session_key: str) -> Optional[UserSession]:
        """Get a user session by session key."""
        return self.db.query(UserSession).filter(
            UserSession.session_key == session_key
        ).first()
    
    def update_session(self, session_key: str, update_data: UserSessionUpdate) -> Optional[UserSession]:
        """Update a user session."""
        try:
            session = self.get_session(session_key)
            if not session:
                return None
            
            if update_data.current_user_id is not None:
                session.current_user_id = update_data.current_user_id
            
            session.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(session)
            return session
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user session: {e}")
            raise
    
    def upsert_session(self, session_key: str, current_user_id: str) -> UserSession:
        """Create or update a user session."""
        try:
            session = self.get_session(session_key)
            if session:
                # Update existing session
                session.current_user_id = current_user_id
                session.updated_at = datetime.now()
                self.db.commit()
                self.db.refresh(session)
                return session
            else:
                # Create new session
                new_session = UserSession(
                    session_key=session_key,
                    current_user_id=current_user_id
                )
                self.db.add(new_session)
                self.db.commit()
                self.db.refresh(new_session)
                return new_session
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error upserting user session: {e}")
            raise

class UserQuestionRepository:
    """Repository for user question operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_question(self, question_data: UserQuestionCreate) -> UserQuestion:
        """Create a new user question."""
        db_question = UserQuestion(
            conversation_id=question_data.conversation_id,
            user_id=question_data.user_id,
            question_text=question_data.question_text
        )
        self.db.add(db_question)
        self.db.commit()
        self.db.refresh(db_question)
        return db_question
    
    def get_question(self, question_id: str) -> Optional[UserQuestion]:
        """Get a question by ID."""
        return self.db.query(UserQuestion).filter(UserQuestion.id == question_id).first()
    
    def get_questions_by_conversation(self, conversation_id: str, limit: int = 100) -> List[UserQuestion]:
        """Get questions for a conversation."""
        return self.db.query(UserQuestion).filter(
            UserQuestion.conversation_id == conversation_id
        ).order_by(UserQuestion.question_timestamp.desc()).limit(limit).all()
    
    def get_questions_by_user(self, user_id: str, limit: int = 100) -> List[UserQuestion]:
        """Get questions for a user."""
        return self.db.query(UserQuestion).filter(
            UserQuestion.user_id == user_id
        ).order_by(UserQuestion.question_timestamp.desc()).limit(limit).all()
    
    def delete_question(self, question_id: str) -> bool:
        """Delete a question."""
        question = self.get_question(question_id)
        if not question:
            return False
        
        self.db.delete(question)
        self.db.commit()
        return True

class AIPromptRepository:
    """Repository for AI prompt operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_prompt(self, prompt_data: AIPromptCreate) -> AIPrompt:
        """Create a new AI prompt."""
        db_prompt = AIPrompt(
            question_id=prompt_data.question_id,
            conversation_id=prompt_data.conversation_id,
            user_id=prompt_data.user_id,
            final_prompt=prompt_data.final_prompt,
            model_used=prompt_data.model_used,
            temperature=prompt_data.temperature,
            max_tokens=prompt_data.max_tokens
        )
        self.db.add(db_prompt)
        self.db.commit()
        self.db.refresh(db_prompt)
        return db_prompt
    
    def get_prompt_by_question(self, question_id: str) -> Optional[AIPrompt]:
        """Get prompt for a specific question."""
        return self.db.query(AIPrompt).filter(AIPrompt.question_id == question_id).first()
    
    def get_prompts_by_conversation(self, conversation_id: str, limit: int = 100) -> List[AIPrompt]:
        """Get prompts for a conversation."""
        return self.db.query(AIPrompt).filter(
            AIPrompt.conversation_id == conversation_id
        ).order_by(AIPrompt.prompt_timestamp.desc()).limit(limit).all()
    
    def get_prompts_by_user(self, user_id: str, limit: int = 100) -> List[AIPrompt]:
        """Get prompts for a user."""
        return self.db.query(AIPrompt).filter(
            AIPrompt.user_id == user_id
        ).order_by(AIPrompt.prompt_timestamp.desc()).limit(limit).all()
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt."""
        prompt = self.db.query(AIPrompt).filter(AIPrompt.id == prompt_id).first()
        if not prompt:
            return False
        
        self.db.delete(prompt)
        self.db.commit()
        return True

class ContextAwarenessRepository:
    """Repository for context awareness data operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_context_data(self, context_data: ContextAwarenessDataCreate) -> ContextAwarenessData:
        """Create new context awareness data."""
        db_context = ContextAwarenessData(
            question_id=context_data.question_id,
            conversation_id=context_data.conversation_id,
            user_id=context_data.user_id,
            context_type=context_data.context_type,
            context_data=context_data.context_data,
            context_metadata=context_data.context_metadata
        )
        self.db.add(db_context)
        self.db.commit()
        self.db.refresh(db_context)
        return db_context
    
    def get_context_by_question(self, question_id: str) -> List[ContextAwarenessData]:
        """Get all context data for a specific question."""
        return self.db.query(ContextAwarenessData).filter(
            ContextAwarenessData.question_id == question_id
        ).order_by(ContextAwarenessData.context_timestamp.asc()).all()
    
    def get_context_by_type(self, question_id: str, context_type: str) -> Optional[ContextAwarenessData]:
        """Get context data of a specific type for a question."""
        return self.db.query(ContextAwarenessData).filter(
            and_(
                ContextAwarenessData.question_id == question_id,
                ContextAwarenessData.context_type == context_type
            )
        ).first()
    
    def get_context_by_conversation(self, conversation_id: str, limit: int = 100) -> List[ContextAwarenessData]:
        """Get context data for a conversation."""
        return self.db.query(ContextAwarenessData).filter(
            ContextAwarenessData.conversation_id == conversation_id
        ).order_by(ContextAwarenessData.context_timestamp.desc()).limit(limit).all()
    
    def get_context_by_user(self, user_id: str, limit: int = 100) -> List[ContextAwarenessData]:
        """Get context data for a user."""
        return self.db.query(ContextAwarenessData).filter(
            ContextAwarenessData.user_id == user_id
        ).order_by(ContextAwarenessData.context_timestamp.desc()).limit(limit).all()
    
    def delete_context_data(self, context_id: str) -> bool:
        """Delete context data."""
        context = self.db.query(ContextAwarenessData).filter(ContextAwarenessData.id == context_id).first()
        if not context:
            return False
        
        self.db.delete(context)
        self.db.commit()
        return True 