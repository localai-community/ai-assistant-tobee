"""
Comprehensive test suite for Phase 3 advanced reasoning features.

This test suite covers:
- Chain-of-Thought (CoT) reasoning strategy
- Tree-of-Thoughts (ToT) reasoning strategy  
- Prompt Engineering Framework
- Integration between advanced strategies
"""

import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone

from backend.app.reasoning.strategies.chain_of_thought import (
    ChainOfThoughtStrategy, CoTConfig, CoTStep
)
from backend.app.reasoning.strategies.tree_of_thoughts import (
    TreeOfThoughtsStrategy, ToTConfig, ToTNode, ToTPath, SearchAlgorithm, PathEvaluationStrategy
)
from backend.app.reasoning.strategies.prompt_engineering import (
    PromptEngineeringFramework, PromptTemplate, PromptType, OptimizationStrategy,
    PromptContext, PromptResult, ABTestConfig, ABTestResult, PromptEngineeringConfig
)
from backend.app.reasoning.core.base import (
    ReasoningResult, ReasoningStep, StepStatus, ValidationLevel, ReasoningType
)


class TestChainOfThoughtStrategy:
    """Test suite for Chain-of-Thought reasoning strategy."""

    @pytest.fixture
    def cot_strategy(self):
        """Create a CoT strategy instance."""
        config = CoTConfig(
            max_steps=5,
            min_confidence_threshold=0.6,
            max_iterations=2,
            enable_validation=True,
            enable_refinement=True
        )
        return ChainOfThoughtStrategy(config=config)

    @pytest.mark.asyncio
    async def test_cot_initialization(self, cot_strategy):
        """Test CoT strategy initialization."""
        assert cot_strategy.name == "Chain-of-Thought"
        assert cot_strategy.reasoning_type == ReasoningType.HYBRID
        assert cot_strategy.config.max_steps == 5
        assert cot_strategy.config.min_confidence_threshold == 0.6

    @pytest.mark.asyncio
    async def test_cot_mathematical_problem(self, cot_strategy):
        """Test CoT with mathematical problem."""
        problem = "What is 15 + 27?"
        
        result = await cot_strategy.reason(problem)
        
        assert result is not None
        assert result.problem_statement == problem
        assert len(result.steps) > 0
        assert result.confidence > 0.0
        assert result.final_answer is not None

    @pytest.mark.asyncio
    async def test_cot_logical_problem(self, cot_strategy):
        """Test CoT with logical problem."""
        problem = "If all A are B, and some B are C, what can we conclude about A and C?"
        
        result = await cot_strategy.reason(problem)
        
        assert result is not None
        assert result.problem_statement == problem
        assert len(result.steps) > 0
        assert result.confidence > 0.0

    @pytest.mark.asyncio
    async def test_cot_general_problem(self, cot_strategy):
        """Test CoT with general problem."""
        problem = "How can I improve my productivity at work?"
        
        result = await cot_strategy.reason(problem)
        
        assert result is not None
        assert result.problem_statement == problem
        assert len(result.steps) > 0

    @pytest.mark.asyncio
    async def test_cot_validation(self, cot_strategy):
        """Test CoT input validation."""
        # Test empty problem
        result = await cot_strategy.reason("")
        assert result is not None
        assert len(result.validation_results) > 0
        assert not result.validation_results[0].is_valid

    @pytest.mark.asyncio
    async def test_cot_step_generation(self, cot_strategy):
        """Test CoT step generation methods."""
        problem_content = "What is 10 + 20?"
        
        # Test mathematical step generation
        steps = cot_strategy._generate_math_cot_steps(problem_content)
        assert len(steps) > 0
        assert all(isinstance(step, CoTStep) for step in steps)
        assert all(step.confidence > 0.0 for step in steps)

    @pytest.mark.asyncio
    async def test_cot_confidence_calculation(self, cot_strategy):
        """Test CoT confidence calculation."""
        # Create a test result with steps
        result = ReasoningResult(problem_statement="Test problem")
        
        # Add test steps with different confidences
        for i in range(3):
            step = ReasoningStep(
                step_number=i + 1,
                description=f"Step {i + 1}",
                reasoning=f"Reasoning {i + 1}",
                confidence=0.5 + (i * 0.1)
            )
            result.add_step(step)
        
        confidence = cot_strategy._calculate_overall_confidence(result)
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should be weighted average

    @pytest.mark.asyncio
    async def test_cot_step_refinement(self, cot_strategy):
        """Test CoT step refinement."""
        # Create a step with low confidence
        step = ReasoningStep(
            step_number=1,
            description="Test step",
            reasoning="Original reasoning",
            confidence=0.3
        )
        
        refined_step = await cot_strategy._refine_step(step)
        assert refined_step is not None
        assert refined_step.confidence > step.confidence
        assert "Refined:" in refined_step.reasoning

    def test_cot_can_handle(self, cot_strategy):
        """Test CoT can_handle method."""
        assert cot_strategy.can_handle("Valid problem")
        assert not cot_strategy.can_handle("")
        assert not cot_strategy.can_handle("   ")

    def test_cot_reset(self, cot_strategy):
        """Test CoT reset functionality."""
        cot_strategy.iteration_count = 5
        cot_strategy.cot_steps = [CoTStep("test", 1, "thought", "action", "obs", 0.8)]
        
        cot_strategy.reset()
        
        assert cot_strategy.iteration_count == 0
        assert len(cot_strategy.cot_steps) == 0


