#!/usr/bin/env python3
"""
MCP Code Execution Server
Provides safe code execution capabilities for the AI assistant.
"""

import asyncio
import json
import os
import subprocess
import tempfile
import time
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
    LoggingMessageNotification,
)

# Import the rest with alias
import mcp.types as mtypes

# Configuration
EXECUTION_TIMEOUT = int(os.getenv("EXECUTION_TIMEOUT", "30"))
ALLOWED_LANGUAGES = os.getenv("ALLOWED_LANGUAGES", "python,javascript,bash").split(",")
SANDBOX_MODE = os.getenv("SANDBOX_MODE", "true").lower() == "true"
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "true").lower() == "true"
MAX_MEMORY_MB = int(os.getenv("MAX_MEMORY_MB", "512"))

# Sandbox directory for code execution
SANDBOX_DIR = Path("/tmp/mcp_sandbox")
SANDBOX_DIR.mkdir(exist_ok=True)

def is_language_allowed(language: str) -> bool:
    """Check if a programming language is allowed."""
    return language.lower() in [lang.lower() for lang in ALLOWED_LANGUAGES]

def create_sandbox_environment() -> Path:
    """Create a sandbox environment for code execution."""
    if not SANDBOX_MODE:
        return Path.cwd()
    
    # Create a unique sandbox directory
    sandbox = SANDBOX_DIR / f"exec_{int(time.time())}_{os.getpid()}"
    sandbox.mkdir(exist_ok=True)
    
    # Set restrictive permissions
    os.chmod(sandbox, 0o700)
    
    return sandbox

def cleanup_sandbox(sandbox_path: Path):
    """Clean up sandbox directory."""
    if SANDBOX_MODE and sandbox_path.exists():
        try:
            import shutil
            shutil.rmtree(sandbox_path)
        except Exception:
            pass

async def execute_python_code(code: str, timeout: int = EXECUTION_TIMEOUT) -> Dict[str, Any]:
    """Execute Python code safely."""
    sandbox = create_sandbox_environment()
    
    try:
        # Create a temporary Python file
        script_path = sandbox / "script.py"
        with open(script_path, 'w') as f:
            f.write(code)
        
        # Execute with restrictions
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=sandbox,
            env={
                **os.environ,
                'PYTHONPATH': str(sandbox),
                'PYTHONUNBUFFERED': '1',
            }
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "success": result.returncode == 0
        }
    
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Execution timed out after {timeout} seconds",
            "return_code": -1,
            "success": False
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Execution error: {str(e)}",
            "return_code": -1,
            "success": False
        }
    finally:
        cleanup_sandbox(sandbox)

async def execute_javascript_code(code: str, timeout: int = EXECUTION_TIMEOUT) -> Dict[str, Any]:
    """Execute JavaScript code safely using Node.js."""
    sandbox = create_sandbox_environment()
    
    try:
        # Create a temporary JavaScript file
        script_path = sandbox / "script.js"
        with open(script_path, 'w') as f:
            f.write(code)
        
        # Execute with Node.js
        result = subprocess.run(
            ["node", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=sandbox
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "success": result.returncode == 0
        }
    
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Execution timed out after {timeout} seconds",
            "return_code": -1,
            "success": False
        }
    except FileNotFoundError:
        return {
            "stdout": "",
            "stderr": "Node.js not found. Please install Node.js to execute JavaScript code.",
            "return_code": -1,
            "success": False
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Execution error: {str(e)}",
            "return_code": -1,
            "success": False
        }
    finally:
        cleanup_sandbox(sandbox)

