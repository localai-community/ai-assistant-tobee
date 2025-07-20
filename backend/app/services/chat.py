"""
LocalAI Community - Chat Service
Direct Ollama integration with streaming responses, conversation management, and MCP tool calling.
"""

import httpx
import json
import asyncio
import re
from typing import AsyncGenerator, Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from sqlalchemy.orm import Session
from .repository import ConversationRepository, MessageRepository
from ..models.schemas import ConversationCreate, MessageCreate
from ..mcp import MCPManager

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
    model: str = Field(default="llama3:latest", description="Ollama model to use")
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
    model: str = Field(default="llama3:latest", description="Model used for this conversation")
    created_at: datetime = Field(default_factory=datetime.now, description="Conversation creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")

class ChatService:
    """Service for handling chat interactions with Ollama and MCP tools."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", db: Optional[Session] = None, mcp_config_path: Optional[str] = None):
        self.ollama_url = ollama_url
        self.db = db
        self.http_client = httpx.AsyncClient(timeout=60.0)
        
        # Initialize repositories if database is available
        if self.db:
            self.conversation_repo = ConversationRepository(self.db)
            self.message_repo = MessageRepository(self.db)
        else:
            self.conversation_repo = None
            self.message_repo = None
        
        # Store MCP config path for later initialization
        self.mcp_config_path = mcp_config_path
        self.mcp_manager = None
        self.mcp_initialized = False
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
        # Don't shutdown the global MCP manager here
    
    async def _ensure_mcp_initialized(self):
        """Ensure MCP manager is initialized."""
        if not self.mcp_initialized:
            self.mcp_manager = await get_mcp_manager(self.mcp_config_path)
            self.mcp_initialized = True
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools."""
        await self._ensure_mcp_initialized()
        tools = await self.mcp_manager.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in tools
        ]
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        await self._ensure_mcp_initialized()
        result = await self.mcp_manager.call_tool(tool_name, arguments)
        
        # Extract text content from result
        content = ""
        if result.content:
            for item in result.content:
                if hasattr(item, 'text'):
                    content += item.text
        
        return {
            "success": not result.isError,
            "content": content,
            "error": result.isError
        }
    
    def _detect_tool_calls(self, message: str) -> List[Dict[str, Any]]:
        """Detect potential tool calls in user message."""
        tool_calls = []
        seen_commands = set()  # Track seen commands to prevent duplicates
        
        # Enhanced pattern matching for tool calls
        patterns = [
            # Terminal commands
            r"run\s+(.+?)(?=\n|$)",
            r"execute\s+(.+?)(?=\n|$)",
            r"run\s+command\s+(.+?)(?=\n|$)",
            r"execute\s+command\s+(.+?)(?=\n|$)",
            r"run\s+`(.+?)`",
            r"execute\s+`(.+?)`",
            r"run\s+terminal\s+command\s+(.+?)(?=\n|$)",
            r"run\s+bash\s+command\s+(.+?)(?=\n|$)",
            
            # Code execution
            r"execute\s+(python|javascript|bash)\s+code[:\s]+(.+?)(?=\n|$)",
            r"run\s+(python|javascript|bash)\s+code[:\s]+(.+?)(?=\n|$)",
            
            # File operations
            r"list\s+files?\s+in\s+(.+?)(?=\n|$)",
            r"list\s+directory\s+(.+?)(?=\n|$)",
            r"show\s+files?\s+in\s+(.+?)(?=\n|$)",
            r"read\s+file\s+(.+?)(?=\n|$)",
            r"write\s+file\s+(.+?)\s+with\s+(.+?)(?=\n|$)",
            r"delete\s+file\s+(.+?)(?=\n|$)",
            
            # Common terminal commands
            r"ps\s+aux",
            r"ls\s+(-la?)?",
            r"pwd",
            r"whoami",
            r"uname\s+-a",
            r"df\s+-h",
            r"top",
            r"htop",
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE | re.DOTALL)
            for match in matches:
                full_match = match.group(0)
                
                # Handle terminal commands
                if any(cmd in full_match.lower() for cmd in ["run", "execute", "command"]):
                    # Extract the actual command
                    if "`" in full_match:
                        # Handle backtick commands like "run `ps aux`"
                        command = re.search(r"`(.+?)`", full_match)
                        if command:
                            actual_command = command.group(1).strip()
                            if actual_command not in seen_commands:
                                seen_commands.add(actual_command)
                                tool_calls.append({
                                    "tool": "code-execution.execute_code",
                                    "arguments": {
                                        "language": "bash",
                                        "code": actual_command
                                    }
                                })
                    else:
                        # Handle plain commands like "run ps aux"
                        command_parts = full_match.split()
                        if len(command_parts) > 1:
                            # Skip the "run" or "execute" part
                            actual_command = " ".join(command_parts[1:]).strip()
                            if actual_command not in seen_commands:
                                seen_commands.add(actual_command)
                                tool_calls.append({
                                    "tool": "code-execution.execute_code",
                                    "arguments": {
                                        "language": "bash",
                                        "code": actual_command
                                    }
                                })
                
                # Handle code execution
                elif any(lang in full_match.lower() for lang in ["python", "javascript", "bash"]):
                    if "python" in full_match.lower() or "javascript" in full_match.lower() or "bash" in full_match.lower():
                        language = match.group(1).lower()
                        code = match.group(2).strip()
                        code_key = f"{language}:{code}"
                        if code_key not in seen_commands:
                            seen_commands.add(code_key)
                            tool_calls.append({
                                "tool": "code-execution.execute_code",
                                "arguments": {
                                    "language": language,
                                    "code": code
                                }
                            })
                
                # Handle file operations
                elif "list" in full_match.lower() or "show" in full_match.lower():
                    path = match.group(1).strip()
                    if path not in seen_commands:
                        seen_commands.add(path)
                        tool_calls.append({
                            "tool": "filesystem.list_directory",
                            "arguments": {"path": path}
                        })
                elif "read" in full_match.lower():
                    path = match.group(1).strip()
                    if path not in seen_commands:
                        seen_commands.add(path)
                        tool_calls.append({
                            "tool": "filesystem.read_file",
                            "arguments": {"path": path}
                        })
                elif "write" in full_match.lower():
                    path = match.group(1).strip()
                    content = match.group(2).strip()
                    write_key = f"write:{path}"
                    if write_key not in seen_commands:
                        seen_commands.add(write_key)
                        tool_calls.append({
                            "tool": "filesystem.write_file",
                            "arguments": {"path": path, "content": content}
                        })
                elif "delete" in full_match.lower():
                    path = match.group(1).strip()
                    if path not in seen_commands:
                        seen_commands.add(path)
                        tool_calls.append({
                            "tool": "filesystem.delete_file",
                            "arguments": {"path": path}
                        })
                
                # Handle direct terminal commands
                elif any(cmd in full_match.lower() for cmd in ["ps aux", "ls", "pwd", "whoami", "uname", "df", "top", "htop"]):
                    command = full_match.strip()
                    if command not in seen_commands:
                        seen_commands.add(command)
                        tool_calls.append({
                            "tool": "code-execution.execute_code",
                            "arguments": {
                                "language": "bash",
                                "code": command
                            }
                        })
        
        return tool_calls
    
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
        model: str = "llama3:latest",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        conversation_id: Optional[str] = None,
        enable_mcp: bool = True
    ) -> ChatResponse:
        """Generate a response from Ollama."""
        
        # Initialize conversation variable
        conversation = None
        
        # Get or create conversation
        if self.conversation_repo and conversation_id:
            conversation = self.conversation_repo.get_conversation(conversation_id)
        
        if not conversation and self.conversation_repo:
            # Create new conversation in database
            conversation_data = ConversationCreate(
                title=f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                model=model
            )
            conversation = self.conversation_repo.create_conversation(conversation_data)
            conversation_id = conversation.id
        elif not conversation:
            # Fallback to in-memory if no database
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            conversation = Conversation(id=conversation_id, model=model)
        
        # Add user message to database
        if self.message_repo:
            user_message_data = MessageCreate(
                conversation_id=conversation_id,
                role="user",
                content=message
            )
            self.message_repo.create_message(user_message_data)
        
        # Get conversation messages for Ollama
        messages = []
        if self.message_repo:
            db_messages = self.message_repo.get_messages(conversation_id)
            for msg in db_messages:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        else:
            # Fallback to in-memory messages
            if hasattr(conversation, 'messages'):
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
        
        # Check for MCP tool calls in the message
        tool_results = []
        if enable_mcp:
            tool_calls = self._detect_tool_calls(message)
            for tool_call in tool_calls:
                try:
                    result = await self.call_mcp_tool(tool_call["tool"], tool_call["arguments"])
                    tool_results.append({
                        "tool": tool_call["tool"],
                        "result": result
                    })
                except Exception as e:
                    logger.error(f"Error calling MCP tool {tool_call['tool']}: {e}")
                    tool_results.append({
                        "tool": tool_call["tool"],
                        "result": {"success": False, "content": f"Error: {str(e)}", "error": True}
                    })
        
        try:
            # Send request to Ollama
            response = await self.http_client.post(
                f"{self.ollama_url}/api/chat",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("message", {}).get("content", "")
                
                # Include tool results in the response if any
                if tool_results:
                    tool_summary = "\n\n**Tool Execution Results:**\n"
                    for tool_result in tool_results:
                        tool_name = tool_result["tool"]
                        result = tool_result["result"]
                        if result["success"]:
                            tool_summary += f"✅ **{tool_name}**: Success\n"
                            tool_summary += f"```\n{result['content']}\n```\n"
                        else:
                            tool_summary += f"❌ **{tool_name}**: Failed\n"
                            tool_summary += f"```\n{result['content']}\n```\n"
                    
                    ai_response += tool_summary
                
                # Add AI response to database
                if self.message_repo:
                    ai_message_data = MessageCreate(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=ai_response,
                        tokens_used=data.get("eval_count"),
                        model_used=model
                    )
                    self.message_repo.create_message(ai_message_data)
                
                # Update conversation timestamp
                if self.conversation_repo:
                    self.conversation_repo.update_conversation(conversation_id)
                
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
        model: str = "llama3:latest",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        conversation_id: Optional[str] = None,
        enable_mcp: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from Ollama."""
        
        # Initialize conversation variable
        conversation = None
        
        # Get or create conversation
        if self.conversation_repo and conversation_id:
            conversation = self.conversation_repo.get_conversation(conversation_id)
        
        if not conversation and self.conversation_repo:
            # Create new conversation in database
            conversation_data = ConversationCreate(
                title=f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                model=model
            )
            conversation = self.conversation_repo.create_conversation(conversation_data)
            conversation_id = conversation.id
        elif not conversation:
            # Fallback to in-memory if no database
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            conversation = Conversation(id=conversation_id, model=model)
        
        # Check for MCP tool calls in the message
        tool_results = []
        if enable_mcp:
            try:
                await self._ensure_mcp_initialized()
                tool_calls = self._detect_tool_calls(message)
                for tool_call in tool_calls:
                    try:
                        result = await self.call_mcp_tool(tool_call["tool"], tool_call["arguments"])
                        tool_results.append({
                            "tool": tool_call["tool"],
                            "result": result
                        })
                    except Exception as e:
                        logger.error(f"Error calling MCP tool {tool_call['tool']}: {e}")
                        tool_results.append({
                            "tool": tool_call["tool"],
                            "result": {"success": False, "content": f"Error: {str(e)}", "error": True}
                        })
            except Exception as e:
                logger.warning(f"MCP not available for streaming: {e}")
                # Don't add tool results if MCP is not available
        
        # Add user message to database
        if self.message_repo:
            user_message_data = MessageCreate(
                conversation_id=conversation_id,
                role="user",
                content=message
            )
            self.message_repo.create_message(user_message_data)
        
        # Get conversation messages for Ollama
        messages = []
        if self.message_repo:
            db_messages = self.message_repo.get_messages(conversation_id)
            for msg in db_messages:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        else:
            # Fallback to in-memory messages
            if hasattr(conversation, 'messages'):
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
                
                # If we have tool results, include them in the response
                if tool_results:
                    tool_summary = "\n\n**Tool Execution Results:**\n"
                    for tool_result in tool_results:
                        tool_name = tool_result["tool"]
                        result = tool_result["result"]
                        if result["success"]:
                            tool_summary += f"✅ **{tool_name}**: Success\n"
                            tool_summary += f"```\n{result['content']}\n```\n"
                        else:
                            tool_summary += f"❌ **{tool_name}**: Failed\n"
                            tool_summary += f"```\n{result['content']}\n```\n"
                    
                    # Yield tool results first
                    yield tool_summary
                    full_response += tool_summary
                
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
                
                # Add complete AI response to database
                if full_response and self.message_repo:
                    ai_message_data = MessageCreate(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=full_response,
                        model_used=model
                    )
                    self.message_repo.create_message(ai_message_data)
                
                # Update conversation timestamp
                if self.conversation_repo:
                    self.conversation_repo.update_conversation(conversation_id)
                
        except Exception as e:
            logger.error(f"Failed to generate streaming response: {e}")
            yield f"Error: {str(e)}"
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        if self.conversation_repo:
            return self.conversation_repo.get_conversation(conversation_id)
        return None
    
    def list_conversations(self) -> List[Conversation]:
        """List all conversations."""
        if self.conversation_repo:
            return self.conversation_repo.get_conversations()
        return []
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        if self.conversation_repo:
            return self.conversation_repo.delete_conversation(conversation_id)
        return False
    
    def clear_conversations(self) -> int:
        """Clear all conversations and return count of deleted conversations."""
        if self.conversation_repo:
            return self.conversation_repo.clear_conversations()
        return 0

# Global MCP manager instance to prevent duplicate initialization
_mcp_manager_instance = None
_mcp_manager_lock = asyncio.Lock()

async def get_mcp_manager(mcp_config_path: Optional[str] = None):
    """Get or create a singleton MCP manager instance."""
    global _mcp_manager_instance
    
    if _mcp_manager_instance is None:
        async with _mcp_manager_lock:
            if _mcp_manager_instance is None:
                _mcp_manager_instance = MCPManager(mcp_config_path)
                await _mcp_manager_instance.initialize()
    
    return _mcp_manager_instance

# Global chat service instance
# Create global chat service instance
import os
ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
chat_service = ChatService(ollama_url=ollama_url)

async def shutdown_mcp_manager():
    """Shutdown the global MCP manager."""
    global _mcp_manager_instance
    if _mcp_manager_instance:
        await _mcp_manager_instance.shutdown()
        _mcp_manager_instance = None 