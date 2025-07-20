#!/usr/bin/env python3
"""
Test script for MCP integration
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

async def test_mcp_servers():
    """Test MCP servers directly."""
    print("🧪 Testing MCP Servers...")
    
    # Test filesystem server
    print("\n📁 Testing Filesystem Server:")
    try:
        from mcp_servers.filesystem.server import server as fs_server
        print("✅ Filesystem server imported successfully")
        
        # Test list tools
        tools = await fs_server.list_tools()
        print(f"📋 Available tools: {len(tools.tools)}")
        for tool in tools.tools:
            print(f"  • {tool.name}: {tool.description}")
            
    except Exception as e:
        print(f"❌ Filesystem server error: {e}")
    
    # Test code-execution server
    print("\n💻 Testing Code Execution Server:")
    try:
        from mcp_servers.code_execution.server import server as ce_server
        print("✅ Code execution server imported successfully")
        
        # Test list tools
        tools = await ce_server.list_tools()
        print(f"📋 Available tools: {len(tools.tools)}")
        for tool in tools.tools:
            print(f"  • {tool.name}: {tool.description}")
            
    except Exception as e:
        print(f"❌ Code execution server error: {e}")

async def test_mcp_manager():
    """Test MCP manager integration."""
    print("\n🔧 Testing MCP Manager...")
    
    try:
        from backend.app.mcp import MCPManager
        
        # Create manager
        manager = MCPManager("mcp-config-local.json")
        
        # Initialize
        success = await manager.initialize()
        print(f"✅ MCP Manager initialized: {success}")
        
        if success:
            # List tools
            tools = await manager.list_tools()
            print(f"📋 Total tools available: {len(tools)}")
            
            # Health check
            health = await manager.health_check()
            print(f"🏥 Health status: {health['overall_healthy']}")
            print(f"🖥️  Servers: {list(health['servers'].keys())}")
            
            # Test a simple tool call
            if tools:
                first_tool = tools[0]
                tool_name = f"filesystem.{first_tool.name}" if "filesystem" in str(first_tool) else f"code-execution.{first_tool.name}"
                print(f"🧪 Testing tool: {tool_name}")
                
                # This would require proper arguments based on the tool
                print("ℹ️  Tool call test skipped (requires specific arguments)")
        
        # Cleanup
        await manager.shutdown()
        print("✅ MCP Manager shutdown complete")
        
    except Exception as e:
        print(f"❌ MCP Manager error: {e}")

async def test_chat_integration():
    """Test chat service with MCP integration."""
    print("\n💬 Testing Chat Service with MCP...")
    
    try:
        from backend.app.services.chat import ChatService
        
        # Create chat service
        chat_service = ChatService(mcp_config_path="mcp-config-local.json")
        
        # Test MCP initialization
        await chat_service._ensure_mcp_initialized()
        print(f"✅ MCP initialized in chat service: {chat_service.mcp_initialized}")
        
        if chat_service.mcp_initialized:
            # Get available tools
            tools = await chat_service.get_available_tools()
            print(f"📋 Tools available in chat: {len(tools)}")
            
            # Test tool detection
            test_message = "list files in /tmp"
            tool_calls = chat_service._detect_tool_calls(test_message)
            print(f"🔍 Tool calls detected: {len(tool_calls)}")
            for tool_call in tool_calls:
                print(f"  • {tool_call['tool']}: {tool_call['arguments']}")
        
        # Cleanup
        await chat_service.mcp_manager.shutdown()
        print("✅ Chat service cleanup complete")
        
    except Exception as e:
        print(f"❌ Chat integration error: {e}")

async def main():
    """Run all tests."""
    print("🚀 Starting MCP Integration Tests...")
    
    await test_mcp_servers()
    await test_mcp_manager()
    await test_chat_integration()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 