# Conversation and Document Awareness System

## Overview

The AI Assistant implements a sophisticated **Context Awareness System** that enables the assistant to maintain context across conversations, remember user preferences, and provide personalized responses. This system builds upon the existing RAG (Retrieval-Augmented Generation) infrastructure to create a comprehensive memory and context management solution.

## Core Architecture

### System Components

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

### Key Services

1. **ContextAwarenessService** (`backend/app/services/context_awareness.py`)
2. **ChatService** (`backend/app/services/chat.py`) 
3. **VectorStore** (`backend/app/services/rag/vector_store.py`)
4. **Document Management** (`backend/app/services/document_manager.py`)

## How Conversation Awareness Works

### 1. Context Detection and Enhancement

When a user sends a message, the system:

```python
# In ChatService.generate_response()
if enable_context_awareness and conversation_id:
    # Get document context for the conversation
    document_context = self.context_service.get_document_context_for_query(
        conversation_id, message
    )
    
    # Build context-aware query
    enhanced_message, context_metadata = self.context_service.build_context_aware_query(
        current_message=message,
        conversation_id=conversation_id,
        user_id=user_id,
        include_memory=include_memory
    )
```

### 2. Context Building Process

The `build_context_aware_query` method:

1. **Retrieves conversation history** (last 5-10 messages)
2. **Extracts key entities** and topics from the conversation
3. **Applies user preferences** (communication style, detail level)
4. **Includes relevant memory chunks** from past conversations
5. **Enhances the query** with contextual information

```python
def build_context_aware_query(
    self, 
    current_message: str, 
    conversation_id: str, 
    user_id: Optional[str] = None,
    include_memory: bool = True
) -> Tuple[str, Dict[str, Any]]:
    """Build a context-aware query by including conversation history and user preferences."""
    
    # Get conversation context
    context = self.get_conversation_context(conversation_id, user_id, include_memory)
    
    # Build enhanced query
    enhanced_query = current_message
    
    # Add conversation context
    if context.topics:
        enhanced_query += f" | Topics: {', '.join(context.topics)}"
    
    # Add key entities
    if context.key_entities:
        entity_names = [entity.text for entity in context.key_entities[:5]]
        enhanced_query += f" | Entities: {', '.join(entity_names)}"
    
    # Add user preferences
    if context.user_preferences:
        enhanced_query += f" | User style: {context.conversation_style}"
    
    return enhanced_query, context_metadata
```

### 3. Memory Management

#### Long-term Memory Storage

Conversations are automatically chunked and stored as searchable memory:

```python
def store_conversation_memory(
    self, 
    conversation_id: str, 
    messages: List[Dict],
    chunk_size: Optional[int] = None
) -> bool:
    """Store conversation as memory chunks for long-term retrieval."""
    
    # Create memory chunks (every 5 messages by default)
    for i in range(0, len(messages), chunk_size):
        chunk_messages = messages[i:i + chunk_size]
        chunk_content = self._create_memory_chunk_content(chunk_messages)
        
        # Store in vector database with metadata
        chunk = MemoryChunk(
            content=chunk_content,
            metadata={
                "conversation_id": conversation_id,
                "message_count": len(chunk_messages),
                "topics": self._extract_topics_from_chunk(chunk_messages),
                "entities": self._extract_entities_from_chunk(chunk_messages)
            }
        )
```

#### Memory Retrieval

When building context, the system retrieves relevant memory chunks:

```python
def retrieve_relevant_memory(
    self, 
    query: str, 
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    k: int = 3
) -> List[Tuple[MemoryChunk, float]]:
    """Retrieve relevant memory chunks using semantic search."""
    
    # Use vector similarity search
    relevant_chunks = self.vector_store.similarity_search_with_score(
        query, k=k, filter={"user_id": user_id}
    )
    
    return relevant_chunks
```

### 4. Entity and Topic Extraction

The system automatically identifies and tracks:

- **Key Entities**: Important concepts, people, places, technical terms
- **Topics**: Main conversation themes and subjects
- **User Preferences**: Communication style, detail level, expertise areas

```python
def _extract_context_entities(self, messages: List[Message]) -> List[ContextEntity]:
    """Extract key entities from conversation messages."""
    
    entities = {}
    for message in messages:
        # Simple entity extraction (enhanced with NLP)
        words = content.split()
        for word in words:
            clean_word = word.lower().strip('.,!?;:"')
            
            if clean_word in entities:
                entities[clean_word].mention_count += 1
                entities[clean_word].importance_score += 0.1
            else:
                entities[clean_word] = ContextEntity(
                    text=clean_word,
                    entity_type="concept",
                    importance_score=1.0,
                    mention_count=1
                )
    
    # Return top entities by importance
    return sorted(entities.values(), key=lambda x: x.importance_score, reverse=True)[:50]
```

