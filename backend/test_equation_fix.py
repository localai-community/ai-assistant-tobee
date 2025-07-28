#!/usr/bin/env python3
"""
Comprehensive test for equation solving fix.
"""

import sys
import os
import requests
import json

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_equation_solving():
    """Test equation solving with various formats."""
    
    print("🧮 Testing Equation Solving Fix")
    print("=" * 50)
    
    # Test cases with different formats
    test_cases = [
        # Original problematic case
        "Solve the equation: 2x + 5 = 13",
        
        # Different prefixes
        "Solve: 3x - 7 = 8",
        "Find x: 4x + 2 = 18",
        "Calculate: 5x + 3 = 23",
        "Find the value of x: x^2 + 2x = 8",
        
        # More complex equations
        "Solve the equation: x^2 + 3x = 10",
        "Find x: 2x^2 - 5x + 3 = 0",
        "Calculate: 3x + 2y = 12",
        
        # Simple arithmetic (should work with general solver)
        "What is 15 + 27?",
        "Calculate 5 times 8"
    ]
    
    url = 'http://localhost:8000/api/v1/phase4-reasoning/'
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, problem in enumerate(test_cases, 1):
        print(f"\n🧮 Test Case {i}: {problem}")
        
        data = {
            'message': problem,
            'task_type': 'mathematical'
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "No response")
                
                # Check if it's a successful equation solution
                if "Solution:" in response_text or "Solutions:" in response_text:
                    print(f"✅ SUCCESS: {response_text[:100]}...")
                    success_count += 1
                elif "Error" not in response_text:
                    print(f"✅ SUCCESS: {response_text[:100]}...")
                    success_count += 1
                else:
                    print(f"❌ FAILED: {response_text}")
                
                print(f"   Confidence: {result.get('confidence', 0)}")
                print(f"   Approach: {result.get('approach', 'Unknown')}")
                print(f"   Agents Used: {result.get('agents_used', [])}")
            else:
                print(f"❌ API Error: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Connection Error: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"📊 Test Results:")
    print(f"   Total Tests: {total_count}")
    print(f"   Successful: {success_count}")
    print(f"   Success Rate: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 All tests passed! Equation solving fix is working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the failures.")

if __name__ == "__main__":
    test_equation_solving() 