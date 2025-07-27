#!/usr/bin/env python3
"""
Test script for the reasoning chat functionality.

This script demonstrates how the reasoning chat provides step-by-step
solutions for mathematical and logical problems.
"""

import requests
import json

# Configuration
BACKEND_URL = "http://localhost:8000"

def test_reasoning_chat():
    """Test the reasoning chat functionality."""
    print("🧠 Testing Reasoning Chat Functionality")
    print("=" * 50)
    
    # Test problems
    test_problems = [
        {
            "problem": "Solve 2x + 3 = 7",
            "type": "mathematical",
            "expected": "linear equation"
        },
        {
            "problem": "Calculate the area of a circle with radius 5",
            "type": "mathematical", 
            "expected": "area calculation"
        },
        {
            "problem": "All humans are mortal. Socrates is human. Is Socrates mortal?",
            "type": "logical",
            "expected": "syllogistic reasoning"
        },
        {
            "problem": "What is the capital of France?",
            "type": "general",
            "expected": "factual question"
        }
    ]
    
    for i, test_case in enumerate(test_problems, 1):
        print(f"\n🔍 Test {i}: {test_case['type'].title()} Problem")
        print(f"Problem: {test_case['problem']}")
        print(f"Expected: {test_case['expected']}")
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/v1/reasoning-chat/",
                json={
                    "message": test_case["problem"],
                    "model": "llama3:latest",
                    "use_reasoning": True,
                    "show_steps": True,
                    "output_format": "markdown"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Status: Success")
                print(f"🧠 Reasoning Used: {data.get('reasoning_used', False)}")
                print(f"📊 Steps Generated: {data.get('steps_count', 0)}")
                
                if data.get("validation_summary"):
                    summary = data["validation_summary"]
                    print(f"✅ Validation: {summary.get('validity_rate', 0):.1%} valid")
                
                # Show a preview of the response
                response_text = data.get("response", "")
                preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
                print(f"📝 Response Preview: {preview}")
                
                # Check if it contains step-by-step reasoning
                if "Step" in response_text or "step" in response_text:
                    print("✅ Step-by-step reasoning detected")
                else:
                    print("⚠️ No step-by-step reasoning detected")
                
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 30)

def test_reasoning_chat_health():
    """Test the reasoning chat health endpoint."""
    print("\n🏥 Testing Reasoning Chat Health...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/reasoning-chat/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"🔧 Service: {data['service']}")
            print(f"🚀 Features:")
            for feature, status in data['features'].items():
                print(f"   • {feature}: {status}")
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def main():
    """Run all tests."""
    print("🧠 Reasoning Chat Test Suite")
    print("=" * 50)
    
    # Test health first
    test_reasoning_chat_health()
    
    # Test reasoning chat functionality
    test_reasoning_chat()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n🎉 You can now test reasoning chat through the frontend:")
    print("   1. Open http://localhost:8501 in your browser")
    print("   2. Enable '🧠 Enable Step-by-Step Reasoning' in the sidebar")
    print("   3. Ask mathematical or logical questions like:")
    print("      • 'Solve 2x + 3 = 7'")
    print("      • 'Calculate the area of a circle with radius 5'")
    print("      • 'All humans are mortal. Socrates is human. Is Socrates mortal?'")
    print("   4. You'll see step-by-step reasoning with validation!")

if __name__ == "__main__":
    main() 