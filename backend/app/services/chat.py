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
from .repository import ConversationRepository, MessageRepository, UserQuestionRepository, AIPromptRepository, ContextAwarenessRepository
from ..models.schemas import ConversationCreate, MessageCreate, UserQuestionCreate, AIPromptCreate, ContextAwarenessDataCreate
from ..mcp import MCPManager
from .context_awareness import ContextAwarenessService

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
    user_id: Optional[str] = Field(default="00000000-0000-0000-0000-000000000001", description="User ID for personalized context")
    # RAG parameters
    k: Optional[int] = Field(default=None, description="Number of documents to retrieve for RAG")
    filter_dict: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filter for RAG")
    # Context awareness parameters
    enable_context_awareness: bool = Field(default=True, description="Enable context awareness features")
    include_memory: bool = Field(default=False, description="Include long-term memory in context")
    context_strategy: str = Field(default="conversation_only", description="Context strategy: auto, conversation_only, memory_only, hybrid")

class ChatResponse(BaseModel):
    """Response model for chat API."""
    response: str = Field(..., description="AI response")
    model: str = Field(..., description="Model used")
    conversation_id: str = Field(..., description="Conversation ID")
    user_id: Optional[str] = Field(default=None, description="User ID used for context")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    tokens_used: Optional[int] = Field(default=None, description="Tokens used in response")
    # RAG context
    rag_context: Optional[str] = Field(default=None, description="RAG context used")
    has_context: Optional[bool] = Field(default=None, description="Whether RAG context was used")
    # Context awareness information
    context_awareness_enabled: bool = Field(default=False, description="Whether context awareness was used")
    context_strategy_used: Optional[str] = Field(default=None, description="Context strategy that was applied")
    context_entities: Optional[List[str]] = Field(default=None, description="Key entities from context")
    context_topics: Optional[List[str]] = Field(default=None, description="Topics from context")
    memory_chunks_used: Optional[int] = Field(default=None, description="Number of memory chunks retrieved")
    user_preferences_applied: Optional[Dict[str, Any]] = Field(default=None, description="User preferences that influenced response")

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
        # Performance optimization: Use connection pooling and faster timeouts
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=5.0),  # Faster connection timeout
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
            http2=False  # Disable HTTP/2 to avoid dependency issues
        )
        
        # Initialize repositories if database is available
        if self.db:
            self.conversation_repo = ConversationRepository(self.db)
            self.message_repo = MessageRepository(self.db)
            self.user_question_repo = UserQuestionRepository(self.db)
            self.ai_prompt_repo = AIPromptRepository(self.db)
            self.context_awareness_repo = ContextAwarenessRepository(self.db)
        else:
            self.conversation_repo = None
            self.message_repo = None
            self.user_question_repo = None
            self.ai_prompt_repo = None
            self.context_awareness_repo = None
        
        # Initialize context awareness service lazily
        self.context_service = None
        self._context_service_initialized = False
        
        # Store MCP config path for later initialization
        self.mcp_config_path = mcp_config_path
        self.mcp_manager = None
        self.mcp_initialized = False
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
        # Don't shutdown the global MCP manager here
    
    def _ensure_context_service_initialized(self):
        """Ensure context awareness service is initialized lazily."""
        if not self._context_service_initialized:
            self.context_service = ContextAwarenessService(db=self.db)
            self._context_service_initialized = True
    
    async def _ensure_mcp_initialized(self):
        """Ensure MCP manager is initialized."""
        if not self.mcp_initialized:
            self.mcp_manager = await get_mcp_manager(self.mcp_config_path)
            self.mcp_initialized = True
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools."""
        await self._ensure_mcp_initialized()
        # Get tool names with server prefixes
        tool_names = self.mcp_manager.get_tool_names()
        tools = []
        
        for tool_name in tool_names:
            tool = self.mcp_manager.tools.get(tool_name)
            if tool:
                tools.append({
                    "name": tool_name,  # This includes the server prefix (e.g., "filesystem.list_directory")
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })
        
        return tools
    
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
        
        # More specific pattern matching for tool calls - only trigger on explicit commands
        patterns = [
            # Explicit terminal commands with "run" or "execute" prefix
            r"^run\s+(.+?)(?=\n|$)",
            r"^execute\s+(.+?)(?=\n|$)",
            r"^run\s+command\s+(.+?)(?=\n|$)",
            r"^execute\s+command\s+(.+?)(?=\n|$)",
            r"^run\s+`(.+?)`",
            r"^execute\s+`(.+?)`",
            r"^run\s+terminal\s+command\s+(.+?)(?=\n|$)",
            r"^run\s+bash\s+command\s+(.+?)(?=\n|$)",
            
            # Explicit code execution commands
            r"^execute\s+(python|javascript|bash)\s+code[:\s]+(.+?)(?=\n|$)",
            r"^run\s+(python|javascript|bash)\s+code[:\s]+(.+?)(?=\n|$)",
            
            # Explicit file operation commands
            r"^list\s+files?\s+in\s+(.+?)(?=\n|$)",
            r"^list\s+directory\s+(.+?)(?=\n|$)",
            r"^show\s+files?\s+in\s+(.+?)(?=\n|$)",
            r"^read\s+file\s+(.+?)(?=\n|$)",
            r"^write\s+file\s+(.+?)\s+with\s+(.+?)(?=\n|$)",
            r"^delete\s+file\s+(.+?)(?=\n|$)",
            
            # Standalone terminal commands (must be at start of line or preceded by whitespace)
            r"(?:^|\s)ps\s+aux(?=\s|$)",
            r"(?:^|\s)ls\s+(-la?)?(?=\s|$)",
            r"(?:^|\s)pwd(?=\s|$)",
            r"(?:^|\s)whoami(?=\s|$)",
            r"(?:^|\s)uname\s+-a(?=\s|$)",
            r"(?:^|\s)df\s+-h(?=\s|$)",
            r"(?:^|\s)top(?=\s|$)",
            r"(?:^|\s)htop(?=\s|$)",
        ]
        
        # Only process if the message looks like it contains explicit commands
        command_indicators = ["run", "execute", "command", "ls", "ps", "pwd", "whoami", "uname", "df", "top", "htop"]
        has_command_indicator = any(indicator in message.lower() for indicator in command_indicators)
        
        # If no command indicators, don't process patterns
        if not has_command_indicator:
            return tool_calls
        
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
        """Check if Ollama is running and healthy with fast timeout."""
        try:
            # Use a faster timeout for health checks
            response = await self.http_client.get(f"{self.ollama_url}/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def get_available_models(self) -> List[str]:
        """Get list of available Ollama models with llama3:latest prioritized."""
        try:
            response = await self.http_client.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                # Prioritize llama3:latest as the first model
                if "llama3:latest" in models:
                    models.remove("llama3:latest")
                    models.insert(0, "llama3:latest")
                return models
            return []
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    # Removed non-streaming generate_response function - only streaming is supported
    
    async def generate_streaming_response(
        self, 
        message: str, 
        model: str = "llama3:latest",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        conversation_id: Optional[str] = None,
        enable_mcp: bool = True,
        # Context awareness parameters
        enable_context_awareness: bool = True,
        include_memory: bool = False,
        context_strategy: str = "conversation_only",
        user_id: Optional[str] = "00000000-0000-0000-0000-000000000001"
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from Ollama."""
        
        # Initialize conversation variable
        conversation = None
        
        # Get or create conversation
        if self.conversation_repo and conversation_id:
            conversation = self.conversation_repo.get_conversation(conversation_id)
        
        if not conversation and self.conversation_repo and user_id and user_id != "00000000-0000-0000-0000-000000000001":
            # Only create new conversation in database if user_id is provided and not guest mode
            conversation_data = ConversationCreate(
                title=f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                model=model,
                user_id=user_id
            )
            # Use the provided conversation_id if available, otherwise let the database generate one
            conversation = self.conversation_repo.create_conversation(conversation_data, conversation_id=conversation_id)
            conversation_id = conversation.id
        elif not conversation:
            # Fallback to in-memory if no database
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            conversation = Conversation(id=conversation_id, model=model)
        
        # Apply context awareness if enabled
        enhanced_message = message
        document_context_available = False
        if enable_context_awareness and conversation_id:
            try:
                self._ensure_context_service_initialized()
                enhanced_message, context_metadata = self.context_service.build_context_aware_query(
                    current_message=message,
                    conversation_id=conversation_id,
                    user_id=user_id,
                    include_memory=include_memory
                )
                document_context_available = context_metadata.get("document_context", False)
                logger.info(f"Enhanced message with context awareness: {len(enhanced_message)} chars vs {len(message)} chars original, documents available: {document_context_available}")
            except Exception as e:
                logger.error(f"Error applying context awareness: {e}")
                enhanced_message = message
        
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
        
        # Store user question and context data (only if user_id is provided and not guest mode)
        question_id = None
        if self.user_question_repo and user_id and user_id != "00000000-0000-0000-0000-000000000001":
            try:
                # Create user question record
                question_data = UserQuestionCreate(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    question_text=message
                )
                user_question = self.user_question_repo.create_question(question_data)
                question_id = user_question.id
                logger.info(f"Stored user question in database with ID: {question_id}")
                
                # Store context awareness data if available
                if enable_context_awareness and conversation_id:
                    try:
                        self._ensure_context_service_initialized()
                        # Get context metadata that was used for enhancement
                        _, context_metadata = self.context_service.build_context_aware_query(
                            current_message=message,
                            conversation_id=conversation_id,
                            user_id=user_id,
                            include_memory=include_memory
                        )
                        
                        # Store different types of context data
                        if context_metadata.get("conversation_history"):
                            context_data = ContextAwarenessDataCreate(
                                question_id=question_id,
                                conversation_id=conversation_id,
                                user_id=user_id,
                                context_type="conversation_history",
                                context_data=context_metadata["conversation_history"],
                                context_metadata={"strategy": context_strategy}
                            )
                            self.context_awareness_repo.create_context_data(context_data)
                        
                        if context_metadata.get("document_context"):
                            context_data = ContextAwarenessDataCreate(
                                question_id=question_id,
                                conversation_id=conversation_id,
                                user_id=user_id,
                                context_type="document_context",
                                context_data=context_metadata["document_context"],
                                context_metadata={"document_count": len(context_metadata.get("document_context", []))}
                            )
                            self.context_awareness_repo.create_context_data(context_data)
                        
                        if context_metadata.get("user_memory"):
                            context_data = ContextAwarenessDataCreate(
                                question_id=question_id,
                                conversation_id=conversation_id,
                                user_id=user_id,
                                context_type="user_memory",
                                context_data=context_metadata["user_memory"],
                                context_metadata={"memory_chunks": len(context_metadata.get("user_memory", []))}
                            )
                            self.context_awareness_repo.create_context_data(context_data)
                        
                        logger.info(f"Stored context awareness data for question {question_id}")
                    except Exception as e:
                        logger.error(f"Error storing context awareness data: {e}")
                
            except Exception as e:
                logger.error(f"Error storing user question: {e}")
        
        # Add user message to database (only if user_id is provided and not guest mode)
        if self.message_repo and user_id and user_id != "00000000-0000-0000-0000-000000000001":
            user_message_data = MessageCreate(
                conversation_id=conversation_id,
                role="user",
                content=message
            )
            self.message_repo.create_message(user_message_data)
            logger.info(f"Stored user message in database for conversation {conversation_id}")
        elif not user_id or user_id == "00000000-0000-0000-0000-000000000001":
            logger.info(f"Guest mode: Not storing user message in database for conversation {conversation_id}")
        else:
            logger.warning("No message repository available for user message storage")
        
        # Get conversation messages for Ollama (excluding the current user message to avoid duplication)
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
        
        # Add current user message with context enhancement
        # Remove the most recent user message from database to avoid duplication (it's the one we just stored)
        if messages and messages[-1]["role"] == "user":
            messages.pop()  # Remove the last user message (the one we just stored)
        messages.append({
            "role": "user",
            "content": enhanced_message
        })
        
        # Debug: Log the messages being sent to Ollama
        logger.info(f"Messages being sent to Ollama: {[{'role': msg['role'], 'content': msg['content'][:100] + '...' if len(msg['content']) > 100 else msg['content']} for msg in messages]}")
        
        # Add system prompt to encourage English responses for DeepSeek models and document awareness
        system_prompt = "You are a helpful AI assistant."
        
        if "deepseek" in model.lower():
            system_prompt += " Please respond in English unless the user specifically asks you to use another language."
        
        # Add document awareness if documents are available
        if document_context_available:
            system_prompt += "\n\nYou have access to documents that have been uploaded to this conversation. When the user asks questions that could be related to these documents (such as asking for summaries, analysis, or information about the content), please use the document information provided in the context to answer their questions. Always cite the source document when you use information from it."
        
        system_message = {
            "role": "system", 
            "content": system_prompt
        }
        messages.insert(0, system_message)
        
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
                assistant_message_stored = False
                
                try:
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
                
                finally:
                    # Always store the assistant message, even if streaming was interrupted
                    # But only if user_id is provided and not guest mode
                    if full_response and self.message_repo and not assistant_message_stored and user_id and user_id != "00000000-0000-0000-0000-000000000001":
                        ai_message_data = MessageCreate(
                            conversation_id=conversation_id,
                            role="assistant",
                            content=full_response,
                            model_used=model
                        )
                        self.message_repo.create_message(ai_message_data)
                        assistant_message_stored = True
                        logger.info(f"Stored assistant message in database for conversation {conversation_id} (interrupted or completed)")
                        
                        # Store AI prompt data if we have a question_id
                        if question_id and self.ai_prompt_repo:
                            try:
                                # Create the final prompt that was sent to the AI model
                                final_prompt = json.dumps(messages, indent=2)
                                
                                prompt_data = AIPromptCreate(
                                    question_id=question_id,
                                    conversation_id=conversation_id,
                                    user_id=user_id,
                                    final_prompt=final_prompt,
                                    model_used=model,
                                    temperature=temperature,
                                    max_tokens=max_tokens
                                )
                                self.ai_prompt_repo.create_prompt(prompt_data)
                                logger.info(f"Stored AI prompt for question {question_id}")
                            except Exception as e:
                                logger.error(f"Error storing AI prompt: {e}")
                        
                        # Add stream interruption marker if the response seems incomplete
                        if self._is_response_incomplete(full_response):
                            interruption_marker = MessageCreate(
                                conversation_id=conversation_id,
                                role="system",
                                content="[STREAM_INTERRUPTED]",
                                model_used="system"
                            )
                            self.message_repo.create_message(interruption_marker)
                            logger.info(f"Added stream interruption marker for conversation {conversation_id}")
                            
                    elif full_response and assistant_message_stored:
                        logger.info(f"Assistant message already stored for conversation {conversation_id}")
                    elif not full_response:
                        logger.warning(f"No assistant message to store - empty response for conversation {conversation_id}")
                
                # Update context awareness after message generation
                if enable_context_awareness and conversation_id and full_response:
                    try:
                        self._ensure_context_service_initialized()
                        self.context_service.update_context_after_message(
                            conversation_id=conversation_id,
                            message={"role": "assistant", "content": full_response},
                            user_id=user_id
                        )
                    except Exception as e:
                        logger.error(f"Error updating context after streaming message: {e}")
                
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
    
    def _is_response_incomplete(self, response: str) -> bool:
        """
        Determine if a response appears to be incomplete/interrupted.
        
        This is a heuristic approach to detect stream interruptions.
        """
        if not response or len(response.strip()) < 10:
            return False
            
        # Check for common incomplete patterns
        incomplete_indicators = [
            # DeepSeek thinking tags not closed
            response.count('<think>') > response.count('</think>'),
            # Ends mid-sentence (no ending punctuation)
            not response.strip().endswith(('.', '!', '?', '。', '！', '？')),
            # Ends with common incomplete words
            response.strip().endswith(('the', 'and', 'but', 'or', 'with', 'for', 'in', 'on', 'at', 'to', 'of')),
            # Very short responses that seem cut off
            len(response.strip()) < 50 and not response.strip().endswith(('.', '!', '?')),
        ]
        
        # Return True if any indicator suggests incompleteness
        return any(incomplete_indicators)
    
    def list_conversations(self, user_id: Optional[str] = None) -> List[Conversation]:
        """List conversations, optionally filtered by user."""
        if self.conversation_repo:
            return self.conversation_repo.get_conversations(user_id=user_id)
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
    
    def _create_document_aware_prompt(
        self, 
        user_message: str, 
        document_context: List,
        conversation_id: str = None
    ) -> str:
        """Create prompt that includes document context."""
        try:
            from ..services.context_awareness import DocumentContext
            from ..services.rag.retriever import RAGRetriever
            
            if not document_context:
                return user_message
            
            # Initialize RAG retriever with conversation-specific vector store
            from ..services.rag.vector_store import VectorStore
            conversation_vector_store = VectorStore(conversation_id=conversation_id)
            rag_retriever = RAGRetriever(vector_store=conversation_vector_store)
            
            # Build document context text
            documents_text = []
            for doc in document_context:
                if isinstance(doc, DocumentContext):
                    if doc.summary:
                        documents_text.append(f"Document: {doc.filename}\nSummary: {doc.summary}")
                    else:
                        # Get relevant content from the document using RAG
                        try:
                            logger.info(f"Attempting to retrieve content for document: {doc.filename}")
                            
                            # Try multiple search strategies to find document content
                            search_queries = [
                                user_message,  # Original user message
                                doc.filename,  # Document filename
                                "content text",  # Generic content search
                                "document content",  # Another generic search
                                "main topics",  # For analysis queries
                                "key points"  # For summary queries
                            ]
                            
                            found_content = False
                            combined_content = ""
                            
                            for search_query in search_queries:
                                try:
                                    logger.info(f"Searching with query: {search_query}")
                                    relevant_chunks = rag_retriever.retrieve_relevant_documents(
                                        search_query,
                                        k=30,  # Get more chunks
                                        filter_dict=None
                                    )
                                    logger.info(f"Retrieved {len(relevant_chunks)} chunks for query: {search_query}")
                                    
                                    # Filter chunks to only include those from this document
                                    document_chunks = []
                                    for chunk_doc, score in relevant_chunks:
                                        chunk_filename = chunk_doc.metadata.get('filename', '')
                                        chunk_source = chunk_doc.metadata.get('source', '')
                                        
                                        # Check if chunk is from our specific document by matching the file path
                                        # The source path should match the file_path from the database
                                        file_path = doc.metadata.get('file_path', '')
                                        if chunk_source and file_path and file_path in chunk_source:
                                            document_chunks.append((chunk_doc, score))
                                            logger.info(f"Found document chunk for {doc.filename} (ID: {doc.document_id}): {chunk_filename} (score: {score})")
                                    
                                    if document_chunks:
                                        logger.info(f"Found {len(document_chunks)} document chunks for {doc.filename}")
                                        # Sort by relevance score and take top chunks
                                        document_chunks.sort(key=lambda x: x[1], reverse=True)
                                        
                                        content_parts = []
                                        for chunk_doc, score in document_chunks[:5]:  # Take top 5 chunks
                                            if score > 0.05:  # Lower threshold for relevance
                                                content_parts.append(chunk_doc.page_content.strip())
                                                logger.info(f"Added content chunk with score {score}: {chunk_doc.page_content[:100]}...")
                                        
                                        if content_parts:
                                            combined_content = "\n\n".join(content_parts)
                                            # Limit content length to avoid token limits
                                            if len(combined_content) > 2000:
                                                combined_content = combined_content[:2000] + "..."
                                            
                                            logger.info(f"Successfully retrieved content for {doc.filename}: {len(combined_content)} chars")
                                            documents_text.append(f"Document: {doc.filename}\nContent:\n{combined_content}")
                                            found_content = True
                                            break
                                            
                                except Exception as search_error:
                                    logger.warning(f"Search failed for query '{search_query}': {search_error}")
                                    continue
                            
                            if not found_content:
                                logger.warning(f"No content found for {doc.filename} after trying all search strategies")
                                documents_text.append(f"Document: {doc.filename}\n(Document is available but no content could be retrieved. The document may be empty or in an unsupported format.)")
                                
                        except Exception as content_error:
                            logger.error(f"Error retrieving content for {doc.filename}: {content_error}")
                            documents_text.append(f"Document: {doc.filename}\n(Document is available but content could not be accessed due to an error: {str(content_error)})")
            
            if documents_text:
                document_context_text = "\n\n".join(documents_text)
                
                return f"""You are an AI assistant with access to the following documents in this conversation:

{document_context_text}

User Question: {user_message}

Please answer the user's question using information from the documents when relevant, and cite the source document when you do so. If the question is not related to the documents, provide a general answer based on your knowledge."""
            else:
                return user_message
                
        except Exception as e:
            logger.error(f"Error creating document-aware prompt: {e}")
            return user_message

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

# Global chat service instance removed - each request creates its own instance with database access

async def shutdown_mcp_manager():
    """Shutdown the global MCP manager."""
    global _mcp_manager_instance
    if _mcp_manager_instance:
        await _mcp_manager_instance.shutdown()
        _mcp_manager_instance = None 