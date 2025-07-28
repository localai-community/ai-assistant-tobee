"""
Local Agents for the Simplified Hybrid Multi-Agent System.

This module provides local agents that wrap our existing reasoning engines
(Mathematical, Logical, Causal, CoT, ToT, Prompt Engineering) to work
within the multi-agent framework.
"""

import asyncio
import logging
from typing import Any, Dict, List

from .base import LocalAgent, AgentTask, AgentResult
from ..engines import (
    MathematicalReasoningEngine,
    LogicalReasoningEngine,
    CausalReasoningEngine
)
from ..strategies import (
    ChainOfThoughtStrategy,
    TreeOfThoughtsStrategy,
    PromptEngineeringFramework
)

logger = logging.getLogger(__name__)


class MathematicalAgent(LocalAgent):
    """Local agent for mathematical reasoning."""
    
    def __init__(self, agent_id: str = "mathematical_agent"):
        super().__init__(agent_id, capabilities=["mathematical", "numerical", "algebraic", "calculus"])
        self.engine = MathematicalReasoningEngine()
        logger.info(f"Initialized Mathematical Agent: {agent_id}")
    
    async def _process_local_task(self, task: AgentTask) -> Any:
        """Process mathematical tasks using the mathematical reasoning engine."""
        try:
            # Use the mathematical reasoning engine
            result = await self.engine.reason(task.problem)
            return result
        except Exception as e:
            logger.error(f"Mathematical agent error: {e}")
            raise
    
    def _calculate_confidence(self, result: Any) -> float:
        """Calculate confidence for mathematical results."""
        if not result:
            return 0.0
        
        # Higher confidence for mathematical results with clear steps
        if hasattr(result, 'steps') and result.steps:
            return 0.9
        elif hasattr(result, 'final_answer') and result.final_answer:
            return 0.8
        else:
            return 0.6


class LogicalAgent(LocalAgent):
    """Local agent for logical reasoning."""
    
    def __init__(self, agent_id: str = "logical_agent"):
        super().__init__(agent_id, capabilities=["logical", "deductive", "syllogistic", "inference"])
        self.engine = LogicalReasoningEngine()
        logger.info(f"Initialized Logical Agent: {agent_id}")
    
    async def _process_local_task(self, task: AgentTask) -> Any:
        """Process logical tasks using the logical reasoning engine."""
        try:
            # Use the logical reasoning engine
            result = await self.engine.reason(task.problem)
            return result
        except Exception as e:
            logger.error(f"Logical agent error: {e}")
            raise
    
    def _calculate_confidence(self, result: Any) -> float:
        """Calculate confidence for logical results."""
        if not result:
            return 0.0
        
        # Higher confidence for logical results with clear inference steps
        if hasattr(result, 'steps') and result.steps:
            return 0.85
        elif hasattr(result, 'final_answer') and result.final_answer:
            return 0.75
        else:
            return 0.6


class CausalAgent(LocalAgent):
    """Local agent for causal reasoning."""
    
    def __init__(self, agent_id: str = "causal_agent"):
        super().__init__(agent_id, capabilities=["causal", "cause_effect", "intervention", "counterfactual"])
        self.engine = CausalReasoningEngine()
        logger.info(f"Initialized Causal Agent: {agent_id}")
    
    async def _process_local_task(self, task: AgentTask) -> Any:
        """Process causal tasks using the causal reasoning engine."""
        try:
            # Use the causal reasoning engine
            result = await self.engine.reason(task.problem)
            return result
        except Exception as e:
            logger.error(f"Causal agent error: {e}")
            raise
    
    def _calculate_confidence(self, result: Any) -> float:
        """Calculate confidence for causal results."""
        if not result:
            return 0.0
        
        # Higher confidence for causal results with clear causal relationships
        if hasattr(result, 'steps') and result.steps:
            return 0.85
        elif hasattr(result, 'final_answer') and result.final_answer:
            return 0.75
        else:
            return 0.6


