#!/usr/bin/env python3
"""
Minimal agent test.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_minimal_agent():
    """Test minimal agent functionality."""
    
    print("🔍 Testing Minimal Agent")
    print("=" * 50)
    
    try:
        # Import minimal components
        from app.reasoning.agents.base import AgentTask, AgentResult
        from app.reasoning.agents.local_agents import MathematicalAgent
        print("✅ Imports successful")
        
        # Create a single agent
        agent = MathematicalAgent()
        print(f"✅ Created agent: {agent.agent_id}")
        
        # Create a task
        task = AgentTask(
            task_id="test_task",
            problem="What is 15 + 27?",
            task_type="mathematical",
            priority="normal"
        )
        print(f"✅ Created task")
        
        # Test agent processing
        print(f"\n🔄 Testing agent processing:")
        result = await agent.process_task(task)
        print(f"   Agent: {result.agent_id}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Processing Time: {result.processing_time}")
        print(f"   Result Type: {type(result.result)}")
        print(f"   Result: {str(result.result)[:100]}...")
        
        if result.confidence > 0:
            print(f"   ✅ SUCCESS: Agent working correctly")
        else:
            print(f"   ❌ FAILURE: Agent not working correctly")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("🏁 Test complete")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_minimal_agent()) 