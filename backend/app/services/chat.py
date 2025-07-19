"""
LocalAI Community - Chat Service
Direct Ollama integration with streaming responses and conversation management.
"""

import httpx
import json
import asyncio
from typing import AsyncGenerator, Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    """Represents a chat message."""
    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")

class ChatRequest(BaseModel):
    """Request model for chat API."""
    message: str = Field(..., description="User message")
    model: str = Field(default="llama3.2", description="Ollama model to use")
    stream: bool = Field(default=True, description="Enable streaming response")
    temperature: float = Field(default=0.7, description="Model temperature (0.0-1.0)")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID for context")

class ChatResponse(BaseModel):
    """Response model for chat API."""
    response: str = Field(..., description="AI response")
    model: str = Field(..., description="Model used")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    tokens_used: Optional[int] = Field(default=None, description="Tokens used in response")

class Conversation(BaseModel):
    """Represents a conversation session."""
    id: str = Field(..., description="Unique conversation ID")
    messages: List[ChatMessage] = Field(default_factory=list, description="Conversation messages")
    model: str = Field(default="llama3.2", description="Model used for this conversation")
    created_at: datetime = Field(default_factory=datetime.now, description="Conversation creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")

class ChatService:
    """Service for handling chat interactions with Ollama."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.conversations: Dict[str, Conversation] = {}
        self.http_client = httpx.AsyncClient(timeout=60.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    async def check_ollama_health(self) -> bool:
        """Check if Ollama is running and healthy."""
        try:
            response = await self.http_client.get(f"{self.ollama_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def get_available_models(self) -> List[str]:
        """Get list of available Ollama models."""
        try:
            response = await self.http_client.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    async def generate_response(
        self, 
        message: str, 
        model: str = "llama3.2",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        conversation_id: Optional[str] = None
    ) -> ChatResponse:
        """Generate a response from Ollama."""
        
        # Get or create conversation
        if conversation_id and conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
        else:
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            conversation = Conversation(id=conversation_id, model=model)
            self.conversations[conversation_id] = conversation
        
        # Add user message to conversation
        user_message = ChatMessage(role="user", content=message)
        conversation.messages.append(user_message)
        conversation.updated_at = datetime.now()
        
        # Prepare messages for Ollama
        messages = []
        for msg in conversation.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            # Send request to Ollama
            response = await self.http_client.post(
                f"{self.ollama_url}/api/chat",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("message", {}).get("content", "")
                
                # Add AI response to conversation
                ai_message = ChatMessage(role="assistant", content=ai_response)
                conversation.messages.append(ai_message)
                conversation.updated_at = datetime.now()
                
                return ChatResponse(
                    response=ai_response,
                    model=model,
                    conversation_id=conversation_id,
                    tokens_used=data.get("eval_count")
                )
            else:
                error_msg = f"Ollama API error: {response.status_code}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    async def generate_streaming_response(
        self, 
        message: str, 
        model: str = "llama3.2",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from Ollama."""
        
        # Get or create conversation
        if conversation_id and conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
        else:
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            conversation = Conversation(id=conversation_id, model=model)
            self.conversations[conversation_id] = conversation
        
        # Add user message to conversation
        user_message = ChatMessage(role="user", content=message)
        conversation.messages.append(user_message)
        conversation.updated_at = datetime.now()
        
        # Prepare messages for Ollama
        messages = []
        for msg in conversation.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            # Send streaming request to Ollama
            async with self.http_client.stream(
                "POST",
                f"{self.ollama_url}/api/chat",
                json=payload
            ) as response:
                
                if response.status_code != 200:
                    error_msg = f"Ollama API error: {response.status_code}"
                    logger.error(error_msg)
                    yield f"Error: {error_msg}"
                    return
                
                full_response = ""
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "message" in data:
                                content = data["message"].get("content", "")
                                full_response += content
                                yield content
                        except json.JSONDecodeError:
                            continue
                
                # Add complete AI response to conversation
                if full_response:
                    ai_message = ChatMessage(role="assistant", content=full_response)
                    conversation.messages.append(ai_message)
                    conversation.updated_at = datetime.now()
                
        except Exception as e:
            logger.error(f"Failed to generate streaming response: {e}")
            yield f"Error: {str(e)}"
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self.conversations.get(conversation_id)
    
    def list_conversations(self) -> List[Conversation]:
        """List all conversations."""
        return list(self.conversations.values())
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False
    
    def clear_conversations(self) -> int:
        """Clear all conversations and return count of deleted conversations."""
        count = len(self.conversations)
        self.conversations.clear()
        return count

# Global chat service instance
# Create global chat service instance
import os
ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
chat_service = ChatService(ollama_url=ollama_url) 