# Vector-Document Relationship System

## Overview

The AI Assistant maintains a sophisticated relationship between vector embeddings and original documents through a multi-layered system that ensures traceability, context preservation, and efficient retrieval. This document explains how vectors are linked to their source documents and how this relationship enables document-aware conversations.

## Relationship Architecture

### Three-Layer Connection System

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Original Document │◄──►│   Database Metadata  │◄──►│   Vector Embeddings │
│   (File System)     │    │   (SQLite)           │    │   (ChromaDB)        │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Physical File     │    │   Document Records   │    │   Chunked Content   │
│   UUID-based Name   │    │   & Chunk Links      │    │   with Metadata     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

## Database Relationships

### 1. ChatDocument Model

The primary document record that stores metadata about the original file:

```python
class ChatDocument(Base):
    """Chat document model for conversation-scoped document storage."""
    __tablename__ = "chat_documents"
    
    # Primary identifiers
    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"))
    user_id = Column(String(36), ForeignKey("users.id"))
    
    # File information linking to original
    filename = Column(String(255), nullable=False)      # Original filename
    file_type = Column(String(50), nullable=False)      # File extension
    file_size = Column(Integer, nullable=False)         # Size in bytes
    file_path = Column(String(500), nullable=False)     # Full path to original file
    
    # Processing information
    summary_text = Column(Text, nullable=True)          # Generated summary
    processing_status = Column(String(50), default="uploaded")
    
    # Relationships
    conversation = relationship("Conversation", backref="documents")
    user = relationship("User", backref="documents")
    chunks = relationship("DocumentChunk", backref="document")  # Links to chunks
```

### 2. DocumentChunk Model

The bridge between documents and vector embeddings:

```python
class DocumentChunk(Base):
    """Document chunk model for storing document segments with embeddings."""
    __tablename__ = "document_chunks"
    
    # Primary identifiers
    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("chat_documents.id"), nullable=False, index=True)
    
    # Chunk content and organization
    chunk_text = Column(Text, nullable=False)           # Actual chunk content
    chunk_index = Column(Integer, nullable=False)       # Order within document
    embedding_id = Column(String(100), nullable=True)   # Reference to vector store
    
    # Relationships
    document = relationship("ChatDocument", backref="chunks")
```

### 3. Relationship Chain

The complete relationship chain:

```
Original File → ChatDocument → DocumentChunk → Vector Embedding
     ↓              ↓              ↓              ↓
storage/uploads/  SQLite DB    SQLite DB     ChromaDB
{uuid}_file.pdf  metadata    chunk_text    embeddings
```

## Vector Metadata System

### 1. LangChain Document Structure

When documents are processed, each chunk becomes a LangChain document with rich metadata:

```python
def process_file(self, file_path: str) -> List[LangChainDocument]:
    """Process a single file and return chunks with metadata."""
    
    # Create base metadata linking to original file
    metadata = {
        "source": str(file_path),              # Full path to original file
        "filename": file_path.name,            # Original filename
        "file_type": file_path.suffix.lower(), # File extension
        "file_size": file_path.stat().st_size  # File size in bytes
    }
    
    # Split text into chunks
    chunks = self.text_splitter.split_text(text)
    
    # Create LangChain documents with metadata
    documents = []
    for i, chunk in enumerate(chunks):
        doc = LangChainDocument(
            page_content=chunk,
            metadata={
                **metadata,
                "chunk_id": i,                 # Chunk index within document
                "total_chunks": len(chunks)    # Total chunks in document
            }
        )
        documents.append(doc)
    
    return documents
```

### 2. Vector Store Metadata

Each vector embedding in ChromaDB contains metadata that links back to the original document:

```python
# Example metadata in vector store
{
    "source": "storage/uploads/02ea38fc-a5c3-46fe-add3-223bc3356821_document.pdf",
    "filename": "document.pdf",
    "file_type": ".pdf",
    "file_size": 280818,
    "chunk_id": 0,
    "total_chunks": 15,
    "conversation_id": "conv_123",
    "document_id": "doc_456"
}
```

## Document Retrieval Process

### 1. Vector Search with Metadata Filtering

When retrieving relevant content, the system uses metadata to trace back to original documents:

