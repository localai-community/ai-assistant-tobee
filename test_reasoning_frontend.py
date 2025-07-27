#!/usr/bin/env python3
"""
Test script for the reasoning system frontend integration.

This script demonstrates how to test the Phase 1 reasoning system
components through the API endpoints.
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8000"

def test_reasoning_health():
    """Test the reasoning system health endpoint."""
    print("🔍 Testing Reasoning System Health...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/reasoning/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']}")
            print(f"📋 Phase: {data['phase']}")
            print(f"🧩 Components:")
            for component_type, component_list in data['components'].items():
                if isinstance(component_list, list):
                    print(f"   • {component_type}: {', '.join(component_list)}")
                else:
                    print(f"   • {component_type}: {component_list}")
            return True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_problem_parsing():
    """Test problem statement parsing."""
    print("\n🔍 Testing Problem Parsing...")
    
    test_problems = [
        "Solve 2x + 3 = 7",
        "Calculate the area of a circle with radius 5",
        "What is the capital of France?",
        "Explain the process of photosynthesis"
    ]
    
    for problem in test_problems:
        try:
            response = requests.post(
                f"{BACKEND_URL}/reasoning/parse-problem",
                json={"problem_statement": problem},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    parsed_data = data['data']
                    print(f"✅ '{problem[:30]}...' -> {parsed_data['problem_type']}")
                    print(f"   📊 Numbers: {parsed_data['extracted_info']['numbers']}")
                    print(f"   🔤 Keywords: {parsed_data['extracted_info']['keywords']}")
                else:
                    print(f"❌ '{problem[:30]}...' -> Failed: {data.get('error_message', 'Unknown error')}")
            else:
                print(f"❌ '{problem[:30]}...' -> HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ '{problem[:30]}...' -> Error: {e}")

def test_step_parsing():
    """Test step-by-step reasoning parsing."""
    print("\n📝 Testing Step Parsing...")
    
    step_output = """
    Step 1: Identify the problem
    This is a mathematical problem involving area calculation.
    Confidence: 0.9
    
    Step 2: Apply the formula
    Area = π * r² = π * 5² = 25π
    Confidence: 0.95
    
    Step 3: Calculate the result
    Using π ≈ 3.14159, Area ≈ 78.54 square units
    Confidence: 0.98
    """
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/reasoning/parse-steps",
            json={"step_output": step_output},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                steps = data['data']
                print(f"✅ Parsed {len(steps)} steps:")
                for i, step in enumerate(steps, 1):
                    print(f"   Step {i}: {step.get('description', 'No description')}")
                    print(f"      Confidence: {step.get('confidence', 0)}")
            else:
                print(f"❌ Step parsing failed: {data.get('error_message', 'Unknown error')}")
        else:
            print(f"❌ Step parsing failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Step parsing error: {e}")

def test_validation():
    """Test reasoning validation."""
    print("\n✅ Testing Validation...")
    
    problem_statement = "Calculate the area of a circle with radius 5"
    steps = [
        {
            "description": "Identify the formula",
            "reasoning": "The area of a circle is A = πr²",
            "confidence": 0.9
        },
        {
            "description": "Substitute values",
            "reasoning": "A = π * 5² = 25π",
            "confidence": 0.95
        },
        {
            "description": "Calculate result",
            "reasoning": "A ≈ 78.54 square units",
            "confidence": 0.98
        }
    ]
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/reasoning/validate",
            json={
                "problem_statement": problem_statement,
                "steps": steps,
                "final_answer": "The area is approximately 78.54 square units",
                "confidence": 0.95
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            summary = data['summary']
            print(f"✅ Validation Summary:")
            print(f"   📊 Total: {summary['total']}")
            print(f"   ✅ Valid: {summary['valid']}")
            print(f"   ❌ Invalid: {summary['invalid']}")
            print(f"   📈 Validity Rate: {summary['validity_rate']:.2%}")
            
            # Show validation levels
            by_level = summary['by_level']
            for level, count in by_level.items():
                if count > 0:
                    print(f"   • {level.title()}: {count}")
        else:
            print(f"❌ Validation failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Validation error: {e}")

def test_formatting():
    """Test output formatting."""
    print("\n📄 Testing Output Formatting...")
    
    problem_statement = "Calculate the area of a circle with radius 5"
    steps = [
        {
            "description": "Identify the formula",
            "reasoning": "The area of a circle is A = πr²",
            "confidence": 0.9
        },
        {
            "description": "Calculate the result",
            "reasoning": "A = π * 5² = 25π ≈ 78.54",
            "confidence": 0.95
        }
    ]
    
    formats = ["json", "text", "markdown"]
    
    for format_type in formats:
        try:
            response = requests.post(
                f"{BACKEND_URL}/reasoning/format",
                json={
                    "problem_statement": problem_statement,
                    "steps": steps,
                    "final_answer": "The area is approximately 78.54 square units",
                    "confidence": 0.95,
                    "format_type": format_type
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    output = data['formatted_output']
                    print(f"✅ {format_type.upper()} Format:")
                    print(f"   Length: {len(output)} characters")
                    print(f"   Preview: {output[:100]}...")
                else:
                    print(f"❌ {format_type.upper()} formatting failed: {data.get('error_message', 'Unknown error')}")
            else:
                print(f"❌ {format_type.upper()} formatting failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {format_type.upper()} formatting error: {e}")

def test_complete_workflow():
    """Test the complete reasoning workflow."""
    print("\n🧪 Testing Complete Workflow...")
    
    test_problems = [
        "Solve 2x + 3 = 7",
        "Calculate the area of a circle with radius 5",
        "What is the capital of France?"
    ]
    
    for problem in test_problems:
        try:
            response = requests.post(
                f"{BACKEND_URL}/reasoning/test-workflow",
                json={
                    "problem_statement": problem,
                    "format_type": "json"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"✅ '{problem[:30]}...' -> Workflow successful")
                    print(f"   📊 Parsed problem type: {data['parsed_problem']['problem_type']}")
                    print(f"   ✅ Validation: {data['validation_results']['validation_summary']['validity_rate']:.2%} valid")
                    print(f"   📄 Output length: {len(data['formatted_output'])} characters")
                else:
                    print(f"❌ '{problem[:30]}...' -> Workflow failed: {data.get('error_message', 'Unknown error')}")
            else:
                print(f"❌ '{problem[:30]}...' -> HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ '{problem[:30]}...' -> Error: {e}")

def main():
    """Run all tests."""
    print("🧠 Reasoning System Frontend Test")
    print("=" * 50)
    
    # Test health first
    if not test_reasoning_health():
        print("❌ Reasoning system is not available. Please make sure the backend is running.")
        return
    
    # Run all tests
    test_problem_parsing()
    test_step_parsing()
    test_validation()
    test_formatting()
    test_complete_workflow()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n🎉 You can now test the reasoning system through the frontend:")
    print("   1. Open http://localhost:8501 in your browser")
    print("   2. Expand the '🧠 Reasoning System' section in the sidebar")
    print("   3. Click the test buttons to try different components")
    print("   4. Use the chat interface to ask questions")

if __name__ == "__main__":
    main() 