#!/usr/bin/env python3
"""
Debug script for Phase 4 agents without ChatService dependency.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_agents_without_chat():
    """Test agents without ChatService dependency."""
    
    print("🔍 Testing agents without ChatService...")
    
    try:
        # Import base classes
        from app.reasoning.agents.base import AgentTask, AgentResult
        print("✅ Base classes imported")
        
        # Import reasoning engines directly
        from app.reasoning.engines import MathematicalReasoningEngine
        print("✅ MathematicalReasoningEngine imported")
        
        # Test the mathematical engine directly
        print("\n🧮 Testing Mathematical Reasoning Engine:")
        engine = MathematicalReasoningEngine()
        problem = "What is 15 + 27?"
        
        print(f"   Problem: {problem}")
        result = await engine.reason(problem)
        print(f"   ✅ Engine result: {result}")
        
        if hasattr(result, 'final_answer'):
            print(f"   Final Answer: {result.final_answer}")
        if hasattr(result, 'steps'):
            print(f"   Steps: {len(result.steps)} steps")
        
        # Test creating a simple agent manually
        print("\n🤖 Testing Manual Agent Creation:")
        
        class SimpleMathematicalAgent:
            def __init__(self):
                self.agent_id = "simple_math_agent"
                self.capabilities = ["mathematical"]
                self.engine = MathematicalReasoningEngine()
            
            async def process_task(self, task):
                result = await self.engine.reason(task.problem)
                return AgentResult(
                    agent_id=self.agent_id,
                    result=str(result),
                    confidence=0.8,
                    processing_time=0.1,
                    metadata={"agent_type": "local"}
                )
        
        # Create agent and task
        agent = SimpleMathematicalAgent()
        task = AgentTask(
            task_id="test_task",
            problem="What is 15 + 27?",
            task_type="mathematical",
            priority="normal"
        )
        
        # Process task
        result = await agent.process_task(task)
        print(f"   ✅ Agent result:")
        print(f"      Confidence: {result.confidence}")
        print(f"      Result: {result.result[:100]}...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("🏁 Debug complete")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_agents_without_chat()) 