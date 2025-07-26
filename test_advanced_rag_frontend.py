#!/usr/bin/env python3
"""
Test script for Advanced RAG Frontend Integration
"""

import requests
import json
import time

def test_advanced_rag_integration():
    """Test the advanced RAG integration between frontend and backend."""
    
    base_url = "http://localhost:8000"
    frontend_url = "http://localhost:8501"
    
    print("🚀 Testing Advanced RAG Frontend Integration")
    print("=" * 50)
    
    # Test 1: Backend Health
    print("\n1. Testing Backend Health...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False
    
    # Test 2: Advanced RAG Health
    print("\n2. Testing Advanced RAG Health...")
    try:
        response = requests.get(f"{base_url}/api/v1/advanced-rag/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print("✅ Advanced RAG is healthy")
                components = data.get("components", {})
                for component, status in components.items():
                    status_icon = "✅" if status else "❌"
                    print(f"   {status_icon} {component}")
            else:
                print(f"❌ Advanced RAG health check failed: {data}")
                return False
        else:
            print(f"❌ Advanced RAG health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Advanced RAG health check error: {e}")
        return False
    
    # Test 3: Advanced RAG Strategies
    print("\n3. Testing Advanced RAG Strategies...")
    try:
        response = requests.get(f"{base_url}/api/v1/advanced-rag/strategies", timeout=5)
        if response.status_code == 200:
            data = response.json()
            strategies = data.get("strategies", {})
            print(f"✅ Found {len(strategies)} strategies:")
            for name, info in strategies.items():
                print(f"   • {name}: {info.get('description', 'No description')}")
        else:
            print(f"❌ Advanced RAG strategies check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Advanced RAG strategies check error: {e}")
        return False
    
    # Test 4: Frontend Accessibility
    print("\n4. Testing Frontend Accessibility...")
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend accessibility check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend accessibility check error: {e}")
        return False
    
    # Test 5: RAG Stats
    print("\n5. Testing RAG Stats...")
    try:
        response = requests.get(f"{base_url}/api/v1/rag/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            total_docs = data.get("total_documents", 0)
            print(f"✅ RAG Stats: {total_docs} documents loaded")
            if total_docs > 0:
                print("   📚 Documents available for testing")
            else:
                print("   ⚠️ No documents loaded - upload some for full testing")
        else:
            print(f"❌ RAG stats check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ RAG stats check error: {e}")
        return False
    
    # Test 6: Advanced RAG Chat (if documents available)
    print("\n6. Testing Advanced RAG Chat...")
    try:
        # First check if we have documents
        stats_response = requests.get(f"{base_url}/api/v1/rag/stats", timeout=5)
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            total_docs = stats_data.get("total_documents", 0)
            
            if total_docs > 0:
                # Test advanced RAG chat
                chat_payload = {
                    "message": "What is the main topic of the documents?",
                    "model": "llama3:latest",
                    "temperature": 0.7,
                    "k": 4,
                    "use_advanced_strategies": True,
                    "conversation_history": []
                }
                
                response = requests.post(
                    f"{base_url}/api/v1/advanced-rag/chat",
                    json=chat_payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Advanced RAG chat test successful")
                    print(f"   Response length: {len(data.get('response', ''))} characters")
                    print(f"   Strategies used: {data.get('strategies_used', [])}")
                    print(f"   Results count: {data.get('results_count', 0)}")
                else:
                    print(f"❌ Advanced RAG chat test failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
            else:
                print("⚠️ Skipping chat test - no documents available")
        else:
            print(f"❌ Could not check document count: {stats_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Advanced RAG chat test error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Advanced RAG integration is working correctly.")
    print("\n📋 Next Steps:")
    print("1. Open the frontend at: http://localhost:8501")
    print("2. Upload some documents in the sidebar")
    print("3. Enable 'Advanced RAG' in the RAG section")
    print("4. Ask questions to see the advanced retrieval in action!")
    
    return True

if __name__ == "__main__":
    success = test_advanced_rag_integration()
    if not success:
        print("\n❌ Some tests failed. Please check the backend and frontend logs.")
        exit(1) 