```python
def _create_document_aware_prompt(self, user_message: str, document_context: List):
    """Create prompt with document content using vector metadata."""
    
    # Initialize conversation-specific retriever
    conversation_vector_store = VectorStore(conversation_id=conversation_id)
    rag_retriever = RAGRetriever(vector_store=conversation_vector_store)
    
    # Retrieve relevant chunks
    relevant_chunks = rag_retriever.retrieve_relevant_documents(
        user_message, k=30
    )
    
    # Filter chunks to specific documents using metadata
    for doc in document_context:
        document_chunks = []
        for chunk_doc, score in relevant_chunks:
            chunk_source = chunk_doc.metadata.get('source', '')
            chunk_filename = chunk_doc.metadata.get('filename', '')
            
            # Match by file path to ensure we get chunks from the right document
            file_path = doc.metadata.get('file_path', '')
            if chunk_source and file_path and file_path in chunk_source:
                document_chunks.append((chunk_doc, score))
                logger.info(f"Found document chunk for {doc.filename}: {chunk_filename} (score: {score})")
        
        # Process and combine chunks
        if document_chunks:
            # Sort by relevance score
            document_chunks.sort(key=lambda x: x[1], reverse=True)
            
            content_parts = []
            for chunk_doc, score in document_chunks[:5]:
                if score > 0.05:  # Relevance threshold
                    content_parts.append(chunk_doc.page_content.strip())
            
            if content_parts:
                combined_content = "\n\n".join(content_parts)
                documents_text.append(f"Document: {doc.filename}\nContent:\n{combined_content}")
```

### 2. Metadata-Based Document Filtering

The system uses multiple metadata fields to ensure accurate document retrieval:

```python
# Filter chunks by document using metadata matching
def filter_chunks_by_document(chunks, target_document):
    """Filter vector chunks to only include those from a specific document."""
    
    filtered_chunks = []
    target_file_path = target_document.metadata.get('file_path', '')
    
    for chunk_doc, score in chunks:
        chunk_metadata = chunk_doc.metadata
        
        # Multiple matching strategies for robustness
        matches = [
            # Direct file path matching
            target_file_path in chunk_metadata.get('source', ''),
            
            # Filename matching
            target_document.filename == chunk_metadata.get('filename', ''),
            
            # Document ID matching (if available)
            target_document.document_id == chunk_metadata.get('document_id', '')
        ]
        
        if any(matches):
            filtered_chunks.append((chunk_doc, score))
    
    return filtered_chunks
```

## Conversation-Specific Organization

### 1. Vector Store Collections

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

### 2. Metadata Enhancement

Additional metadata is added to link vectors to conversations:

```python
# Enhanced metadata for conversation awareness
enhanced_metadata = {
    **base_metadata,
    "conversation_id": conversation_id,
    "user_id": user_id,
    "upload_timestamp": datetime.now().isoformat(),
    "document_id": document_id
}
```

## Traceability Features

### 1. Complete Audit Trail

Every vector embedding can be traced back to its source:

```
Vector Embedding
       ↓
ChromaDB Metadata
       ↓
DocumentChunk Record
       ↓
ChatDocument Record
       ↓
Original File
```

### 2. Bidirectional Lookup

The system supports lookup in both directions:

```python
# From document to vectors
def get_document_vectors(document_id: str):
    """Get all vector embeddings for a specific document."""
    chunks = document_repo.get_document_chunks(document_id)
    vector_ids = [chunk.embedding_id for chunk in chunks if chunk.embedding_id]
    return vector_store.get_vectors_by_ids(vector_ids)

# From vector to document
def get_vector_source(vector_id: str):
    """Get the original document for a specific vector."""
    chunk = chunk_repo.get_chunk_by_embedding_id(vector_id)
    if chunk:
        document = document_repo.get_document(chunk.document_id)
        return document
    return None
```

### 3. Source Citation

When using document content in responses, the system provides source citations:

