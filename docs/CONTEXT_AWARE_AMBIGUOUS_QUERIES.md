# Handling Ambiguous Follow-up Questions in RAG Systems

## The Problem with Ambiguous Questions

You've identified a critical challenge in RAG systems: **ambiguous follow-up questions** like "What is the document about?" or "How does it work?" that lack sufficient context to be understood in isolation.

### Why Traditional RAG Fails

Traditional RAG systems process each query independently:

```python
# Traditional RAG - processes query in isolation
query = "What is the document about?"  # ❌ Too ambiguous!
embedding = model.encode(query)
similar_docs = vector_store.search(embedding, k=5)
# Result: Poor or irrelevant results
```

**Problems:**
1. **Lost Context**: No reference to previous conversation
2. **Ambiguous Pronouns**: "it", "this", "that" have no meaning
3. **Follow-up Questions**: "Can you elaborate?" has no context
4. **Inconsistent Results**: Same question returns different answers

## Our Context-Aware Solution

Our system solves this through **Context-Aware RAG** that maintains conversation history and enhances queries with contextual information.

### 1. Context Enhancement Process

```python
def build_context_aware_query(
    self, 
    current_message: str, 
    conversation_id: str,
    user_id: Optional[str] = None,
    include_memory: bool = True
) -> Tuple[str, Dict[str, Any]]:
    """Build a context-aware query with conversation history and memory."""
    
    # Step 1: Get conversation context
    context = self.get_conversation_context(conversation_id, user_id, include_memory)
    
    # Step 2: Extract key information from conversation
    context_parts = []
    
    # Add recent topics
    if context.topics:
        context_parts.append(f"Recent topics: {', '.join(context.topics[-5:])}")
    
    # Add key entities/concepts
    if context.key_entities:
        recent_entities = [e.text for e in context.key_entities if e.importance_score > 0.7][:5]
        if recent_entities:
            context_parts.append(f"Key concepts: {', '.join(recent_entities)}")
    
    # Step 3: Enhance the query
    if context_parts:
        enhanced_query = f"{current_message} | Context: {'; '.join(context_parts)}"
    else:
        enhanced_query = current_message
    
    # Step 4: Add memory context
    if include_memory:
        relevant_memory = self.retrieve_relevant_memory(current_message, user_id, conversation_id, k=3)
        if relevant_memory:
            memory_context = []
            for chunk, score in relevant_memory:
                memory_context.append(f"[{score:.2f}] {chunk.content[:100]}...")
            if memory_context:
                enhanced_query += f" | Relevant memory: {'; '.join(memory_context)}"
    
    return enhanced_query, context_metadata
```

### 2. Example: Context Enhancement in Action

**Scenario: Document Analysis Conversation**

```python
# Initial conversation
messages = [
    {"role": "user", "content": "I uploaded a research paper about neural networks"},
    {"role": "assistant", "content": "I can see the research paper about neural networks. What would you like to know about it?"},
    {"role": "user", "content": "What is the document about?"}  # ❌ Ambiguous!
]

# Context enhancement process
original_query = "What is the document about?"

# Extract context from conversation
context = {
    "topics": ["neural networks", "research paper", "document analysis"],
    "entities": ["research paper", "neural networks", "document"],
    "recent_conversation": "I uploaded a research paper about neural networks"
}

# Enhanced query
enhanced_query = "What is the document about? | Context: Recent topics: neural networks, research paper, document analysis; Key concepts: research paper, neural networks, document"

# Now the embedding search has context!
embedding = model.encode(enhanced_query)
similar_docs = vector_store.search(embedding, k=5)
# Result: ✅ Relevant results about the neural networks research paper
```

## Context Detection and Enhancement Strategies

### 1. Context-Dependent Query Detection

The system automatically detects when queries need context:

