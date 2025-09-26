# PDF Summary Implementation Plan

## Overview

This document outlines the comprehensive implementation plan for adding PDF summary functionality to the AI Assistant project. The feature will allow users to upload documents (PDF, DOCX, TXT, DOC) within chat conversations, automatically offer summarization, and maintain document context throughout the conversation for enhanced Q&A capabilities.

## Current System Analysis

### ✅ Existing Infrastructure
- **Document Processing**: PyMuPDF, python-docx, unstructured libraries
- **RAG System**: Vector storage with ChromaDB, document retrieval
- **Context Awareness**: Conversation management and context tracking
- **File Upload API**: Basic document upload endpoints
- **Chat Service**: Conversation management with streaming responses
- **Database Models**: User, Conversation, Message models with user_id support

### ❌ Issues Identified
- **Broken user_id handling**: Conversations not properly associated with users
- **No chat-scoped documents**: Documents are global, not conversation-specific
- **Missing summarization**: No AI-powered document summarization
- **Limited document context**: Documents not integrated into conversation context

## Implementation Tasks

### Task 1: Fix user_id handling in conversation creation and enhance document upload API
**Priority**: High  
**Estimated Time**: 2-3 hours

#### Scope
- Fix broken user_id handling in conversation creation
- Extend document upload API for chat-scoped storage
- Add proper document metadata tracking

#### Technical Details
**Fix conversation creation in `ChatService.generate_response()`:**
```python
# Current (broken) - line 366-370 in chat.py
conversation_data = ConversationCreate(
    title=f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    model=model
)

# Fixed version
conversation_data = ConversationCreate(
    title=f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    model=model,
    user_id=user_id  # <-- Add this line
)
```

**Extend upload API endpoint:**
- Modify `POST /api/v1/rag/upload` to accept `conversation_id` and `user_id` parameters
- Create chat-scoped document storage (documents only available in specific conversation)
- Add document metadata tracking (upload time, conversation association, file type)
- Support PDF, DOCX, TXT, DOC files using existing parsing libraries

**Database Schema Extensions:**
```sql
CREATE TABLE chat_documents (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255),
    file_type VARCHAR(50),
    file_size INTEGER,
    upload_timestamp TIMESTAMP,
    summary_text TEXT,
    summary_type VARCHAR(50),
    processing_status VARCHAR(50),
    file_path VARCHAR(500)
);

CREATE TABLE document_chunks (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES chat_documents(id),
    chunk_text TEXT,
    chunk_index INTEGER,
    embedding VECTOR(384)
);
```

#### Files to Modify
- `backend/app/services/chat.py` - Fix conversation creation
- `backend/app/api/rag.py` - Extend upload endpoint
- `backend/app/models/database.py` - Add new models
- `backend/app/models/schemas.py` - Add new schemas

---

### Task 2: Create document summary service with AI-powered summarization
**Priority**: High  
**Estimated Time**: 4-5 hours

#### Scope
- Create dedicated document summarization service
- Implement multi-level summarization capabilities
- Integrate with existing Ollama LLM for summary generation

#### Technical Details
**Create `DocumentSummaryService` class:**
```python
# backend/app/services/document_summary.py
class DocumentSummaryService:
    def __init__(self, ollama_url: str, db: Session):
        self.ollama_url = ollama_url
        self.db = db
        self.summary_cache = {}
    
    async def generate_summary(
        self, 
        document_text: str, 
        summary_type: str = "brief",
        conversation_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate document summary using Ollama LLM"""
        
    async def generate_multi_level_summary(self, document_text: str) -> Dict[str, str]:
        """Generate brief, detailed, and key points summaries"""
        
    def _create_summary_prompt(self, text: str, summary_type: str) -> str:
        """Create optimized prompts for different summary types"""
```

**Summary Types:**
- **Brief**: 2-3 sentence overview
- **Detailed**: Comprehensive summary with main points
- **Key Points**: Bulleted list of important information
- **Executive**: High-level summary for decision makers

**Integration Points:**
- Use existing Ollama HTTP client from `ChatService`
- Cache summaries to avoid re-processing
- Support different summary styles based on user preferences

#### Files to Create
- `backend/app/services/document_summary.py`

---

### Task 3: Implement chat-scoped document context management
**Priority**: High  
**Estimated Time**: 3-4 hours

#### Scope
- Extend context awareness service for document context
- Create document context tracking and retrieval
- Implement document relevance scoring

