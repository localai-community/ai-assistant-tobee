#!/usr/bin/env python3
"""
Direct test of the API manager.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_api_direct():
    """Test the API manager directly."""
    
    print("🔍 Testing API Manager Directly")
    print("=" * 50)
    
    try:
        # Import exactly what the API imports
        from app.reasoning.agents import SimplifiedHybridManager, create_all_local_agents
        from app.reasoning.agents.base import AgentTask
        print("✅ Imports successful")
        
        # Create manager exactly like the API
        manager = SimplifiedHybridManager()
        print(f"✅ Created manager")
        
        # Register agents exactly like the API
        agents = create_all_local_agents()
        for agent in agents:
            manager.register_local_agent(agent)
        print(f"✅ Registered {len(agents)} agents")
        
        # Test with exact same problem
        problem = "What is 15 + 27?"
        task_type = "mathematical"
        
        print(f"\n🎯 Testing solve_problem:")
        print(f"   Problem: {problem}")
        print(f"   Task Type: {task_type}")
        
        # Test solve_problem
        result = await manager.solve_problem(problem, task_type)
        
        print(f"\n📊 Results:")
        print(f"   Result: {result['result'][:100]}...")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Approach: {result['approach']}")
        print(f"   Agents Used: {result['agents_used']}")
        print(f"   Total Agents: {result['total_agents']}")
        
        if result['confidence'] > 0:
            print(f"   ✅ SUCCESS: Direct API test working")
        else:
            print(f"   ❌ FAILURE: Direct API test not working")
            
            # Test individual components
            print(f"\n🔍 Testing individual components:")
            
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
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("🏁 Test complete")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_api_direct()) 