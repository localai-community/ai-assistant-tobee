#!/usr/bin/env python3
"""
Simple Phase 4 Test

Quick test to verify Phase 4 multi-agent system is working correctly.
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.reasoning.agents import (
    SimplifiedHybridManager,
    create_all_local_agents
)


async def test_phase4_simple():
    """Run a simple test of Phase 4 functionality."""
    print("🧪 Simple Phase 4 Test")
    print("=" * 40)
    
    # Create manager and register agents
    manager = SimplifiedHybridManager()
    agents = create_all_local_agents()
    for agent in agents:
        manager.register_local_agent(agent)
    
    print(f"✅ Registered {len(agents)} agents")
    
    # Test questions from the sidebar
    test_questions = [
        {
            "question": "What is 15 + 27? Please explain step by step.",
            "type": "mathematical",
            "expected_agent": "mathematical_agent"
        },
        {
            "question": "What is 5 times 8?",
            "type": "mathematical", 
            "expected_agent": "mathematical_agent"
        },
        {
            "question": "If all A are B, and some B are C, what can we conclude about A and C?",
            "type": "logical",
            "expected_agent": "logical_agent"
        },
        {
            "question": "What causes inflation and how does it affect the economy?",
            "type": "causal",
            "expected_agent": "causal_agent"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_questions):
        print(f"\n🔍 Test {i+1}: {test_case['question']}")
        
        try:
            # Solve the problem
            result = await manager.solve_problem(
                test_case["question"], 
                task_type=test_case["type"]
            )
            
            # Check results
            agent_used = result.get("agent_used", "unknown")
            confidence = result.get("confidence", 0.0)
            approach = result.get("approach", "unknown")
            answer = result.get("answer", "")
            
            print(f"  Agent Used: {agent_used}")
            print(f"  Expected Agent: {test_case['expected_agent']}")
            print(f"  Confidence: {confidence:.2f}")
            print(f"  Approach: {approach}")
            print(f"  Answer: {answer[:100]}...")
            
            # Check if correct agent was selected
            agent_correct = agent_used == test_case["expected_agent"]
            print(f"  Agent Selection: {'✅' if agent_correct else '❌'}")
            
            results.append({
                "test": i + 1,
                "question": test_case["question"],
                "agent_used": agent_used,
                "expected_agent": test_case["expected_agent"],
                "agent_correct": agent_correct,
                "confidence": confidence,
                "approach": approach
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({
                "test": i + 1,
                "question": test_case["question"],
                "error": str(e)
            })
    
    # Summary
    print("\n📊 Summary")
    print("=" * 40)
    
    successful_tests = [r for r in results if "error" not in r]
    agent_correct_count = sum(1 for r in successful_tests if r.get("agent_correct", False))
    
    print(f"Total Tests: {len(results)}")
    print(f"Successful Tests: {len(successful_tests)}")
    print(f"Correct Agent Selection: {agent_correct_count}/{len(successful_tests)}")
    
    if successful_tests:
        avg_confidence = sum(r["confidence"] for r in successful_tests) / len(successful_tests)
        print(f"Average Confidence: {avg_confidence:.2f}")
    
    print("\n✅ Simple test completed!")


if __name__ == "__main__":
    asyncio.run(test_phase4_simple()) 