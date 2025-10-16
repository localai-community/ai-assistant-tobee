"""
LocalAI Community - Chat API Endpoints
API routes for chat functionality with Ollama integration.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
from sqlalchemy.orm import Session
import json
import logging
import os
from functools import lru_cache
import uuid
from datetime import datetime
from pathlib import Path

from ..services.chat import ChatService, ChatRequest, ChatResponse, Conversation
from ..services.document_manager import DocumentManager
from ..services.rag.document_processor import DocumentProcessor
from ..services.rag.vector_store import VectorStore
from ..core.database import get_db
from ..core.models import ErrorResponse
from ..models.schemas import Message

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Cache for frequently accessed data
_models_cache = {}
_models_cache_time = 0
CACHE_TTL = 60  # 1 minute cache

# Removed non-streaming chat endpoint - only streaming is supported

@router.post("/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message and get a streaming response from the AI model.
    
    Args:
        request: Chat request containing message and parameters
        db: Database session
        
    Returns:
        StreamingResponse: Stream of AI response chunks
    """
    try:
        # Create chat service with database
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        
        # Check if Ollama is available
        if not await chat_service.check_ollama_health():
            raise HTTPException(
                status_code=503,
                detail="Ollama service is not available. Please make sure Ollama is running."
            )
        
        # Get or create conversation ID
        conversation_id = request.conversation_id
        if not conversation_id and chat_service.conversation_repo:
            # Create new conversation in database
            from app.models.schemas import ConversationCreate
            from datetime import datetime
            conversation_data = ConversationCreate(
                title=f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                model=request.model,
                user_id=request.user_id
            )
            conversation = chat_service.conversation_repo.create_conversation(conversation_data)
            conversation_id = conversation.id
        
        async def generate_stream():
            first_chunk = True
            async for chunk in chat_service.generate_streaming_response(
                message=request.message,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                conversation_id=conversation_id,
                enable_context_awareness=request.enable_context_awareness,
                include_memory=request.include_memory,
                context_strategy=request.context_strategy,
                user_id=request.user_id
            ):
                if first_chunk:
                    # Send metadata in the first chunk
                    yield f"data: {json.dumps({'content': chunk, 'conversation_id': conversation_id, 'type': 'metadata'})}\n\n"
                    first_chunk = False
                else:
                    # Send content chunks
                    yield f"data: {json.dumps({'content': chunk, 'type': 'content'})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        logger.error(f"Chat stream error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models", response_model=List[str])
