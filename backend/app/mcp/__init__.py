"""
MCP (Model Context Protocol) Integration Layer
Connects MCP servers to the chat engine for tool calling capabilities.
"""

from .client import MCPClient
from .manager import MCPManager

__all__ = ["MCPClient", "MCPManager"] 