class TestTreeOfThoughtsStrategy:
    """Test suite for Tree-of-Thoughts reasoning strategy."""

    @pytest.fixture
    def tot_strategy(self):
        """Create a ToT strategy instance."""
        config = ToTConfig(
            max_depth=3,
            max_branching_factor=2,
            max_nodes=20,
            search_algorithm=SearchAlgorithm.BEAM,
            evaluation_strategy=PathEvaluationStrategy.HYBRID,
            beam_width=2
        )
        return TreeOfThoughtsStrategy(config=config)

    @pytest.mark.asyncio
    async def test_tot_initialization(self, tot_strategy):
        """Test ToT strategy initialization."""
        assert tot_strategy.name == "Tree-of-Thoughts"
        assert tot_strategy.reasoning_type == ReasoningType.HYBRID
        assert tot_strategy.config.max_depth == 3
        assert tot_strategy.config.search_algorithm == SearchAlgorithm.BEAM

    @pytest.mark.asyncio
    async def test_tot_mathematical_problem(self, tot_strategy):
        """Test ToT with mathematical problem."""
        problem = "What is 25 * 4?"
        
        result = await tot_strategy.reason(problem)
        
        assert result is not None
        assert result.problem_statement == problem
        assert len(result.steps) > 0
        assert result.confidence > 0.0

    @pytest.mark.asyncio
    async def test_tot_complex_problem(self, tot_strategy):
        """Test ToT with complex problem."""
        problem = "How can I design a system to handle user authentication with multiple providers?"
        
        result = await tot_strategy.reason(problem)
        
        assert result is not None
        assert result.problem_statement == problem
        assert len(result.steps) > 0

    @pytest.mark.asyncio
    async def test_tot_root_node_creation(self, tot_strategy):
        """Test ToT root node creation."""
        parsed_problem = {
            "type": "mathematical",
            "content": "What is 10 + 20?"
        }
        
        root_node = await tot_strategy._create_root_node(parsed_problem)
        
        assert root_node is not None
        assert root_node.node_id == "root"
        assert root_node.depth == 0
        assert root_node.parent_id is None
        assert "mathematical" in root_node.thought.lower()

    @pytest.mark.asyncio
    async def test_tot_beam_search(self, tot_strategy):
        """Test ToT beam search algorithm."""
        # Create a root node
        root_node = ToTNode(
            node_id="root",
            thought="Initial thought",
            action="Initial action",
            observation="Initial observation",
            confidence=0.8,
            depth=0
        )
        
        tot_strategy.nodes[root_node.node_id] = root_node
        
        # Run beam search
        await tot_strategy._beam_search(root_node)
        
        # Check that nodes were created
        assert len(tot_strategy.nodes) > 1
        assert root_node.children

    @pytest.mark.asyncio
    async def test_tot_path_evaluation(self, tot_strategy):
        """Test ToT path evaluation."""
        # Create test nodes
        nodes = [
            ToTNode("node1", "thought1", "action1", "obs1", 0.8, 0),
            ToTNode("node2", "thought2", "action2", "obs2", 0.9, 1),
            ToTNode("node3", "thought3", "action3", "obs3", 0.7, 2)
        ]
        
        # Create test path
        path = ToTPath(
            path_id="test_path",
            nodes=nodes,
            total_confidence=0.8,
            completeness=0.9,
            efficiency=0.7,
            evaluation_score=0.0
        )
        
        # Evaluate path
        score = tot_strategy._evaluate_path(path)
        assert score > 0.0
        assert score <= 1.0

    @pytest.mark.asyncio
    async def test_tot_optimal_path_finding(self, tot_strategy):
        """Test ToT optimal path finding."""
        # Create test nodes and paths
        tot_strategy.nodes = {
            "root": ToTNode("root", "thought", "action", "obs", 0.8, 0),
            "child1": ToTNode("child1", "thought1", "action1", "obs1", 0.9, 1, "root"),
            "child2": ToTNode("child2", "thought2", "action2", "obs2", 0.7, 1, "root")
        }
        
        # Set up parent-child relationships
        tot_strategy.nodes["root"].children = ["child1", "child2"]
        
        # Find optimal path
        optimal_path = await tot_strategy._find_optimal_path()
        
        assert optimal_path is not None
        assert optimal_path.evaluation_score > 0.0

    def test_tot_can_handle(self, tot_strategy):
        """Test ToT can_handle method."""
        # ToT prefers complex problems
        assert tot_strategy.can_handle("This is a complex problem that requires multiple steps")
        assert not tot_strategy.can_handle("Simple")
        assert not tot_strategy.can_handle("")

    def test_tot_tree_stats(self, tot_strategy):
        """Test ToT tree statistics."""
        # Add some test nodes
        tot_strategy.nodes = {
            "root": ToTNode("root", "thought", "action", "obs", 0.8, 0),
            "child1": ToTNode("child1", "thought1", "action1", "obs1", 0.9, 1, "root"),
            "child2": ToTNode("child2", "thought2", "action2", "obs2", 0.7, 2, "child1")
        }
        
        stats = tot_strategy.get_tree_stats()
        
        assert stats["total_nodes"] == 3
        assert stats["max_depth"] == 2
        assert stats["iteration_count"] == 0

    def test_tot_reset(self, tot_strategy):
        """Test ToT reset functionality."""
        # Add some test data
        tot_strategy.nodes = {"test": ToTNode("test", "thought", "action", "obs", 0.8, 0)}
        tot_strategy.iteration_count = 5
        tot_strategy.explored_nodes = {"test"}
        
        tot_strategy.reset()
        
        assert len(tot_strategy.nodes) == 0
        assert tot_strategy.iteration_count == 0
        assert len(tot_strategy.explored_nodes) == 0


