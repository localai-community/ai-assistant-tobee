"""
Context Awareness Service
Advanced context management for conversational AI with long-term memory capabilities.
"""

import logging
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np
from pathlib import Path

from sqlalchemy.orm import Session
from ..models.database import Conversation, Message, User, ChatDocument
from ..models.schemas import ConversationCreate, MessageCreate
from .repository import ConversationRepository, MessageRepository, ChatDocumentRepository
from .rag.vector_store import VectorStore
from .rag.advanced_retriever import AdvancedRAGRetriever

logger = logging.getLogger(__name__)

@dataclass
class ContextEntity:
    """Represents a key entity or concept in the conversation."""
    text: str
    entity_type: str  # 'person', 'concept', 'topic', 'preference', 'fact'
    importance_score: float
    first_mentioned: datetime
    last_mentioned: datetime
    mention_count: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContextSummary:
    """Summary of conversation context."""
    conversation_id: str
    user_id: Optional[str]
    topics: List[str]
    key_entities: List[ContextEntity]
    user_preferences: Dict[str, Any]
    conversation_style: str  # 'technical', 'casual', 'formal', 'educational'
    summary_text: str
    created_at: datetime
    updated_at: datetime

@dataclass
class MemoryChunk:
    """A chunk of conversation memory for RAG storage."""
    content: str
    metadata: Dict[str, Any]
    conversation_id: str
    chunk_id: str
    created_at: datetime
    relevance_score: float = 0.0

@dataclass
class DocumentContext:
    """Represents a document in conversation context."""
    document_id: str
    filename: str
    file_type: str
    summary: Optional[str] = None
    upload_time: datetime = field(default_factory=datetime.now)
    relevance_score: float = 0.0
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

