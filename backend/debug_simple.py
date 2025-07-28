#!/usr/bin/env python3
"""
Simple debug script for Phase 4 agents.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_agent_processing():
    """Test agent processing."""
    # Test imports one by one
    print("🔍 Testing imports...")

    try:
        from app.reasoning.agents.base import AgentTask, AgentResult
        print("✅ Base classes imported")
    except Exception as e:
        print(f"❌ Base classes import failed: {e}")

    try:
        from app.reasoning.agents.local_agents import MathematicalAgent
        print("✅ MathematicalAgent imported")
    except Exception as e:
        print(f"❌ MathematicalAgent import failed: {e}")

    try:
        from app.reasoning.agents.manager import SimplifiedHybridManager
        print("✅ SimplifiedHybridManager imported")
    except Exception as e:
        print(f"❌ SimplifiedHybridManager import failed: {e}")

    print("\n" + "=" * 50)

    # Test simple agent creation
    print("🧪 Testing agent creation...")
    
    try:
        # Create a mathematical agent
        math_agent = MathematicalAgent()
        print(f"✅ Created MathematicalAgent: {math_agent.agent_id}")
        print(f"   Capabilities: {math_agent.capabilities}")
        
        # Create a task
        task = AgentTask(
            task_id="test_task",
            problem="What is 15 + 27?",
            task_type="mathematical",
            priority="normal"
        )
        print(f"✅ Created task: {task.task_id}")
        
        # Test if agent can handle task
        can_handle = math_agent.can_handle_task(task)
        print(f"✅ Agent can handle task: {can_handle}")
        
        # Test agent processing
        print("🔄 Testing agent processing...")
        result = await math_agent.process_task(task)
        print(f"✅ Agent processing completed:")
        print(f"   Confidence: {result.confidence}")
        print(f"   Processing Time: {result.processing_time}")
        print(f"   Result: {str(result.result)[:100]}...")
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("🏁 Debug complete")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_agent_processing()) 