```python
def _is_context_dependent_query(self, query: str, conversation_history: List[Dict]) -> bool:
    """Determine if a query is context-dependent using LLM reasoning."""
    
    # Create context detection prompt
    context_detection_prompt = f"""You are an AI assistant that determines whether a user's question requires conversation context to answer properly.

CONVERSATION CONTEXT:
{context_summary}

CURRENT QUESTION: "{query}"

TASK: Determine if this question is context-dependent or general knowledge.

A question is CONTEXT-DEPENDENT if:
- It uses pronouns like "it", "this", "that", "they", "them"
- It refers to something mentioned in the conversation
- It's a follow-up question that builds on previous answers
- It asks for clarification or elaboration about previous topics
- It compares or contrasts with previously discussed concepts

A question is GENERAL KNOWLEDGE if:
- It asks for basic facts, definitions, or information
- It's a standalone question that doesn't reference the conversation
- It's about geography, history, science, or other general topics
- It doesn't use pronouns or references to previous discussion

RESPONSE FORMAT: Answer with exactly "CONTEXT" or "GENERAL" followed by a brief explanation."""

    # Use LLM to determine context dependency
    response = llm.generate(context_detection_prompt)
    
    return "CONTEXT" in response
```

### 2. Entity and Topic Extraction

The system extracts key entities and topics from conversation history:

```python
def _extract_context_entities(self, messages: List[Message]) -> List[ContextEntity]:
    """Extract key entities from conversation messages."""
    
    entities = {}
    current_time = datetime.now()
    
    for message in messages:
        content = message.content
        if len(content) < 10:  # Skip very short messages
            continue
        
        # Extract entities from text
        words = content.split()
        for word in words:
            clean_word = word.lower().strip('.,!?;:"')
            if len(clean_word) < 3:
                continue
            
            # Skip common words
            if clean_word in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all']:
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
    
    # Return top entities by importance
    return sorted(entities.values(), key=lambda x: x.importance_score, reverse=True)[:50]
```

### 3. Memory Retrieval for Cross-Conversation Context

The system retrieves relevant memory from past conversations:

```python
def retrieve_relevant_memory(
    self, 
    query: str, 
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    k: int = 5
) -> List[Tuple[MemoryChunk, float]]:
    """Retrieve relevant memory chunks for context."""
    
    # Build enhanced query with user context
    enhanced_query = query
    if user_id:
        user_context = self.get_user_context(user_id, include_cross_conversation=False)
        if user_context.get("topics_of_interest"):
            # Add user's interests to query for better retrieval
            interests = " ".join(user_context["topics_of_interest"][:5])
            enhanced_query = f"{query} {interests}"
    
    # Retrieve relevant documents using vector search
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
            created_at=datetime.now(),
            relevance_score=score
        )
        memory_chunks.append((chunk, score))
    
    return memory_chunks
```

## Document-Aware Context Enhancement

### 1. Document Context Integration

When documents are involved, the system enhances queries with document-specific context:

```python
def _create_document_aware_prompt(
    self, 
    user_message: str, 
    document_context: List[DocumentContext],
    conversation_id: str = None
) -> str:
    """Create prompt that includes document context."""
    
    # Initialize conversation-specific retriever
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
            
            # Filter chunks to specific documents using metadata
            document_chunks = []
            for chunk_doc, score in relevant_chunks:
                chunk_source = chunk_doc.metadata.get('source', '')
                file_path = doc.metadata.get('file_path', '')
                
                # Match by file path to ensure we get chunks from the right document
                if chunk_source and file_path and file_path in chunk_source:
                    document_chunks.append((chunk_doc, score))
            
            # Process and combine chunks
            if document_chunks:
                document_chunks.sort(key=lambda x: x[1], reverse=True)
                content_parts = []
                for chunk_doc, score in document_chunks[:5]:
                    if score > 0.05:  # Relevance threshold
                        content_parts.append(chunk_doc.page_content.strip())
                
                if content_parts:
                    combined_content = "\n\n".join(content_parts)
                    documents_text.append(f"Document: {doc.filename}\nContent:\n{combined_content}")
    
    # Create enhanced prompt with document context
    if documents_text:
        document_context_text = "\n\n".join(documents_text)
        return f"""You are an AI assistant with access to the following documents in this conversation:

{document_context_text}

User Question: {user_message}

Please answer the user's question using information from the documents when relevant, and cite the source document when you do so."""
    
    return user_message
```

