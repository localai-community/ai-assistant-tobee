#!/usr/bin/env python3
"""
Test Phase 2 UI Implementation

This script tests the Phase 2 reasoning engine UI implementation by:
1. Testing the backend API endpoints
2. Verifying engine status
3. Testing sample problems
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8000"

def test_phase2_status():
    """Test Phase 2 engine status endpoint."""
    print("🔍 Testing Phase 2 engine status...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/phase2-reasoning/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Phase 2 status endpoint working")
            print(f"   Status: {data.get('status')}")
            
            engines = data.get('engines', {})
            for engine_name, engine_info in engines.items():
                status = engine_info.get('status', 'unknown')
                features = engine_info.get('features', [])
                print(f"   {engine_name.title()}: {status} - {', '.join(features)}")
            
            return True
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
        return False

def test_phase2_health():
    """Test Phase 2 health endpoint."""
    print("\n🔍 Testing Phase 2 health endpoint...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/phase2-reasoning/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Phase 2 health endpoint working")
            print(f"   Service: {data.get('service')}")
            print(f"   Status: {data.get('status')}")
            
            features = data.get('features', {})
            for feature, status in features.items():
                print(f"   {feature}: {status}")
            
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_phase2_reasoning(problem, engine_type="auto"):
    """Test Phase 2 reasoning with a sample problem."""
    print(f"\n🔍 Testing Phase 2 reasoning with {engine_type} engine...")
    print(f"   Problem: {problem}")
    
    try:
        payload = {
            "message": problem,
            "model": "llama3:latest",
            "temperature": 0.7,
            "use_phase2_reasoning": True,
            "engine_type": engine_type,
            "show_steps": True,
            "output_format": "markdown",
            "include_validation": True
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/phase2-reasoning/",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Phase 2 reasoning working")
            print(f"   Engine used: {data.get('engine_used')}")
            print(f"   Reasoning type: {data.get('reasoning_type')}")
            print(f"   Steps count: {data.get('steps_count')}")
            print(f"   Confidence: {data.get('confidence')}")
            
            # Show a snippet of the response
            response_text = data.get('response', '')
            if response_text:
                snippet = response_text[:200] + "..." if len(response_text) > 200 else response_text
                print(f"   Response snippet: {snippet}")
            
            return True
        else:
            print(f"❌ Reasoning endpoint failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Reasoning endpoint error: {e}")
        return False

def main():
    """Run all Phase 2 UI tests."""
    print("🚀 Phase 2 UI Implementation Test")
    print("=" * 50)
    
    # Test backend health first
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not running. Please start the backend server first.")
            return
    except:
        print("❌ Backend is not running. Please start the backend server first.")
        return
    
    print("✅ Backend is running")
    
    # Test Phase 2 endpoints
    status_ok = test_phase2_status()
    health_ok = test_phase2_health()
    
    if status_ok and health_ok:
        print("\n🧪 Testing Phase 2 reasoning engines...")
        
        # Test mathematical reasoning
        math_problems = [
            "Solve 2x + 3 = 7",
            "Calculate the area of a circle with radius 5"
        ]
        
        for problem in math_problems:
            test_phase2_reasoning(problem, "mathematical")
            time.sleep(1)  # Small delay between requests
        
        # Test logical reasoning
        logic_problems = [
            "All A are B. Some B are C. What can we conclude?",
            "If P then Q. P is true. Is Q necessarily true?"
        ]
        
        for problem in logic_problems:
            test_phase2_reasoning(problem, "logical")
            time.sleep(1)
        
        # Test causal reasoning
        causal_problems = [
            "Does smoking cause lung cancer? Assume S = smoking, L = lung cancer",
            "What is the causal effect of education on income?"
        ]
        
        for problem in causal_problems:
            test_phase2_reasoning(problem, "causal")
            time.sleep(1)
        
        # Test auto-detection
        print("\n🔍 Testing auto-detection...")
        auto_problems = [
            "Solve x² - 4x + 3 = 0",
            "All humans are mortal. Socrates is human.",
            "Does exercise improve health outcomes?"
        ]
        
        for problem in auto_problems:
            test_phase2_reasoning(problem, "auto")
            time.sleep(1)
    
    print("\n" + "=" * 50)
    print("🎉 Phase 2 UI test completed!")
    print("\n📋 Next steps:")
    print("1. Start the frontend: cd frontend && streamlit run app.py")
    print("2. Open http://localhost:8501")
    print("3. Expand '🚀 Phase 2: Advanced Reasoning Engines' in the sidebar")
    print("4. Enable Phase 2 reasoning and test with sample questions")

if __name__ == "__main__":
    main() 