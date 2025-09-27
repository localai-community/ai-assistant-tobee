"""
LocalAI Community - RAG API Endpoints
API routes for document upload, processing, and RAG functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import os
import logging
from pathlib import Path
import shutil
import json
import asyncio
from pydantic import BaseModel

from ..services.rag.retriever import RAGRetriever
from ..services.chat import ChatService
from ..services.repository import ChatDocumentRepository, DocumentChunkRepository
from ..services.document_summary import DocumentSummaryService
from ..services.document_manager import DocumentManager
from ..core.database import get_db
from ..core.models import ErrorResponse
from ..models.schemas import ChatDocumentCreate, ChatDocumentUpdate

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/rag", tags=["rag"])

# Initialize services
rag_retriever = RAGRetriever()
# chat_service will be created per request with database access

# Ensure upload directory exists
UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class RAGStreamRequest(BaseModel):
    message: str
    model: str = "llama3:latest"
    temperature: float = 0.7
    conversation_id: Optional[str] = None
    k: int = 4
    filter_dict: Optional[Dict[str, Any]] = None

@router.post("/stream")
async def rag_stream_chat(request: RAGStreamRequest, db: Session = Depends(get_db)):
    """
    Stream RAG-enhanced chat response.
    
    Args:
        request: RAG stream request with message and parameters
        db: Database session
        
    Returns:
        StreamingResponse: Server-sent events with RAG-enhanced response
    """
    try:
        # Get RAG context first
        enhanced_prompt = rag_retriever.create_intelligent_rag_prompt(
            request.message, 
            request.k, 
            request.filter_dict
        )
        

        
        # Get RAG context information
        rag_context = ""
        has_context = False
        try:
            relevant_docs = rag_retriever.retrieve_relevant_documents(
                request.message, 
                request.k, 
                request.filter_dict
            )
            if relevant_docs:
                has_context = True
                rag_context = rag_retriever.get_context_for_query(
                    request.message, 
                    request.k, 
                    request.filter_dict
                )
        except Exception as e:
            logger.warning(f"Could not get RAG context: {e}")
        
        # Stream the response using the chat service
        async def generate_stream():
            try:
                full_response = ""
                
                # Create a proper chat service instance with database
                ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
                rag_chat_service = ChatService(ollama_url=ollama_url, db=db)
                
                # Use a simpler prompt format for streaming
                simple_prompt = f"Answer this question: {request.message}"
                if has_context:
                    simple_prompt += f"\n\nUse this context: {rag_context}"
                
                async for chunk in rag_chat_service.generate_streaming_response(
                    message=simple_prompt,
                    model=request.model,
                    temperature=request.temperature,
                    conversation_id=request.conversation_id
                ):
                    full_response += chunk
                    # Use the same format as regular streaming
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                
                # Send completion signal with RAG context
                yield f"data: {json.dumps({'content': '', 'rag_context': rag_context, 'has_context': has_context})}\n\n"
            except Exception as e:
                error_chunk = {"error": str(e), "type": "error"}
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"RAG stream error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document for RAG with conversation-scoped storage.
    
    Args:
        file: Document file to upload
        conversation_id: Optional conversation ID for chat-scoped storage
        user_id: Optional user ID for document ownership
        db: Database session
        
    Returns:
        dict: Upload and processing results
    """
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.txt', '.md', '.doc'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Create unique filename to avoid conflicts
        import uuid
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file to upload directory
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Initialize repositories
        document_repo = ChatDocumentRepository(db)
        chunk_repo = DocumentChunkRepository(db)
        
        # Create conversation if it doesn't exist and conversation_id is provided
        if conversation_id:
            from ..services.repository import ConversationRepository
            from ..models.schemas import ConversationCreate
            from datetime import datetime
            
            conversation_repo = ConversationRepository(db)
            existing_conversation = conversation_repo.get_conversation(conversation_id)
            
            if not existing_conversation:
                # Create new conversation
                conversation_data = ConversationCreate(
                    title=f"Document Upload - {file.filename}",
                    model="llama3:latest",
                    user_id=user_id
                )
                new_conversation = conversation_repo.create_conversation(conversation_data, conversation_id)
                logger.info(f"Created new conversation for document upload: {conversation_id}")
            else:
                logger.info(f"Using existing conversation: {conversation_id}")
        
        # Create chat document record
        document_data = ChatDocumentCreate(
            filename=file.filename,
            file_type=file_extension,
            file_size=file.size,
            file_path=str(file_path),
            conversation_id=conversation_id or "global",
            user_id=user_id
        )
        
        chat_document = document_repo.create_document(document_data)
        
        # Process document with RAG using conversation-specific retriever
        from ..services.rag.vector_store import VectorStore
        logger.info(f"Creating conversation-specific vector store for conversation_id: {conversation_id}")
        conversation_vector_store = VectorStore(conversation_id=conversation_id)
        logger.info(f"Vector store created with collection: {conversation_vector_store.collection_name}")
        conversation_rag_retriever = RAGRetriever(vector_store=conversation_vector_store)
        result = conversation_rag_retriever.add_document(str(file_path))
        
        if result["success"]:
            # Update document status
            document_repo.update_document(chat_document.id, {
                "processing_status": "processed"
            })
            
            return {
                "success": True,
                "document_id": chat_document.id,
                "filename": file.filename,
                "file_size": file.size,
                "conversation_id": conversation_id,
                "user_id": user_id,
                "chunks_created": result.get("chunks_created", 0),
                "stats": result.get("stats", {}),
                "message": f"Document '{file.filename}' processed successfully"
            }
        else:
            # Update document status to failed
            document_repo.update_document(chat_document.id, {
                "processing_status": "failed"
            })
            
            # Clean up file if processing failed
            if file_path.exists():
                file_path.unlink()
            
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process document: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{conversation_id}")
async def get_conversation_documents(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all documents for a specific conversation.
    
    Args:
        conversation_id: Conversation ID
        db: Database session
        
    Returns:
        List of documents in the conversation
    """
    try:
        document_repo = ChatDocumentRepository(db)
        documents = document_repo.get_conversation_documents(conversation_id)
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "file_type": doc.file_type,
                    "file_size": doc.file_size,
                    "upload_timestamp": doc.upload_timestamp,
                    "summary_text": doc.summary_text,
                    "summary_type": doc.summary_type,
                    "processing_status": doc.processing_status
                }
                for doc in documents
            ],
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error getting conversation documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a document from the system.
    
    Args:
        document_id: Document ID to delete
        db: Database session
        
    Returns:
        Success confirmation
    """
    try:
        document_repo = ChatDocumentRepository(db)
        chunk_repo = DocumentChunkRepository(db)
        
        # Get document info before deletion
        document = document_repo.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete document chunks first
        chunk_repo.delete_document_chunks(document_id)
        
        # Delete the document
        success = document_repo.delete_document(document_id)
        
        if success:
            # Clean up file
            file_path = Path(document.file_path)
            if file_path.exists():
                file_path.unlink()
            
            return {
                "success": True,
                "message": f"Document '{document.filename}' deleted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete document")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize/{document_id}")
async def summarize_document(
    document_id: str,
    summary_type: str = "brief",
    conversation_context: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Generate a summary for a document.
    
    Args:
        document_id: Document ID to summarize
        summary_type: Type of summary (brief, detailed, key_points, executive)
        conversation_context: Optional conversation context
        db: Database session
        
    Returns:
        Document summary
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        summary_service = DocumentSummaryService(ollama_url, db)
        
        result = await summary_service.generate_summary(
            document_id, 
            summary_type, 
            conversation_context
        )
        
        if result["success"]:
            return {
                "success": True,
                "document_id": document_id,
                "summary": result["summary"],
                "summary_type": summary_type,
                "cached": result.get("cached", False)
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize/{document_id}/multi")
async def summarize_document_multi(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate multiple types of summaries for a document.
    
    Args:
        document_id: Document ID to summarize
        db: Database session
        
    Returns:
        Multiple summary types
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        summary_service = DocumentSummaryService(ollama_url, db)
        
        result = await summary_service.generate_multi_level_summary(document_id)
        
        if result["success"]:
            return {
                "success": True,
                "document_id": document_id,
                "summaries": result["summaries"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating multi-level summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/document/{document_id}/summary")
async def get_document_summary(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get existing summary for a document.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Document summary if available
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        summary_service = DocumentSummaryService(ollama_url, db)
        
        result = await summary_service.get_document_summary(document_id)
        
        if result["success"]:
            return {
                "success": True,
                "document_id": document_id,
                "summary": result["summary"],
                "summary_type": result["summary_type"],
                "created_at": result["created_at"]
            }
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/analytics/{user_id}")
async def get_document_analytics(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get document usage analytics for a user.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Document analytics
    """
    try:
        document_manager = DocumentManager(db)
        analytics = document_manager.get_document_analytics(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "analytics": analytics
        }
    except Exception as e:
        logger.error(f"Error getting document analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/health")
async def get_document_health(db: Session = Depends(get_db)):
    """
    Get document system health status.
    
    Args:
        db: Database session
        
    Returns:
        Document system health
    """
    try:
        document_manager = DocumentManager(db)
        health = document_manager.get_document_health()
        
        return {
            "success": True,
            "health": health
        }
    except Exception as e:
        logger.error(f"Error getting document health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/cleanup/{conversation_id}")
async def cleanup_conversation_documents(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """
    Clean up all documents for a conversation.
    
    Args:
        conversation_id: Conversation ID
        db: Database session
        
    Returns:
        Cleanup results
    """
    try:
        document_manager = DocumentManager(db)
        cleanup_stats = document_manager.cleanup_conversation_documents(conversation_id)
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "cleanup_stats": cleanup_stats
        }
    except Exception as e:
        logger.error(f"Error cleaning up conversation documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/archive/{document_id}")
async def archive_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Archive a document for long-term storage.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Archive result
    """
    try:
        document_manager = DocumentManager(db)
        success = document_manager.archive_document(document_id)
        
        if success:
            return {
                "success": True,
                "message": f"Document {document_id} archived successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error archiving document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/restore/{document_id}")
async def restore_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Restore an archived document.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Restore result
    """
    try:
        document_manager = DocumentManager(db)
        success = document_manager.restore_document(document_id)
        
        if success:
            return {
                "success": True,
                "message": f"Document {document_id} restored successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restoring document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/cleanup-old")
async def cleanup_old_documents(
    days_old: int = 30,
    db: Session = Depends(get_db)
):
    """
    Clean up documents older than specified days.
    
    Args:
        days_old: Number of days old (default: 30)
        db: Database session
        
    Returns:
        Cleanup results
    """
    try:
        document_manager = DocumentManager(db)
        cleanup_stats = document_manager.cleanup_old_documents(days_old)
        
        return {
            "success": True,
            "days_old": days_old,
            "cleanup_stats": cleanup_stats
        }
    except Exception as e:
        logger.error(f"Error cleaning up old documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-directory")
async def upload_directory(
    directory_path: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Process all documents in a directory for RAG.
    
    Args:
        directory_path: Path to directory containing documents
        db: Database session
        
    Returns:
        dict: Processing results
    """
    try:
        # Validate directory exists
        if not Path(directory_path).exists():
            raise HTTPException(
                status_code=400,
                detail=f"Directory not found: {directory_path}"
            )
        
        # Process directory with RAG
        result = rag_retriever.add_documents_from_directory(directory_path)
        
        if result["success"]:
            return {
                "success": True,
                "directory_path": directory_path,
                "total_chunks": result.get("total_chunks", 0),
                "stats": result.get("stats", {}),
                "message": f"Directory '{directory_path}' processed successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process directory: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Directory upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_documents(
    query: str = Form(...),
    k: int = Form(10),
    filter_dict: Optional[Dict[str, Any]] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Search documents in the RAG system.
    
    Args:
        query: Search query
        k: Number of results to return
        filter_dict: Optional metadata filter
        db: Database session
        
    Returns:
        dict: Search results
    """
    try:
        results = rag_retriever.search_documents(query, k, filter_dict)
        
        return {
            "success": True,
            "query": query,
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat-with-rag")
async def chat_with_rag(
    message: str = Form(...),
    k: int = Form(4),
    filter_dict: Optional[Dict[str, Any]] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Get RAG-enhanced context for a chat message.
    
    Args:
        message: User message
        k: Number of relevant documents to retrieve
        filter_dict: Optional metadata filter
        db: Database session
        
    Returns:
        dict: RAG context and enhanced prompt
    """
    try:
        # Get relevant documents and create intelligent prompt
        relevant_docs = rag_retriever.retrieve_relevant_documents(message, k, filter_dict)
        
        # Create intelligent prompt that adapts based on available context
        enhanced_prompt = rag_retriever.create_intelligent_rag_prompt(message, k, filter_dict)
        
        # Format context for display
        context_parts = []
        for doc, score in relevant_docs:
            context_parts.append(f"Document: {doc.metadata.get('filename', 'Unknown')}")
            context_parts.append(f"Relevance: {score:.3f}")
            context_parts.append(f"Content: {doc.page_content[:200]}...")
            context_parts.append("---")
        
        context = "\n".join(context_parts)
        
        return {
            "success": True,
            "has_context": True,
            "message": message,
            "context": context,
            "enhanced_prompt": enhanced_prompt,
            "relevant_documents_count": len(relevant_docs)
        }
        
    except Exception as e:
        logger.error(f"RAG chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_rag_stats(db: Session = Depends(get_db)):
    """
    Get RAG system statistics.
    
    Args:
        db: Database session
        
    Returns:
        dict: RAG system statistics
    """
    try:
        stats = rag_retriever.get_system_stats()
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def rag_health(db: Session = Depends(get_db)):
    """
    Check RAG system health.
    
    Args:
        db: Database session
        
    Returns:
        dict: Health status
    """
    try:
        health = rag_retriever.health_check()
        return {
            "success": True,
            "health": health
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "success": False,
            "health": {
                "status": "error",
                "error": str(e)
            }
        }

@router.delete("/documents")
async def clear_documents(db: Session = Depends(get_db)):
    """
    Clear all documents from the RAG system.
    
    Args:
        db: Database session
        
    Returns:
        dict: Operation result
    """
    try:
        success = rag_retriever.clear_all_documents()
        
        if success:
            return {
                "success": True,
                "message": "All documents cleared from RAG system"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to clear documents"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clear documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/by-metadata")
async def delete_documents_by_metadata(
    metadata_filter: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Delete documents based on metadata filter.
    
    Args:
        metadata_filter: Metadata filter criteria
        db: Database session
        
    Returns:
        dict: Operation result
    """
    try:
        success = rag_retriever.delete_documents_by_metadata(metadata_filter)
        
        if success:
            return {
                "success": True,
                "message": f"Documents deleted with filter: {metadata_filter}"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete documents"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 