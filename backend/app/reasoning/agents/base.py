"""
Base classes for the simplified hybrid multi-agent system.

This module provides the foundational classes for both local agents and
Google A2A agents in our simplified hybrid approach.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import asyncio
import logging

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Status of an agent."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class TaskPriority(Enum):
    """Priority levels for agent tasks."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentTask:
    """Represents a task for an agent to process."""
    task_id: str
    problem: str
    task_type: str
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if isinstance(self.priority, str):
            self.priority = TaskPriority(self.priority)


@dataclass
class AgentResult:
    """Result from an agent's processing."""
    agent_id: str
    result: Any
    confidence: float
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass
class AgentMessage:
    """Message between agents."""
    sender_id: str
    receiver_id: str
    message_type: str
    content: Any
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Response from an agent to a message."""
    agent_id: str
    response_type: str
    content: Any
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base class for all reasoning agents in the simplified hybrid system.
    
    This class provides the common interface for both local agents and
    Google A2A agents.
    """
    
    def __init__(self, agent_id: str, capabilities: List[str], agent_type: str = "local"):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.agent_type = agent_type  # "local" or "a2a"
        self.status = AgentStatus.IDLE
        self.performance_metrics = {
            "tasks_processed": 0,
            "success_rate": 1.0,
            "average_processing_time": 0.0,
            "total_processing_time": 0.0
        }
        self.last_activity = datetime.now(timezone.utc)
        logger.info(f"Initialized agent {agent_id} with capabilities: {capabilities}")
    
    @abstractmethod
    async def process_task(self, task: AgentTask) -> AgentResult:
        """
        Process a task and return results.
        
        Args:
            task: The task to process
            
        Returns:
            AgentResult containing the processing results
        """
        pass
    
    async def communicate(self, message: AgentMessage) -> AgentResponse:
        """
        Communicate with other agents.
        
        Args:
            message: Message from another agent
            
        Returns:
            AgentResponse with the agent's response
        """
        self.last_activity = datetime.now(timezone.utc)
        logger.debug(f"Agent {self.agent_id} received message: {message.message_type}")
        
        # Default implementation - can be overridden by specific agents
        return AgentResponse(
            agent_id=self.agent_id,
            response_type="acknowledgment",
            content=f"Message received: {message.message_type}",
            metadata={"original_message": message}
        )
    
    def can_handle_task(self, task: AgentTask) -> bool:
        """
        Check if this agent can handle the given task.
        
        Args:
            task: The task to check
            
        Returns:
            True if the agent can handle the task, False otherwise
        """
        return task.task_type in self.capabilities
    
    def update_performance_metrics(self, processing_time: float, success: bool = True):
        """
        Update agent performance metrics.
        
        Args:
            processing_time: Time taken to process the task
            success: Whether the task was processed successfully
        """
        self.performance_metrics["tasks_processed"] += 1
        self.performance_metrics["total_processing_time"] += processing_time
        
        # Update success rate
        current_success_rate = self.performance_metrics["success_rate"]
        total_tasks = self.performance_metrics["tasks_processed"]
        if success:
            new_success_rate = ((current_success_rate * (total_tasks - 1)) + 1) / total_tasks
        else:
            new_success_rate = (current_success_rate * (total_tasks - 1)) / total_tasks
        
        self.performance_metrics["success_rate"] = new_success_rate
        self.performance_metrics["average_processing_time"] = (
            self.performance_metrics["total_processing_time"] / total_tasks
        )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status and metrics.
        
        Returns:
            Dictionary containing agent status and performance metrics
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "performance_metrics": self.performance_metrics.copy(),
            "last_activity": self.last_activity.isoformat()
        }
    
    async def health_check(self) -> bool:
        """
        Perform a health check on the agent.
        
        Returns:
            True if the agent is healthy, False otherwise
        """
        try:
            # Basic health check - can be overridden by specific agents
            return self.status != AgentStatus.ERROR
        except Exception as e:
            logger.error(f"Health check failed for agent {self.agent_id}: {e}")
            return False
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.agent_id}, type={self.agent_type})"
    
    def __repr__(self) -> str:
        return self.__str__()


