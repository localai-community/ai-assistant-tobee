# Document Storage System

## Overview

The AI Assistant implements a comprehensive document storage system that preserves original files while creating searchable, context-aware content for conversations. This dual-storage approach ensures both data preservation and efficient retrieval capabilities.

## Storage Architecture

### Core Components

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Original Files    │    │   Database Metadata  │    │   Vector Database   │
│   (File System)     │    │   (SQLite)           │    │   (ChromaDB)        │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Physical Storage  │    │   Document Records   │    │   Chunked Content   │
│   UUID-based Names  │    │   & Metadata         │    │   & Embeddings      │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

## Original File Storage

### **Yes, Original Documents Are Preserved**

The system maintains complete copies of all uploaded documents in the file system.

### Storage Location

**Primary Directory**: `backend/storage/uploads/`

```python
# From backend/app/api/rag.py
UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
```

### File Naming Convention

Original files are stored with a unique naming pattern to prevent conflicts:

```python
# Create unique filename to avoid conflicts
import uuid
unique_filename = f"{uuid.uuid4()}_{file.filename}"
file_path = UPLOAD_DIR / unique_filename
```

**Pattern**: `{UUID}_{original_filename}`

**Examples**:
- `02ea38fc-a5c3-46fe-add3-223bc3356821_document.pdf`
- `0319572c-9709-4e9f-bdb8-79991639a628_report.docx`
- `123c0926-e393-4750-975c-1e982574472e_notes.txt`

### File Storage Process

```python
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None)
):
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.txt', '.md', '.doc'}
    
    # Create unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save original file to upload directory
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
```

### Supported File Types

```python
# From backend/app/core/config.py
allowed_file_types: list = [".pdf", ".docx", ".txt", ".md", ".doc"]
```

- **PDF**: `.pdf` - Research papers, reports, documents
- **Word**: `.docx`, `.doc` - Microsoft Word documents
- **Text**: `.txt` - Plain text files
- **Markdown**: `.md` - Markdown formatted documents

### File Size Limits

```python
max_file_size: int = 50 * 1024 * 1024  # 50MB maximum
```

## Database Metadata Storage

### ChatDocument Model

The system stores comprehensive metadata about each document in the SQLite database:

```python
class ChatDocument(Base):
    """Chat document model for conversation-scoped document storage."""
    __tablename__ = "chat_documents"
    
    # Primary identifiers
    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)  # Original filename
    file_type = Column(String(50), nullable=False)  # File extension
    file_size = Column(Integer, nullable=False)     # Size in bytes
    file_path = Column(String(500), nullable=False) # Full path to original file
    
    # Processing information
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    summary_text = Column(Text, nullable=True)      # Generated summary
    summary_type = Column(String(50), nullable=True) # Summary generation method
    processing_status = Column(String(50), default="uploaded") # Status tracking
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    conversation = relationship("Conversation", backref="documents")
    user = relationship("User", backref="documents")
```

### Metadata Fields Explained

| Field | Purpose | Example |
|-------|---------|---------|
| `id` | Unique document identifier | `"02ea38fc-a5c3-46fe-add3-223bc3356821"` |
| `conversation_id` | Links to specific conversation | `"conv_123"` |
| `user_id` | Document owner | `"user_456"` |
| `filename` | Original filename | `"research_paper.pdf"` |
| `file_type` | File extension | `".pdf"` |
| `file_size` | Size in bytes | `280818` |
| `file_path` | Full path to original file | `"storage/uploads/02ea38fc...research_paper.pdf"` |
| `processing_status` | Current processing state | `"processed"`, `"uploaded"`, `"failed"` |
| `summary_text` | Generated document summary | `"This paper discusses..."` |

## Document Processing Pipeline

### 1. Upload and Storage

```python
# Step 1: Validate and store original file
unique_filename = f"{uuid.uuid4()}_{file.filename}"
file_path = UPLOAD_DIR / unique_filename

with open(file_path, "wb") as buffer:
    shutil.copyfileobj(file.file, buffer)
```

### 2. Database Record Creation

```python
# Step 2: Create database metadata record
document_data = ChatDocumentCreate(
    filename=file.filename,
    file_type=file_extension,
    file_size=file.size,
    file_path=str(file_path),
    conversation_id=conversation_id,
    user_id=user_id
)

chat_document = document_repo.create_document(document_data)
```

### 3. Content Processing

```python
# Step 3: Process document with RAG
conversation_vector_store = VectorStore(conversation_id=conversation_id)
conversation_rag_retriever = RAGRetriever(vector_store=conversation_vector_store)
result = conversation_rag_retriever.add_document(str(file_path))
```

### 4. Status Updates

