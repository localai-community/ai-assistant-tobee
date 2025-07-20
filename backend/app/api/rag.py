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
from ..core.database import get_db
from ..core.models import ErrorResponse

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/rag", tags=["rag"])

# Initialize services
rag_retriever = RAGRetriever()
chat_service = ChatService()

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
                async for chunk in chat_service.generate_streaming_response(
                    message=enhanced_prompt,
                    model=request.model,
                    temperature=request.temperature,
                    conversation_id=request.conversation_id
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'response': chunk})}\n\n"
                
                # Send completion signal with RAG context
                yield f"data: {json.dumps({
                    'done': True,
                    'rag_context': rag_context,
                    'has_context': has_context
                })}\n\n"
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
    db: Session = Depends(get_db)
):
    """
    Upload and process a document for RAG.
    
    Args:
        file: Document file to upload
        db: Database session
        
    Returns:
        dict: Upload and processing results
    """
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.txt', '.md'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file to upload directory
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document with RAG
        result = rag_retriever.add_document(str(file_path))
        
        if result["success"]:
            return {
                "success": True,
                "filename": file.filename,
                "file_size": file.size,
                "chunks_created": result.get("chunks_created", 0),
                "stats": result.get("stats", {}),
                "message": f"Document '{file.filename}' processed successfully"
            }
        else:
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