class LocalAgent(BaseAgent):
    """
    Base class for local agents that run within our system.
    
    Local agents are our existing reasoning engines wrapped in the agent interface.
    """
    
    def __init__(self, agent_id: str, capabilities: List[str]):
        super().__init__(agent_id, capabilities, agent_type="local")
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """
        Process a task using local reasoning capabilities.
        
        Args:
            task: The task to process
            
        Returns:
            AgentResult containing the processing results
        """
        start_time = datetime.now(timezone.utc)
        self.status = AgentStatus.BUSY
        
        try:
            result = await self._process_local_task(task)
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            self.update_performance_metrics(processing_time, success=True)
            self.status = AgentStatus.IDLE
            
            return AgentResult(
                agent_id=self.agent_id,
                result=result,
                confidence=self._calculate_confidence(result),
                processing_time=processing_time,
                metadata={"agent_type": "local", "task_type": task.task_type}
            )
            
        except Exception as e:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.update_performance_metrics(processing_time, success=False)
            self.status = AgentStatus.ERROR
            logger.error(f"Error processing task in agent {self.agent_id}: {e}")
            raise
    
    @abstractmethod
    async def _process_local_task(self, task: AgentTask) -> Any:
        """
        Process a task using local reasoning capabilities.
        
        Args:
            task: The task to process
            
        Returns:
            The processing result
        """
        pass
    
    def _calculate_confidence(self, result: Any) -> float:
        """
        Calculate confidence score for the result.
        
        Args:
            result: The processing result
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Default confidence calculation - can be overridden by specific agents
        return 0.8  # Default confidence for local agents


class A2AAgent(BaseAgent):
    """
    Base class for Google A2A agents.
    
    A2A agents communicate with Google's Agent2Agent protocol for enhanced capabilities.
    """
    
    def __init__(self, agent_id: str, capabilities: List[str], a2a_config: Dict[str, Any]):
        super().__init__(agent_id, capabilities, agent_type="a2a")
        self.a2a_config = a2a_config
        self.is_available = True  # Will be updated based on A2A availability
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """
        Process a task using Google A2A capabilities.
        
        Args:
            task: The task to process
            
        Returns:
            AgentResult containing the processing results
        """
        if not self.is_available:
            raise Exception(f"A2A agent {self.agent_id} is not available")
        
        start_time = datetime.now(timezone.utc)
        self.status = AgentStatus.BUSY
        
        try:
            result = await self._process_a2a_task(task)
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            self.update_performance_metrics(processing_time, success=True)
            self.status = AgentStatus.IDLE
            
            return AgentResult(
                agent_id=self.agent_id,
                result=result,
                confidence=self._calculate_a2a_confidence(result),
                processing_time=processing_time,
                metadata={"agent_type": "a2a", "task_type": task.task_type}
            )
            
        except Exception as e:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.update_performance_metrics(processing_time, success=False)
            self.status = AgentStatus.ERROR
            logger.error(f"Error processing task in A2A agent {self.agent_id}: {e}")
            raise
    
    @abstractmethod
    async def _process_a2a_task(self, task: AgentTask) -> Any:
        """
        Process a task using Google A2A capabilities.
        
        Args:
            task: The task to process
            
        Returns:
            The processing result
        """
        pass
    
    def _calculate_a2a_confidence(self, result: Any) -> float:
        """
        Calculate confidence score for A2A result.
        
        Args:
            result: The processing result
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Default confidence calculation for A2A agents
        return 0.9  # Higher default confidence for A2A agents
    
    async def check_a2a_availability(self) -> bool:
        """
        Check if the A2A agent is available.
        
        Returns:
            True if the A2A agent is available, False otherwise
        """
        # This will be implemented with actual A2A availability checking
        return self.is_available 