### 2. Document Relevance Scoring

The system calculates relevance scores for documents based on query similarity:

```python
def update_document_relevance(self, document_id: str, query: str) -> float:
    """Update document relevance based on query similarity."""
    
    document = self.document_repo.get_document(document_id)
    if not document:
        return 0.0
    
    relevance_score = 0.0
    query_lower = query.lower()
    
    # Check filename similarity
    if query_lower in document.filename.lower():
        relevance_score += 0.3
    
    # Check summary similarity
    if document.summary_text and query_lower in document.summary_text.lower():
        relevance_score += 0.7
    
    # Check for general document-related keywords
    document_keywords = ["document", "file", "paper", "report", "text", "content", "about", "summarize"]
    if any(keyword in query_lower for keyword in document_keywords):
        relevance_score += 0.5  # Base relevance for document-related queries
    
    return min(relevance_score, 1.0)
```

## Real-World Examples

### Example 1: Technical Discussion

```python
# Conversation flow
conversation = [
    {"role": "user", "content": "I uploaded a paper about transformer architectures"},
    {"role": "assistant", "content": "I can see the paper about transformer architectures. What would you like to know?"},
    {"role": "user", "content": "How does it work?"}  # ❌ Ambiguous!
]

# Context enhancement
original_query = "How does it work?"

# Extract context
context = {
    "topics": ["transformer architectures", "paper", "neural networks"],
    "entities": ["transformer", "architecture", "paper", "neural network"],
    "recent_conversation": "I uploaded a paper about transformer architectures"
}

# Enhanced query
enhanced_query = "How does it work? | Context: Recent topics: transformer architectures, paper, neural networks; Key concepts: transformer, architecture, paper, neural network"

# Result: ✅ Now the system knows "it" refers to transformer architectures
```

### Example 2: Document Analysis

```python
# Conversation flow
conversation = [
    {"role": "user", "content": "Can you analyze this research paper on machine learning?"},
    {"role": "assistant", "content": "I've analyzed the research paper on machine learning. It covers supervised learning, unsupervised learning, and reinforcement learning."},
    {"role": "user", "content": "What about the methodology section?"}  # ❌ Ambiguous!
]

# Context enhancement
original_query = "What about the methodology section?"

# Extract context
context = {
    "topics": ["research paper", "machine learning", "methodology"],
    "entities": ["research paper", "machine learning", "methodology", "supervised learning"],
    "recent_conversation": "Can you analyze this research paper on machine learning?"
}

# Enhanced query
enhanced_query = "What about the methodology section? | Context: Recent topics: research paper, machine learning, methodology; Key concepts: research paper, machine learning, methodology, supervised learning"

# Result: ✅ Now the system knows "the methodology section" refers to the research paper's methodology
```

### Example 3: Follow-up Questions

```python
# Conversation flow
conversation = [
    {"role": "user", "content": "Explain attention mechanisms in neural networks"},
    {"role": "assistant", "content": "Attention mechanisms allow neural networks to focus on relevant parts of input..."},
    {"role": "user", "content": "Can you give me an example?"}  # ❌ Ambiguous!
]

# Context enhancement
original_query = "Can you give me an example?"

# Extract context
context = {
    "topics": ["attention mechanisms", "neural networks", "examples"],
    "entities": ["attention", "mechanism", "neural network", "example"],
    "recent_conversation": "Explain attention mechanisms in neural networks"
}

# Enhanced query
enhanced_query = "Can you give me an example? | Context: Recent topics: attention mechanisms, neural networks, examples; Key concepts: attention, mechanism, neural network, example"

# Result: ✅ Now the system knows "an example" refers to attention mechanisms
```

## Context Strategies

### 1. Auto Strategy (Default)

Automatically determines the best approach based on query type:

