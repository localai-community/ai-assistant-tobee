#!/usr/bin/env python3
"""
MCP Filesystem Server
Provides file system operations for the AI assistant.
"""

import asyncio
import json
import os
import stat
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# Import common types directly
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    LoggingLevel,
    LogMessage,
)

# Import the rest with alias
import mcp.types as mtypes

# Configuration
ALLOWED_PATHS = os.getenv("ALLOWED_PATHS", "/workspace,/tmp,/app/uploads,/app/storage").split(",")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "100485760"))  # ~100MB default
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "true").lower() == "true"

def is_path_allowed(path: str) -> bool:
    """Check if a path is within allowed directories."""
    try:
        path = os.path.abspath(path)
        return any(path.startswith(os.path.abspath(allowed)) for allowed in ALLOWED_PATHS)
    except Exception:
        return False

def get_file_info(file_path: Path) -> Dict[str, Any]:
    """Get file information."""
    try:
        stat_info = file_path.stat()
        return {
            "name": file_path.name,
            "path": str(file_path),
            "size": stat_info.st_size,
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir(),
            "modified": stat_info.st_mtime,
            "permissions": oct(stat_info.st_mode)[-3:],
        }
    except Exception as e:
        return {"error": str(e)}

async def list_directory_tool(path: str) -> CallToolResult:
    """List contents of a directory."""
    try:
        if not is_path_allowed(path):
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Path not allowed")],
                isError=True
            )
        
        dir_path = Path(path)
        if not dir_path.exists():
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: Directory {path} does not exist")],
                isError=True
            )
        
        if not dir_path.is_dir():
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {path} is not a directory")],
                isError=True
            )
        
        items = []
        for item in dir_path.iterdir():
            items.append(get_file_info(item))
        
        result = {
            "path": str(dir_path),
            "items": items,
            "total_items": len(items)
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error listing directory: {str(e)}")],
            isError=True
        )

async def read_file_tool(path: str, encoding: str = "utf-8") -> CallToolResult:
    """Read contents of a file."""
    try:
        if not is_path_allowed(path):
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Path not allowed")],
                isError=True
            )
        
        file_path = Path(path)
        if not file_path.exists():
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: File {path} does not exist")],
                isError=True
            )
        
        if not file_path.is_file():
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {path} is not a file")],
                isError=True
            )
        
        if file_path.stat().st_size > MAX_FILE_SIZE:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: File too large (max {MAX_FILE_SIZE} bytes)")],
                isError=True
            )
        
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        result = {
            "path": str(file_path),
            "size": len(content),
            "content": content
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error reading file: {str(e)}")],
            isError=True
        )

async def write_file_tool(path: str, content: str, encoding: str = "utf-8") -> CallToolResult:
    """Write content to a file."""
    try:
        if not is_path_allowed(path):
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Path not allowed")],
                isError=True
            )
        
        file_path = Path(path)
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        result = {
            "path": str(file_path),
            "size": len(content),
            "message": "File written successfully"
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error writing file: {str(e)}")],
            isError=True
        )

async def delete_file_tool(path: str) -> CallToolResult:
    """Delete a file or directory."""
    try:
        if not is_path_allowed(path):
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Path not allowed")],
                isError=True
            )
        
        file_path = Path(path)
        if not file_path.exists():
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: Path {path} does not exist")],
                isError=True
            )
        
        if file_path.is_file():
            file_path.unlink()
        elif file_path.is_dir():
            import shutil
            shutil.rmtree(file_path)
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {path} is not a file or directory")],
                isError=True
            )
        
        result = {
            "path": str(file_path),
            "message": "Deleted successfully"
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error deleting: {str(e)}")],
            isError=True
        )

async def get_file_info_tool(path: str) -> CallToolResult:
    """Get detailed information about a file or directory."""
    try:
        if not is_path_allowed(path):
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Path not allowed")],
                isError=True
            )
        
        file_path = Path(path)
        if not file_path.exists():
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: Path {path} does not exist")],
                isError=True
            )
        
        info = get_file_info(file_path)
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(info, indent=2))]
        )
    
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error getting file info: {str(e)}")],
            isError=True
        )

# Create the MCP server
server = Server("filesystem")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools."""
    tools = [
        Tool(
            name="list_directory",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory to list"
                    }
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
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    }
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
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="delete_file",
            description="Delete a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file or directory to delete"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="get_file_info",
            description="Get detailed information about a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file or directory"
                    }
                },
                "required": ["path"]
            }
        )
    ]
    return ListToolsResult(tools=tools)

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    try:
        if name == "list_directory":
            return await list_directory_tool(arguments["path"])
        elif name == "read_file":
            encoding = arguments.get("encoding", "utf-8")
            return await read_file_tool(arguments["path"], encoding)
        elif name == "write_file":
            encoding = arguments.get("encoding", "utf-8")
            return await write_file_tool(arguments["path"], arguments["content"], encoding)
        elif name == "delete_file":
            return await delete_file_tool(arguments["path"])
        elif name == "get_file_info":
            return await get_file_info_tool(arguments["path"])
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                isError=True
            )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")],
            isError=True
        )

if __name__ == "__main__":
    asyncio.run(stdio_server(server)) 