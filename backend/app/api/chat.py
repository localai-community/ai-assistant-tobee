"""
LocalAI Community - Chat API Endpoints
API routes for chat functionality with Ollama integration.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional
import json
import logging

from ..services.chat import (
    chat_service, 
    ChatRequest, 
    ChatResponse, 
    Conversation
)
from ..core.models import ErrorResponse

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get a response from the AI model.
    
    Args:
        request: Chat request containing message and parameters
        
    Returns:
        ChatResponse: AI response with conversation details
    """
    try:
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
async def chat_stream(request: ChatRequest):
    """
    Send a message and get a streaming response from the AI model.
    
    Args:
        request: Chat request containing message and parameters
        
    Returns:
        StreamingResponse: Stream of AI response chunks
    """
    try:
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
async def get_models():
    """
    Get list of available Ollama models.
    
    Returns:
        List[str]: Available model names
    """
    try:
        models = await chat_service.get_available_models()
        return models
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def chat_health():
    """
    Check chat service health and Ollama availability.
    
    Returns:
        dict: Health status information
    """
    try:
        ollama_healthy = await chat_service.check_ollama_health()
        models = await chat_service.get_available_models() if ollama_healthy else []
        
        return {
            "status": "healthy" if ollama_healthy else "unhealthy",
            "ollama_available": ollama_healthy,
            "available_models": models,
            "conversation_count": len(chat_service.conversations)
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "error",
            "ollama_available": False,
            "available_models": [],
            "conversation_count": len(chat_service.conversations),
            "error": str(e)
        }

@router.get("/conversations", response_model=List[Conversation])
async def list_conversations():
    """
    List all conversations.
    
    Returns:
        List[Conversation]: All conversations
    """
    try:
        return chat_service.list_conversations()
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """
    Get a specific conversation by ID.
    
    Args:
        conversation_id: Unique conversation identifier
        
    Returns:
        Conversation: Conversation details
    """
    try:
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
async def delete_conversation(conversation_id: str):
    """
    Delete a specific conversation.
    
    Args:
        conversation_id: Unique conversation identifier
        
    Returns:
        dict: Deletion status
    """
    try:
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
async def clear_conversations():
    """
    Clear all conversations.
    
    Returns:
        dict: Clear status with count
    """
    try:
        count = chat_service.clear_conversations()
        return {
            "message": f"Cleared {count} conversations successfully",
            "deleted_count": count
        }
    except Exception as e:
        logger.error(f"Failed to clear conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 