## How Document Awareness Works

### 1. Document Storage and Association

Documents are uploaded and associated with specific conversations:

```python
# Document upload process
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None)
):
    # Create conversation-specific vector store
    conversation_vector_store = VectorStore(conversation_id=conversation_id)
    
    # Process document with RAG
    conversation_rag_retriever = RAGRetriever(vector_store=conversation_vector_store)
    result = conversation_rag_retriever.process_document(file_path)
    
    # Store document metadata
    chat_document = ChatDocument(
        filename=file.filename,
        conversation_id=conversation_id,
        user_id=user_id,
        file_path=str(file_path)
    )
```

### 2. Conversation-Specific Document Retrieval

Each conversation has its own vector store collection:

```python
class VectorStore:
    def __init__(self, conversation_id: str = None):
        # Create conversation-specific collection name
        if conversation_id:
            self.collection_name = f"documents_conv_{conversation_id}"
        else:
            self.collection_name = "documents"
        
        # Initialize with conversation-specific collection
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )
```

### 3. Document Context Integration

When processing user queries, the system:

1. **Retrieves relevant documents** for the conversation
2. **Calculates relevance scores** based on query similarity
3. **Extracts relevant content** using RAG retrieval
4. **Integrates document context** into the prompt

```python
def _create_document_aware_prompt(
    self, 
    user_message: str, 
    document_context: List[DocumentContext],
    conversation_id: str = None
) -> str:
    """Create prompt that includes document context."""
    
    # Initialize conversation-specific RAG retriever
    conversation_vector_store = VectorStore(conversation_id=conversation_id)
    rag_retriever = RAGRetriever(vector_store=conversation_vector_store)
    
    # Build document context text
    documents_text = []
    for doc in document_context:
        if doc.summary:
            documents_text.append(f"Document: {doc.filename}\nSummary: {doc.summary}")
        else:
            # Retrieve relevant content using RAG
            relevant_chunks = rag_retriever.retrieve_relevant_documents(
                user_message, k=30
            )
            
            # Filter chunks for this specific document
            document_chunks = [
                chunk for chunk, score in relevant_chunks
                if doc.metadata['file_path'] in chunk.metadata.get('source', '')
            ]
            
            # Combine top chunks
            content_parts = []
            for chunk_doc, score in document_chunks[:5]:
                if score > 0.05:
                    content_parts.append(chunk_doc.page_content.strip())
            
            if content_parts:
                combined_content = "\n\n".join(content_parts)
                documents_text.append(f"Document: {doc.filename}\nContent:\n{combined_content}")
    
    # Create enhanced prompt
    if documents_text:
        document_context_text = "\n\n".join(documents_text)
        return f"""You are an AI assistant with access to the following documents in this conversation:

{document_context_text}

User Question: {user_message}

Please answer the user's question using information from the documents when relevant, and cite the source document when you do so."""
    
    return user_message
```

### 4. Document Relevance Scoring

The system calculates relevance scores for documents based on:

- **Filename similarity** with the query
- **Summary content** matching
- **General document-related keywords**
- **Access patterns** and usage history

```python
def update_document_relevance(self, document_id: str, query: str) -> float:
    """Update document relevance based on query similarity."""
    
    relevance_score = 0.0
    query_lower = query.lower()
    
    # Check filename similarity
    if query_lower in document.filename.lower():
        relevance_score += 0.3
    
    # Check summary similarity
    if document.summary_text and query_lower in document.summary_text.lower():
        relevance_score += 0.7
    
    # Check for document-related keywords
    document_keywords = ["document", "file", "paper", "report", "text", "content"]
    if any(keyword in query_lower for keyword in document_keywords):
        relevance_score += 0.5
    
    return min(relevance_score, 1.0)
```

## Context Strategies

The system supports multiple context strategies:

### 1. Auto Strategy (Default)
- Automatically determines the best approach based on query type
- Combines conversation context, memory, and document context as needed

### 2. Conversation Only
- Uses only the current conversation history
- No cross-conversation memory retrieval

### 3. Memory Only
- Uses only long-term memory from past conversations
- Ignores current conversation context

