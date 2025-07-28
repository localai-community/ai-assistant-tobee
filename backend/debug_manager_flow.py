#!/usr/bin/env python3
"""
Debug script to test the full manager flow.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def debug_manager_flow():
    """Debug the full manager flow step by step."""
    
    print("🔍 Debugging Manager Flow")
    print("=" * 50)
    
    try:
        from app.reasoning.agents.base import AgentTask
        from app.reasoning.agents.local_agents import MathematicalAgent, GeneralReasoningAgent
        from app.reasoning.agents.manager import SimplifiedHybridManager
        print("✅ Imports successful")
        
        # Create the manager
        manager = SimplifiedHybridManager()
        print(f"✅ Created manager")
        
        # Create agents
        math_agent = MathematicalAgent()
        general_agent = GeneralReasoningAgent()
        
        # Register agents
        manager.register_local_agent(math_agent)
        manager.register_local_agent(general_agent)
        print(f"✅ Registered agents")
        
        # Test agent registry
        print(f"\n📋 Testing Agent Registry:")
        status = manager.get_system_status()
        print(f"   Registry status: {status['registry']['total_agents']} total agents")
        for agent_id, agent_info in status['registry']['local_agents'].items():
            print(f"   - {agent_id}: {agent_info.get('capabilities', [])}")
        
        # Test task routing
        print(f"\n🔄 Testing Task Routing:")
        problem = "What is 15 + 27?"
        task_type = "mathematical"
        
        # Test agent selection
        available_agents = manager.registry.get_agents_for_task(task_type)
        print(f"   Available agents for '{task_type}': {len(available_agents)}")
        for agent in available_agents:
            print(f"   - {agent.agent_id} ({agent.agent_type})")
        
        # Test local agent processing
        print(f"\n🤖 Testing Local Agent Processing:")
        local_results = await manager.local_manager.process_with_local_agents(problem, task_type)
        print(f"   Local results: {len(local_results)}")
        for result in local_results:
            print(f"   - {result.agent_id}: confidence={result.confidence}, result={result.result is not None}")
        
        # Test best result selection
        print(f"\n🏆 Testing Best Result Selection:")
        best_result = manager._get_best_result(local_results)
        if best_result:
            print(f"   ✅ Best result: {best_result.agent_id} (confidence: {best_result.confidence})")
        else:
            print(f"   ❌ No best result found")
        
        # Test full solve_problem
        print(f"\n🎯 Testing Full solve_problem:")
        final_result = await manager.solve_problem(problem, task_type)
        print(f"   Final result:")
        print(f"      Result: {final_result['result'][:100]}...")
        print(f"      Confidence: {final_result['confidence']}")
        print(f"      Approach: {final_result['approach']}")
        print(f"      Agents Used: {final_result['agents_used']}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("🏁 Debug complete")

# Run the test
if __name__ == "__main__":
    asyncio.run(debug_manager_flow()) 