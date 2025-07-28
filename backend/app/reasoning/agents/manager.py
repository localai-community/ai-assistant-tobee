"""
Simplified Hybrid Manager for Multi-Agent System.

This module implements the core manager that coordinates local agents
with Google A2A agents using a local-first with A2A fallback approach.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from .base import (
    BaseAgent, LocalAgent, A2AAgent, AgentTask, AgentResult, 
    AgentStatus, TaskPriority
)

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for managing all agents in the system."""
    
    def __init__(self):
        self.local_agents: Dict[str, LocalAgent] = {}
        self.a2a_agents: Dict[str, A2AAgent] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
    
    def register_local_agent(self, agent: LocalAgent):
        """Register a local agent."""
        self.local_agents[agent.agent_id] = agent
        self.agent_capabilities[agent.agent_id] = agent.capabilities
        logger.info(f"Registered local agent: {agent.agent_id}")
    
    def register_a2a_agent(self, agent: A2AAgent):
        """Register an A2A agent."""
        self.a2a_agents[agent.agent_id] = agent
        self.agent_capabilities[agent.agent_id] = agent.capabilities
        logger.info(f"Registered A2A agent: {agent.agent_id}")
    
    def get_agents_for_task(self, task_type: str) -> List[BaseAgent]:
        """Get all agents that can handle a specific task type."""
        available_agents = []
        
        # Add local agents
        for agent in self.local_agents.values():
            if agent.can_handle_task(AgentTask(task_id="", problem="", task_type=task_type)):
                available_agents.append(agent)
        
        # Add A2A agents (only if available)
        for agent in self.a2a_agents.values():
            if agent.can_handle_task(AgentTask(task_id="", problem="", task_type=task_type)) and agent.is_available:
                available_agents.append(agent)
        
        return available_agents
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        status = {
            "local_agents": {},
            "a2a_agents": {},
            "total_agents": len(self.local_agents) + len(self.a2a_agents)
        }
        
        for agent_id, agent in self.local_agents.items():
            status["local_agents"][agent_id] = agent.get_status()
        
        for agent_id, agent in self.a2a_agents.items():
            status["a2a_agents"][agent_id] = agent.get_status()
        
        return status


class LocalAgentManager:
    """Manages local agents and their coordination."""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.task_queue: List[AgentTask] = []
    
    async def process_with_local_agents(self, problem: str, task_type: str) -> List[AgentResult]:
        """
        Process a problem using local agents only.
        
        Args:
            problem: The problem to solve
            task_type: Type of task to perform
            
        Returns:
            List of results from local agents
        """
        available_agents = self.registry.get_agents_for_task(task_type)
        local_agents = [agent for agent in available_agents if agent.agent_type == "local"]
        
        if not local_agents:
            logger.warning(f"No local agents available for task type: {task_type}")
            return []
        
        # Create tasks for each local agent
        tasks = []
        for agent in local_agents:
            task = AgentTask(
                task_id=str(uuid4()),
                problem=problem,
                task_type=task_type,
                priority=TaskPriority.NORMAL
            )
            tasks.append((agent, task))
        
        # Process tasks in parallel
        results = []
        tasks_to_execute = [(agent.process_task(task), agent.agent_id) for agent, task in tasks]
        
        for coro, agent_id in tasks_to_execute:
            try:
                result = await coro
                logger.info(f"Local agent {agent_id} completed task successfully: confidence={result.confidence}, result_type={type(result.result)}")
                results.append(result)
            except Exception as e:
                logger.error(f"Local agent {agent_id} failed to process task: {e}")
                # Create a failed result for tracking
                failed_result = AgentResult(
                    agent_id=agent_id,
                    result=None,
                    confidence=0.0,
                    processing_time=0.0,
                    metadata={"error": str(e), "agent_type": "local"}
                )
                results.append(failed_result)
        
        return results


