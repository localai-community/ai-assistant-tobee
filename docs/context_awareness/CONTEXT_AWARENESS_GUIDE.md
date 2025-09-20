# Context Awareness Guide

## Overview

The Context Awareness system provides advanced conversational AI capabilities that enable the assistant to maintain context across conversations, remember user preferences, and provide personalized responses. This system builds upon the existing RAG infrastructure to create a comprehensive memory and context management solution.

## Key Features

### 🧠 **Long-term Memory**
- **Conversation Memory**: Automatically stores conversation chunks as searchable memory
- **Cross-conversation Context**: Retrieves relevant information from past conversations
- **Semantic Retrieval**: Uses vector similarity search to find relevant past interactions

### 👤 **User Personalization**
- **User Preferences**: Learns and applies user communication preferences
- **Expertise Areas**: Identifies user's areas of interest and expertise
- **Communication Style**: Adapts responses based on user's preferred style (technical, casual, detailed)

### 🎯 **Smart Context Detection**
- **Context-dependent Query Detection**: Automatically determines if a query needs conversation context
- **Entity Extraction**: Identifies and tracks key entities across conversations
- **Topic Analysis**: Extracts and maintains conversation topics

### 🔄 **Multiple Context Strategies**
- **Auto**: Automatically selects the best strategy based on query type
- **Conversation Only**: Uses only current conversation context
- **Memory Only**: Uses only long-term memory from past conversations
- **Hybrid**: Combines both conversation and memory context

## Architecture

### Core Components

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   ContextAwareness  │    │    Vector Store      │    │   Database Layer    │
│      Service        │◄──►│   (Memory Storage)   │◄──►│  (Conversations)    │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Context Builder   │    │   Memory Chunks      │    │   User Profiles     │
│   & Query Enhancer  │    │   (RAG Storage)      │    │   & Preferences     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

### Data Flow

1. **User Query** → **Context Detection** → **Memory Retrieval** → **Query Enhancement**
2. **Response Generation** → **Context Update** → **Memory Storage** → **User Profile Update**

## Usage

### Backend API

#### Chat with Context Awareness

```python
# Enhanced chat request with context awareness
POST /api/v1/chat/
{
    "message": "How does this relate to what we discussed earlier?",
    "conversation_id": "conv_123",
    "user_id": "user_456",
    "enable_context_awareness": true,
    "include_memory": true,
    "context_strategy": "auto"
}
```

#### Get Conversation Context

```python
# Get detailed context information
GET /api/v1/chat/context/{conversation_id}?user_id=user_456

# Response includes:
{
    "conversation_id": "conv_123",
    "user_id": "user_456",
    "topics": ["machine learning", "neural networks"],
    "entities": [
        {
            "text": "transformer",
            "type": "concept",
            "importance": 0.9,
            "mentions": 5
        }
    ],
    "user_preferences": {
        "detail_level": "detailed",
        "communication_style": "technical"
    },
    "conversation_style": "inquisitive"
}
```

#### Get User Context

```python
# Get user context across all conversations
GET /api/v1/chat/context/user/{user_id}

# Response includes:
{
    "user_id": "user_456",
    "total_conversations": 15,
    "preferences": {
        "detail_level": "detailed",
        "communication_style": "technical"
    },
    "topics_of_interest": ["ai", "programming", "science"],
    "expertise_areas": ["technical", "research"],
    "communication_style": "technical"
}
```

### Frontend Integration

#### Context Awareness Controls

The frontend provides intuitive controls for context awareness:

```python
# Sidebar controls
st.checkbox("🧠 Enable Context Awareness")
st.text_input("👤 User ID (Optional)")
st.selectbox("🎯 Context Strategy", ["auto", "conversation_only", "memory_only", "hybrid"])
st.checkbox("💾 Include Long-term Memory")
```

#### Context Information Display

Context information is displayed in expandable sections for each assistant response:

```python
with st.expander("🧠 Context Information"):
    st.write("**Strategy:** auto")
    st.write("**Key Entities:** transformer, attention, neural network")
    st.write("**Topics:** machine learning, deep learning")
    st.write("**Memory Chunks Used:** 3")
    st.write("**User Preferences Applied:** {detail_level: 'detailed'}")
```

## Configuration

### Environment Variables

```bash
# Context awareness settings
CONTEXT_AWARENESS_ENABLED=true
MEMORY_CHUNK_SIZE=5
MAX_CONTEXT_ENTITIES=50
CONTEXT_DECAY_DAYS=30
```

