"""
Integration tests for Phase 4.1: Simplified Hybrid Multi-Agent System.

This test suite verifies that the multi-agent system works correctly
with real problems and integrates properly with existing reasoning engines.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from backend.app.reasoning.agents import (
    SimplifiedHybridManager,
    create_local_agent,
    create_all_local_agents
)


class TestMultiAgentIntegration:
    """Test the multi-agent system with real problems."""
    
    @pytest.fixture
    def hybrid_manager(self):
        """Create a hybrid manager with all local agents."""
        manager = SimplifiedHybridManager()
        
        # Register all local agents
        agents = create_all_local_agents()
        for agent in agents:
            manager.register_local_agent(agent)
        
        return manager
    
    @pytest.mark.asyncio
    async def test_mathematical_problem_solving(self, hybrid_manager):
        """Test solving mathematical problems with multiple agents."""
        problem = "What is 15 + 27? Please explain step by step."
        
        result = await hybrid_manager.solve_problem(problem, "mathematical")
        
        assert result is not None
        assert "result" in result
        assert "confidence" in result
        assert "approach" in result
        assert "agents_used" in result
        assert result["approach"] in ["local_only", "hybrid"]
        
        print(f"Mathematical Problem Result:")
        print(f"  Result: {result['result'][:100]}...")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Approach: {result['approach']}")
        print(f"  Agents Used: {result['agents_used']}")
    
    @pytest.mark.asyncio
    async def test_logical_problem_solving(self, hybrid_manager):
        """Test solving logical problems with multiple agents."""
        problem = "If all A are B, and some B are C, what can we conclude about A and C?"
        
        result = await hybrid_manager.solve_problem(problem, "logical")
        
        assert result is not None
        assert "result" in result
        assert "confidence" in result
        assert "approach" in result
        assert result["approach"] in ["local_only", "hybrid"]
        
        print(f"Logical Problem Result:")
        print(f"  Result: {result['result'][:100]}...")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Approach: {result['approach']}")
        print(f"  Agents Used: {result['agents_used']}")
    
    @pytest.mark.asyncio
    async def test_complex_problem_solving(self, hybrid_manager):
        """Test solving complex problems that require multiple reasoning approaches."""
        problem = "Explain the relationship between supply and demand in economics, including mathematical models and real-world examples."
        
        result = await hybrid_manager.solve_problem(problem, "general")
        
        assert result is not None
        assert "result" in result
        assert "confidence" in result
        assert "approach" in result
        assert result["approach"] in ["local_only", "hybrid"]
        
        print(f"Complex Problem Result:")
        print(f"  Result: {result['result'][:100]}...")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Approach: {result['approach']}")
        print(f"  Agents Used: {result['agents_used']}")
    
    @pytest.mark.asyncio
    async def test_enhancement_threshold_behavior(self, hybrid_manager):
        """Test that enhancement threshold affects A2A usage."""
        # Set high threshold to force A2A usage (when available)
        hybrid_manager.set_enhancement_threshold(0.95)
        
        problem = "What is 2 + 2? Please explain step by step."
        
        result = await hybrid_manager.solve_problem(problem, "mathematical")
        
        assert result is not None
        assert "result" in result
        assert "confidence" in result
        assert "approach" in result
        
        print(f"High Threshold Result:")
        print(f"  Result: {result['result'][:100]}...")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Approach: {result['approach']}")
        print(f"  Agents Used: {result['agents_used']}")
    
    @pytest.mark.asyncio
    async def test_system_status_monitoring(self, hybrid_manager):
        """Test system status monitoring and agent health."""
        status = hybrid_manager.get_system_status()
        
        assert "registry" in status
        assert "a2a_available" in status
        assert "enhancement_threshold" in status
        assert "timestamp" in status
        
        registry = status["registry"]
        assert "local_agents" in registry
        assert "a2a_agents" in registry
        assert "total_agents" in registry
        
        # Should have 7 local agents registered
        assert registry["total_agents"] == 7
        assert len(registry["local_agents"]) == 7
        
        print(f"System Status:")
        print(f"  Total Agents: {registry['total_agents']}")
        print(f"  Local Agents: {len(registry['local_agents'])}")
        print(f"  A2A Available: {status['a2a_available']}")
        print(f"  Enhancement Threshold: {status['enhancement_threshold']}")
    
    @pytest.mark.asyncio
    async def test_agent_capability_matching(self, hybrid_manager):
        """Test that tasks are routed to appropriate agents."""
        from backend.app.reasoning.agents.base import AgentTask
        
        # Test mathematical task routing
        math_task = AgentTask("", "What is 2 + 2?", "mathematical")
        available_agents = hybrid_manager.registry.get_agents_for_task("mathematical")
        
        # Should have mathematical agents available
        math_agents = [agent for agent in available_agents if "mathematical" in agent.capabilities]
        assert len(math_agents) > 0
        
        # Test logical task routing
        logic_task = AgentTask("", "If A then B, A is true, therefore...", "logical")
        available_agents = hybrid_manager.registry.get_agents_for_task("logical")
        
        # Should have logical agents available
        logic_agents = [agent for agent in available_agents if "logical" in agent.capabilities]
        assert len(logic_agents) > 0
        
        print(f"Agent Capability Matching:")
        print(f"  Mathematical Agents: {len(math_agents)}")
        print(f"  Logical Agents: {len(logic_agents)}")
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, hybrid_manager):
        """Test error handling when agents fail."""
        # Create a problematic task that might cause issues
        problem = "This is a very complex problem that might cause some agents to fail: " + "x" * 1000
        
        # Should not crash, should handle gracefully
        result = await hybrid_manager.solve_problem(problem, "general")
        
        assert result is not None
        assert "result" in result
        assert "confidence" in result
        assert "approach" in result
        
        print(f"Error Handling Test:")
        print(f"  Result: {result['result'][:100]}...")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Approach: {result['approach']}")
    
    @pytest.mark.asyncio
    async def test_performance_characteristics(self, hybrid_manager):
        """Test performance characteristics of the multi-agent system."""
        import time
        
        problems = [
            "What is 5 + 3?",
            "If A then B, A is true, what can we conclude?",
            "Explain the concept of causality in simple terms.",
            "What is the relationship between price and demand?",
            "How do you solve a quadratic equation?"
        ]
        
        total_time = 0
        successful_results = 0
        
        for i, problem in enumerate(problems):
            start_time = time.time()
            
            try:
                result = await hybrid_manager.solve_problem(problem, "general")
                end_time = time.time()
                
                processing_time = end_time - start_time
                total_time += processing_time
                successful_results += 1
                
                print(f"Problem {i+1} ({processing_time:.2f}s): {result['confidence']:.2f} confidence")
                
            except Exception as e:
                print(f"Problem {i+1} failed: {e}")
        
        avg_time = total_time / successful_results if successful_results > 0 else 0
        
        print(f"Performance Summary:")
        print(f"  Total Problems: {len(problems)}")
        print(f"  Successful: {successful_results}")
        print(f"  Average Time: {avg_time:.2f}s")
        print(f"  Total Time: {total_time:.2f}s")
        
        # Performance assertions
        assert successful_results > 0, "At least some problems should be solved"
        assert avg_time < 10.0, "Average processing time should be reasonable"


class TestAgentCommunication:
    """Test agent communication and coordination."""
    
    @pytest.mark.asyncio
    async def test_agent_message_passing(self):
        """Test that agents can communicate with each other."""
        from backend.app.reasoning.agents.base import AgentMessage, AgentResponse
        
        # Create agents
        math_agent = create_local_agent("mathematical")
        logic_agent = create_local_agent("logical")
        
        # Test message passing
        message = AgentMessage(
            sender_id="math_agent",
            receiver_id="logic_agent",
            message_type="collaboration_request",
            content="Can you help with logical reasoning for this mathematical problem?"
        )
        
        response = await logic_agent.communicate(message)
        
        assert response is not None
        assert response.agent_id == "logical_agent"
        assert response.response_type == "acknowledgment"
        
        print(f"Agent Communication Test:")
        print(f"  Message: {message.message_type}")
        print(f"  Response: {response.response_type}")
    
    @pytest.mark.asyncio
    async def test_agent_health_checking(self):
        """Test agent health checking functionality."""
        # Create agents
        agents = create_all_local_agents()
        
        healthy_agents = 0
        
        for agent in agents:
            is_healthy = await agent.health_check()
            if is_healthy:
                healthy_agents += 1
        
        print(f"Agent Health Check:")
        print(f"  Total Agents: {len(agents)}")
        print(f"  Healthy Agents: {healthy_agents}")
        
        # All agents should be healthy
        assert healthy_agents == len(agents), "All agents should be healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 