class A2AAgentManager:
    """Manages Google A2A agents and their integration."""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.a2a_available = True  # Will be updated based on actual A2A availability
    
    async def check_a2a_availability(self) -> bool:
        """Check if A2A agents are available."""
        # This would integrate with actual Google A2A availability checking
        # For now, we'll use a simple flag
        return self.a2a_available
    
    async def process_with_a2a_agents(self, problem: str, task_type: str) -> List[AgentResult]:
        """
        Process a problem using A2A agents only.
        
        Args:
            problem: The problem to solve
            task_type: Type of task to perform
            
        Returns:
            List of results from A2A agents
        """
        if not await self.check_a2a_availability():
            logger.warning("A2A agents are not available")
            return []
        
        available_agents = self.registry.get_agents_for_task(task_type)
        a2a_agents = [agent for agent in available_agents if agent.agent_type == "a2a"]
        
        if not a2a_agents:
            logger.warning(f"No A2A agents available for task type: {task_type}")
            return []
        
        # Create tasks for each A2A agent
        tasks = []
        for agent in a2a_agents:
            task = AgentTask(
                task_id=str(uuid4()),
                problem=problem,
                task_type=task_type,
                priority=TaskPriority.HIGH  # A2A tasks get higher priority
            )
            tasks.append((agent, task))
        
        # Process tasks in parallel
        results = []
        tasks_to_execute = [(agent.process_task(task), agent.agent_id) for agent, task in tasks]
        
        for coro, agent_id in tasks_to_execute:
            try:
                result = await coro
                results.append(result)
                logger.info(f"A2A agent {agent_id} completed task successfully")
            except Exception as e:
                logger.error(f"A2A agent {agent_id} failed to process task: {e}")
                # Create a failed result for tracking
                failed_result = AgentResult(
                    agent_id=agent_id,
                    result=None,
                    confidence=0.0,
                    processing_time=0.0,
                    metadata={"error": str(e), "agent_type": "a2a"}
                )
                results.append(failed_result)
        
        return results