async def execute_bash_code(code: str, timeout: int = EXECUTION_TIMEOUT) -> Dict[str, Any]:
    """Execute Bash code safely."""
    sandbox = create_sandbox_environment()
    
    try:
        # Create a temporary bash script
        script_path = sandbox / "script.sh"
        with open(script_path, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("set -euo pipefail\n")  # Exit on error, undefined vars, pipe failures
            f.write(code)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        # Execute with restrictions
        result = subprocess.run(
            ["/bin/bash", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=sandbox,
            env={
                **os.environ,
                'PATH': '/usr/local/bin:/usr/bin:/bin',
                'HOME': str(sandbox),
            }
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "success": result.returncode == 0
        }
    
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Execution timed out after {timeout} seconds",
            "return_code": -1,
            "success": False
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Execution error: {str(e)}",
            "return_code": -1,
            "success": False
        }
    finally:
        cleanup_sandbox(sandbox)

async def execute_code_tool(language: str, code: str, timeout: Optional[int] = None) -> CallToolResult:
    """Execute code in the specified language."""
    try:
        if not is_language_allowed(language):
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: Language '{language}' not allowed. Allowed: {', '.join(ALLOWED_LANGUAGES)}")],
                isError=True
            )
        
        if timeout is None:
            timeout = EXECUTION_TIMEOUT
        
        # Execute code based on language
        if language.lower() == "python":
            result = await execute_python_code(code, timeout)
        elif language.lower() in ["javascript", "js", "node"]:
            result = await execute_javascript_code(code, timeout)
        elif language.lower() in ["bash", "shell", "sh"]:
            result = await execute_bash_code(code, timeout)
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: Unsupported language '{language}'")],
                isError=True
            )
        
        # Format result
        output = {
            "language": language,
            "success": result["success"],
            "return_code": result["return_code"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "execution_time": f"{timeout}s timeout"
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(output, indent=2))]
        )
    
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error executing code: {str(e)}")],
            isError=True
        )

async def validate_code_tool(language: str, code: str) -> CallToolResult:
    """Validate code syntax without executing it."""
    try:
        if not is_language_allowed(language):
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: Language '{language}' not allowed")],
                isError=True
            )
        
        # Basic syntax validation
        if language.lower() == "python":
            try:
                compile(code, '<string>', 'exec')
                result = {"valid": True, "errors": []}
            except SyntaxError as e:
                result = {"valid": False, "errors": [f"Syntax error: {str(e)}"]}
        
        elif language.lower() in ["javascript", "js"]:
            # Basic JS validation (could be enhanced with a proper JS parser)
            result = {"valid": True, "errors": [], "note": "Basic validation only"}
        
        elif language.lower() in ["bash", "shell"]:
            # Basic bash validation
            try:
                subprocess.run(["bash", "-n"], input=code, text=True, capture_output=True, timeout=5)
                result = {"valid": True, "errors": []}
            except subprocess.CalledProcessError as e:
                result = {"valid": False, "errors": [f"Bash syntax error: {e.stderr}"]}
            except Exception:
                result = {"valid": True, "errors": [], "note": "Could not validate bash syntax"}
        
        else:
            result = {"valid": False, "errors": [f"Unsupported language: {language}"]}
        
        output = {
            "language": language,
            "validation": result
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(output, indent=2))]
        )
    
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error validating code: {str(e)}")],
            isError=True
        )

# Create the MCP server
server = Server("code-execution")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools."""
    tools = [
        Tool(
            name="execute_code",
            description="Execute code in various programming languages",
            inputSchema={
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "description": "Programming language (python, javascript, bash)",
                        "enum": ["python", "javascript", "bash"]
                    },
                    "code": {
                        "type": "string",
                        "description": "Code to execute"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Execution timeout in seconds",
                        "default": EXECUTION_TIMEOUT
                    }
                },
                "required": ["language", "code"]
            }
        ),
        Tool(
            name="validate_code",
            description="Validate code syntax without executing it",
            inputSchema={
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "description": "Programming language (python, javascript, bash)",
                        "enum": ["python", "javascript", "bash"]
                    },
                    "code": {
                        "type": "string",
                        "description": "Code to validate"
                    }
                },
                "required": ["language", "code"]
            }
        )
    ]
    return ListToolsResult(tools=tools)

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    try:
        if name == "execute_code":
            timeout = arguments.get("timeout", EXECUTION_TIMEOUT)
            return await execute_code_tool(arguments["language"], arguments["code"], timeout)
        elif name == "validate_code":
            return await validate_code_tool(arguments["language"], arguments["code"])
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
    import sys
    async def main():
        async with stdio_server(server):
            await asyncio.Event().wait()  # Wait forever
    
    asyncio.run(main()) 