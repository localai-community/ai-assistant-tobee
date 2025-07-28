#!/usr/bin/env python3
"""
Simple test for mathematical problem solving.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_simple_math():
    """Test simple mathematical problem solving."""
    
    print("🧮 Testing Simple Mathematical Problem")
    print("=" * 50)
    
    try:
        from app.reasoning.agents.base import AgentTask
        from app.reasoning.agents.local_agents import MathematicalAgent, GeneralReasoningAgent
        from app.reasoning.agents.manager import SimplifiedHybridManager
        print("✅ Imports successful")
        
        # Create the manager
        manager = SimplifiedHybridManager()
        
        # Create agents
        math_agent = MathematicalAgent()
        general_agent = GeneralReasoningAgent()
        
        # Register agents
        manager.register_local_agent(math_agent)
        manager.register_local_agent(general_agent)
        print(f"✅ Registered agents")
        
        # Test the exact same problem as the test
        problem = "What is 15 + 27? Please explain step by step."
        task_type = "mathematical"
        
        print(f"\n🎯 Testing solve_problem:")
        print(f"   Problem: {problem}")
        print(f"   Task Type: {task_type}")
        
        result = await manager.solve_problem(problem, task_type)
        
        print(f"\n📊 Results:")
        print(f"   Result: {result['result'][:100]}...")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Approach: {result['approach']}")
        print(f"   Agents Used: {result['agents_used']}")
        
        if result['confidence'] > 0:
            print(f"   ✅ SUCCESS: Agents working correctly")
        else:
            print(f"   ❌ FAILURE: Agents not working correctly")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("🏁 Test complete")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_simple_math()) 