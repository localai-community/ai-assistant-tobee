#!/usr/bin/env python3
"""
LocalAI Community - Chat Service Test
Tests the chat service and Ollama integration.
"""

import asyncio
import sys
import os

# Path is set by the test runner

from app.services.chat import ChatService, ChatRequest
import httpx

async def test_ollama_connection():
    """Test connection to Ollama."""
    print("🔗 Testing Ollama Connection...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                print(f"  ✅ Ollama is running")
                print(f"  📋 Available models: {models}")
                return True, models
            else:
                print(f"  ❌ Ollama responded with status: {response.status_code}")
                return False, []
    except Exception as e:
        print(f"  ❌ Failed to connect to Ollama: {e}")
        return False, []

async def test_chat_service():
    """Test the chat service."""
    print("\n🤖 Testing Chat Service...")
    
    try:
        async with ChatService() as chat_service:
            # Test health check
            print("  🔍 Testing health check...")
            health = await chat_service.check_ollama_health()
            if health:
                print("    ✅ Health check passed")
            else:
                print("    ❌ Health check failed")
                return False
            
            # Test model listing
            print("  📋 Testing model listing...")
            models = await chat_service.get_available_models()
            if models:
                print(f"    ✅ Found {len(models)} models: {models}")
            else:
                print("    ⚠️  No models found")
            
            # Test basic chat (if models available)
            if models:
                print("  💬 Testing basic chat...")
                try:
                    response = await chat_service.generate_response(
                        message="Hello! Please respond with 'Hello from Ollama!'",
                        model=models[0],
                        temperature=0.1
                    )
                    print(f"    ✅ Chat response: {response.response[:100]}...")
                    print(f"    📊 Conversation ID: {response.conversation_id}")
                    return True
                except Exception as e:
                    print(f"    ❌ Chat test failed: {e}")
                    return False
            else:
                print("    ⚠️  Skipping chat test (no models available)")
                return True
                
    except Exception as e:
        print(f"  ❌ Chat service test failed: {e}")
        return False

async def test_chat_api():
    """Test the chat API endpoints."""
    print("\n🌐 Testing Chat API...")
    
    try:
        async with httpx.AsyncClient() as client:
            base_url = "http://localhost:8000"
            
            # Test health endpoint
            print("  🔍 Testing API health...")
            response = await client.get(f"{base_url}/api/v1/chat/health")
            if response.status_code == 200:
                data = response.json()
                print(f"    ✅ API health: {data}")
            else:
                print(f"    ❌ API health failed: {response.status_code}")
                return False
            
            # Test models endpoint
            print("  📋 Testing models endpoint...")
            response = await client.get(f"{base_url}/api/v1/chat/models")
            if response.status_code == 200:
                models = response.json()
                print(f"    ✅ Available models: {models}")
            else:
                print(f"    ❌ Models endpoint failed: {response.status_code}")
                return False
            
            # Test chat endpoint (if models available)
            if models:
                print("  💬 Testing chat endpoint...")
                chat_request = {
                    "message": "Hello! Please respond with 'Hello from API!'",
                    "model": models[0],
                    "temperature": 0.1
                }
                response = await client.post(f"{base_url}/api/v1/chat/", json=chat_request)
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✅ Chat response: {data['response'][:100]}...")
                    print(f"    📊 Conversation ID: {data['conversation_id']}")
                    return True
                else:
                    print(f"    ❌ Chat endpoint failed: {response.status_code}")
                    print(f"    📄 Response: {response.text}")
                    return False
            else:
                print("    ⚠️  Skipping chat endpoint test (no models available)")
                return True
                
    except Exception as e:
        print(f"  ❌ Chat API test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🧪 LocalAI Community - Chat Service Test")
    print("=" * 50)
    
    # Test Ollama connection
    ollama_ok, models = await test_ollama_connection()
    
    if not ollama_ok:
        print("\n❌ Ollama is not running or not accessible.")
        print("   Please start Ollama first:")
        print("   ollama serve")
        print("   ollama pull llama3.2")
        return False
    
    # Test chat service
    service_ok = await test_chat_service()
    
    # Test chat API (if backend is running)
    api_ok = await test_chat_api()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"🔗 Ollama Connection: {'✅' if ollama_ok else '❌'}")
    print(f"🤖 Chat Service: {'✅' if service_ok else '❌'}")
    print(f"🌐 Chat API: {'✅' if api_ok else '❌'}")
    
    if ollama_ok and service_ok:
        print("\n🎉 Chat functionality is working!")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 