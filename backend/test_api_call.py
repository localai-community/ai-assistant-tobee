#!/usr/bin/env python3
"""
Test that mimics the exact API call.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_api_call():
    """Test that mimics the exact API call."""
    
    print("🔍 Testing API Call Mimic")
    print("=" * 50)
    
    try:
        # Import exactly like the API
        from app.reasoning.agents import SimplifiedHybridManager, create_all_local_agents
        from app.reasoning.agents.base import AgentTask
        import asyncio
        print("✅ Imports successful")
        
        # Create manager exactly like the API
        manager = SimplifiedHybridManager()
        
        # Register agents exactly like the API
        agents = create_all_local_agents()
        for agent in agents:
            manager.register_local_agent(agent)
        print(f"✅ Registered {len(agents)} agents")
        
        # Test exactly like the API call
        request_message = "What is 15 + 27?"
        request_task_type = "mathematical"
        
        print(f"\n🎯 Testing API call mimic:")
        print(f"   Message: {request_message}")
        print(f"   Task Type: {request_task_type}")
        
        # Set enhancement threshold (like API)
        manager.set_enhancement_threshold(0.7)
        
        # Create task exactly like the API
        task = AgentTask(
            task_id=f"task_{asyncio.get_event_loop().time()}",
            problem=request_message,
            task_type=request_task_type,
            priority="normal"
        )
        
        # Solve problem exactly like the API
        start_time = asyncio.get_event_loop().time()
        result = await manager.solve_problem(request_message, request_task_type)
        processing_time = asyncio.get_event_loop().time() - start_time
        
        # Get system status exactly like the API
        status = manager.get_system_status()
        
        print(f"\n📊 Results (API call mimic):")
        print(f"   Result: {result['result'][:100]}...")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Approach: {result['approach']}")
        print(f"   Agents Used: {result['agents_used']}")
        print(f"   Total Agents: {result['total_agents']}")
        print(f"   Processing Time: {processing_time}")
        print(f"   Enhancement Threshold: {status['enhancement_threshold']}")
        print(f"   A2A Available: {status['a2a_available']}")
        
        if result['confidence'] > 0:
            print(f"   ✅ SUCCESS: API call mimic working")
        else:
            print(f"   ❌ FAILURE: API call mimic not working")
            
            # Debug the exact same way
            print(f"\n🔍 Debugging API call mimic:")
            
            # Test agent registry
            print(f"   Registry: {status['registry']['total_agents']} total agents")
            
            # Test agent selection
            available_agents = manager.registry.get_agents_for_task(request_task_type)
            print(f"   Available agents for '{request_task_type}': {len(available_agents)}")
            for agent in available_agents:
                print(f"   - {agent.agent_id} ({agent.agent_type})")
            
            # Test local agent processing
            local_results = await manager.local_manager.process_with_local_agents(request_message, request_task_type)
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
    asyncio.run(test_api_call()) 