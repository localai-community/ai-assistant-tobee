#!/usr/bin/env python3
"""
Debug script to test agent results directly.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def debug_agent_results():
    """Debug agent results directly."""
    
    print("🔍 Debugging Agent Results")
    print("=" * 50)
    
    try:
        from app.reasoning.agents.base import AgentTask
        from app.reasoning.agents.local_agents import MathematicalAgent, GeneralReasoningAgent
        print("✅ Imports successful")
        
        # Create agents
        math_agent = MathematicalAgent()
        general_agent = GeneralReasoningAgent()
        
        # Create task
        task = AgentTask(
            task_id="debug_task",
            problem="What is 15 + 27?",
            task_type="mathematical",
            priority="normal"
        )
        
        print(f"\n🧮 Testing Mathematical Agent:")
        try:
            result = await math_agent.process_task(task)
            print(f"   ✅ Success:")
            print(f"      Agent ID: {result.agent_id}")
            print(f"      Confidence: {result.confidence}")
            print(f"      Processing Time: {result.processing_time}")
            print(f"      Result Type: {type(result.result)}")
            print(f"      Result: {str(result.result)[:200]}...")
            print(f"      Metadata: {result.metadata}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n🧠 Testing General Reasoning Agent:")
        try:
            result = await general_agent.process_task(task)
            print(f"   ✅ Success:")
            print(f"      Agent ID: {result.agent_id}")
            print(f"      Confidence: {result.confidence}")
            print(f"      Processing Time: {result.processing_time}")
            print(f"      Result Type: {type(result.result)}")
            print(f"      Result: {str(result.result)[:200]}...")
            print(f"      Metadata: {result.metadata}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test the manager's _get_best_result method
        print(f"\n🤖 Testing Manager Result Selection:")
        from app.reasoning.agents.manager import SimplifiedHybridManager
        
        manager = SimplifiedHybridManager()
        
        # Create some test results
        test_results = []
        
        # Add mathematical agent result
        try:
            math_result = await math_agent.process_task(task)
            test_results.append(math_result)
            print(f"   Added math result: {math_result.confidence} confidence")
        except Exception as e:
            print(f"   ❌ Math agent failed: {e}")
        
        # Add general agent result
        try:
            general_result = await general_agent.process_task(task)
            test_results.append(general_result)
            print(f"   Added general result: {general_result.confidence} confidence")
        except Exception as e:
            print(f"   ❌ General agent failed: {e}")
        
        # Test _get_best_result
        best_result = manager._get_best_result(test_results)
        if best_result:
            print(f"   ✅ Best result found:")
            print(f"      Agent: {best_result.agent_id}")
            print(f"      Confidence: {best_result.confidence}")
        else:
            print(f"   ❌ No best result found")
            print(f"      Total results: {len(test_results)}")
            for i, result in enumerate(test_results):
                print(f"      Result {i}: confidence={result.confidence}, result={result.result is not None}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("🏁 Debug complete")

# Run the test
if __name__ == "__main__":
    asyncio.run(debug_agent_results()) 