```python
# Step 4: Update processing status
if result["success"]:
    document_repo.update_document(chat_document.id, {
        "processing_status": "processed"
    })
else:
    document_repo.update_document(chat_document.id, {
        "processing_status": "failed"
    })
```

## Vector Database Storage

### Conversation-Specific Collections

Each conversation gets its own vector database collection:

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

### Document Chunking and Embedding

Documents are processed into searchable chunks:

```python
# Document processing creates chunks with embeddings
def add_document(self, file_path: str) -> Dict[str, Any]:
    """Process document and add to vector store."""
    
    # Load and parse document
    documents = self.document_processor.process_document(file_path)
    
    # Split into chunks
    chunks = self.text_splitter.split_documents(documents)
    
    # Create embeddings and store
    self.vector_store.add_documents(chunks)
    
    return {
        "success": True,
        "chunks_created": len(chunks),
        "stats": {"total_chunks": len(chunks)}
    }
```

## Storage Organization

### Directory Structure

```
backend/storage/
├── uploads/                    # Original files
│   ├── {uuid}_document1.pdf
│   ├── {uuid}_document2.docx
│   └── {uuid}_notes.txt
└── vector_db/                  # Vector database
    ├── chroma.sqlite3         # ChromaDB metadata
    ├── {conversation_id_1}/   # Conversation-specific collections
    ├── {conversation_id_2}/
    └── {conversation_id_n}/
```

### Conversation Isolation

- **Original Files**: Stored globally but linked to conversations via database
- **Vector Collections**: Isolated per conversation for privacy and organization
- **Metadata**: Linked to specific conversations and users

## Document Retrieval Process

### 1. Context-Aware Retrieval

When processing user queries, the system:

```python
def get_document_context_for_query(self, conversation_id: str, query: str):
    """Get relevant documents for a specific query."""
    
    # Get all documents for conversation
    documents = self.get_conversation_documents(conversation_id)
    
    # Calculate relevance scores
    for doc in documents:
        doc.relevance_score = self.update_document_relevance(doc.document_id, query)
    
    # Return sorted by relevance
    return sorted(documents, key=lambda x: x.relevance_score, reverse=True)
```

### 2. Content Extraction

```python
def _create_document_aware_prompt(self, user_message: str, document_context: List):
    """Create prompt with document content."""
    
    # Initialize conversation-specific retriever
    conversation_vector_store = VectorStore(conversation_id=conversation_id)
    rag_retriever = RAGRetriever(vector_store=conversation_vector_store)
    
    # Retrieve relevant content
    relevant_chunks = rag_retriever.retrieve_relevant_documents(user_message, k=30)
    
    # Filter and combine content
    for doc in document_context:
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
```

## Document Management

### Cleanup Operations

The system provides comprehensive cleanup capabilities:

```python
def cleanup_conversation_documents(self, conversation_id: str) -> Dict[str, Any]:
    """Clean up all documents for a conversation."""
    
    cleanup_stats = {
        "documents_deleted": 0,
        "chunks_deleted": 0,
        "files_deleted": 0,
        "total_size_freed": 0,
        "errors": []
    }
    
    for document in documents:
        try:
            # Delete document chunks from vector DB
            chunks_deleted = self.chunk_repo.delete_document_chunks(document.id)
            cleanup_stats["chunks_deleted"] += chunks_deleted
            
            # Delete physical file
            file_path = Path(document.file_path)
            if file_path.exists():
                file_size = file_path.stat().st_size
                file_path.unlink()
                cleanup_stats["files_deleted"] += 1
                cleanup_stats["total_size_freed"] += file_size
            
            # Delete database record
            if self.document_repo.delete_document(document.id):
                cleanup_stats["documents_deleted"] += 1
                
        except Exception as e:
            cleanup_stats["errors"].append(f"Error cleaning up document {document.id}: {e}")
    
    return cleanup_stats
```

### Analytics and Monitoring

```python
def get_document_analytics(self, user_id: str) -> Dict[str, Any]:
    """Get document usage analytics."""
    
    analytics = {
        "total_documents": len(documents),
        "total_size": sum(doc.file_size for doc in documents),
        "file_types": {},
        "conversations": set(),
        "upload_timeline": [],
        "processing_status": {},
        "recent_activity": []
    }
    
    # Analyze document patterns
    for doc in documents:
        # File type distribution
        file_type = doc.file_type
        analytics["file_types"][file_type] = analytics["file_types"].get(file_type, 0) + 1
        
        # Processing status tracking
        status = doc.processing_status
        analytics["processing_status"][status] = analytics["processing_status"].get(status, 0) + 1
        
        # Upload timeline
        analytics["upload_timeline"].append({
            "date": doc.upload_timestamp.isoformat(),
            "filename": doc.filename,
            "size": doc.file_size
        })
    
    return analytics
```

