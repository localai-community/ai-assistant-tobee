"""
MCP Client for communicating with MCP servers.
"""

import asyncio
import json
import logging
import subprocess
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
    
    async def _send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the MCP server and get response."""
        if not self.process:
            raise RuntimeError(f"MCP server {self.server_name} is not running")
        
        async with self._lock:
            try:
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
            request = ListToolsRequest()
            response = await self._send_message(request.model_dump())
            
            if "result" in response:
                result = ListToolsResult(**response["result"])
                return result.tools
            else:
                logger.error(f"Invalid response from {self.server_name}: {response}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to list tools from {self.server_name}: {e}")
            return []
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Call a tool on the MCP server."""
        try:
            request = CallToolRequest(name=name, arguments=arguments)
            response = await self._send_message(request.model_dump())
            
            if "result" in response:
                result = CallToolResult(**response["result"])
                return result
            else:
                logger.error(f"Invalid response from {self.server_name}: {response}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: Invalid response from {self.server_name}")],
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

# Import os at the top level
import os 