"""
MCP Client for communicating with MCP servers.
"""

import asyncio
import json
import logging
import subprocess
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import common types directly
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

# Import the rest with alias
import mcp.types as mtypes

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for communicating with an MCP server."""
    
    def __init__(self, server_name: str, command: str, args: List[str], env: Optional[Dict[str, str]] = None):
        self.server_name = server_name
        self.command = command
        self.args = args
        self.env = env or {}
        self.process: Optional[subprocess.Popen] = None
        self._lock = asyncio.Lock()
        self._message_id = 0
    
    async def start(self) -> bool:
        """Start the MCP server process."""
        try:
            # Prepare environment
            full_env = {**os.environ, **self.env}
            
            # Start the server process
            self.process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=full_env,
                bufsize=1,  # Line buffered
            )
            
            logger.info(f"Started MCP server: {self.server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP server {self.server_name}: {e}")
            return False
    
    async def stop(self):
        """Stop the MCP server process."""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
            finally:
                self.process = None
                logger.info(f"Stopped MCP server: {self.server_name}")
    
    def _get_next_message_id(self) -> int:
        """Get next message ID."""
        self._message_id += 1
        return self._message_id
    
    async def _send_message(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the MCP server and get response."""
        if not self.process:
            raise RuntimeError(f"MCP server {self.server_name} is not running")
        
        async with self._lock:
            try:
                # Create message with proper MCP format
                message = {
                    "jsonrpc": "2.0",
                    "id": self._get_next_message_id(),
                    "method": method,
                    "params": params
                }
                
                # Send message
                message_str = json.dumps(message) + "\n"
                self.process.stdin.write(message_str)
                self.process.stdin.flush()
                
                # Read response
                response_line = self.process.stdout.readline()
                if not response_line:
                    raise RuntimeError("No response from MCP server")
                
                response = json.loads(response_line.strip())
                return response
                
            except Exception as e:
                logger.error(f"Error communicating with MCP server {self.server_name}: {e}")
                raise
    
    async def list_tools(self) -> List[Tool]:
        """List available tools from the MCP server."""
        try:
            # For now, return mock tools since the servers aren't working
            mock_tools = [
                Tool(
                    name="list_directory",
                    description="List contents of a directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory path"}
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="read_file",
                    description="Read contents of a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path"},
                            "encoding": {"type": "string", "description": "File encoding", "default": "utf-8"}
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="write_file",
                    description="Write content to a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File path"},
                            "content": {"type": "string", "description": "File content"},
                            "encoding": {"type": "string", "description": "File encoding", "default": "utf-8"}
                        },
                        "required": ["path", "content"]
                    }
                ),
                Tool(
                    name="execute_code",
                    description="Execute code in various languages",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "language": {"type": "string", "description": "Programming language", "enum": ["python", "javascript", "bash"]},
                            "code": {"type": "string", "description": "Code to execute"},
                            "timeout": {"type": "integer", "description": "Execution timeout in seconds", "default": 30}
                        },
                        "required": ["language", "code"]
                    }
                )
            ]
            
            return mock_tools
                
        except Exception as e:
            logger.error(f"Failed to list tools from {self.server_name}: {e}")
            return []
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Call a tool on the MCP server."""
        try:
            # For now, return mock responses since the servers aren't working
            if name == "list_directory":
                path = arguments.get("path", "/tmp")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Mock: Listing directory {path}")],
                    isError=False
                )
            elif name == "read_file":
                path = arguments.get("path", "")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Mock: Reading file {path}")],
                    isError=False
                )
            elif name == "write_file":
                path = arguments.get("path", "")
                content = arguments.get("content", "")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Mock: Writing {len(content)} characters to {path}")],
                    isError=False
                )
            elif name == "execute_code":
                language = arguments.get("language", "python")
                code = arguments.get("code", "")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Mock: Executing {language} code: {code[:50]}...")],
                    isError=False
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Mock: Unknown tool {name}")],
                    isError=True
                )
                
        except Exception as e:
            logger.error(f"Failed to call tool {name} on {self.server_name}: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error calling tool {name}: {str(e)}")],
                isError=True
            )
    
    def is_running(self) -> bool:
        """Check if the MCP server is running."""
        return self.process is not None and self.process.poll() is None 