class CoTAgent(LocalAgent):
    """Local agent for Chain-of-Thought reasoning."""
    
    def __init__(self, agent_id: str = "cot_agent"):
        super().__init__(agent_id, capabilities=["cot", "step_by_step", "reasoning", "complex"])
        self.strategy = ChainOfThoughtStrategy()
        logger.info(f"Initialized CoT Agent: {agent_id}")
    
    async def _process_local_task(self, task: AgentTask) -> Any:
        """Process tasks using Chain-of-Thought reasoning."""
        try:
            # Use the Chain-of-Thought strategy
            result = await self.strategy.reason(task.problem)
            return result
        except Exception as e:
            logger.error(f"CoT agent error: {e}")
            raise
    
    def _calculate_confidence(self, result: Any) -> float:
        """Calculate confidence for CoT results."""
        if not result:
            return 0.0
        
        # Higher confidence for CoT results with detailed steps
        if hasattr(result, 'steps') and result.steps and len(result.steps) > 2:
            return 0.9
        elif hasattr(result, 'final_answer') and result.final_answer:
            return 0.8
        else:
            return 0.7


class ToTAgent(LocalAgent):
    """Local agent for Tree-of-Thoughts reasoning."""
    
    def __init__(self, agent_id: str = "tot_agent"):
        super().__init__(agent_id, capabilities=["tot", "multi_path", "exploration", "complex"])
        self.strategy = TreeOfThoughtsStrategy()
        logger.info(f"Initialized ToT Agent: {agent_id}")
    
    async def _process_local_task(self, task: AgentTask) -> Any:
        """Process tasks using Tree-of-Thoughts reasoning."""
        try:
            # Use the Tree-of-Thoughts strategy
            result = await self.strategy.reason(task.problem)
            return result
        except Exception as e:
            logger.error(f"ToT agent error: {e}")
            raise
    
    def _calculate_confidence(self, result: Any) -> float:
        """Calculate confidence for ToT results."""
        if not result:
            return 0.0
        
        # Higher confidence for ToT results with multiple paths explored
        if hasattr(result, 'steps') and result.steps and len(result.steps) > 3:
            return 0.95
        elif hasattr(result, 'final_answer') and result.final_answer:
            return 0.85
        else:
            return 0.7


class PromptEngineeringAgent(LocalAgent):
    """Local agent for prompt engineering and optimization."""
    
    def __init__(self, agent_id: str = "prompt_engineering_agent"):
        super().__init__(agent_id, capabilities=["prompt_engineering", "optimization", "template", "enhancement"])
        self.framework = PromptEngineeringFramework()
        logger.info(f"Initialized Prompt Engineering Agent: {agent_id}")
    
    async def _process_local_task(self, task: AgentTask) -> Any:
        """Process tasks using prompt engineering framework."""
        try:
            # Use the prompt engineering framework
            result = await self.framework.optimize_prompt(task.problem)
            return result
        except Exception as e:
            logger.error(f"Prompt Engineering agent error: {e}")
            raise
    
    def _calculate_confidence(self, result: Any) -> float:
        """Calculate confidence for prompt engineering results."""
        if not result:
            return 0.0
        
        # Higher confidence for optimized prompts
        if hasattr(result, 'optimized_prompt') and result.optimized_prompt:
            return 0.85
        elif hasattr(result, 'enhanced_prompt') and result.enhanced_prompt:
            return 0.8
        else:
            return 0.7


