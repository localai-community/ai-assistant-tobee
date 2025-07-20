#!/usr/bin/env python3
"""
LocalAI Community Frontend - Chat API Test
Tests the frontend's ability to communicate with the new chat API.
"""

import asyncio
import httpx
import sys
import os

# Configuration
BACKEND_URL = "http://localhost:8000"

async def test_backend_health():
    """Test backend health endpoint."""
    print("🔍 Testing Backend Health...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/health", timeout=5.0)
            if response.status_code == 200:
                print("  ✅ Backend is running")
                return True
            else:
                print(f"  ❌ Backend health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"  ❌ Backend connection failed: {e}")
        return False

async def test_chat_health():
    """Test chat service health."""
    print("\n🤖 Testing Chat Service Health...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/api/v1/chat/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Chat service health: {data['status']}")
                print(f"  🔗 Ollama available: {data.get('ollama_available', False)}")
                print(f"  📋 Available models: {data.get('available_models', [])}")
                print(f"  💬 Conversation count: {data.get('conversation_count', 0)}")
                return data
            else:
                print(f"  ❌ Chat health check failed: {response.status_code}")
                return None
    except Exception as e:
        print(f"  ❌ Chat health check failed: {e}")
        return None

async def test_chat_models():
    """Test getting available models."""
    print("\n📋 Testing Available Models...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/api/v1/chat/models", timeout=5.0)
            if response.status_code == 200:
                models = response.json()
                print(f"  ✅ Found {len(models)} models: {models}")
                return models
            else:
                print(f"  ❌ Models endpoint failed: {response.status_code}")
                return []
    except Exception as e:
        print(f"  ❌ Models endpoint failed: {e}")
        return []

async def test_chat_message():
    """Test sending a chat message."""
    print("\n💬 Testing Chat Message...")
    
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "message": "Hello! Please respond with 'Hello from API test!'",
                "model": "llama3.2",
                "temperature": 0.1,
                "stream": False
            }
            
            response = await client.post(f"{BACKEND_URL}/api/v1/chat/", json=payload, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Chat response: {data['response'][:100]}...")
                print(f"  📊 Conversation ID: {data['conversation_id']}")
                print(f"  🤖 Model used: {data['model']}")
                return data
            elif response.status_code == 503:
                print("  ❌ Ollama service not available")
                return None
            else:
                print(f"  ❌ Chat endpoint failed: {response.status_code}")
                print(f"  📄 Response: {response.text}")
                return None
    except Exception as e:
        print(f"  ❌ Chat message test failed: {e}")
        return None

async def test_conversations():
    """Test conversation management."""
    print("\n💭 Testing Conversation Management...")
    
    try:
        async with httpx.AsyncClient() as client:
            # List conversations
            response = await client.get(f"{BACKEND_URL}/api/v1/chat/conversations", timeout=5.0)
            if response.status_code == 200:
                conversations = response.json()
                print(f"  ✅ Found {len(conversations)} conversations")
                for conv in conversations[:3]:  # Show first 3
                    print(f"    • {conv['id']}: {len(conv['messages'])} messages")
                return conversations
            else:
                print(f"  ❌ Conversations endpoint failed: {response.status_code}")
                return []
    except Exception as e:
        print(f"  ❌ Conversations test failed: {e}")
        return []

async def test_frontend_compatibility():
    """Test if frontend can communicate with the API."""
    print("\n🌐 Testing Frontend Compatibility...")
    
    try:
        # Test the same endpoints the frontend uses
        async with httpx.AsyncClient() as client:
            # Test health endpoint (frontend uses this)
            response = await client.get(f"{BACKEND_URL}/health", timeout=5.0)
            if response.status_code != 200:
                print("  ❌ Frontend health check would fail")
                return False
            
            # Test chat health endpoint (frontend uses this)
            response = await client.get(f"{BACKEND_URL}/api/v1/chat/health", timeout=5.0)
            if response.status_code != 200:
                print("  ❌ Frontend chat health check would fail")
                return False
            
            # Test models endpoint (frontend uses this)
            response = await client.get(f"{BACKEND_URL}/api/v1/chat/models", timeout=5.0)
            if response.status_code != 200:
                print("  ❌ Frontend models check would fail")
                return False
            
            # Test chat endpoint (frontend uses this)
            payload = {
                "message": "Test message",
                "model": "llama3.2",
                "temperature": 0.7,
                "stream": False
            }
            response = await client.post(f"{BACKEND_URL}/api/v1/chat/", json=payload, timeout=10.0)
            if response.status_code not in [200, 503]:  # 503 is OK if Ollama not running
                print("  ❌ Frontend chat endpoint would fail")
                return False
            
            print("  ✅ Frontend compatibility test passed")
            return True
            
    except Exception as e:
        print(f"  ❌ Frontend compatibility test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🧪 LocalAI Community Frontend - Chat API Test")
    print("=" * 60)
    
    # Test backend health
    backend_ok = await test_backend_health()
    
    if not backend_ok:
        print("\n❌ Backend is not running.")
        print("   Please start the backend first:")
        print("   cd backend && ./start_server.sh")
        return False
    
    # Test chat health
    chat_health = await test_chat_health()
    
    # Test available models
    models = await test_chat_models()
    
    # Test chat message (if Ollama is available)
    if chat_health and chat_health.get("ollama_available", False):
        chat_response = await test_chat_message()
    else:
        print("\n⚠️  Skipping chat message test (Ollama not available)")
        chat_response = None
    
    # Test conversations
    conversations = await test_conversations()
    
    # Test frontend compatibility
    frontend_ok = await test_frontend_compatibility()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FRONTEND CHAT API TEST SUMMARY")
    print("=" * 60)
    print(f"🔗 Backend Health: {'✅' if backend_ok else '❌'}")
    print(f"🤖 Chat Service: {'✅' if chat_health else '❌'}")
    print(f"📋 Models Available: {'✅' if models else '❌'}")
    print(f"💬 Chat Response: {'✅' if chat_response else '❌'}")
    print(f"💭 Conversations: {'✅' if conversations is not None else '❌'}")
    print(f"🌐 Frontend Compatible: {'✅' if frontend_ok else '❌'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 Frontend is ready to use with the chat API!")
        if chat_health and chat_health.get("ollama_available", False):
            print("   Ollama is available and ready for chat.")
        else:
            print("   ⚠️  Ollama not available - chat won't work until Ollama is started.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 