```python
def create_document_aware_prompt(self, user_message: str, document_context: List):
    """Create prompt with proper source citations."""
    
    documents_text = []
    for doc in document_context:
        if doc.summary:
            documents_text.append(f"Document: {doc.filename}\nSummary: {doc.summary}")
        else:
            # Get content with source tracking
            content_parts = self.get_document_content(doc)
            if content_parts:
                combined_content = "\n\n".join(content_parts)
                documents_text.append(f"Document: {doc.filename}\nContent:\n{combined_content}")
    
    if documents_text:
        document_context_text = "\n\n".join(documents_text)
        return f"""You are an AI assistant with access to the following documents:

{document_context_text}

User Question: {user_message}

Please answer using information from the documents when relevant, and cite the source document when you do so."""
```

## Data Integrity and Consistency

### 1. Referential Integrity

Database relationships ensure data consistency:

```python
# Foreign key constraints
document_id = Column(String(36), ForeignKey("chat_documents.id"), nullable=False, index=True)
conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, index=True)
user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
```

### 2. Cleanup Operations

When documents are deleted, all related data is cleaned up:

```python
def cleanup_conversation_documents(self, conversation_id: str):
    """Clean up all documents and related data for a conversation."""
    
    for document in documents:
        # Delete document chunks from database
        chunks_deleted = self.chunk_repo.delete_document_chunks(document.id)
        
        # Delete vector embeddings (handled by ChromaDB collection deletion)
        # Each conversation has its own collection, so deleting the collection
        # removes all vectors for that conversation
        
        # Delete physical file
        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # Delete document record
        self.document_repo.delete_document(document.id)
```

### 3. Metadata Validation

The system validates metadata consistency:

```python
def validate_document_metadata(document: ChatDocument):
    """Validate that document metadata is consistent."""
    
    # Check if original file exists
    if not Path(document.file_path).exists():
        logger.warning(f"Original file missing for document {document.id}")
        return False
    
    # Check if chunks exist
    chunks = document_repo.get_document_chunks(document.id)
    if not chunks:
        logger.warning(f"No chunks found for document {document.id}")
        return False
    
    # Check if vectors exist in vector store
    vector_store = VectorStore(conversation_id=document.conversation_id)
    for chunk in chunks:
        if chunk.embedding_id:
            # Verify vector exists in ChromaDB
            if not vector_store.vector_exists(chunk.embedding_id):
                logger.warning(f"Vector missing for chunk {chunk.id}")
                return False
    
    return True
```

## Performance Optimizations

### 1. Indexed Relationships

Database indexes ensure fast lookups:

```python
# Indexed foreign keys for fast joins
document_id = Column(String(36), ForeignKey("chat_documents.id"), nullable=False, index=True)
conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, index=True)
```

### 2. Cached Metadata

Frequently accessed metadata is cached:

```python
# Cache document metadata for fast access
@lru_cache(maxsize=1000)
def get_document_metadata(document_id: str):
    """Get cached document metadata."""
    return document_repo.get_document(document_id)
```

### 3. Batch Operations

Vector operations are batched for efficiency:

```python
def add_documents_batch(self, documents: List[LangChainDocument]):
    """Add multiple documents to vector store efficiently."""
    
    # Batch add to vector store
    self.vector_store.add_documents(documents)
    
    # Batch create database records
    chunk_records = []
    for i, doc in enumerate(documents):
        chunk_record = DocumentChunkCreate(
            document_id=doc.metadata.get('document_id'),
            chunk_text=doc.page_content,
            chunk_index=doc.metadata.get('chunk_id'),
            embedding_id=doc.metadata.get('embedding_id')
        )
        chunk_records.append(chunk_record)
    
    # Batch insert to database
    chunk_repo.create_chunks_batch(chunk_records)
```

## Error Handling and Recovery

### 1. Orphaned Vector Detection

The system can detect and handle orphaned vectors:

```python
def cleanup_orphaned_vectors(self):
    """Remove vectors that no longer have corresponding database records."""
    
    # Get all vector IDs from ChromaDB
    all_vector_ids = vector_store.get_all_vector_ids()
    
    # Get all embedding IDs from database
    db_embedding_ids = set(chunk_repo.get_all_embedding_ids())
    
    # Find orphaned vectors
    orphaned_ids = set(all_vector_ids) - db_embedding_ids
    
    # Remove orphaned vectors
    for vector_id in orphaned_ids:
        vector_store.delete_vector(vector_id)
        logger.info(f"Removed orphaned vector: {vector_id}")
```

### 2. Metadata Repair