class ContextAwarenessService:
    """
    Advanced context awareness service that manages:
    - Long-term memory using RAG
    - User preferences and profiles
    - Cross-conversation context
    - Context summarization and compression
    - Smart context retrieval
    """
    
    def __init__(
        self, 
        db: Optional[Session] = None,
        vector_store: Optional[VectorStore] = None,
        memory_chunk_size: int = 5,  # Number of messages per chunk
        max_context_entities: int = 50,
        context_decay_days: int = 30  # How long to keep context
    ):
        self.db = db
        self.vector_store = vector_store or VectorStore()
        self.memory_chunk_size = memory_chunk_size
        self.max_context_entities = max_context_entities
        self.context_decay_days = context_decay_days
        
        # Initialize repositories
        if self.db:
            self.conversation_repo = ConversationRepository(self.db)
            self.message_repo = MessageRepository(self.db)
            self.document_repo = ChatDocumentRepository(self.db)
            logger.info("Context Awareness Service initialized with database")
        else:
            self.conversation_repo = None
            self.message_repo = None
            self.document_repo = None
            logger.info("Context Awareness Service initialized without database")
        
        # Initialize advanced retriever for context-aware retrieval
        self.advanced_retriever = AdvancedRAGRetriever(
            vector_store=self.vector_store,
            max_history_messages=20,
            max_entities=max_context_entities
        )
        
        # In-memory caches for performance
        self._context_cache: Dict[str, ContextSummary] = {}
        self._user_preferences_cache: Dict[str, Dict[str, Any]] = {}
        self._memory_chunks_cache: Dict[str, List[MemoryChunk]] = {}
        
        
        logger.info("Context Awareness Service initialized")
    
    
    def get_conversation_context(
        self, 
        conversation_id: str, 
        user_id: Optional[str] = None,
        include_memory: bool = True
    ) -> ContextSummary:
        """Get comprehensive context for a conversation."""
        try:
            # Check cache first
            cache_key = f"{conversation_id}_{user_id}_{include_memory}"
            if cache_key in self._context_cache:
                return self._context_cache[cache_key]
            
            # Get conversation and messages
            if not self.conversation_repo:
                return self._create_empty_context(conversation_id, user_id)
            
            conversation = self.conversation_repo.get_conversation(conversation_id)
            if not conversation:
                logger.warning(f"No conversation found in database for {conversation_id}")
                return self._create_empty_context(conversation_id, user_id)
            
            messages = self.message_repo.get_messages(conversation_id)
            if not messages:
                logger.warning(f"No messages found for conversation {conversation_id}")
                return self._create_empty_context(conversation_id, user_id)
            
            # Extract context components
            context_entities = self._extract_context_entities(messages)
            topics = self._extract_topics(messages)
            user_preferences = self._extract_user_preferences(messages, user_id)
            conversation_style = self._analyze_conversation_style(messages)
            summary_text = self._create_conversation_summary(messages)
            
            # Create context summary
            context = ContextSummary(
                conversation_id=conversation_id,
                user_id=user_id,
                topics=topics,
                key_entities=context_entities,
                user_preferences=user_preferences,
                conversation_style=conversation_style,
                summary_text=summary_text,
                created_at=conversation.created_at if conversation else datetime.now(),
                updated_at=conversation.updated_at if conversation else datetime.now()
            )
            
            # Cache the result
            self._context_cache[cache_key] = context
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return self._create_empty_context(conversation_id, user_id)
    
    def get_user_context(
        self, 
        user_id: str, 
        include_cross_conversation: bool = True
    ) -> Dict[str, Any]:
        """Get comprehensive user context across all conversations."""
        try:
            # Check cache first
            if user_id in self._user_preferences_cache and not include_cross_conversation:
                return self._user_preferences_cache[user_id]
            
            if not self.conversation_repo:
                return {}
            
            # Get all conversations for user
            conversations = self.conversation_repo.get_conversations(user_id=user_id, limit=100)
            
            user_context = {
                "user_id": user_id,
                "total_conversations": len(conversations),
                "preferences": {},
                "topics_of_interest": set(),
                "communication_style": "casual",  # default
                "expertise_areas": set(),
                "recent_context": []
            }
            
            # Analyze conversations for user patterns
            for conversation in conversations[:20]:  # Analyze recent conversations
                context = self.get_conversation_context(conversation.id, user_id, include_memory=False)
                
                # Aggregate preferences
                user_context["preferences"].update(context.user_preferences)
                user_context["topics_of_interest"].update(context.topics)
                
                # Determine communication style
                if context.conversation_style != "casual":
                    user_context["communication_style"] = context.conversation_style
                
                # Extract expertise areas from topics
                for topic in context.topics:
                    if any(keyword in topic.lower() for keyword in ["code", "programming", "algorithm", "technical"]):
                        user_context["expertise_areas"].add("technical")
                    elif any(keyword in topic.lower() for keyword in ["business", "strategy", "management"]):
                        user_context["expertise_areas"].add("business")
                    elif any(keyword in topic.lower() for keyword in ["science", "research", "analysis"]):
                        user_context["expertise_areas"].add("research")
            
            # Convert sets to lists for JSON serialization
            user_context["topics_of_interest"] = list(user_context["topics_of_interest"])
            user_context["expertise_areas"] = list(user_context["expertise_areas"])
            
            # Cache user context
            self._user_preferences_cache[user_id] = user_context
            
            return user_context
            
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return {}
    
    def store_conversation_memory(
        self, 
        conversation_id: str, 
        messages: List[Dict],
        chunk_size: Optional[int] = None
    ) -> bool:
        """Store conversation as memory chunks for long-term retrieval."""
        try:
            if not messages:
                return False
            
            chunk_size = chunk_size or self.memory_chunk_size
            chunks = []
            
            # Create memory chunks
            for i in range(0, len(messages), chunk_size):
                chunk_messages = messages[i:i + chunk_size]
                chunk_content = self._create_memory_chunk_content(chunk_messages)
                
                # Generate chunk ID
                chunk_id = self._generate_chunk_id(conversation_id, i)
                
                chunk = MemoryChunk(
                    content=chunk_content,
                    metadata={
                        "conversation_id": conversation_id,
                        "message_count": len(chunk_messages),
                        "start_index": i,
                        "end_index": i + len(chunk_messages) - 1,
                        "topics": self._extract_topics_from_chunk(chunk_messages),
                        "entities": self._extract_entities_from_chunk(chunk_messages)
                    },
                    conversation_id=conversation_id,
                    chunk_id=chunk_id,
                    created_at=datetime.now()
                )
                chunks.append(chunk)
            
            # Store chunks in vector store
            if self.vector_store:
                documents = []
                for chunk in chunks:
                    from langchain.schema import Document as LangChainDocument
                    doc = LangChainDocument(
                        page_content=chunk.content,
                        metadata=chunk.metadata
                    )
                    documents.append(doc)
                
                success = self.vector_store.add_documents(documents)
                if success:
                    logger.info(f"Stored {len(chunks)} memory chunks for conversation {conversation_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error storing conversation memory: {e}")
            return False
    
    def retrieve_relevant_memory(
        self, 
        query: str, 
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        k: int = 5
    ) -> List[Tuple[MemoryChunk, float]]:
        """Retrieve relevant memory chunks for context."""
        try:
            if not self.vector_store:
                return []
            
            # Build enhanced query with user context
            enhanced_query = query
            if user_id:
                user_context = self.get_user_context(user_id, include_cross_conversation=False)
                if user_context.get("topics_of_interest"):
                    # Add user's interests to query for better retrieval
                    interests = " ".join(user_context["topics_of_interest"][:5])
                    enhanced_query = f"{query} {interests}"
            
            # Retrieve relevant documents
            results = self.vector_store.similarity_search(enhanced_query, k)
            
            # Convert to memory chunks
            memory_chunks = []
            for doc, score in results:
                # Filter by conversation if specified
                if conversation_id and doc.metadata.get("conversation_id") != conversation_id:
                    continue
                
                chunk = MemoryChunk(
                    content=doc.page_content,
                    metadata=doc.metadata,
                    conversation_id=doc.metadata.get("conversation_id", "unknown"),
                    chunk_id=doc.metadata.get("chunk_id", "unknown"),
                    created_at=datetime.now(),  # Would be better to store actual timestamp
                    relevance_score=score
                )
                memory_chunks.append((chunk, score))
            
            return memory_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving relevant memory: {e}")
            return []
    
    def build_context_aware_query(
        self, 
        current_message: str, 
        conversation_id: str,
        user_id: Optional[str] = None,
        include_memory: bool = True
    ) -> Tuple[str, Dict[str, Any]]:
        """Build a context-aware query with conversation history and memory."""
        try:
            # Get conversation context
            context = self.get_conversation_context(conversation_id, user_id, include_memory)
            
            # Get user context
            user_context = {}
            if user_id:
                user_context = self.get_user_context(user_id, include_cross_conversation=False)
            
            # Build enhanced query components
            context_parts = []
            context_metadata = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "topics": context.topics,
                "entities": [entity.text for entity in context.key_entities],
                "user_preferences": context.user_preferences,
                "conversation_style": context.conversation_style,
                "user_expertise": user_context.get("expertise_areas", [])
            }
            
            # Add recent conversation context
            if context.topics:
                context_parts.append(f"Recent topics: {', '.join(context.topics[-5:])}")
            
            if context.key_entities:
                recent_entities = [e.text for e in context.key_entities if e.importance_score > 0.7][:5]
                if recent_entities:
                    context_parts.append(f"Key concepts: {', '.join(recent_entities)}")
            
            # Add user preferences context
            if user_context.get("preferences"):
                pref_context = []
                for key, value in list(user_context["preferences"].items())[:3]:
                    pref_context.append(f"{key}: {value}")
                if pref_context:
                    context_parts.append(f"User preferences: {', '.join(pref_context)}")
            
            # Combine with current message
            if context_parts:
                enhanced_query = f"{current_message} | Context: {'; '.join(context_parts)}"
            else:
                enhanced_query = current_message
            
            # Add memory context if requested
            if include_memory:
                relevant_memory = self.retrieve_relevant_memory(
                    current_message, user_id, conversation_id, k=3
                )
                if relevant_memory:
                    memory_context = []
                    for chunk, score in relevant_memory:
                        memory_context.append(f"[{score:.2f}] {chunk.content[:100]}...")
                    if memory_context:
                        enhanced_query += f" | Relevant memory: {'; '.join(memory_context)}"
                        context_metadata["memory_chunks"] = len(relevant_memory)
            
            # Add document context
            try:
                document_context = self.get_document_context_for_query(conversation_id, current_message)
                if document_context:
                    doc_context_parts = []
                    for doc in document_context[:3]:  # Limit to top 3 documents
                        if doc.summary:
                            doc_context_parts.append(f"Document '{doc.filename}': {doc.summary}")
                        else:
                            doc_context_parts.append(f"Document '{doc.filename}' is available (no summary)")
                    
                    if doc_context_parts:
                        # Add document context as a separate section for better AI understanding
                        document_section = f"\n\nAvailable Documents:\n" + "\n".join([f"- {doc}" for doc in doc_context_parts])
                        enhanced_query += document_section
                        context_metadata["documents_available"] = len(document_context)
                        context_metadata["document_context"] = True
            except Exception as e:
                logger.warning(f"Error adding document context: {e}")
            
            return enhanced_query, context_metadata
            
        except Exception as e:
            logger.error(f"Error building context-aware query: {e}")
            return current_message, {"conversation_id": conversation_id}
    
    def update_context_after_message(
        self, 
        conversation_id: str, 
        message: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> bool:
        """Update context after a new message is added."""
        try:
            # Don't store messages here - they are already stored by chat service
            # This function is only for updating context awareness, not for message storage
            
            # Clear cache to force refresh
            cache_key = f"{conversation_id}_{user_id}_True"
            if cache_key in self._context_cache:
                del self._context_cache[cache_key]
            
            # If this is a user message, check if we should store memory
            if message.get("role") == "user":
                # Get recent messages to decide if we should create a memory chunk
                if self.message_repo:
                    recent_messages = self.message_repo.get_messages(conversation_id, limit=10)
                    if len(recent_messages) >= self.memory_chunk_size:
                        # Store as memory chunk
                        message_dicts = [
                            {"role": msg.role, "content": msg.content, "created_at": msg.created_at}
                            for msg in recent_messages[-self.memory_chunk_size:]
                        ]
                        self.store_conversation_memory(conversation_id, message_dicts)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating context after message: {e}")
            return False
    
    def _extract_context_entities(self, messages: List[Message]) -> List[ContextEntity]:
        """Extract key entities from conversation messages."""
        try:
            entities = {}
            current_time = datetime.now()
            
            for message in messages:
                content = message.content
                if len(content) < 10:  # Skip very short messages
                    continue
                
                # Simple entity extraction (could be enhanced with NLP)
                words = content.split()
                for word in words:
                    # Clean word
                    clean_word = word.lower().strip('.,!?;:"')
                    if len(clean_word) < 3:
                        continue
                    
                    # Skip common words
                    if clean_word in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use']:
                        continue
                    
                    if clean_word in entities:
                        entities[clean_word].mention_count += 1
                        entities[clean_word].last_mentioned = message.created_at
                        entities[clean_word].importance_score += 0.1
                    else:
                        entities[clean_word] = ContextEntity(
                            text=clean_word,
                            entity_type="concept",
                            importance_score=1.0,
                            first_mentioned=message.created_at,
                            last_mentioned=message.created_at,
                            mention_count=1
                        )
            
            # Sort by importance and return top entities
            sorted_entities = sorted(entities.values(), key=lambda x: x.importance_score, reverse=True)
            return sorted_entities[:self.max_context_entities]
            
        except Exception as e:
            logger.error(f"Error extracting context entities: {e}")
            return []
    
    def _extract_topics(self, messages: List[Message]) -> List[str]:
        """Extract conversation topics."""
        try:
            topics = set()
            
            # Simple topic extraction based on keywords
            topic_keywords = {
                "programming": ["code", "programming", "python", "javascript", "algorithm", "function", "variable"],
                "ai": ["ai", "artificial intelligence", "machine learning", "neural network", "model"],
                "business": ["business", "strategy", "marketing", "sales", "revenue", "profit"],
                "science": ["science", "research", "experiment", "hypothesis", "theory"],
                "technology": ["technology", "software", "hardware", "system", "database", "api"],
                "education": ["learn", "teaching", "education", "course", "study", "knowledge"]
            }
            
            all_content = " ".join([msg.content.lower() for msg in messages])
            
            for topic, keywords in topic_keywords.items():
                if any(keyword in all_content for keyword in keywords):
                    topics.add(topic)
            
            return list(topics)
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []
    
    def _extract_user_preferences(self, messages: List[Message], user_id: Optional[str]) -> Dict[str, Any]:
        """Extract user preferences from conversation."""
        try:
            preferences = {}
            
            # Look for preference indicators in messages
            for message in messages:
                if message.role == "user":
                    content = message.content.lower()
                    
                    # Extract preferences based on patterns
                    if "i prefer" in content or "i like" in content:
                        # Simple preference extraction
                        if "detailed" in content or "comprehensive" in content:
                            preferences["detail_level"] = "detailed"
                        elif "brief" in content or "short" in content:
                            preferences["detail_level"] = "brief"
                    
                    if "technical" in content:
                        preferences["communication_style"] = "technical"
                    elif "simple" in content or "explain simply" in content:
                        preferences["communication_style"] = "simple"
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error extracting user preferences: {e}")
            return {}
    
    def _analyze_conversation_style(self, messages: List[Message]) -> str:
        """Analyze the style of conversation."""
        try:
            if not messages:
                return "casual"
            
            # Analyze message patterns
            avg_length = sum(len(msg.content) for msg in messages) / len(messages)
            question_count = sum(1 for msg in messages if "?" in msg.content)
            
            # Determine style based on patterns
            if avg_length > 200:
                return "detailed"
            elif question_count / len(messages) > 0.3:
                return "inquisitive"
            elif any("please" in msg.content.lower() or "thank you" in msg.content.lower() for msg in messages):
                return "formal"
            else:
                return "casual"
                
        except Exception as e:
            logger.error(f"Error analyzing conversation style: {e}")
            return "casual"
    
    def _create_conversation_summary(self, messages: List[Message]) -> str:
        """Create a summary of the conversation."""
        try:
            if not messages:
                return "Empty conversation"
            
            # Take key messages and create summary
            key_messages = messages[-5:]  # Last 5 messages
            summary_parts = []
            
            for msg in key_messages:
                role = msg.role
                content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                summary_parts.append(f"{role}: {content}")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error creating conversation summary: {e}")
            return "Error creating summary"
    
    def _create_memory_chunk_content(self, messages: List[Dict]) -> str:
        """Create content for a memory chunk."""
        try:
            content_parts = []
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                timestamp = msg.get("created_at", datetime.now())
                content_parts.append(f"{role.upper()} ({timestamp}): {content}")
            
            return "\n".join(content_parts)
            
        except Exception as e:
            logger.error(f"Error creating memory chunk content: {e}")
            return ""
    
    def _generate_chunk_id(self, conversation_id: str, start_index: int) -> str:
        """Generate a unique chunk ID."""
        return hashlib.md5(f"{conversation_id}_{start_index}".encode()).hexdigest()[:12]
    
    def _extract_topics_from_chunk(self, messages: List[Dict]) -> List[str]:
        """Extract topics from a chunk of messages."""
        # Simple implementation - could be enhanced
        return ["conversation_chunk"]
    
    def _extract_entities_from_chunk(self, messages: List[Dict]) -> List[str]:
        """Extract entities from a chunk of messages."""
        # Simple implementation - could be enhanced
        entities = set()
        for msg in messages:
            words = msg["content"].split()
            for word in words:
                if len(word) > 4 and word.isalpha():
                    entities.add(word.lower())
        return list(entities)[:10]  # Limit to 10 entities
    
    def _create_empty_context(self, conversation_id: str, user_id: Optional[str]) -> ContextSummary:
        """Create an empty context summary."""
        return ContextSummary(
            conversation_id=conversation_id,
            user_id=user_id,
            topics=[],
            key_entities=[],
            user_preferences={},
            conversation_style="casual",
            summary_text="No conversation history available",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    # Document Context Management Methods
    
    def get_conversation_documents(self, conversation_id: str) -> List[DocumentContext]:
        """Get all documents associated with a conversation."""
        try:
            if not self.document_repo:
                return []
            
            documents = self.document_repo.get_conversation_documents(conversation_id)
            
            return [
                DocumentContext(
                    document_id=doc.id,
                    filename=doc.filename,
                    file_type=doc.file_type,
                    summary=doc.summary_text,
                    upload_time=doc.upload_timestamp,
                    relevance_score=0.0,
                    last_accessed=doc.updated_at,
                    access_count=0,
                    metadata={
                        "file_size": doc.file_size,
                        "processing_status": doc.processing_status,
                        "file_path": doc.file_path,
                        "summary_type": doc.summary_type
                    }
                )
                for doc in documents
            ]
            
        except Exception as e:
            logger.error(f"Error getting conversation documents: {e}")
            return []
    
    def update_document_relevance(self, document_id: str, query: str) -> float:
        """Update document relevance based on query similarity."""
        try:
            if not self.document_repo:
                return 0.0
            
            document = self.document_repo.get_document(document_id)
            if not document:
                return 0.0
            
            # Simple relevance scoring based on filename and summary
            relevance_score = 0.0
            query_lower = query.lower()
            
            # Check filename similarity
            if query_lower in document.filename.lower():
                relevance_score += 0.3
            
            # Check summary similarity
            if document.summary_text and query_lower in document.summary_text.lower():
                relevance_score += 0.7
            
            # Check for general document-related keywords
            document_keywords = ["document", "file", "paper", "report", "text", "content", "about", "summarize", "summary", "what", "this"]
            if any(keyword in query_lower for keyword in document_keywords):
                relevance_score += 0.5  # Base relevance for document-related queries
            
            # Update access count and last accessed time
            self.document_repo.update_document(document_id, {
                "updated_at": datetime.now()
            })
            
            return min(relevance_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error updating document relevance: {e}")
            return 0.0
    
    def get_document_context_for_query(self, conversation_id: str, query: str) -> List[DocumentContext]:
        """Get relevant documents for a specific query in a conversation."""
        try:
            documents = self.get_conversation_documents(conversation_id)
            logger.info(f"Found {len(documents)} documents for conversation {conversation_id}")
            
            if not documents:
                logger.info(f"No documents found for conversation {conversation_id}")
                return []
            
            # Calculate relevance scores for each document
            for doc in documents:
                doc.relevance_score = self.update_document_relevance(doc.document_id, query)
                doc.access_count += 1
                doc.last_accessed = datetime.now()
            
            # Sort by relevance score and return top documents
            relevant_docs = sorted(documents, key=lambda x: x.relevance_score, reverse=True)
            
            # For document-related queries, be more inclusive
            # Return all documents if any have relevance > 0, otherwise return all documents
            if any(doc.relevance_score > 0 for doc in relevant_docs):
                return [doc for doc in relevant_docs if doc.relevance_score > 0]
            else:
                # If no specific relevance, return all documents for general queries
                return relevant_docs
            
        except Exception as e:
            logger.error(f"Error getting document context for query: {e}")
            return []
    
    def get_document_summary_context(self, conversation_id: str) -> str:
        """Get a summary of all documents in the conversation for context."""
        try:
            documents = self.get_conversation_documents(conversation_id)
            
            if not documents:
                return ""
            
            context_parts = []
            for doc in documents:
                if doc.summary:
                    context_parts.append(f"Document: {doc.filename}\nSummary: {doc.summary}")
                else:
                    context_parts.append(f"Document: {doc.filename} (no summary available)")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting document summary context: {e}")
            return ""
    
    def cleanup_conversation_documents(self, conversation_id: str) -> int:
        """Clean up all documents for a conversation."""
        try:
            if not self.document_repo:
                return 0
            
            return self.document_repo.cleanup_conversation_documents(conversation_id)
            
        except Exception as e:
            logger.error(f"Error cleaning up conversation documents: {e}")
            return 0