class GeneralReasoningAgent(LocalAgent):
    """General-purpose reasoning agent that can handle multiple task types."""
    
    def __init__(self, agent_id: str = "general_reasoning_agent"):
        super().__init__(agent_id, capabilities=[
            "general", "reasoning", "analysis", "problem_solving",
            "mathematical", "logical", "causal", "cot", "tot"
        ])
        # Initialize all engines and strategies
        self.mathematical_engine = MathematicalReasoningEngine()
        self.logical_engine = LogicalReasoningEngine()
        self.causal_engine = CausalReasoningEngine()
        self.cot_strategy = ChainOfThoughtStrategy()
        self.tot_strategy = TreeOfThoughtsStrategy()
        self.prompt_framework = PromptEngineeringFramework()
        
        logger.info(f"Initialized General Reasoning Agent: {agent_id}")
    
    async def _process_local_task(self, task: AgentTask) -> Any:
        """Process tasks using the most appropriate reasoning approach."""
        try:
            # Determine the best approach based on task type and problem content
            approach = self._select_best_approach(task)
            
            if approach == "mathematical":
                result = await self.mathematical_engine.reason(task.problem)
            elif approach == "logical":
                result = await self.logical_engine.reason(task.problem)
            elif approach == "causal":
                result = await self.causal_engine.reason(task.problem)
            elif approach == "cot":
                result = await self.cot_strategy.reason(task.problem)
            elif approach == "tot":
                result = await self.tot_strategy.reason(task.problem)
            else:
                # Default to CoT for general problems
                result = await self.cot_strategy.reason(task.problem)
            
            return result
            
        except Exception as e:
            logger.error(f"General reasoning agent error: {e}")
            raise
    
    def _select_best_approach(self, task: AgentTask) -> str:
        """Select the best reasoning approach for the task."""
        problem = task.problem.lower()
        
        # Check for mathematical content
        math_keywords = ["calculate", "solve", "equation", "formula", "number", "sum", "multiply", "divide"]
        if any(keyword in problem for keyword in math_keywords):
            return "mathematical"
        
        # Check for logical content
        logic_keywords = ["if", "then", "therefore", "because", "implies", "conclusion", "premise"]
        if any(keyword in problem for keyword in logic_keywords):
            return "logical"
        
        # Check for causal content
        causal_keywords = ["cause", "effect", "because", "result", "consequence", "impact", "influence"]
        if any(keyword in problem for keyword in causal_keywords):
            return "causal"
        
        # Check for complex reasoning
        complex_keywords = ["explain", "analyze", "compare", "evaluate", "complex", "difficult"]
        if any(keyword in problem for keyword in complex_keywords):
            return "tot"  # Use Tree-of-Thoughts for complex problems
        
        # Default to Chain-of-Thought for general problems
        return "cot"
    
    def _calculate_confidence(self, result: Any) -> float:
        """Calculate confidence for general reasoning results."""
        if not result:
            return 0.0
        
        # Base confidence on result quality
        if hasattr(result, 'steps') and result.steps and len(result.steps) > 2:
            return 0.85
        elif hasattr(result, 'final_answer') and result.final_answer:
            return 0.8
        else:
            return 0.7


# Factory function to create local agents
def create_local_agent(agent_type: str, agent_id: str = None) -> LocalAgent:
    """
    Factory function to create local agents.
    
    Args:
        agent_type: Type of agent to create
        agent_id: Optional custom agent ID
        
    Returns:
        LocalAgent instance
    """
    if agent_id is None:
        agent_id = f"{agent_type}_agent"
    
    agent_map = {
        "mathematical": MathematicalAgent,
        "logical": LogicalAgent,
        "causal": CausalAgent,
        "cot": CoTAgent,
        "tot": ToTAgent,
        "prompt_engineering": PromptEngineeringAgent,
        "general": GeneralReasoningAgent
    }
    
    if agent_type not in agent_map:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return agent_map[agent_type](agent_id)


def create_all_local_agents() -> List[LocalAgent]:
    """
    Create all available local agents.
    
    Returns:
        List of all local agents
    """
    return [
        MathematicalAgent(),
        LogicalAgent(),
        CausalAgent(),
        CoTAgent(),
        ToTAgent(),
        PromptEngineeringAgent(),
        GeneralReasoningAgent()
    ] 