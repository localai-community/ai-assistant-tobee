#!/usr/bin/env python3
"""
Debug script to test the API manager directly.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def debug_api_manager():
    """Debug the API manager directly."""
    
    print("🔍 Debugging API Manager")
    print("=" * 50)
    
    try:
        # Import the same modules as the API
        from app.reasoning.agents import SimplifiedHybridManager, create_all_local_agents
        from app.reasoning.agents.base import AgentTask
        print("✅ Imports successful")
        
        # Create the manager (same as API)
        manager = SimplifiedHybridManager()
        print(f"✅ Created manager")
        
        # Register agents (same as API)
        agents = create_all_local_agents()
        for agent in agents:
            manager.register_local_agent(agent)
        print(f"✅ Registered {len(agents)} agents")
        
        # Test the exact same problem as the API
        problem = "What is 15 + 27?"
        task_type = "mathematical"
        
        print(f"\n🎯 Testing API Manager:")
        print(f"   Problem: {problem}")
        print(f"   Task Type: {task_type}")
        
        # Test solve_problem (same as API)
        result = await manager.solve_problem(problem, task_type)
        
        print(f"\n📊 API Manager Results:")
        print(f"   Result: {result['result'][:100]}...")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Approach: {result['approach']}")
        print(f"   Agents Used: {result['agents_used']}")
        print(f"   Total Agents: {result['total_agents']}")
        
        if result['confidence'] > 0:
            print(f"   ✅ SUCCESS: API Manager working correctly")
        else:
            print(f"   ❌ FAILURE: API Manager not working correctly")
            
            # Debug further
            print(f"\n🔍 Debugging further:")
            
            # Test agent registry
            status = manager.get_system_status()
            print(f"   Registry: {status['registry']['total_agents']} total agents")
            
            # Test agent selection
            available_agents = manager.registry.get_agents_for_task(task_type)
            print(f"   Available agents for '{task_type}': {len(available_agents)}")
            for agent in available_agents:
                print(f"   - {agent.agent_id} ({agent.agent_type})")
            
            # Test local agent processing
            local_results = await manager.local_manager.process_with_local_agents(problem, task_type)
            print(f"   Local results: {len(local_results)}")
            for result_item in local_results:
                print(f"   - {result_item.agent_id}: confidence={result_item.confidence}, result={result_item.result is not None}")
            
            # Test best result selection
            best_result = manager._get_best_result(local_results)
            if best_result:
                print(f"   ✅ Best result: {best_result.agent_id} (confidence: {best_result.confidence})")
            else:
                print(f"   ❌ No best result found")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("🏁 Debug complete")

# Run the test
if __name__ == "__main__":
    asyncio.run(debug_api_manager()) 