#### Technical Details
**Extend `ContextAwarenessService`:**
```python
# Add to backend/app/services/context_awareness.py
@dataclass
class DocumentContext:
    """Represents a document in conversation context."""
    document_id: str
    filename: str
    file_type: str
    summary: str
    upload_time: datetime
    relevance_score: float
    last_accessed: datetime
    access_count: int = 0

class ContextAwarenessService:
    def get_conversation_documents(self, conversation_id: str) -> List[DocumentContext]:
        """Get all documents associated with a conversation"""
        
    def update_document_relevance(self, document_id: str, query: str) -> float:
        """Update document relevance based on query"""
        
    def get_document_context_for_query(self, conversation_id: str, query: str) -> List[DocumentContext]:
        """Get relevant documents for a specific query"""
```

**Document Context Features:**
- Track document access patterns
- Calculate relevance scores based on query similarity
- Maintain document metadata in conversation context
- Support multiple documents per conversation

#### Files to Modify
- `backend/app/services/context_awareness.py`

---

### Task 4: Add document-aware conversation context integration
**Priority**: High  
**Estimated Time**: 3-4 hours

#### Scope
- Integrate document context into chat responses
- Implement automatic document context injection
- Add document citation and source referencing

#### Technical Details
**Modify `ChatService.generate_response()`:**
```python
# Add document context retrieval
document_context = None
if enable_context_awareness and conversation_id:
    document_context = self.context_awareness.get_document_context_for_query(
        conversation_id, message
    )

# Include document context in prompt
if document_context:
    document_prompt = self._create_document_aware_prompt(
        message, document_context, conversation_context
    )
else:
    document_prompt = message
```

**Document-Aware Prompt Templates:**
```python
def _create_document_aware_prompt(
    self, 
    user_message: str, 
    document_context: List[DocumentContext],
    conversation_context: Optional[str] = None
) -> str:
    """Create prompt that includes document context"""
    
    documents_text = "\n\n".join([
        f"Document: {doc.filename}\nSummary: {doc.summary}\n"
        for doc in document_context
    ])
    
    return f"""You are an AI assistant with access to the following documents in this conversation:

{documents_text}

User Question: {user_message}

Please answer the user's question using information from the documents when relevant, and cite the source document when you do so."""
```

**Features:**
- Automatic document context injection when relevant
- Document citation in responses
- Support for multi-document scenarios
- Integration with existing context awareness system

#### Files to Modify
- `backend/app/services/chat.py`

---

### Task 5: Create frontend document upload UI with summary prompt
**Priority**: Medium  
**Estimated Time**: 4-5 hours

#### Scope
- Add file upload component to Streamlit frontend
- Implement document upload workflow with summary prompts
- Display document status and metadata

#### Technical Details
**Frontend Components:**
```python
# Add to frontend/app.py
def render_document_upload():
    """Render document upload interface"""
    st.subheader("📄 Upload Document")
    
    uploaded_file = st.file_uploader(
        "Choose a document",
        type=['pdf', 'docx', 'txt', 'doc'],
        help="Upload PDF, Word, or text documents for analysis"
    )
    
    if uploaded_file:
        if st.button("Upload Document"):
            result = upload_document_for_rag(uploaded_file)
            if result["success"]:
                st.success(f"Document '{uploaded_file.name}' uploaded successfully!")
                
                # Ask if user wants summary
                if st.button("📝 Summarize this document"):
                    summary = generate_document_summary(uploaded_file.name)
                    st.write("**Document Summary:**")
                    st.write(summary)
            else:
                st.error(f"Upload failed: {result['error']}")

def generate_document_summary(filename: str) -> str:
    """Generate and display document summary"""
    # Call backend summarization API
    pass
```

**UI Features:**
- Drag-and-drop file upload
- File type validation and preview
- Upload progress indicators
- Automatic summary prompt after upload
- Document list in sidebar
- Document status indicators

#### Files to Modify
- `frontend/app.py`

---

### Task 6: Implement document Q&A capabilities in chat responses
**Priority**: High  
**Estimated Time**: 3-4 hours

#### Scope
- Enhance RAG retrieval to prioritize chat-scoped documents
- Implement document-specific query routing
- Create document-aware response generation

#### Technical Details
**Enhance RAG System:**
```python
# Modify backend/app/services/rag/retriever.py
class DocumentAwareRetriever:
    def __init__(self, vector_store: VectorStore, conversation_id: str):
        self.vector_store = vector_store
        self.conversation_id = conversation_id
    
    def retrieve_document_context(
        self, 
        query: str, 
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant document chunks for conversation"""
        
        # First, get conversation-specific documents
        conversation_docs = self.get_conversation_documents()
        
        # Then perform similarity search within those documents
        results = []
        for doc in conversation_docs:
            doc_results = self.vector_store.similarity_search(
                query, 
                k=k,
                filter={"document_id": doc["id"]}
            )
            results.extend(doc_results)
        
        return results
```