class SimplifiedHybridManager:
    """
    Simplified Hybrid Manager implementing local-first with A2A fallback.
    
    This manager follows the principle of trying local agents first,
    and only using A2A agents when local results need enhancement.
    """
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.local_manager = LocalAgentManager(self.registry)
        self.a2a_manager = A2AAgentManager(self.registry)
        self.enhancement_threshold = 0.7  # Confidence threshold for A2A enhancement
    
    async def solve_problem(self, problem: str, task_type: str = "general") -> Dict[str, Any]:
        """
        Solve a problem using the simplified hybrid approach.
        
        Args:
            problem: The problem to solve
            task_type: Type of task to perform
            
        Returns:
            Dictionary containing the final result and metadata
        """
        logger.info(f"Starting hybrid problem solving for task type: {task_type}")
        
        # Step 1: Try local agents first
        local_results = await self.local_manager.process_with_local_agents(problem, task_type)
        
        if not local_results:
            logger.warning("No local agents available, trying A2A agents")
            a2a_results = await self.a2a_manager.process_with_a2a_agents(problem, task_type)
            return self._create_final_result(a2a_results, "a2a_only")
        
        # Step 2: Assess if local results need enhancement
        best_local_result = self._get_best_result(local_results)
        
        if self._needs_enhancement(best_local_result):
            logger.info("Local results need enhancement, trying A2A agents")
            a2a_results = await self.a2a_manager.process_with_a2a_agents(problem, task_type)
            
            if a2a_results:
                # Combine local and A2A results
                combined_results = local_results + a2a_results
                return self._create_final_result(combined_results, "hybrid")
            else:
                # A2A failed, return local results
                return self._create_final_result(local_results, "local_only")
        else:
            # Local results are sufficient
            return self._create_final_result(local_results, "local_only")
    
    def _needs_enhancement(self, result: AgentResult) -> bool:
        """
        Determine if a result needs enhancement from A2A agents.
        
        Args:
            result: The result to evaluate
            
        Returns:
            True if enhancement is needed, False otherwise
        """
        if result is None or result.confidence is None:
            return True
        
        # Check confidence threshold
        if result.confidence < self.enhancement_threshold:
            return True
        
        # Check if result is empty or incomplete
        if not result.result or (isinstance(result.result, str) and len(result.result.strip()) < 50):
            return True
        
        return False
    
    def _get_best_result(self, results: List[AgentResult]) -> Optional[AgentResult]:
        """
        Get the best result from a list of results.
        
        Args:
            results: List of agent results
            
        Returns:
            The best result based on confidence and quality
        """
        if not results:
            logger.warning("No results provided to _get_best_result")
            return None
        
        # Debug: Log all results
        logger.info(f"_get_best_result: Processing {len(results)} results")
        for i, result in enumerate(results):
            logger.info(f"  Result {i}: agent={result.agent_id}, confidence={result.confidence}, result_type={type(result.result)}")
        
        # Filter out failed results
        valid_results = [r for r in results if r.confidence > 0.0 and r.result is not None]
        
        logger.info(f"_get_best_result: Found {len(valid_results)} valid results")
        for i, result in enumerate(valid_results):
            logger.info(f"  Valid Result {i}: agent={result.agent_id}, confidence={result.confidence}")
        
        if not valid_results:
            logger.warning("No valid results found in _get_best_result")
            return None
        
        # Return the result with highest confidence
        best_result = max(valid_results, key=lambda r: r.confidence)
        logger.info(f"_get_best_result: Selected best result: {best_result.agent_id} with confidence {best_result.confidence}")
        return best_result
    
    def _create_final_result(self, results: List[AgentResult], approach: str) -> Dict[str, Any]:
        """
        Create the final result from agent results.
        
        Args:
            results: List of agent results
            approach: The approach used ("local_only", "a2a_only", "hybrid")
            
        Returns:
            Dictionary containing the final result and metadata
        """
        if not results:
            return {
                "result": "No agents were able to process this problem.",
                "confidence": 0.0,
                "approach": approach,
                "agents_used": [],
                "processing_time": 0.0,
                "metadata": {"error": "No agents available"}
            }
        
        # Get the best result
        best_result = self._get_best_result(results)
        
        # Format the result for output
        formatted_result = "No valid result obtained"
        if best_result and best_result.result:
            result_obj = best_result.result
            
            # Check for LLM response first (most preferred)
            if hasattr(result_obj, 'llm_response') and result_obj.llm_response:
                formatted_result = result_obj.llm_response
            # Check for final answer
            elif hasattr(result_obj, 'final_answer') and result_obj.final_answer:
                formatted_result = str(result_obj.final_answer)
            # Check for steps
            elif hasattr(result_obj, 'steps') and result_obj.steps:
                steps_text = "\n".join([f"Step {i+1}: {step}" for i, step in enumerate(result_obj.steps)])
                formatted_result = f"Solution:\n{steps_text}"
            # Check for optimized prompt (for prompt engineering agent)
            elif hasattr(result_obj, 'optimized_prompt') and result_obj.optimized_prompt:
                formatted_result = f"Optimized Prompt:\n{result_obj.optimized_prompt}"
            # Check for enhanced prompt
            elif hasattr(result_obj, 'enhanced_prompt') and result_obj.enhanced_prompt:
                formatted_result = f"Enhanced Prompt:\n{result_obj.enhanced_prompt}"
            # Fallback to string representation
            else:
                formatted_result = str(result_obj)
        
        # Calculate aggregate metrics
        total_processing_time = sum(r.processing_time for r in results if r.processing_time)
        avg_confidence = sum(r.confidence for r in results if r.confidence) / len(results)
        
        # Create final result
        final_result = {
            "result": formatted_result,
            "answer": formatted_result,  # Alias for compatibility
            "confidence": best_result.confidence if best_result else 0.0,
            "approach": approach,
            "agent_used": best_result.agent_id if best_result else "unknown",  # Primary agent used
            "agents_used": [r.agent_id for r in results],  # All agents that participated
            "processing_time": total_processing_time,
            "total_agents": len(results),
            "average_confidence": avg_confidence,
            "reasoning_steps": [],  # Placeholder for reasoning steps
            "metadata": {
                "local_agents": len([r for r in results if r.metadata.get("agent_type") == "local"]),
                "a2a_agents": len([r for r in results if r.metadata.get("agent_type") == "a2a"]),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        logger.info(f"Final result created using approach: {approach}")
        return final_result
    
    def register_local_agent(self, agent: LocalAgent):
        """Register a local agent."""
        self.registry.register_local_agent(agent)
    
    def register_a2a_agent(self, agent: A2AAgent):
        """Register an A2A agent."""
        self.registry.register_a2a_agent(agent)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the status of the entire hybrid system."""
        return {
            "registry": self.registry.get_agent_status(),
            "a2a_available": self.a2a_manager.a2a_available,
            "enhancement_threshold": self.enhancement_threshold,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def set_enhancement_threshold(self, threshold: float):
        """
        Set the confidence threshold for A2A enhancement.
        
        Args:
            threshold: Confidence threshold between 0.0 and 1.0
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        
        self.enhancement_threshold = threshold
        logger.info(f"Enhancement threshold set to: {threshold}") 