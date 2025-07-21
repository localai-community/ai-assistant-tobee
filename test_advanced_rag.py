#!/usr/bin/env python3
"""
Test script for Advanced RAG implementation
"""

import sys
import os
import asyncio
import httpx
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_advanced_rag_health():
    """Test advanced RAG health endpoint"""
    print("🔍 Testing Advanced RAG Health...")
    
    try:
        with httpx.Client() as client:
            response = client.get("http://localhost:8000/api/v1/advanced-rag/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['status']}")
                print(f"   Components: {data['components']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_advanced_rag_strategies():
    """Test advanced RAG strategies endpoint"""
    print("\n🔍 Testing Advanced RAG Strategies...")
    
    try:
        with httpx.Client() as client:
            response = client.get("http://localhost:8000/api/v1/advanced-rag/strategies")
            
            if response.status_code == 200:
                data = response.json()
                strategies = data['strategies']
                print(f"✅ Strategies endpoint working")
                print(f"   Available strategies: {list(strategies.keys())}")
                
                for name, info in strategies.items():
                    print(f"   - {name}: {info['description']}")
                return True
            else:
                print(f"❌ Strategies endpoint failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Strategies test error: {e}")
        return False

def test_advanced_rag_search():
    """Test advanced RAG search endpoint"""
    print("\n🔍 Testing Advanced RAG Search...")
    
    try:
        with httpx.Client() as client:
            # Test search with advanced strategies
            search_data = {
                "query": "What is attention in neural networks?",
                "k": 5,
                "use_advanced_strategies": True
            }
            
            response = client.post(
                "http://localhost:8000/api/v1/advanced-rag/search",
                data=search_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Search endpoint working")
                print(f"   Query: {data['query']}")
                print(f"   Strategies used: {data['strategies_used']}")
                print(f"   Results count: {data['results_count']}")
                return True
            else:
                print(f"❌ Search endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Search test error: {e}")
        return False

def test_advanced_rag_chat():
    """Test advanced RAG chat endpoint"""
    print("\n🔍 Testing Advanced RAG Chat...")
    
    try:
        with httpx.Client() as client:
            # Test chat with conversation history
            chat_data = {
                "message": "What is attention?",
                "model": "llama3:latest",
                "temperature": 0.7,
                "k": 4,
                "use_advanced_strategies": True,
                "conversation_history": [
                    {"role": "user", "content": "Tell me about neural networks"},
                    {"role": "assistant", "content": "Neural networks are computational models..."}
                ]
            }
            
            response = client.post(
                "http://localhost:8000/api/v1/advanced-rag/chat",
                json=chat_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat endpoint working")
                print(f"   Response length: {len(data['response'])} characters")
                print(f"   Strategies used: {data['strategies_used']}")
                print(f"   Has context: {data['has_context']}")
                return True
            else:
                print(f"❌ Chat endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Chat test error: {e}")
        return False

def test_backend_status():
    """Test if backend is running"""
    print("🔍 Testing Backend Status...")
    
    try:
        with httpx.Client() as client:
            response = client.get("http://localhost:8000/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend is running: {data['status']}")
                return True
            else:
                print(f"❌ Backend not responding: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        print("   Make sure the backend is running on http://localhost:8000")
        return False

def main():
    """Run all tests"""
    print("🚀 Advanced RAG Implementation Test")
    print("=" * 50)
    
    # Test backend status first
    if not test_backend_status():
        print("\n❌ Backend not available. Please start the backend first:")
        print("   cd backend && python -m uvicorn app.main:app --reload")
        return
    
    # Run advanced RAG tests
    tests = [
        test_advanced_rag_health,
        test_advanced_rag_strategies,
        test_advanced_rag_search,
        test_advanced_rag_chat
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Advanced RAG implementation is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the implementation.")
    
    print("\n📋 Next Steps:")
    print("1. Install advanced dependencies: pip install -r backend/requirements-advanced.txt")
    print("2. Install spaCy model: python -m spacy download en_core_web_sm")
    print("3. Add documents to test with: POST /api/v1/rag/upload")
    print("4. Use advanced RAG: POST /api/v1/advanced-rag/chat")

if __name__ == "__main__":
    main() 