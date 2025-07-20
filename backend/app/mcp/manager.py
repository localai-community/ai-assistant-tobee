"""
MCP Manager for coordinating multiple MCP servers.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .client import MCPClient

# Import common types directly
from mcp.types import (
    CallToolResult,
    Tool,
    TextContent,
)

# Import the rest with alias
import mcp.types as mtypes

logger = logging.getLogger(__name__)

class MCPManager:
    """Manager for coordinating multiple MCP servers."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "mcp-config-local.json"
        self.clients: Dict[str, MCPClient] = {}
        self.tools: Dict[str, Tool] = {}
        self._initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> bool:
        """Initialize the MCP manager and start all configured servers."""
        async with self._lock:
            if self._initialized:
                return True
            
            try:
                # Load configuration
                config = self._load_config()
                if not config:
                    logger.warning("No MCP configuration found, MCP features will be disabled")
                    return False
                
                # Start all configured servers
                for server_name, server_config in config.get("mcpServers", {}).items():
                    await self._start_server(server_name, server_config)
                
                # Wait a moment for servers to fully start
                await asyncio.sleep(1)
                
                # Discover tools from all servers
                await self._discover_tools()
                
                self._initialized = True
                logger.info(f"MCP Manager initialized with {len(self.clients)} servers and {len(self.tools)} tools")
                return True
                
            except Exception as e:
                logger.error(f"Failed to initialize MCP Manager: {e}")
                return False
    
    def _load_config(self) -> Optional[Dict[str, Any]]:
        """Load MCP configuration from file."""
        try:
            config_path = Path(self.config_path)
            if not config_path.exists():
                logger.warning(f"MCP config file not found: {config_path}")
                return None
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            return None
    
    async def _start_server(self, server_name: str, server_config: Dict[str, Any]) -> bool:
        """Start an individual MCP server."""
        try:
            command = server_config.get("command", "python")
            args = server_config.get("args", [])
            env = server_config.get("env", {})
            
            # Create client
            client = MCPClient(server_name, command, args, env)
            
            # Start server
            if await client.start():
                self.clients[server_name] = client
                logger.info(f"Started MCP server: {server_name}")
                return True
            else:
                logger.error(f"Failed to start MCP server: {server_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting MCP server {server_name}: {e}")
            return False
    
    async def _discover_tools(self):
        """Discover tools from all running MCP servers."""
        self.tools.clear()
        
        for server_name, client in self.clients.items():
            try:
                tools = await client.list_tools()
                for tool in tools:
                    # Prefix tool name with server name to avoid conflicts
                    tool_name = f"{server_name}.{tool.name}"
                    self.tools[tool_name] = tool
                    logger.debug(f"Discovered tool: {tool_name}")
                    
            except Exception as e:
                logger.error(f"Failed to discover tools from {server_name}: {e}")
    
    async def list_tools(self) -> List[Tool]:
        """List all available tools from all MCP servers."""
        if not self._initialized:
            await self.initialize()
        
        return list(self.tools.values())
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Call a tool by name."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Parse tool name to find server
            if "." not in tool_name:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: Tool name must be in format 'server.tool': {tool_name}")],
                    isError=True
                )
            
            server_name, actual_tool_name = tool_name.split(".", 1)
            
            if server_name not in self.clients:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: MCP server '{server_name}' not found")],
                    isError=True
                )
            
            client = self.clients[server_name]
            
            # Retry logic for server readiness
            max_retries = 3
            for attempt in range(max_retries):
                if not client.is_running():
                    if attempt < max_retries - 1:
                        logger.warning(f"MCP server '{server_name}' not running, retrying in 1 second (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(1)
                        continue
                    else:
                        return CallToolResult(
                            content=[TextContent(type="text", text=f"Error: MCP server '{server_name}' is not running after {max_retries} attempts")],
                            isError=True
                        )
                else:
                    break
            
            # Call the tool
            result = await client.call_tool(actual_tool_name, arguments)
            return result
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error calling tool {tool_name}: {str(e)}")],
                isError=True
            )
    
    async def get_tool_info(self, tool_name: str) -> Optional[Tool]:
        """Get information about a specific tool."""
        if not self._initialized:
            await self.initialize()
        
        return self.tools.get(tool_name)
    
    async def refresh_tools(self):
        """Refresh the list of available tools."""
        await self._discover_tools()
    
    async def shutdown(self):
        """Shutdown all MCP servers."""
        tasks = []
        for client in self.clients.values():
            tasks.append(client.stop())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.clients.clear()
        self.tools.clear()
        self._initialized = False
        logger.info("MCP Manager shutdown complete")
    
    def get_server_status(self) -> Dict[str, bool]:
        """Get status of all MCP servers."""
        return {
            server_name: client.is_running()
            for server_name, client in self.clients.items()
        }
    
    def get_tool_names(self) -> List[str]:
        """Get list of all available tool names."""
        return list(self.tools.keys())
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all MCP servers."""
        status = {
            "initialized": self._initialized,
            "servers": {},
            "tools_count": len(self.tools),
            "overall_healthy": True
        }
        
        for server_name, client in self.clients.items():
            is_running = client.is_running()
            status["servers"][server_name] = {
                "running": is_running,
                "healthy": is_running
            }
            if not is_running:
                status["overall_healthy"] = False
        
        return status 