### 4. Hybrid
- Combines both conversation and memory context
- Most comprehensive but potentially slower

## User Personalization

### Learning User Preferences

The system learns and applies user preferences:

```python
def _extract_user_preferences(self, messages: List[Message], user_id: Optional[str]) -> Dict[str, Any]:
    """Extract user preferences from conversation patterns."""
    
    preferences = {}
    
    # Analyze communication style
    technical_indicators = ["algorithm", "implementation", "architecture", "optimization"]
    casual_indicators = ["cool", "awesome", "thanks", "please"]
    
    technical_count = sum(1 for msg in messages 
                         if any(indicator in msg.content.lower() 
                               for indicator in technical_indicators))
    
    if technical_count > len(messages) * 0.3:
        preferences["communication_style"] = "technical"
    else:
        preferences["communication_style"] = "casual"
    
    # Determine detail level preference
    if any("explain" in msg.content.lower() or "detail" in msg.content.lower() 
           for msg in messages):
        preferences["detail_level"] = "detailed"
    else:
        preferences["detail_level"] = "brief"
    
    return preferences
```

### Applying User Preferences

User preferences are applied to enhance responses:

```python
# In context building
if context.user_preferences:
    if context.user_preferences.get("communication_style") == "technical":
        enhanced_query += " | Provide technical details and implementation specifics"
    elif context.user_preferences.get("detail_level") == "detailed":
        enhanced_query += " | Provide comprehensive explanations with examples"
```

## Performance Optimizations

### 1. Caching
- Context summaries are cached for performance
- User preferences are cached across requests
- Memory chunks are cached in memory

### 2. Limits and Thresholds
- Maximum 50 entities tracked per conversation
- Only last 20 messages processed for entity extraction
- Memory chunks limited to 5 messages each
- Document content limited to 2000 characters per document

### 3. Efficient Retrieval
- Vector similarity search with configurable k values
- Database queries optimized with proper indexing
- Async processing for non-blocking operations

## API Usage

### Enable Context Awareness

```python
# Chat request with context awareness
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

### Get Context Information

```python
# Get conversation context
GET /api/v1/chat/context/{conversation_id}?user_id=user_456

# Response includes:
{
    "conversation_id": "conv_123",
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
    }
}
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

## Benefits

### 1. Improved Conversational Flow
- Follow-up questions work naturally
- Context is maintained across messages
- References to previous topics are understood

### 2. Personalized Responses
- Adapts to user communication style
- Remembers user preferences and expertise
- Provides appropriate detail level

### 3. Document-Aware Conversations
- Documents are automatically considered in responses
- Relevant content is retrieved and integrated
- Source citations are provided when using document content

### 4. Long-term Memory
- Past conversations inform current responses
- User patterns and preferences are learned
- Cross-conversation context is maintained

## Example Scenarios

### Scenario 1: Technical Discussion with Context

```
User: "What is attention in neural networks?"
Assistant: [Provides detailed explanation with RAG context from documents]

User: "How does it relate to transformers?"
Assistant: [Successfully retrieves relevant documents and provides context-aware answer about attention mechanisms in transformers]
```

### Scenario 2: Document Analysis with Follow-up

```
User: "What are the main points in the research paper?"
Assistant: [Provides summary using document content]

User: "Can you elaborate on the methodology section?"
Assistant: [Retrieves specific methodology content from the same document and provides detailed explanation]
```

### Scenario 3: Cross-Conversation Memory

```
User (in new conversation): "Remember when we discussed the transformer architecture?"
Assistant: [Retrieves relevant memory chunks from past conversations and provides context-aware response]
```

## Troubleshooting

### Common Issues

1. **Context not being applied**: Check `enable_context_awareness` is true and `conversation_id` is provided
2. **Memory not retrieved**: Verify `include_memory` is enabled and vector store has memory chunks
3. **Performance issues**: Reduce `max_context_entities` or `memory_chunk_size` settings
4. **Document context missing**: Ensure documents are uploaded to the correct conversation

### Debug Information

Enable debug logging to troubleshoot:

```python
import logging
logging.getLogger("backend.app.services.context_awareness").setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Multi-modal Context**: Support for images, audio, and other media types
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

The Conversation and Document Awareness system transforms the AI assistant from a stateless tool into an intelligent, personalized conversational partner. By maintaining context across conversations, learning user preferences, and providing semantic memory retrieval, it creates a more natural and effective user experience.

The system is designed to be scalable, performant, and privacy-conscious, providing powerful context management capabilities while maintaining user control and data security.