async def get_models(db: Session = Depends(get_db)):
    """
    Get list of available Ollama models with caching for performance.
    
    Args:
        db: Database session
        
    Returns:
        List[str]: Available model names
    """
    import time
    
    global _models_cache_time, _models_cache
    
    # Check cache first
    current_time = time.time()
    if current_time - _models_cache_time < CACHE_TTL and _models_cache:
        return _models_cache.get("models", [])
    
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        models = await chat_service.get_available_models()
        
        # Update cache
        _models_cache["models"] = models
        _models_cache_time = current_time
        
        return models
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        # Return cached models if available, even if expired
        if _models_cache.get("models"):
            logger.warning("Returning cached models due to error")
            return _models_cache["models"]
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def chat_health(db: Session = Depends(get_db)):
    """
    Check chat service health and Ollama availability.
    
    Args:
        db: Database session
        
    Returns:
        dict: Health status information
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        ollama_healthy = await chat_service.check_ollama_health()
        models = await chat_service.get_available_models() if ollama_healthy else []
        conversations = chat_service.list_conversations()
        
        return {
            "status": "healthy" if ollama_healthy else "unhealthy",
            "ollama_available": ollama_healthy,
            "available_models": models,
            "conversation_count": len(conversations)
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "error",
            "ollama_available": False,
            "available_models": [],
            "conversation_count": 0,
            "error": str(e)
        }

@router.get("/conversations", response_model=List[Conversation])
async def list_conversations(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    List conversations, optionally filtered by user.
    
    Args:
        user_id: Optional user ID to filter conversations
        db: Database session
        
    Returns:
        List[Conversation]: Conversations for the specified user (or all if no user_id)
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        return chat_service.list_conversations(user_id=user_id)
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    Get a specific conversation by ID.
    
    Args:
        conversation_id: Unique conversation identifier
        db: Database session
        
    Returns:
        Conversation: Conversation details
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        conversation = chat_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_conversation_messages(conversation_id: str, db: Session = Depends(get_db)):
    """
    Get messages for a specific conversation.
    
    Args:
        conversation_id: Unique conversation identifier
        db: Database session
        
    Returns:
        List[Message]: Messages in the conversation
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        
        # Check if conversation exists
        conversation = chat_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages for the conversation
        if chat_service.message_repo:
            messages = chat_service.message_repo.get_messages(conversation_id)
            return messages
        else:
            return []
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    Delete a specific conversation.
    
    Args:
        conversation_id: Unique conversation identifier
        db: Database session
        
    Returns:
        dict: Deletion status
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        deleted = chat_service.delete_conversation(conversation_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversations")
async def clear_conversations(db: Session = Depends(get_db)):
    """
    Clear all conversations.
    
    Args:
        db: Database session
        
    Returns:
        dict: Clear status with count
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        count = chat_service.clear_conversations()
        return {
            "message": f"Cleared {count} conversations successfully",
            "deleted_count": count
        }
    except Exception as e:
        logger.error(f"Failed to clear conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# MCP Tool Endpoints
@router.get("/tools")
async def list_mcp_tools(db: Session = Depends(get_db)):
    """
    List all available MCP tools.
    
    Args:
        db: Database session
        
    Returns:
        List[dict]: Available MCP tools
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        mcp_config_path = os.getenv("MCP_CONFIG_PATH", "mcp-config-local.json")
        chat_service = ChatService(ollama_url=ollama_url, db=db, mcp_config_path=mcp_config_path)
        tools = await chat_service.get_available_tools()
        return tools
    except Exception as e:
        logger.error(f"Failed to list MCP tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/{tool_name}/call")
async def call_mcp_tool(tool_name: str, arguments: dict, db: Session = Depends(get_db)):
    """
    Call a specific MCP tool.
    
    Args:
        tool_name: Name of the tool to call (format: server.tool)
        arguments: Tool arguments
        db: Database session
        
    Returns:
        dict: Tool execution result
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        mcp_config_path = os.getenv("MCP_CONFIG_PATH", "mcp-config-local.json")
        chat_service = ChatService(ollama_url=ollama_url, db=db, mcp_config_path=mcp_config_path)
        result = await chat_service.call_mcp_tool(tool_name, arguments)
        return result
    except Exception as e:
        logger.error(f"Failed to call MCP tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools/health")
async def mcp_health_check(db: Session = Depends(get_db)):
    """
    Check MCP tools health status.
    
    Args:
        db: Database session
        
    Returns:
        dict: MCP health status
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        mcp_config_path = os.getenv("MCP_CONFIG_PATH", "mcp-config-local.json")
        chat_service = ChatService(ollama_url=ollama_url, db=db, mcp_config_path=mcp_config_path)
        
        # Ensure MCP manager is initialized
        await chat_service._ensure_mcp_initialized()
        
        # Get MCP manager health
        health_status = await chat_service.mcp_manager.health_check()
        
        return {
            "mcp_enabled": chat_service.mcp_initialized,
            "servers": health_status["servers"],
            "tools_count": health_status["tools_count"],
            "overall_healthy": health_status["overall_healthy"]
        }
    except Exception as e:
        logger.error(f"MCP health check error: {e}")
        return {
            "mcp_enabled": False,
            "servers": {},
            "tools_count": 0,
            "overall_healthy": False,
            "error": str(e)
        }

# Context Awareness Endpoints
@router.get("/context/{conversation_id}")
async def get_conversation_context(conversation_id: str, user_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get comprehensive context information for a conversation.
    
    Args:
        conversation_id: Unique conversation identifier
        user_id: Optional user ID for personalized context
        db: Database session
        
    Returns:
        dict: Conversation context information
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        
        context = chat_service.context_service.get_conversation_context(
            conversation_id=conversation_id,
            user_id=user_id,
            include_memory=True
        )
        
        return {
            "conversation_id": context.conversation_id,
            "user_id": context.user_id,
            "topics": context.topics,
            "entities": [
                {
                    "text": entity.text,
                    "type": entity.entity_type,
                    "importance": entity.importance_score,
                    "mentions": entity.mention_count
                }
                for entity in context.key_entities
            ],
            "user_preferences": context.user_preferences,
            "conversation_style": context.conversation_style,
            "summary": context.summary_text,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get conversation context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context/user/{user_id}")
async def get_user_context(user_id: str, include_cross_conversation: bool = True, db: Session = Depends(get_db)):
    """
    Get comprehensive user context across all conversations.
    
    Args:
        user_id: Unique user identifier
        include_cross_conversation: Include context from all user's conversations
        db: Database session
        
    Returns:
        dict: User context information
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        
        user_context = chat_service.context_service.get_user_context(
            user_id=user_id,
            include_cross_conversation=include_cross_conversation
        )
        
        return user_context
        
    except Exception as e:
        logger.error(f"Failed to get user context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/context/{conversation_id}/memory")
async def store_conversation_memory(conversation_id: str, db: Session = Depends(get_db)):
    """
    Store conversation as memory chunks for long-term retrieval.
    
    Args:
        conversation_id: Unique conversation identifier
        db: Database session
        
    Returns:
        dict: Memory storage status
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        
        # Get conversation messages
        conversation = chat_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Convert to message dicts
        messages = []
        if chat_service.message_repo:
            db_messages = chat_service.message_repo.get_messages(conversation_id)
            messages = [
                {"role": msg.role, "content": msg.content, "created_at": msg.created_at}
                for msg in db_messages
            ]
        
        # Store as memory
        success = chat_service.context_service.store_conversation_memory(
            conversation_id=conversation_id,
            messages=messages
        )
        
        return {
            "success": success,
            "message": "Conversation memory stored successfully" if success else "Failed to store conversation memory",
            "conversation_id": conversation_id,
            "message_count": len(messages)
        }
        
    except Exception as e:
        logger.error(f"Failed to store conversation memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a document for RAG processing.
    
    Args:
        file: The uploaded file
        conversation_id: Optional conversation ID to associate with the document
        user_id: Optional user ID to associate with the document
        db: Database session
        
    Returns:
        dict: Upload result with document information
    """
    try:
        # Validate file type
        allowed_types = ['.pdf', '.docx', '.txt', '.md', '.doc']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Create upload directory if it doesn't exist
        upload_dir = Path("storage/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / f"{document_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Initialize services
        document_manager = DocumentManager(db)
        document_processor = DocumentProcessor()
        vector_store = VectorStore(conversation_id=conversation_id)
        
        # Process document
        documents = document_processor.process_file(str(file_path))
        
        if not documents:
            # Clean up file if processing failed
            file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail="Failed to process document. The file may be empty or corrupted."
            )
        
        # Store in vector database
        vector_store.add_documents(documents)
        
        # Create document record in database
        from ..models.schemas import ChatDocumentCreate
        document_data = ChatDocumentCreate(
            id=document_id,
            filename=file.filename,
            file_path=str(file_path),
            file_type=file_extension,
            file_size=len(content),
            conversation_id=conversation_id,
            user_id=user_id,
            processing_status="completed",
            upload_timestamp=datetime.now()
        )
        
        document = document_manager.document_repo.create_document(document_data)
        
        # Generate automatic summary
        try:
            from ..services.document_summary import DocumentSummaryService
            summary_service = DocumentSummaryService(ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434"), db=db)
            
            # Generate a brief summary
            summary_result = await summary_service.generate_summary(
                document_id=document_id,
                summary_type="brief"
            )
            
            if summary_result.get("success"):
                logger.info(f"Generated summary for document {document_id}")
            else:
                logger.warning(f"Failed to generate summary for document {document_id}: {summary_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error generating summary for document {document_id}: {e}")
            # Don't fail the upload if summary generation fails
        
        return {
            "success": True,
            "document_id": document_id,
            "filename": file.filename,
            "file_type": file_extension,
            "file_size": len(content),
            "chunks_created": len(documents),
            "conversation_id": conversation_id,
            "message": f"Document '{file.filename}' uploaded and processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/documents/{conversation_id}")
async def get_conversation_documents(conversation_id: str, db: Session = Depends(get_db)):
    """
    Get all documents for a conversation.
    
    Args:
        conversation_id: The conversation ID
        db: Database session
        
    Returns:
        dict: List of documents for the conversation
    """
    try:
        document_manager = DocumentManager(db)
        documents = document_manager.document_repo.get_conversation_documents(conversation_id)
        
        document_list = []
        for doc in documents:
            document_list.append({
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "processing_status": doc.processing_status,
                "upload_timestamp": doc.upload_timestamp.isoformat(),
                "summary_text": getattr(doc, 'summary_text', None)
            })
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "documents": document_list,
            "total_documents": len(document_list)
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get documents: {str(e)}") 