## Configuration

### Environment Settings

```python
# From backend/app/core/config.py
class Settings:
    # File Storage
    upload_dir: str = "./storage/uploads"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [".pdf", ".docx", ".txt", ".md"]
    
    # Vector Database
    vector_db_path: str = "./storage/vector_db"
    
    # Database
    database_url: str = "sqlite:///./localai_community.db"
```

### Customizable Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `upload_dir` | `"./storage/uploads"` | Directory for original files |
| `max_file_size` | `50MB` | Maximum file size limit |
| `vector_db_path` | `"./storage/vector_db"` | Vector database location |
| `allowed_file_types` | `[".pdf", ".docx", ".txt", ".md"]` | Supported file extensions |

## Current Storage Status

### File Statistics

Based on the current system state:

- **Total Files**: 94 documents stored
- **File Types**: 62 PDFs, 32 text files
- **Storage Location**: `backend/storage/uploads/`
- **Vector Collections**: Multiple conversation-specific collections in `backend/storage/vector_db/`

### Example Stored Files

```
storage/uploads/
├── 02ea38fc-a5c3-46fe-add3-223bc3356821_BİRCAN BİLİCİ_18092025095630_300154945_2_1.pdf
├── 0319572c-9709-4e9f-bdb8-79991639a628_test_auto_response.txt
├── 04b56c0a-5016-4548-824d-a9e03657473f_Is EC2 Dying_ AWS Quietly Admitted Something Big.pdf
├── 069c3deb-b1d9-4fa8-8833-a85c40810773_Convention_ENG.pdf
├── 123c0926-e393-4750-975c-1e982574472e_simple_test.txt
└── 148a4209-6e89-401a-92ac-8667de53a712_LeiaRenee-CV.pdf
```

## Benefits of This Storage Approach

### 1. **Data Preservation**
- Original files are never lost
- Can re-process documents with updated algorithms
- Full audit trail of all uploaded content

### 2. **Efficient Retrieval**
- Vector embeddings enable fast semantic search
- Conversation-specific collections improve privacy
- Chunked content allows precise information retrieval

### 3. **Scalability**
- File system storage scales with disk space
- Vector database handles millions of chunks
- Database provides fast metadata queries

### 4. **Privacy and Isolation**
- Each conversation has isolated document access
- User-specific document ownership
- Configurable cleanup and retention policies

### 5. **Flexibility**
- Support for multiple file formats
- Configurable processing pipelines
- Rich metadata for analytics and management

## API Endpoints

### Document Upload

```python
POST /api/v1/rag/upload
Content-Type: multipart/form-data

Parameters:
- file: UploadFile (required)
- conversation_id: str (optional)
- user_id: str (optional)

Response:
{
    "success": true,
    "document_id": "uuid",
    "filename": "original_name.pdf",
    "file_size": 280818,
    "conversation_id": "conv_123",
    "chunks_created": 45,
    "message": "Document processed successfully"
}
```

### Get Conversation Documents

```python
GET /api/v1/rag/documents/{conversation_id}

Response:
{
    "documents": [
        {
            "id": "uuid",
            "filename": "document.pdf",
            "file_type": ".pdf",
            "file_size": 280818,
            "processing_status": "processed",
            "upload_timestamp": "2024-01-01T12:00:00Z",
            "summary_text": "Document summary..."
        }
    ]
}
```

## Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Check file size limits (50MB default)
   - Verify file type is supported
   - Ensure upload directory has write permissions

2. **Processing Errors**
   - Check file format compatibility
   - Verify vector database connectivity
   - Review processing status in database

3. **Storage Space Issues**
   - Monitor upload directory size
   - Implement cleanup policies
   - Consider compression for large files

### Debug Information

```python
# Enable debug logging
import logging
logging.getLogger("backend.app.services.rag").setLevel(logging.DEBUG)
logging.getLogger("backend.app.api.rag").setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Compression**: Automatic compression of stored files
2. **Versioning**: Document version management
3. **Backup**: Automated backup of original files
4. **Encryption**: File-level encryption for sensitive documents
5. **Cloud Storage**: Integration with cloud storage providers

### Integration Opportunities

1. **External Storage**: S3, Google Cloud Storage, Azure Blob
2. **Document Processing**: Advanced OCR, image extraction
3. **Content Analysis**: Automatic tagging and categorization
4. **Collaboration**: Multi-user document sharing

## Conclusion

The document storage system provides a robust, scalable solution for managing documents in conversational AI applications. By preserving original files while creating searchable, context-aware content, it ensures both data integrity and efficient retrieval capabilities.

The dual-storage approach with conversation-specific organization makes it suitable for both individual and multi-user scenarios, while the comprehensive metadata tracking enables rich analytics and management capabilities.
