# Context-Aware RAG Feature Implementation Plan

## Overview

The current RAG (Retrieval-Augmented Generation) system has a fundamental limitation: it processes each user query in isolation, without considering the conversation history. This makes it ineffective for follow-up questions, contextual references, and multi-turn conversations.

This document outlines the implementation plan for a **Context-Aware RAG** feature that will significantly improve the system's conversational capabilities.

## Problem Statement

### Current Limitations

1. **Isolated Query Processing**: Each RAG query only considers the current message, not conversation history
2. **Poor Follow-up Question Handling**: Questions like "What about the second part?" or "Can you explain that further?" fail to retrieve relevant documents
3. **Lost Context**: Important context from previous messages is ignored during document retrieval
4. **Inconsistent Results**: Same follow-up questions may return different results depending on conversation state

### Example Scenarios

**Scenario 1: Technical Discussion**
```
User: "What is attention in neural networks?"
Assistant: [Provides answer with RAG context from documents]

User: "How does it relate to transformers?"
Assistant: [Fails to find relevant documents because it only searches for "transformers"]
```

**Scenario 2: Document Analysis**
```
User: "What are the main points in the research paper?"
Assistant: [Provides summary with RAG context]

User: "Can you elaborate on the methodology section?"
Assistant: [Fails to find methodology section because it doesn't know which paper]
```

## Solution Design

### Core Concept

The Context-Aware RAG system will:

1. **Build Context-Aware Queries**: Combine recent conversation history with the current message
2. **Enhanced Document Retrieval**: Use the enriched query for more relevant document retrieval
3. **Conversation-Aware Prompting**: Include conversation context in the RAG prompt
4. **Consistent Implementation**: Apply context-awareness to both regular and streaming RAG endpoints

### Technical Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Message  │───▶│ Context Builder  │───▶│ Enhanced Query  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Conversation    │───▶│ History Retrieval│───▶│ Context-Aware   │
│ History         │    │ (Last 5 messages)│    │ RAG Processing  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Implementation Plan

### Phase 1: Core Infrastructure (Priority: High)

#### 1.1 Add Context Builder Method
**File**: `backend/app/services/chat.py`
**Method**: `_build_context_aware_query()`

```python
def _build_context_aware_query(self, current_message: str, conversation_id: Optional[str]) -> str:
    """Build a context-aware query by including recent conversation history."""
    if not conversation_id or not self.message_repo:
        return current_message
    
    try:
        # Get recent messages from the conversation (last 5 messages)
        recent_messages = self.message_repo.get_messages(conversation_id, limit=5)
        
        if not recent_messages:
            return current_message
        
        # Build context from recent messages
        context_parts = []
        for msg in recent_messages:
            if msg.role == "user":
                context_parts.append(f"User: {msg.co 