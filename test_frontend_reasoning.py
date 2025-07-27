#!/usr/bin/env python3
"""
Test script to verify the frontend reasoning chat integration.
"""

import requests
import json
import time

# Configuration
FRONTEND_URL = "http://localhost:8501"
BACKEND_URL = "http://localhost:8000"

def test_frontend_access():
    """Test if the frontend is accessible."""
    print("🌐 Testing Frontend Access...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend access error: {e}")
        return False

def test_backend_reasoning_chat():
    """Test the backend reasoning chat endpoint."""
    print("\n🧠 Testing Backend Reasoning Chat...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/reasoning-chat/",
            json={
                "message": "Solve 2x + 3 = 7",
                "model": "llama3:latest",
                "use_reasoning": True
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend reasoning chat is working")
            print(f"   • Reasoning used: {data.get('reasoning_used', False)}")
            print(f"   • Steps count: {data.get('steps_count', 0)}")
            print(f"   • Response length: {len(data.get('response', ''))} characters")
            return True
        else:
            print(f"❌ Backend reasoning chat failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend reasoning chat error: {e}")
        return False

def test_backend_health():
    """Test backend health endpoints."""
    print("\n🏥 Testing Backend Health...")
    
    endpoints = [
        ("/health", "Main Health"),
        ("/api/v1/reasoning-chat/health", "Reasoning Chat Health"),
        ("/reasoning/health", "Reasoning System Health")
    ]
    
    all_healthy = True
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Healthy")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                all_healthy = False
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            all_healthy = False
    
    return all_healthy

def main():
    """Run all tests."""
    print("🧠 Frontend Reasoning Chat Integration Test")
    print("=" * 50)
    
    # Test frontend access
    frontend_ok = test_frontend_access()
    
    # Test backend health
    backend_ok = test_backend_health()
    
    # Test reasoning chat functionality
    reasoning_ok = test_backend_reasoning_chat()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   • Frontend Access: {'✅' if frontend_ok else '❌'}")
    print(f"   • Backend Health: {'✅' if backend_ok else '❌'}")
    print(f"   • Reasoning Chat: {'✅' if reasoning_ok else '❌'}")
    
    if frontend_ok and backend_ok and reasoning_ok:
        print("\n🎉 All tests passed! The reasoning chat integration is working correctly.")
        print("\n📝 Next Steps:")
        print("   1. Open http://localhost:8501 in your browser")
        print("   2. Look for '🧠 Reasoning Chat' section in the sidebar")
        print("   3. Enable 'Enable Step-by-Step Reasoning' checkbox")
        print("   4. Ask a mathematical question like 'Solve 2x + 3 = 7'")
        print("   5. You should see step-by-step reasoning in the response!")
    else:
        print("\n⚠️ Some tests failed. Please check the services and try again.")
        
        if not frontend_ok:
            print("   • Make sure the frontend is running: cd frontend && streamlit run app.py")
        if not backend_ok:
            print("   • Make sure the backend is running: cd backend && python -m uvicorn app.main:app")
        if not reasoning_ok:
            print("   • Check the backend logs for reasoning chat errors")

if __name__ == "__main__":
    main() 