The system can repair inconsistent metadata:

```python
def repair_document_metadata(self, document_id: str):
    """Repair metadata inconsistencies for a document."""
    
    document = document_repo.get_document(document_id)
    if not document:
        return False
    
    # Check if original file exists
    if not Path(document.file_path).exists():
        logger.error(f"Cannot repair document {document_id}: original file missing")
        return False
    
    # Re-process document to recreate vectors and metadata
    processor = DocumentProcessor()
    chunks = processor.process_file(document.file_path)
    
    # Update vector store
    vector_store = VectorStore(conversation_id=document.conversation_id)
    vector_store.add_documents(chunks)
    
    # Update database records
    chunk_repo.delete_document_chunks(document_id)
    for chunk in chunks:
        chunk_record = DocumentChunkCreate(
            document_id=document_id,
            chunk_text=chunk.page_content,
            chunk_index=chunk.metadata.get('chunk_id'),
            embedding_id=chunk.metadata.get('embedding_id')
        )
        chunk_repo.create_chunk(chunk_record)
    
    return True
```

## API Integration

### 1. Document Retrieval with Source Tracking

```python
@router.get("/documents/{conversation_id}/content/{document_id}")
async def get_document_content(
    conversation_id: str,
    document_id: str,
    query: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get document content with source tracking."""
    
    # Get document metadata
    document = document_repo.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get relevant chunks if query provided
    if query:
        vector_store = VectorStore(conversation_id=conversation_id)
        relevant_chunks = vector_store.similarity_search(query, k=10)
        
        # Filter to document-specific chunks
        document_chunks = filter_chunks_by_document(relevant_chunks, document)
        
        return {
            "document_id": document_id,
            "filename": document.filename,
            "query": query,
            "relevant_chunks": [
                {
                    "content": chunk.page_content,
                    "metadata": chunk.metadata,
                    "relevance_score": score
                }
                for chunk, score in document_chunks
            ]
        }
    
    # Return all chunks if no query
    chunks = document_repo.get_document_chunks(document_id)
    return {
        "document_id": document_id,
        "filename": document.filename,
        "total_chunks": len(chunks),
        "chunks": [
            {
                "chunk_id": chunk.id,
                "content": chunk.chunk_text,
                "chunk_index": chunk.chunk_index
            }
            for chunk in chunks
        ]
    }
```

### 2. Vector-Document Relationship Query

```python
@router.get("/vectors/{vector_id}/source")
async def get_vector_source(vector_id: str, db: Session = Depends(get_db)):
    """Get the source document for a specific vector."""
    
    # Find chunk with this embedding ID
    chunk = chunk_repo.get_chunk_by_embedding_id(vector_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Vector not found")
    
    # Get source document
    document = document_repo.get_document(chunk.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Source document not found")
    
    return {
        "vector_id": vector_id,
        "chunk_id": chunk.id,
        "document_id": document.id,
        "filename": document.filename,
        "file_path": document.file_path,
        "conversation_id": document.conversation_id,
        "chunk_content": chunk.chunk_text,
        "chunk_index": chunk.chunk_index
    }
```

## Benefits of This Relationship System

### 1. **Complete Traceability**
- Every vector can be traced back to its source document
- Full audit trail from embedding to original file
- Metadata preserves context and relationships

### 2. **Efficient Retrieval**
- Fast vector similarity search with metadata filtering
- Conversation-specific collections improve privacy
- Chunked content enables precise information retrieval

### 3. **Data Integrity**
- Referential integrity through database relationships
- Consistent cleanup operations
- Metadata validation and repair capabilities

### 4. **Source Citation**
- Accurate source attribution in responses
- Proper document citations for transparency
- Metadata-driven content attribution

### 5. **Scalable Architecture**
- Conversation-specific organization
- Efficient batch operations
- Cached metadata for performance

## Conclusion

The vector-document relationship system provides a robust, traceable connection between vector embeddings and their source documents. Through a combination of database relationships, metadata tracking, and conversation-specific organization, it ensures that every piece of retrieved content can be traced back to its original source while maintaining efficient retrieval performance.

This system enables document-aware conversations where the AI can provide accurate source citations and maintain context about which documents are being referenced, creating a transparent and trustworthy user experience.
