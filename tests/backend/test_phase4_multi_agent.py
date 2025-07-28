"""
Tests for Phase 4: Simplified Hybrid Multi-Agent System.

This test suite verifies the functionality of the simplified hybrid
multi-agent system with local-first and A2A fallback approach.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from backend.app.reasoning.agents import (
    SimplifiedHybridManager,
    create_local_agent,
    create_all_local_agents,
    AgentTask,
    TaskPriority
)


class TestSimplifiedHybridManager:
    """Test the simplified hybrid manager functionality."""
    
    @pytest.fixture
    def hybrid_manager(self):
        """Create a hybrid manager for testing."""
        return SimplifiedHybridManager()
    
    @pytest.fixture
    def sample_problem(self):
        """Sample problem for testing."""
        return "What is 2 + 2? Please explain step by step."
    
    @pytest.fixture
    def complex_problem(self):
        """Complex problem for testing."""
        return "Explain the relationship between supply and demand in economics, including mathematical models and real-world examples."
    
    def test_manager_initialization(self, hybrid_manager):
        """Test that the hybrid manager initializes correctly."""
        assert hybrid_manager is not None
        assert hybrid_manager.registry is not None
        assert hybrid_manager.local_manager is not None
        assert hybrid_manager.a2a_manager is not None
        assert hybrid_manager.enhancement_threshold == 0.7
    
    def test_register_local_agent(self, hybrid_manager):
        """Test registering local agents."""
        # Create a mock local agent
        mock_agent = Mock()
        mock_agent.agent_id = "test_agent"
        mock_agent.capabilities = ["mathematical"]
        mock_agent.agent_type = "local"
        
        # Register the agent
        hybrid_manager.register_local_agent(mock_agent)
        
        # Verify registration
        assert "test_agent" in hybrid_manager.registry.local_agents
        assert hybrid_manager.registry.local_agents["test_agent"] == mock_agent
    
    def test_register_a2a_agent(self, hybrid_manager):
        """Test registering A2A agents."""
        # Create a mock A2A agent
        mock_agent = Mock()
        mock_agent.agent_id = "test_a2a_agent"
        mock_agent.capabilities = ["general"]
        mock_agent.agent_type = "a2a"
        mock_agent.is_available = True
        
        # Register the agent
        hybrid_manager.register_a2a_agent(mock_agent)
        
        # Verify registration
        assert "test_a2a_agent" in hybrid_manager.registry.a2a_agents
        assert hybrid_manager.registry.a2a_agents["test_a2a_agent"] == mock_agent
    
    def test_get_system_status(self, hybrid_manager):
        """Test getting system status."""
        status = hybrid_manager.get_system_status()
        
        assert "registry" in status
        assert "a2a_available" in status
        assert "enhancement_threshold" in status
        assert "timestamp" in status
        assert status["enhancement_threshold"] == 0.7
    
    def test_set_enhancement_threshold(self, hybrid_manager):
        """Test setting enhancement threshold."""
        # Test valid threshold
        hybrid_manager.set_enhancement_threshold(0.8)
        assert hybrid_manager.enhancement_threshold == 0.8
        
        # Test invalid threshold
        with pytest.raises(ValueError):
            hybrid_manager.set_enhancement_threshold(1.5)
        
        with pytest.raises(ValueError):
            hybrid_manager.set_enhancement_threshold(-0.1)


class TestLocalAgents:
    """Test local agent functionality."""
    
    def test_create_mathematical_agent(self):
        """Test creating mathematical agent."""
        agent = create_local_agent("mathematical")
        assert agent.agent_id == "mathematical_agent"
        assert "mathematical" in agent.capabilities
        assert agent.agent_type == "local"
    
    def test_create_logical_agent(self):
        """Test creating logical agent."""
        agent = create_local_agent("logical")
        assert agent.agent_id == "logical_agent"
        assert "logical" in agent.capabilities
        assert agent.agent_type == "local"
    
    def test_create_cot_agent(self):
        """Test creating CoT agent."""
        agent = create_local_agent("cot")
        assert agent.agent_id == "cot_agent"
        assert "cot" in agent.capabilities
        assert agent.agent_type == "local"
    
    def test_create_tot_agent(self):
        """Test creating ToT agent."""
        agent = create_local_agent("tot")
        assert agent.agent_id == "tot_agent"
        assert "tot" in agent.capabilities
        assert agent.agent_type == "local"
    
    def test_create_prompt_engineering_agent(self):
        """Test creating prompt engineering agent."""
        agent = create_local_agent("prompt_engineering")
        assert agent.agent_id == "prompt_engineering_agent"
        assert "prompt_engineering" in agent.capabilities
        assert agent.agent_type == "local"
    
    def test_create_general_agent(self):
        """Test creating general reasoning agent."""
        agent = create_local_agent("general")
        assert agent.agent_id == "general_agent"
        assert "general" in agent.capabilities
        assert agent.agent_type == "local"
    
    def test_create_agent_with_custom_id(self):
        """Test creating agent with custom ID."""
        agent = create_local_agent("mathematical", "custom_math_agent")
        assert agent.agent_id == "custom_math_agent"
        assert "mathematical" in agent.capabilities
    
    def test_create_unknown_agent_type(self):
        """Test creating agent with unknown type."""
        with pytest.raises(ValueError):
            create_local_agent("unknown_type")
    
    def test_create_all_local_agents(self):
        """Test creating all local agents."""
        agents = create_all_local_agents()
        
        assert len(agents) == 7  # All agent types
        agent_ids = [agent.agent_id for agent in agents]
        
        expected_ids = [
            "mathematical_agent",
            "logical_agent", 
            "causal_agent",
            "cot_agent",
            "tot_agent",
            "prompt_engineering_agent",
            "general_reasoning_agent"
        ]
        
        for expected_id in expected_ids:
            assert expected_id in agent_ids


class TestAgentTask:
    """Test AgentTask functionality."""
    
    def test_agent_task_creation(self):
        """Test creating an agent task."""
        task = AgentTask(
            task_id="test_task",
            problem="What is 2 + 2?",
            task_type="mathematical"
        )
        
        assert task.task_id == "test_task"
        assert task.problem == "What is 2 + 2?"
        assert task.task_type == "mathematical"
        assert task.priority == TaskPriority.NORMAL
        assert task.dependencies == []
        assert task.metadata == {}
    
    def test_agent_task_with_priority(self):
        """Test creating agent task with priority."""
        task = AgentTask(
            task_id="test_task",
            problem="What is 2 + 2?",
            task_type="mathematical",
            priority=TaskPriority.HIGH
        )
        
        assert task.priority == TaskPriority.HIGH
    
    def test_agent_task_with_priority_string(self):
        """Test creating agent task with priority as string."""
        task = AgentTask(
            task_id="test_task",
            problem="What is 2 + 2?",
            task_type="mathematical",
            priority="high"
        )
        
        assert task.priority == TaskPriority.HIGH


class TestAgentResult:
    """Test AgentResult functionality."""
    
    def test_agent_result_creation(self):
        """Test creating an agent result."""
        from backend.app.reasoning.agents.base import AgentResult
        
        result = AgentResult(
            agent_id="test_agent",
            result="The answer is 4",
            confidence=0.9,
            processing_time=1.5
        )
        
        assert result.agent_id == "test_agent"
        assert result.result == "The answer is 4"
        assert result.confidence == 0.9
        assert result.processing_time == 1.5
        assert result.metadata == {}
    
    def test_agent_result_invalid_confidence(self):
        """Test agent result with invalid confidence."""
        from backend.app.reasoning.agents.base import AgentResult
        
        with pytest.raises(ValueError):
            AgentResult(
                agent_id="test_agent",
                result="The answer is 4",
                confidence=1.5,  # Invalid confidence
                processing_time=1.5
            )


class TestSimplifiedHybridWorkflow:
    """Test the complete simplified hybrid workflow."""
    
    @pytest.mark.asyncio
    async def test_local_only_workflow(self):
        """Test workflow with only local agents."""
        manager = SimplifiedHybridManager()
        
        # Register local agents
        mathematical_agent = create_local_agent("mathematical")
        logical_agent = create_local_agent("logical")
        
        manager.register_local_agent(mathematical_agent)
        manager.register_local_agent(logical_agent)
        
        # Test solving a problem
        problem = "What is 2 + 2? Please explain step by step."
        result = await manager.solve_problem(problem, "mathematical")
        
        assert result is not None
        assert "result" in result
        assert "confidence" in result
        assert "approach" in result
        assert result["approach"] in ["local_only", "hybrid"]
    
    @pytest.mark.asyncio
    async def test_enhancement_threshold_workflow(self):
        """Test workflow with enhancement threshold."""
        manager = SimplifiedHybridManager()
        
        # Set low enhancement threshold to trigger A2A
        manager.set_enhancement_threshold(0.9)
        
        # Register local agent that will produce low confidence result
        mathematical_agent = create_local_agent("mathematical")
        manager.register_local_agent(mathematical_agent)
        
        # Test solving a problem
        problem = "What is 2 + 2? Please explain step by step."
        result = await manager.solve_problem(problem, "mathematical")
        
        assert result is not None
        assert "result" in result
        assert "confidence" in result
        assert "approach" in result


class TestAgentCapabilities:
    """Test agent capability matching."""
    
    def test_agent_can_handle_task(self):
        """Test that agents can correctly identify if they can handle tasks."""
        from backend.app.reasoning.agents.base import AgentTask
        
        # Create mathematical agent
        mathematical_agent = create_local_agent("mathematical")
        
        # Test mathematical task
        math_task = AgentTask("", "What is 2 + 2?", "mathematical")
        assert mathematical_agent.can_handle_task(math_task) is True
        
        # Test non-mathematical task
        logic_task = AgentTask("", "If A then B, A is true, therefore...", "logical")
        assert mathematical_agent.can_handle_task(logic_task) is False
    
    def test_general_agent_capabilities(self):
        """Test that general agent can handle multiple task types."""
        from backend.app.reasoning.agents.base import AgentTask
        
        general_agent = create_local_agent("general")
        
        # Test various task types
        task_types = ["mathematical", "logical", "causal", "cot", "tot"]
        
        for task_type in task_types:
            task = AgentTask("", "Test problem", task_type)
            assert general_agent.can_handle_task(task) is True


if __name__ == "__main__":
    pytest.main([__file__]) 