class TestPromptEngineeringFramework:
    """Test suite for Prompt Engineering Framework."""

    @pytest.fixture
    def prompt_framework(self):
        """Create a prompt engineering framework instance."""
        config = PromptEngineeringConfig(
            enable_optimization=True,
            enable_ab_testing=True,
            enable_context_injection=True
        )
        return PromptEngineeringFramework(config=config)

    def test_prompt_framework_initialization(self, prompt_framework):
        """Test prompt framework initialization."""
        assert prompt_framework.config.enable_optimization is True
        assert prompt_framework.config.enable_ab_testing is True
        assert len(prompt_framework.templates) > 0  # Should have default templates

    def test_template_management(self, prompt_framework):
        """Test template management functionality."""
        # Test adding template
        template = PromptTemplate(
            template_id="test_template",
            name="Test Template",
            description="A test template",
            template="Test template with {variable}",
            prompt_type=PromptType.REASONING,
            variables=["variable"]
        )
        
        success = prompt_framework.add_template(template)
        assert success is True
        
        # Test getting template
        retrieved_template = prompt_framework.get_template("test_template")
        assert retrieved_template is not None
        assert retrieved_template.name == "Test Template"
        
        # Test getting templates by type
        reasoning_templates = prompt_framework.get_templates_by_type(PromptType.REASONING)
        assert len(reasoning_templates) > 0
        
        # Test removing template
        success = prompt_framework.remove_template("test_template")
        assert success is True
        
        # Verify template was removed
        retrieved_template = prompt_framework.get_template("test_template")
        assert retrieved_template is None

    def test_prompt_generation(self, prompt_framework):
        """Test prompt generation functionality."""
        # Create context
        context = PromptContext(
            problem_statement="What is 2 + 2?",
            problem_type="mathematical",
            reasoning_type=ReasoningType.MATHEMATICAL,
            system_context={"domain": "mathematics"},
            user_preferences={"detail_level": "high"}
        )
        
        # Generate prompt
        result = prompt_framework.generate_prompt(context)
        
        assert result is not None
        assert result.generated_prompt is not None
        assert len(result.generated_prompt) > 0
        assert result.template_used is not None
        assert result.context == context

    def test_template_optimization(self, prompt_framework):
        """Test template optimization functionality."""
        # Create a test template
        template = PromptTemplate(
            template_id="test_optimize",
            name="Test Template",
            description="A test template",
            template="You are a helpful assistant. Please solve: {problem_statement}",
            prompt_type=PromptType.REASONING,
            variables=["problem_statement"]
        )
        
        prompt_framework.add_template(template)
        
        # Create performance data
        performance_data = [
            ("test1", 0.7),
            ("test2", 0.8),
            ("test3", 0.6)
        ]
        
        # Optimize template
        optimized_template = prompt_framework.optimize_template("test_optimize", performance_data)
        
        assert optimized_template is not None
        assert optimized_template.template_id != template.template_id
        assert "optimized" in optimized_template.template_id
        assert optimized_template.metadata.get("optimized") is True

    def test_ab_testing(self, prompt_framework):
        """Test A/B testing functionality."""
        # Create two test templates
        template_a = PromptTemplate(
            template_id="template_a",
            name="Template A",
            description="Template A",
            template="Template A: {problem_statement}",
            prompt_type=PromptType.REASONING,
            variables=["problem_statement"]
        )
        
        template_b = PromptTemplate(
            template_id="template_b",
            name="Template B",
            description="Template B",
            template="Template B: {problem_statement}",
            prompt_type=PromptType.REASONING,
            variables=["problem_statement"]
        )
        
        prompt_framework.add_template(template_a)
        prompt_framework.add_template(template_b)
        
        # Create A/B test
        test_id = prompt_framework.create_ab_test("template_a", "template_b")
        assert test_id is not None
        
        # Record some test results
        prompt_framework.record_ab_test_result(test_id, "template_a", 0.8)
        prompt_framework.record_ab_test_result(test_id, "template_b", 0.9)
        prompt_framework.record_ab_test_result(test_id, "template_a", 0.7)
        prompt_framework.record_ab_test_result(test_id, "template_b", 0.85)
        
        # Get test result
        result = prompt_framework.get_ab_test_result(test_id)
        assert result is not None
        assert result.winner is not None
        assert result.confidence_level > 0.0

    def test_performance_stats(self, prompt_framework):
        """Test performance statistics."""
        stats = prompt_framework.get_performance_stats()
        
        assert "total_templates" in stats
        assert "templates_by_type" in stats
        assert "average_performance" in stats
        assert "top_performers" in stats
        assert stats["total_templates"] > 0

    def test_export_import(self, prompt_framework):
        """Test template export and import functionality."""
        # Export templates
        export_data = prompt_framework.export_templates()
        
        assert "templates" in export_data
        assert "ab_tests" in export_data
        assert "ab_results" in export_data
        assert "exported_at" in export_data
        
        # Create new framework and import
        new_framework = PromptEngineeringFramework()
        success = new_framework.import_templates(export_data)
        
        assert success is True
        assert len(new_framework.templates) > 0