**Document Q&A Features:**
- Prioritize conversation documents over global documents
- Support questions about specific documents
- Handle multi-document queries
- Maintain document context throughout conversation
- Provide source citations

#### Files to Modify
- `backend/app/services/rag/retriever.py`
- `backend/app/services/rag/advanced_retriever.py`

---

### Task 7: Add document metadata and session management
**Priority**: Medium  
**Estimated Time**: 2-3 hours

#### Scope
- Create comprehensive document lifecycle management
- Implement document session tracking and cleanup
- Add document analytics and usage tracking

#### Technical Details
**Document Lifecycle Management:**
```python
# backend/app/services/document_manager.py
class DocumentManager:
    def __init__(self, db: Session):
        self.db = db
    
    def create_document_session(
        self, 
        conversation_id: str, 
        user_id: str
    ) -> str:
        """Create a new document session for conversation"""
        
    def cleanup_conversation_documents(self, conversation_id: str):
        """Clean up documents when conversation ends"""
        
    def get_document_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get document usage analytics for user"""
        
    def archive_document(self, document_id: str):
        """Archive document for long-term storage"""
```

**Session Management Features:**
- Document session tracking
- Automatic cleanup of old documents
- Document retention policies
- Usage analytics and reporting
- Document sharing capabilities

#### Files to Create
- `backend/app/services/document_manager.py`

---

## API Endpoints to Add/Modify

### New Endpoints
- `POST /api/v1/rag/upload` - Enhanced with conversation_id and user_id
- `POST /api/v1/rag/summarize` - Document summarization endpoint
- `GET /api/v1/rag/documents/{conversation_id}` - List conversation documents
- `DELETE /api/v1/rag/documents/{document_id}` - Remove document from conversation
- `GET /api/v1/rag/document/{document_id}/summary` - Get document summary

### Modified Endpoints
- `POST /api/v1/chat/stream` - Enhanced with document context
- `GET /api/v1/context/{conversation_id}` - Include document context

## Dependencies and Libraries

### Already Available
- ✅ PyMuPDF for PDF processing
- ✅ python-docx for Word documents
- ✅ LangChain for text processing
- ✅ ChromaDB for vector storage
- ✅ FastAPI for API endpoints
- ✅ Streamlit for frontend
- ✅ SQLAlchemy for database operations

### No Additional Dependencies Required
All necessary libraries are already included in the project requirements.

## Success Criteria

### Functional Requirements
- ✅ Users can upload PDFs, DOCX, TXT, DOC files within a chat session
- ✅ AI automatically offers to summarize uploaded documents
- ✅ Document context is maintained throughout the conversation
- ✅ Users can ask questions about documents and get relevant answers
- ✅ Documents are isolated to their specific conversation context
- ✅ System handles multiple documents per conversation

### Performance Requirements
- ✅ Document processing completes within 30 seconds for typical files
- ✅ Summary generation completes within 10 seconds
- ✅ Chat responses include document context without significant delay
- ✅ System handles up to 10 documents per conversation

### User Experience Requirements
- ✅ Intuitive file upload interface
- ✅ Clear document status indicators
- ✅ Automatic summary prompts
- ✅ Source citations in responses
- ✅ Document list in conversation sidebar

## Implementation Timeline

### Phase 1: Core Infrastructure (Tasks 1-2)
**Duration**: 6-8 hours
- Fix user_id handling
- Create document summary service
- Extend upload API

### Phase 2: Context Integration (Tasks 3-4)
**Duration**: 6-8 hours
- Implement document context management
- Integrate document context into chat responses

### Phase 3: Frontend and Q&A (Tasks 5-6)
**Duration**: 7-9 hours
- Create frontend upload UI
- Implement document Q&A capabilities

### Phase 4: Polish and Management (Task 7)
**Duration**: 2-3 hours
- Add document metadata and session management

**Total Estimated Time**: 21-28 hours

## Risk Mitigation

### Technical Risks
- **Large file processing**: Implement file size limits and progress indicators
- **Memory usage**: Use streaming for large documents
- **Vector storage**: Implement efficient indexing for conversation-scoped documents

### User Experience Risks
- **Upload failures**: Provide clear error messages and retry mechanisms
- **Processing delays**: Show progress indicators and estimated completion times
- **Context confusion**: Clear document source citations and boundaries

## Future Enhancements

### Phase 2 Features
- Document annotation and highlighting
- Multi-language document support
- Document comparison capabilities
- Advanced search within documents
- Document export and sharing

### Integration Opportunities
- MCP document analysis tools
- Advanced RAG strategies for documents
- Document-based reasoning chains
- Cross-document relationship analysis
