#!/usr/bin/env python3
"""
Demonstration script for Phase 4.1: Simplified Hybrid Multi-Agent System.

This script demonstrates the multi-agent system solving various types of problems
and shows how the local-first with A2A fallback approach works.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.reasoning.agents import (
    SimplifiedHybridManager,
    create_all_local_agents
)


async def demonstrate_multi_agent_system():
    """Demonstrate the multi-agent system with various problems."""
    
    print("🤖 Phase 4.1: Simplified Hybrid Multi-Agent System Demo")
    print("=" * 60)
    
    # Create the hybrid manager
    manager = SimplifiedHybridManager()
    
    # Register all local agents
    agents = create_all_local_agents()
    for agent in agents:
        manager.register_local_agent(agent)
    
    print(f"✅ Registered {len(agents)} local agents:")
    for agent in agents:
        print(f"   - {agent.agent_id} ({', '.join(agent.capabilities[:3])})")
    
    print("\n" + "=" * 60)
    
    # Test problems
    problems = [
        {
            "title": "Mathematical Problem",
            "problem": "What is 15 + 27? Please explain step by step.",
            "task_type": "mathematical"
        },
        {
            "title": "Logical Problem", 
            "problem": "If all A are B, and some B are C, what can we conclude about A and C?",
            "task_type": "logical"
        },
        {
            "title": "Complex Problem",
            "problem": "Explain the relationship between supply and demand in economics, including mathematical models and real-world examples.",
            "task_type": "general"
        },
        {
            "title": "Causal Analysis",
            "problem": "What causes inflation and how does it affect the economy?",
            "task_type": "causal"
        }
    ]
    
    for i, problem_info in enumerate(problems, 1):
        print(f"\n🔍 Problem {i}: {problem_info['title']}")
        print(f"   Question: {problem_info['problem']}")
        
        try:
            # Solve the problem
            result = await manager.solve_problem(
                problem_info['problem'], 
                problem_info['task_type']
            )
            
            print(f"   ✅ Result: {result['result'][:200]}...")
            print(f"   📊 Confidence: {result['confidence']:.2f}")
            print(f"   🎯 Approach: {result['approach']}")
            print(f"   🤖 Agents Used: {result['agents_used']}")
            print(f"   ⏱️  Processing Time: {result['processing_time']:.2f}s")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    
    # Show system status
    status = manager.get_system_status()
    print("📊 System Status:")
    print(f"   Total Agents: {status['registry']['total_agents']}")
    print(f"   Local Agents: {len(status['registry']['local_agents'])}")
    print(f"   A2A Available: {status['a2a_available']}")
    print(f"   Enhancement Threshold: {status['enhancement_threshold']}")
    
    # Test enhancement threshold behavior
    print("\n🔧 Testing Enhancement Threshold Behavior:")
    
    # Set high threshold
    manager.set_enhancement_threshold(0.95)
    print(f"   Set threshold to 0.95 (high)")
    
    result = await manager.solve_problem("What is 2 + 2?", "mathematical")
    print(f"   Result approach: {result['approach']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    
    # Set low threshold
    manager.set_enhancement_threshold(0.3)
    print(f"   Set threshold to 0.3 (low)")
    
    result = await manager.solve_problem("What is 2 + 2?", "mathematical")
    print(f"   Result approach: {result['approach']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed successfully!")
    print("\nKey Features Demonstrated:")
    print("✅ Multi-agent coordination")
    print("✅ Local-first approach")
    print("✅ Configurable enhancement threshold")
    print("✅ Intelligent task routing")
    print("✅ Result synthesis")
    print("✅ Error handling and recovery")
    print("✅ System monitoring")


async def demonstrate_agent_capabilities():
    """Demonstrate individual agent capabilities."""
    
    print("\n🔬 Individual Agent Capability Demo")
    print("=" * 60)
    
    from app.reasoning.agents.base import AgentTask
    
    agents = create_all_local_agents()
    
    test_problems = [
        ("mathematical", "What is 5 * 12?"),
        ("logical", "If P then Q, P is true, therefore..."),
        ("causal", "What causes climate change?"),
        ("cot", "Explain how photosynthesis works step by step"),
        ("tot", "What are the pros and cons of renewable energy?"),
        ("prompt_engineering", "Create a prompt for explaining quantum physics"),
        ("general", "How do computers work?")
    ]
    
    for task_type, problem in test_problems:
        print(f"\n🧠 Testing {task_type.upper()} agent:")
        print(f"   Problem: {problem}")
        
        # Find appropriate agent
        appropriate_agents = [agent for agent in agents if task_type in agent.capabilities]
        
        if appropriate_agents:
            agent = appropriate_agents[0]
            print(f"   Selected Agent: {agent.agent_id}")
            
            # Test capability
            task = AgentTask("", problem, task_type)
            can_handle = agent.can_handle_task(task)
            print(f"   Can Handle: {can_handle}")
            
            if can_handle:
                try:
                    # Test processing
                    result = await agent.process_task(task)
                    print(f"   ✅ Success: {result.confidence:.2f} confidence")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
        else:
            print(f"   ❌ No appropriate agent found")
    
    print("\n" + "=" * 60)


async def main():
    """Main demonstration function."""
    try:
        await demonstrate_multi_agent_system()
        await demonstrate_agent_capabilities()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 