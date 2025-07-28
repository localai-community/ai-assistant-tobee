#!/usr/bin/env python3
"""
Debug script for Phase 4 agents.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.reasoning.agents import (
    SimplifiedHybridManager,
    create_all_local_agents,
    AgentTask
)


async def debug_agent_processing():
    """Debug agent processing step by step."""
    
    print("🔍 Debugging Phase 4 Agent Processing")
    print("=" * 50)
    
    # Create the hybrid manager
    manager = SimplifiedHybridManager()
    
    # Register all local agents
    agents = create_all_local_agents()
    for agent in agents:
        manager.register_local_agent(agent)
    
    print(f"✅ Registered {len(agents)} local agents:")
    for agent in agents:
        print(f"   - {agent.agent_id} ({', '.join(agent.capabilities[:3])})")
    
    print("\n" + "=" * 50)
    
    # Test a simple mathematical problem
    problem = "What is 15 + 27?"
    task_type = "mathematical"
    
    print(f"🧮 Testing Mathematical Problem:")
    print(f"   Problem: {problem}")
    print(f"   Task Type: {task_type}")
    
    # Create task
    task = AgentTask(
        task_id="debug_task_1",
        problem=problem,
        task_type=task_type,
        priority="normal"
    )
    
    # Test individual agents
    print(f"\n🔬 Testing Individual Agents:")
    
    for agent in agents:
        if "mathematical" in agent.capabilities or "general" in agent.capabilities:
            print(f"\n   Testing {agent.agent_id}:")
            try:
                result = await agent.process_task(task)
                print(f"      ✅ Success: {result.confidence:.2f} confidence")
                print(f"      Result: {str(result.result)[:100]}...")
            except Exception as e:
                print(f"      ❌ Error: {e}")
    
    print(f"\n" + "=" * 50)
    
    # Test the full manager
    print(f"🤖 Testing Full Manager:")
    try:
        result = await manager.solve_problem(problem, task_type)
        print(f"   ✅ Manager Result:")
        print(f"      Result: {result['result'][:100]}...")
        print(f"      Confidence: {result['confidence']}")
        print(f"      Approach: {result['approach']}")
        print(f"      Agents Used: {result['agents_used']}")
    except Exception as e:
        print(f"   ❌ Manager Error: {e}")


if __name__ == "__main__":
    asyncio.run(debug_agent_processing()) 