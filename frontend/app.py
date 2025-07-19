"""
LocalAI Community Frontend
A Chainlit-based chat interface for the LocalAI Community backend.
"""

import chainlit as cl
import httpx
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")
CHAT_HISTORY = []
CURRENT_CONVERSATION_ID = None
AVAILABLE_MODELS = []

@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    global AVAILABLE_MODELS
    
    # Check backend health and get available models
    if await check_backend_health():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BACKEND_URL}/api/v1/chat/models", timeout=5.0)
                if response.status_code == 200:
                    AVAILABLE_MODELS = response.json()
        except:
            AVAILABLE_MODELS = []
    
    # Build welcome message
    welcome_msg = "🤖 Welcome to LocalAI Community!\n\n"
    welcome_msg += "I'm your local-first AI assistant with MCP and RAG capabilities.\n\n"
    welcome_msg += "**Features:**\n"
    welcome_msg += "• Direct Ollama integration\n"
    welcome_msg += "• Document processing (PDF, DOCX, TXT)\n"
    welcome_msg += "• RAG (Retrieval-Augmented Generation)\n"
    welcome_msg += "• MCP (Model Context Protocol) tools\n\n"
    
    if AVAILABLE_MODELS:
        welcome_msg += f"**Available Models:** {', '.join(AVAILABLE_MODELS)}\n\n"
    else:
        welcome_msg += "**⚠️ No models available** - Please make sure Ollama is running and models are installed.\n\n"
    
    welcome_msg += "**Getting Started:**\n"
    welcome_msg += "1. Ask questions and get AI responses\n"
    welcome_msg += "2. Use MCP tools for file operations\n"
    welcome_msg += "3. Upload documents via the backend API\n\n"
    welcome_msg += "How can I help you today?"
    
    await cl.Message(content=welcome_msg).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""
    global CURRENT_CONVERSATION_ID
    
    try:
        # Check backend health first
        if not await check_backend_health():
            await cl.Message(
                content="❌ Backend service is not available. "
                        "Please make sure the backend server is running on "
                        f"{BACKEND_URL}"
            ).send()
            return

        # Check if Ollama is available
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BACKEND_URL}/api/v1/chat/health", timeout=5.0)
                if response.status_code == 200:
                    health_data = response.json()
                    if not health_data.get("ollama_available", False):
                        await cl.Message(
                            content="❌ Ollama is not available. "
                                    "Please make sure Ollama is running and models are installed.\n\n"
                                    "**To fix this:**\n"
                                    "1. Start Ollama: `ollama serve`\n"
                                    "2. Install a model: `ollama pull llama3.2`"
                        ).send()
                        return
        except:
            pass

        # Send message to backend with conversation context
        response = await send_to_backend(message.content, CURRENT_CONVERSATION_ID)
        
        if response and not response.startswith("❌"):
            # Extract conversation ID from response if available
            # (This would need to be implemented in the backend response)
            await cl.Message(content=response).send()
        else:
            await cl.Message(
                content=response or "❌ Unable to get response from backend. "
                        "Please try again or check the backend logs."
            ).send()
            
    except Exception as e:
        await cl.Message(
            content=f"❌ Error: {str(e)}\n\n"
                    "Please check if the backend server is running."
        ).send()

async def check_backend_health() -> bool:
    """Check if the backend is healthy."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/health", timeout=5.0)
            return response.status_code == 200
    except:
        return False

async def send_to_backend(message: str, conversation_id: Optional[str] = None) -> Optional[str]:
    """Send message to backend and get response."""
    try:
        async with httpx.AsyncClient() as client:
            # Use the first available model or fallback to llama3:latest
            model = AVAILABLE_MODELS[0] if AVAILABLE_MODELS else "llama3:latest"
            
            payload = {
                "message": message,
                "model": model,
                "temperature": 0.7,
                "stream": False
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            response = await client.post(
                f"{BACKEND_URL}/api/v1/chat/",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response from backend")
            elif response.status_code == 503:
                return "❌ Ollama service is not available. Please make sure Ollama is running."
            else:
                return f"Backend error: {response.status_code}"
                
    except httpx.TimeoutException:
        return "Request timed out. Please try again."
    except Exception as e:
        return f"Communication error: {str(e)}"

async def get_chat_health() -> dict:
    """Get detailed chat service health information."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/api/v1/chat/health", timeout=5.0)
            if response.status_code == 200:
                return response.json()
    except:
        pass
    return {}

async def list_conversations() -> list:
    """List all conversations."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/api/v1/chat/conversations", timeout=5.0)
            if response.status_code == 200:
                return response.json()
    except:
        pass
    return [] 