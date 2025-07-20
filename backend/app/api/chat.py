"""
LocalAI Community - Chat API Endpoints
API routes for chat functionality with Ollama integration.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional
from sqlalchemy.orm import Session
import json
import logging
import os

from ..services.chat import ChatService, ChatRequest, ChatResponse, Conversation
from ..core.database import get_db
from ..core.models import ErrorResponse

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message and get a response from the AI model.
    
    Args:
        request: Chat request containing message and parameters
        db: Database session
        
    Returns:
        ChatResponse: AI response with conversation details
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
        
        # Generate response
        response = await chat_service.generate_response(
            message=request.message,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            conversation_id=request.conversation_id
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        
        async def generate_stream():
            async for chunk in chat_service.generate_streaming_response(
                message=request.message,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                conversation_id=request.conversation_id
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        
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
    Get list of available Ollama models.
    
    Args:
        db: Database session
        
    Returns:
        List[str]: Available model names
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        models = await chat_service.get_available_models()
        return models
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
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
async def list_conversations(db: Session = Depends(get_db)):
    """
    List all conversations.
    
    Args:
        db: Database session
        
    Returns:
        List[Conversation]: All conversations
    """
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        return chat_service.list_conversations()
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