### Service Configuration

```python
context_service = ContextAwarenessService(
    db=db_session,
    vector_store=vector_store,
    memory_chunk_size=5,        # Messages per memory chunk
    max_context_entities=50,    # Maximum entities to track
    context_decay_days=30       # How long to keep context
)
```

## Advanced Features

### Context-Dependent Query Detection

The system automatically detects when queries require conversation context:

**Context-dependent queries:**
- "How does it work?" (refers to previous topic)
- "What about the second part?" (references previous content)
- "Can you explain that further?" (follow-up question)

**General knowledge queries:**
- "What is the capital of France?" (standalone fact)
- "How do I bake a cake?" (general instruction)
- "What is photosynthesis?" (basic definition)

### Memory Chunking Strategy

Conversations are automatically chunked into searchable memory:

1. **Size-based chunking**: Every 5 messages (configurable)
2. **Topic-based chunking**: When conversation topic changes
3. **Metadata enrichment**: Each chunk includes conversation ID, topics, entities
4. **Vector storage**: Chunks stored in vector database for semantic search

### User Preference Learning

The system learns user preferences through conversation analysis:

- **Detail level**: Detailed vs. brief explanations
- **Communication style**: Technical vs. casual language
- **Expertise areas**: Technical, business, research, etc.
- **Topic interests**: Frequently discussed subjects

## Performance Considerations

### Optimization Features

1. **Caching**: Context summaries are cached for performance
2. **Entity Limits**: Maximum 50 entities tracked per conversation
3. **Message Limits**: Only last 20 messages processed for entity extraction
4. **Memory Limits**: Database queries limited to recent conversations

### Scalability

- **Vector Database**: Handles millions of memory chunks
- **Database Indexing**: Optimized queries for conversation retrieval
- **Async Processing**: Non-blocking context updates
- **Batch Operations**: Efficient memory storage and retrieval

## Testing

### Unit Tests

```bash
# Run context awareness tests
cd backend
python -m pytest tests/context_awareness/ -v
```

### Integration Tests

```bash
# Test full context awareness workflow
python -m pytest tests/integration/test_context_awareness_integration.py -v
```

### Manual Testing

1. **Start a conversation** with context awareness enabled
2. **Ask follow-up questions** like "How does this work?" or "What about that?"
3. **Check context information** in the expandable sections
4. **Verify memory storage** by asking about past conversations
5. **Test user preferences** by expressing communication style preferences

## Troubleshooting

### Common Issues

#### Context Not Being Applied

**Symptoms**: Responses don't seem to use conversation context

**Solutions**:
1. Check that `enable_context_awareness` is `true`
2. Verify conversation_id is provided
3. Ensure database connection is working
4. Check vector store is initialized

#### Memory Not Being Retrieved

**Symptoms**: Past conversation information not available

**Solutions**:
1. Verify `include_memory` is enabled
2. Check vector store has memory chunks stored
3. Ensure user_id is consistent across conversations
4. Verify memory chunking is working

#### Performance Issues

**Symptoms**: Slow response times with context awareness

**Solutions**:
1. Reduce `max_context_entities` setting
2. Decrease `memory_chunk_size`
3. Enable context caching
4. Optimize database queries

### Debug Information

Enable debug logging to troubleshoot context awareness:

```python
import logging
logging.getLogger("backend.app.services.context_awareness").setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Multi-modal Context**: Support for images, documents, and other media
2. **Temporal Context**: Time-aware context that considers when conversations occurred
3. **Collaborative Context**: Shared context across multiple users
4. **Context Summarization**: Automatic summarization of long conversations
5. **Privacy Controls**: Granular control over what context is stored and shared

### Integration Opportunities

1. **External Knowledge Bases**: Integration with external knowledge graphs
2. **User Feedback**: Learning from user corrections and preferences
3. **Context Analytics**: Insights into conversation patterns and user behavior
4. **API Extensions**: RESTful API for context management

## Conclusion

The Context Awareness system transforms the AI assistant from a stateless tool into an intelligent, personalized conversational partner. By maintaining context across conversations, learning user preferences, and providing semantic memory retrieval, it creates a more natural and effective user experience.

The system is designed to be scalable, performant, and privacy-conscious, providing powerful context management capabilities while maintaining user control and data security.