class TestPhase3Integration:
    """Test suite for Phase 3 integration features."""

    @pytest.fixture
    def integrated_system(self):
        """Create an integrated system with all Phase 3 components."""
        return {
            "cot": ChainOfThoughtStrategy(),
            "tot": TreeOfThoughtsStrategy(),
            "prompt_framework": PromptEngineeringFramework()
        }

    @pytest.mark.asyncio
    async def test_strategy_selection(self, integrated_system):
        """Test automatic strategy selection based on problem type."""
        cot = integrated_system["cot"]
        tot = integrated_system["tot"]
        
        # Simple problem - should prefer CoT
        simple_problem = "What is 5 + 3?"
        assert cot.can_handle(simple_problem)
        assert not tot.can_handle(simple_problem)
        
        # Complex problem - should prefer ToT
        complex_problem = "How can I design a scalable microservices architecture with proper authentication, authorization, and data consistency across multiple services?"
        assert tot.can_handle(complex_problem)
        assert cot.can_handle(complex_problem)  # CoT can handle most problems

    @pytest.mark.asyncio
    async def test_prompt_integration(self, integrated_system):
        """Test integration between prompt framework and reasoning strategies."""
        prompt_framework = integrated_system["prompt_framework"]
        
        # Create context for a mathematical problem
        context = PromptContext(
            problem_statement="What is 15 * 7?",
            problem_type="mathematical",
            reasoning_type=ReasoningType.MATHEMATICAL
        )
        
        # Generate prompt
        prompt_result = prompt_framework.generate_prompt(context)
        assert prompt_result is not None
        
        # The generated prompt could be used by reasoning strategies
        assert len(prompt_result.generated_prompt) > 0

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, integrated_system):
        """Test end-to-end workflow with all Phase 3 components."""
        cot = integrated_system["cot"]
        prompt_framework = integrated_system["prompt_framework"]
        
        # Test problem
        problem = "What is 12 * 8?"
        
        # Generate prompt using framework
        context = PromptContext(
            problem_statement=problem,
            problem_type="mathematical",
            reasoning_type=ReasoningType.MATHEMATICAL
        )
        
        prompt_result = prompt_framework.generate_prompt(context)
        assert prompt_result is not None
        
        # Use CoT strategy with the generated prompt
        result = await cot.reason(problem)
        assert result is not None
        assert result.problem_statement == problem
        assert len(result.steps) > 0
        assert result.confidence > 0.0

    def test_performance_comparison(self, integrated_system):
        """Test performance comparison between strategies."""
        cot = integrated_system["cot"]
        tot = integrated_system["tot"]
        
        # Test problems of different complexity
        simple_problem = "What is 10 + 5?"
        complex_problem = "How can I implement a distributed caching system with Redis?"
        
        # Simple problem should work well with CoT
        assert cot.can_handle(simple_problem)
        
        # Complex problem should work well with ToT
        assert tot.can_handle(complex_problem)


if __name__ == "__main__":
    pytest.main([__file__]) 