```python
def apply_context_strategy(self, query: str, context: ContextSummary, strategy: str = "auto"):
    """Apply context strategy based on query analysis."""
    
    if strategy == "auto":
        # Determine if query is context-dependent
        if self._is_context_dependent_query(query, context):
            return self._apply_full_context(query, context)
        else:
            return self._apply_minimal_context(query, context)
    
    elif strategy == "conversation_only":
        return self._apply_conversation_context(query, context)
    
    elif strategy == "memory_only":
        return self._apply_memory_context(query, context)
    
    elif strategy == "hybrid":
        return self._apply_hybrid_context(query, context)
```

### 2. Conversation-Only Strategy

Uses only current conversation context:

```python
def _apply_conversation_context(self, query: str, context: ContextSummary):
    """Apply only conversation context."""
    
    context_parts = []
    if context.topics:
        context_parts.append(f"Topics: {', '.join(context.topics[-3:])}")
    
    if context.key_entities:
        entities = [e.text for e in context.key_entities[:3]]
        context_parts.append(f"Entities: {', '.join(entities)}")
    
    if context_parts:
        return f"{query} | Context: {'; '.join(context_parts)}"
    
    return query
```

### 3. Memory-Only Strategy

Uses only long-term memory from past conversations:

```python
def _apply_memory_context(self, query: str, context: ContextSummary):
    """Apply only memory context."""
    
    # Retrieve relevant memory chunks
    relevant_memory = self.retrieve_relevant_memory(query, k=3)
    
    if relevant_memory:
        memory_context = []
        for chunk, score in relevant_memory:
            memory_context.append(f"[{score:.2f}] {chunk.content[:100]}...")
        
        return f"{query} | Memory: {'; '.join(memory_context)}"
    
    return query
```

## Performance Considerations

### 1. Context Caching

Context summaries are cached for performance:

```python
def get_conversation_context(self, conversation_id: str, user_id: Optional[str] = None):
    """Get conversation context with caching."""
    
    # Check cache first
    cache_key = f"{conversation_id}_{user_id}"
    if cache_key in self._context_cache:
        return self._context_cache[cache_key]
    
    # Build context
    context = self._build_conversation_context(conversation_id, user_id)
    
    # Cache for future use
    self._context_cache[cache_key] = context
    
    return context
```

### 2. Entity Limits

To prevent performance issues:

```python
# Limit entities to prevent overwhelming context
max_context_entities = 50
max_topics = 10
max_memory_chunks = 5

# Only include high-importance entities
recent_entities = [e.text for e in context.key_entities 
                  if e.importance_score > 0.7][:5]
```

### 3. Context Compression

For long conversations, context is compressed:

```python
def _compress_conversation_context(self, messages: List[Message]) -> str:
    """Compress long conversation context."""
    
    if len(messages) <= 10:
        return self._create_full_context(messages)
    
    # Use summarization for long conversations
    summary = self._summarize_conversation(messages)
    return f"Conversation summary: {summary}"
```

## Benefits of Context-Aware RAG

### 1. **Handles Ambiguous Questions**
- Pronouns like "it", "this", "that" are resolved
- Follow-up questions work naturally
- Context-dependent queries are understood

### 2. **Maintains Conversation Flow**
- References to previous topics work
- Multi-turn conversations are coherent
- Context is preserved across messages

### 3. **Improves Retrieval Quality**
- Enhanced queries find more relevant documents
- Context-aware search improves precision
- Better understanding of user intent

### 4. **Enables Document-Aware Conversations**
- Questions about specific documents work
- Document context is maintained
- Source citations are accurate

## Conclusion

Context-aware RAG solves the fundamental problem of ambiguous follow-up questions by:

1. **Maintaining conversation history** and extracting key entities/topics
2. **Enhancing queries** with contextual information before embedding search
3. **Using conversation-specific document retrieval** to maintain document context
4. **Applying intelligent context strategies** based on query type
5. **Providing memory retrieval** from past conversations when needed

This approach transforms ambiguous questions like "What is the document about?" into context-rich queries that the RAG system can understand and answer accurately, creating a natural conversational experience where follow-up questions work seamlessly.
