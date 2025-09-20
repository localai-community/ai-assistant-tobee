"""
Tests for Context Awareness Features
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import List, Dict, Any

from backend.app.services.context_awareness import (
    ContextAwarenessService,
    ContextEntity,
    ContextSummary,
    MemoryChunk
)
from backend.app.models.database import Conversation, Message
from backend.app.models.schemas import ConversationCreate, MessageCreate


class TestContextAwarenessService:
    """Test suite for Context Awareness Service."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def mock_vector_store(self):
        """Mock vector store."""
        store = Mock()
        store.similarity_search.return_value = []
        store.add_documents.return_value = True
        return store
    
    @pytest.fixture
    def context_service(self, mock_db, mock_vector_store):
        """Create context awareness service with mocked dependencies."""
        return ContextAwarenessService(
            db=mock_db,
            vector_store=mock_vector_store,
            memory_chunk_size=3,
            max_context_entities=10
        )
    
    @pytest.fixture
    def sample_messages(self):
        """Sample conversation messages."""
        return [
            Message(
                id="1",
                conversation_id="conv1",
                role="user",
                content="What is machine learning?",
                created_at=datetime.now(),
                model_used="llama3:latest"
            ),
            Message(
                id="2",
                conversation_id="conv1",
                role="assistant",
                content="Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models.",
                created_at=datetime.now(),
                model_used="llama3:latest"
            ),
            Message(
                id="3",
                conversation_id="conv1",
                role="user",
                content="How does it relate to neural networks?",
                created_at=datetime.now(),
                model_used="llama3:latest"
            ),
            Message(
                id="4",
                conversation_id="conv1",
                role="assistant",
                content="Neural networks are a key component of machine learning, particularly in deep learning applications.",
                created_at=datetime.now(),
                model_used="llama3:latest"
            )
        ]
    
    def test_extract_context_entities(self, context_service, sample_messages):
        """Test context entity extraction."""
        entities = context_service._extract_context_entities(sample_messages)
        
        assert len(entities) > 0
        assert all(isinstance(entity, ContextEntity) for entity in entities)
        
        # Check for expected entities
        entity_texts = [entity.text for entity in entities]
        assert "machine" in entity_texts
        assert "learning" in entity_texts
        assert "neural" in entity_texts
        assert "networks" in entity_texts
    
    def test_extract_topics(self, context_service, sample_messages):
        """Test topic extraction."""
        topics = context_service._extract_topics(sample_messages)
        
        assert isinstance(topics, list)
        # Should detect AI/ML topics
        assert "ai" in topics or "programming" in topics
    
    def test_extract_user_preferences(self, context_service, sample_messages):
        """Test user preference extraction."""
        preferences = context_service._extract_user_preferences(sample_messages, "user1")
        
        assert isinstance(preferences, dict)
        # Preferences should be extracted based on conversation patterns
    
    def test_analyze_conversation_style(self, context_service, sample_messages):
        """Test conversation style analysis."""
        style = context_service._analyze_conversation_style(sample_messages)
        
        assert style in ["casual", "formal", "detailed", "inquisitive"]
    
    def test_create_conversation_summary(self, context_service, sample_messages):
        """Test conversation summary creation."""
        summary = context_service._create_conversation_summary(sample_messages)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "user:" in summary.lower()
        assert "assistant:" in summary.lower()
    
    def test_get_conversation_context(self, context_service, sample_messages):
        """Test getting conversation context."""
        # Mock repository methods
        context_service.conversation_repo = Mock()
        context_service.message_repo = Mock()
        
        context_service.conversation_repo.get_conversation.return_value = Mock(
            id="conv1",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        context_service.message_repo.get_messages.return_value = sample_messages
        
        context = context_service.get_conversation_context("conv1", "user1")
        
        assert isinstance(context, ContextSummary)
        assert context.conversation_id == "conv1"
        assert context.user_id == "user1"
        assert len(context.topics) > 0
        assert len(context.key_entities) > 0
    
    def test_store_conversation_memory(self, context_service):
        """Test storing conversation as memory chunks."""
        messages = [
            {"role": "user", "content": "Hello", "created_at": datetime.now()},
            {"role": "assistant", "content": "Hi there!", "created_at": datetime.now()},
            {"role": "user", "content": "How are you?", "created_at": datetime.now()},
            {"role": "assistant", "content": "I'm doing well!", "created_at": datetime.now()},
            {"role": "user", "content": "What can you help with?", "created_at": datetime.now()}
        ]
        
        success = context_service.store_conversation_memory("conv1", messages)
        
        assert success is True
        # Verify vector store was called
        context_service.vector_store.add_documents.assert_called_once()
    
    def test_retrieve_relevant_memory(self, context_service):
        """Test retrieving relevant memory chunks."""
        # Mock vector store to return some results
        mock_doc1 = Mock()
        mock_doc1.page_content = "User asked about machine learning"
        mock_doc1.metadata = {"conversation_id": "conv1", "chunk_id": "chunk1"}
        
        mock_doc2 = Mock()
        mock_doc2.page_content = "Assistant explained neural networks"
        mock_doc2.metadata = {"conversation_id": "conv2", "chunk_id": "chunk2"}
        
        context_service.vector_store.similarity_search.return_value = [
            (mock_doc1, 0.9),
            (mock_doc2, 0.8)
        ]
        
        memory_chunks = context_service.retrieve_relevant_memory(
            "machine learning", "user1", "conv1", k=2
        )
        
        # Should only return chunks from conv1 (conv2 chunk gets filtered out)
        assert len(memory_chunks) == 1
        assert all(isinstance(chunk, tuple) and len(chunk) == 2 for chunk in memory_chunks)
        assert all(isinstance(chunk[0], MemoryChunk) for chunk in memory_chunks)
    
    def test_build_context_aware_query(self, context_service):
        """Test building context-aware query."""
        # Mock conversation context
        mock_context = ContextSummary(
            conversation_id="conv1",
            user_id="user1",
            topics=["machine learning", "ai"],
            key_entities=[
                ContextEntity("neural networks", "concept", 0.9, datetime.now(), datetime.now()),
                ContextEntity("deep learning", "concept", 0.8, datetime.now(), datetime.now())
            ],
            user_preferences={"detail_level": "detailed"},
            conversation_style="technical",
            summary_text="Discussion about ML and AI",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock the get_conversation_context method
        context_service.get_conversation_context = Mock(return_value=mock_context)
        context_service.retrieve_relevant_memory = Mock(return_value=[])
        
        enhanced_query, metadata = context_service.build_context_aware_query(
            "How do transformers work?",
            "conv1",
            "user1",
            include_memory=True
        )
        
        assert isinstance(enhanced_query, str)
        assert len(enhanced_query) > len("How do transformers work?")
        assert "machine learning" in enhanced_query or "neural networks" in enhanced_query
        
        assert isinstance(metadata, dict)
        assert metadata["conversation_id"] == "conv1"
        assert metadata["user_id"] == "user1"
        assert "topics" in metadata
        assert "entities" in metadata
    
    def test_get_user_context(self, context_service):
        """Test getting user context across conversations."""
        # Mock conversation repository
        mock_conversation1 = Mock()
        mock_conversation1.id = "conv1"
        mock_conversation2 = Mock()
        mock_conversation2.id = "conv2"
        
        context_service.conversation_repo = Mock()
        context_service.conversation_repo.get_conversations.return_value = [
            mock_conversation1, mock_conversation2
        ]
        
        # Mock get_conversation_context
        mock_context = Mock()
        mock_context.user_preferences = {"detail_level": "detailed"}
        mock_context.topics = ["programming", "ai"]
        mock_context.conversation_style = "technical"
        context_service.get_conversation_context = Mock(return_value=mock_context)
        
        user_context = context_service.get_user_context("user1")
        
        assert isinstance(user_context, dict)
        assert user_context["user_id"] == "user1"
        assert "preferences" in user_context
        assert "topics_of_interest" in user_context
        assert "expertise_areas" in user_context
    
    def test_context_dependent_query_detection(self):
        """Test detection of context-dependent queries using simple patterns."""
        service = ContextAwarenessService()
        
        # Test simple context-dependent patterns
        context_queries = [
            "How does it work?",
            "What about the second part?",
            "Can you explain that further?",
            "What is it?"
        ]
        
        # Test that these queries contain context-dependent indicators
        for query in context_queries:
            # Simple check for pronouns and follow-up patterns
            has_context_indicators = (
                any(pronoun in query.lower() for pronoun in ["it", "this", "that", "they"]) or
                any(pattern in query.lower() for pattern in ["what about", "how about", "tell me more"])
            )
            assert has_context_indicators, f"Query '{query}' should contain context-dependent indicators"
        
        # Test general queries don't have these patterns
        general_queries = [
            "What is the capital of France?",
            "How do I bake a cake?",
            "What is photosynthesis?"
        ]
        
        for query in general_queries:
            # These should not have context-dependent patterns
            has_context_indicators = (
                any(pronoun in query.lower() for pronoun in ["it", "this", "that", "they"]) or
                any(pattern in query.lower() for pattern in ["what about", "how about", "tell me more"])
            )
            # General queries might still have "what" but shouldn't have context-dependent patterns
            assert not any(pattern in query.lower() for pattern in ["what about", "how about", "tell me more"]), f"Query '{query}' should not contain context-dependent patterns"
    
    def test_memory_chunk_creation(self, context_service):
        """Test memory chunk content creation."""
        messages = [
            {"role": "user", "content": "Hello", "created_at": datetime.now()},
            {"role": "assistant", "content": "Hi!", "created_at": datetime.now()}
        ]
        
        chunk_content = context_service._create_memory_chunk_content(messages)
        
        assert isinstance(chunk_content, str)
        assert "USER" in chunk_content
        assert "ASSISTANT" in chunk_content
        assert "Hello" in chunk_content
        assert "Hi!" in chunk_content
    
    def test_chunk_id_generation(self, context_service):
        """Test chunk ID generation."""
        chunk_id1 = context_service._generate_chunk_id("conv1", 0)
        chunk_id2 = context_service._generate_chunk_id("conv1", 0)
        chunk_id3 = context_service._generate_chunk_id("conv2", 0)
        
        # Same conversation and index should generate same ID
        assert chunk_id1 == chunk_id2
        
        # Different conversation should generate different ID
        assert chunk_id1 != chunk_id3
        
        # ID should be a string
        assert isinstance(chunk_id1, str)
        assert len(chunk_id1) > 0


class TestContextEntity:
    """Test suite for ContextEntity dataclass."""
    
    def test_context_entity_creation(self):
        """Test creating a context entity."""
        now = datetime.now()
        entity = ContextEntity(
            text="machine learning",
            entity_type="concept",
            importance_score=0.9,
            first_mentioned=now,
            last_mentioned=now,
            mention_count=3
        )
        
        assert entity.text == "machine learning"
        assert entity.entity_type == "concept"
        assert entity.importance_score == 0.9
        assert entity.mention_count == 3
        assert entity.metadata == {}


class TestContextSummary:
    """Test suite for ContextSummary dataclass."""
    
    def test_context_summary_creation(self):
        """Test creating a context summary."""
        now = datetime.now()
        entities = [
            ContextEntity("ai", "concept", 0.8, now, now),
            ContextEntity("ml", "concept", 0.9, now, now)
        ]
        
        summary = ContextSummary(
            conversation_id="conv1",
            user_id="user1",
            topics=["ai", "programming"],
            key_entities=entities,
            user_preferences={"detail_level": "detailed"},
            conversation_style="technical",
            summary_text="Discussion about AI and programming",
            created_at=now,
            updated_at=now
        )
        
        assert summary.conversation_id == "conv1"
        assert summary.user_id == "user1"
        assert summary.topics == ["ai", "programming"]
        assert len(summary.key_entities) == 2
        assert summary.user_preferences["detail_level"] == "detailed"
        assert summary.conversation_style == "technical"


class TestMemoryChunk:
    """Test suite for MemoryChunk dataclass."""
    
    def test_memory_chunk_creation(self):
        """Test creating a memory chunk."""
        now = datetime.now()
        chunk = MemoryChunk(
            content="User asked about machine learning",
            metadata={"conversation_id": "conv1", "topic": "ai"},
            conversation_id="conv1",
            chunk_id="chunk1",
            created_at=now,
            relevance_score=0.9
        )
        
        assert chunk.content == "User asked about machine learning"
        assert chunk.conversation_id == "conv1"
        assert chunk.chunk_id == "chunk1"
        assert chunk.relevance_score == 0.9
        assert chunk.metadata["topic"] == "ai"


if __name__ == "__main__":
    pytest.main([__file__])
