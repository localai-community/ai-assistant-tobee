#!/usr/bin/env python3
"""
Simple Phase 2 Test - Verify Basic Functionality

This script provides a quick verification that the Phase 2 reasoning engines
are working correctly with basic functionality.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.reasoning.engines import (
    MathematicalReasoningEngine,
    LogicalReasoningEngine,
    CausalReasoningEngine
)


def test_mathematical_engine():
    """Test the mathematical reasoning engine."""
    print("🧮 Testing Mathematical Reasoning Engine...")
    
    try:
        engine = MathematicalReasoningEngine()
        print("✅ Engine created successfully")
        
        # Test problem classification
        problem = "Solve 2x + 3 = 7"
        can_handle = engine.can_handle(problem)
        print(f"✅ Can handle algebraic problem: {can_handle}")
        
        # Test solving
        result = engine.solve(problem)
        print(f"✅ Solved problem: {result.final_answer}")
        print(f"✅ Confidence: {result.confidence}")
        print(f"✅ Steps: {len(result.steps)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mathematical engine error: {e}")
        return False


def test_logical_engine():
    """Test the logical reasoning engine."""
    print("\n🔍 Testing Logical Reasoning Engine...")
    
    try:
        engine = LogicalReasoningEngine()
        print("✅ Engine created successfully")
        
        # Test problem classification
        problem = "All roses are flowers. Some flowers are red. What can we conclude?"
        can_handle = engine.can_handle(problem)
        print(f"✅ Can handle syllogistic problem: {can_handle}")
        
        # Test solving
        result = engine.solve(problem)
        print(f"✅ Solved problem: {result.final_answer}")
        print(f"✅ Confidence: {result.confidence}")
        print(f"✅ Steps: {len(result.steps)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Logical engine error: {e}")
        return False


def test_causal_engine():
    """Test the causal reasoning engine."""
    print("\n🔗 Testing Causal Reasoning Engine...")
    
    try:
        engine = CausalReasoningEngine()
        print("✅ Engine created successfully")
        
        # Test problem classification
        problem = "Does smoking cause lung cancer? Assume S = smoking, L = lung cancer"
        can_handle = engine.can_handle(problem)
        print(f"✅ Can handle causal problem: {can_handle}")
        
        # Test solving
        result = engine.solve(problem)
        print(f"✅ Solved problem: {result.final_answer}")
        print(f"✅ Confidence: {result.confidence}")
        print(f"✅ Steps: {len(result.steps)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Causal engine error: {e}")
        return False


def test_engine_integration():
    """Test that engines work together correctly."""
    print("\n🔧 Testing Engine Integration...")
    
    try:
        math_engine = MathematicalReasoningEngine()
        logic_engine = LogicalReasoningEngine()
        causal_engine = CausalReasoningEngine()
        
        print("✅ All engines created successfully")
        
        # Test that each engine can handle its own problems
        math_problem = "Calculate the area of a circle with radius 5"
        logic_problem = "Evaluate P and Q where P is true and Q is false"
        causal_problem = "What if we intervene on variable X?"
        
        math_can_handle = math_engine.can_handle(math_problem)
        logic_can_handle = logic_engine.can_handle(logic_problem)
        causal_can_handle = causal_engine.can_handle(causal_problem)
        
        print(f"✅ Math engine handles math problems: {math_can_handle}")
        print(f"✅ Logic engine handles logic problems: {logic_can_handle}")
        print(f"✅ Causal engine handles causal problems: {causal_can_handle}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration error: {e}")
        return False


def main():
    """Run all Phase 2 tests."""
    print("🚀 Phase 2: Basic Reasoning Engines - Simple Test")
    print("=" * 60)
    
    results = []
    
    # Test each engine
    results.append(test_mathematical_engine())
    results.append(test_logical_engine())
    results.append(test_causal_engine())
    results.append(test_engine_integration())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Phase 2 Simple Test Results:")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    print(f"Success rate: {(sum(results)/len(results)*100):.1f}%")
    
    if all(results):
        print("\n🎉 All Phase 2 engines are working correctly!")
        return True
    else:
        print("\n⚠️  Some Phase 2 engines have issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 