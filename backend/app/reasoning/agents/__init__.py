"""
Multi-Agent Reasoning System - Simplified Hybrid Approach

This module implements a simplified hybrid multi-agent system that combines
local reasoning agents with Google A2A agents for enhanced problem solving.

Architecture:
- Local Agents: Our existing reasoning engines (Mathematical, Logical, Causal, CoT, ToT)
- Google A2A Agents: External agents via Google's A2A protocol (fallback)
- Simplified Coordinator: Local-first with A2A fallback when needed
"""

from .base import (
    BaseAgent,
    AgentStatus,
    AgentTask,
    AgentResult,
    AgentMessage,
    AgentResponse,
    TaskPriority
)

from .manager import (
    SimplifiedHybridManager,
    LocalAgentManager,
    A2AAgentManager,
    AgentRegistry
)

from .synthesis import (
    ResultSynthesizer,
    LocalResultProcessor,
    A2AResultProcessor,
    HybridResultProcessor
)

from .local_agents import (
    MathematicalAgent,
    LogicalAgent,
    CausalAgent,
    CoTAgent,
    ToTAgent,
    PromptEngineeringAgent,
    GeneralReasoningAgent,
    create_local_agent,
    create_all_local_agents
)

from .a2a_integration import (
    A2AProtocolHandler,
    A2AAgentAdapter,
    A2AResultTranslator
)

__version__ = "1.0.0"

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentStatus", 
    "AgentTask",
    "AgentResult",
    "AgentMessage",
    "AgentResponse",
    "TaskPriority",
    
    # Managers
    "SimplifiedHybridManager",
    "LocalAgentManager", 
    "A2AAgentManager",
    "AgentRegistry",
    
    # Synthesis
    "ResultSynthesizer",
    "LocalResultProcessor",
    "A2AResultProcessor", 
    "HybridResultProcessor",
    
    # Local Agents
    "MathematicalAgent",
    "LogicalAgent",
    "CausalAgent", 
    "CoTAgent",
    "ToTAgent",
    "PromptEngineeringAgent",
    "GeneralReasoningAgent",
    "create_local_agent",
    "create_all_local_agents",
    
    # A2A Integration
    "A2AProtocolHandler",
    "A2AAgentAdapter",
    "A2AResultTranslator"
] 