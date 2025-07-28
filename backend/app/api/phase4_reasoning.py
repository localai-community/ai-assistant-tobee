"""
Phase 4 Multi-Agent Reasoning System API Endpoints
API routes for Phase 4 simplified hybrid multi-agent system with local-first + A2A fallback.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import json
import logging
import os
import asyncio

from ..services.chat import ChatService, ChatRequest, ChatResponse
from ..core.database import get_db
from ..core.models import ErrorResponse
from ..reasoning.agents import (
    SimplifiedHybridManager,
    create_all_local_agents,
    AgentTask,
    AgentResult
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/phase4-reasoning", tags=["phase4-reasoning"])

class Phase4ReasoningRequest(ChatRequest):
    """Phase 4 multi-agent reasoning request."""
    use_phase4_reasoning: bool = True
    task_type: str = "general"  # "general", "mathematical", "logical", "causal"
    enhancement_threshold: Optional[float] = None
    use_streaming: bool = False
    include_agent_details: bool = True

class Phase4ReasoningResponse(ChatResponse):
    """Phase 4 multi-agent reasoning response."""
    approach: str  # "local_only", "a2a_enhanced", "hybrid", "a2a_only"
    agents_used: List[str]
    total_agents: int
    confidence: float
    processing_time: float
    enhancement_threshold: float
    a2a_available: bool
    synthesis_method: str

# Initialize the multi-agent manager
manager = SimplifiedHybridManager()

# Register all local agents immediately
try:
    agents = create_all_local_agents()
    for agent in agents:
        manager.register_local_agent(agent)
    logger.info(f"✅ Registered {len(agents)} local agents for Phase 4")
except Exception as e:
    logger.error(f"❌ Failed to initialize Phase 4 agents: {e}")

# Register all local agents on startup (backup)
@router.on_event("startup")
async def initialize_agents():
    """Initialize and register all local agents."""
    try:
        agents = create_all_local_agents()
        for agent in agents:
            manager.register_local_agent(agent)
        logger.info(f"✅ Registered {len(agents)} local agents for Phase 4 (startup)")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Phase 4 agents: {e}")

@router.post("/", response_model=Phase4ReasoningResponse)
async def phase4_reasoning_chat(request: Phase4ReasoningRequest, db: Session = Depends(get_db)):
    """
    Send a message and get a response using Phase 4 multi-agent reasoning system.
    
    Args:
        request: Phase 4 reasoning request containing message and task type
        db: Database session
        
    Returns:
        Phase4ReasoningResponse: AI response with multi-agent coordination details
    """
    try:
        # Set enhancement threshold if provided
        if request.enhancement_threshold is not None:
            manager.set_enhancement_threshold(request.enhancement_threshold)
        
        # Create task
        task = AgentTask(
            task_id=f"task_{asyncio.get_event_loop().time()}",
            problem=request.message,
            task_type=request.task_type,
            priority="normal"
        )
        
        # Solve problem using multi-agent system
        start_time = asyncio.get_event_loop().time()
        
        # Debug: Log the manager state before solving
        logger.info(f"Manager state before solving: {len(manager.registry.local_agents)} local agents")
        logger.info(f"Task: {request.message}, Type: {request.task_type}")
        
        result = await manager.solve_problem(request.message, request.task_type)
        processing_time = asyncio.get_event_loop().time() - start_time
        
        # Debug: Log the result
        logger.info(f"Manager result: confidence={result.get('confidence', 0)}, approach={result.get('approach', 'unknown')}")
        
        # Get system status
        status = manager.get_system_status()
        
        # Create response
        response = Phase4ReasoningResponse(
            response=result['result'],
            model=request.model,
            conversation_id=result.get('conversation_id', 'phase4-reasoning'),
            approach=result['approach'],
            agents_used=result['agents_used'],
            total_agents=result['total_agents'],
            confidence=result['confidence'],
            processing_time=processing_time,
            enhancement_threshold=status['enhancement_threshold'],
            a2a_available=status['a2a_available'],
            synthesis_method=result.get('synthesis_method', 'unknown')
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in Phase 4 reasoning: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in multi-agent reasoning: {str(e)}"
        )

@router.post("/stream")
async def phase4_reasoning_stream(request: Phase4ReasoningRequest, db: Session = Depends(get_db)):
    """
    Stream a response using Phase 4 multi-agent reasoning system.
    
    Args:
        request: Phase 4 reasoning request
        db: Database session
        
    Returns:
        StreamingResponse: Streamed AI response
    """
    try:
        # Set enhancement threshold if provided
        if request.enhancement_threshold is not None:
            manager.set_enhancement_threshold(request.enhancement_threshold)
        
        async def generate_stream():
            """Generate streaming response."""
            try:
                # Create task
                task = AgentTask(
                    task_id=f"stream_task_{asyncio.get_event_loop().time()}",
                    problem=request.message,
                    task_type=request.task_type,
                    priority="normal"
                )
                
                # Start solving
                start_time = asyncio.get_event_loop().time()
                
                # Send initial status
                yield f"data: {json.dumps({'type': 'status', 'message': 'Starting multi-agent reasoning...'})}\n\n"
                
                # Solve problem
                result = await manager.solve_problem(request.message, request.task_type)
                processing_time = asyncio.get_event_loop().time() - start_time
                
                # Get system status
                status = manager.get_system_status()
                
                # Send result
                response_data = {
                    'type': 'result',
                    'response': result['result'],
                    'approach': result['approach'],
                    'agents_used': result['agents_used'],
                    'total_agents': result['total_agents'],
                    'confidence': result['confidence'],
                    'processing_time': processing_time,
                    'enhancement_threshold': status['enhancement_threshold'],
                    'a2a_available': status['a2a_available'],
                    'synthesis_method': result.get('synthesis_method', 'unknown')
                }
                
                yield f"data: {json.dumps(response_data)}\n\n"
                
            except Exception as e:
                error_data = {'type': 'error', 'message': str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except Exception as e:
        logger.error(f"Error in Phase 4 streaming: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in multi-agent streaming: {str(e)}"
        )

@router.get("/health")
async def phase4_health():
    """
    Get health status of Phase 4 multi-agent system.
    
    Returns:
        Dict: Health status information
    """
    try:
        status = manager.get_system_status()
        
        return {
            "status": "healthy",
            "service": "phase4-multi-agent-reasoning",
            "registry": {
                "total_agents": status['registry']['total_agents'],
                "local_agents": len(status['registry']['local_agents']),
                "a2a_agents": len(status['registry'].get('a2a_agents', []))
            },
            "configuration": {
                "enhancement_threshold": status['enhancement_threshold'],
                "a2a_available": status['a2a_available']
            },
            "capabilities": {
                "task_types": ["general", "mathematical", "logical", "causal"],
                "approaches": ["local_only", "a2a_enhanced", "hybrid", "a2a_only"],
                "synthesis_methods": ["weighted_average", "consensus", "best_result", "hybrid"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error in Phase 4 health check: {e}")
        return {
            "status": "unhealthy",
            "service": "phase4-multi-agent-reasoning",
            "error": str(e)
        }

@router.get("/agents")
async def get_phase4_agents():
    """
    Get information about available agents in the Phase 4 system.
    
    Returns:
        Dict: Agent information
    """
    try:
        status = manager.get_system_status()
        
        agents_info = []
        for agent_id, agent in status['registry']['local_agents'].items():
            # agent is already a dictionary from get_status()
            agents_info.append({
                "agent_id": agent_id,
                "type": "local",
                "capabilities": agent.get('capabilities', []),
                "status": "available"
            })
        
        # Add A2A agents if available
        if status['a2a_available']:
            for agent_id, agent in status['registry'].get('a2a_agents', {}).items():
                agents_info.append({
                    "agent_id": agent_id,
                    "type": "a2a",
                    "capabilities": agent.get('capabilities', []),
                    "status": "available" if agent.get('status') != 'error' else "unavailable"
                })
        
        return {
            "total_agents": len(agents_info),
            "local_agents": len([a for a in agents_info if a['type'] == 'local']),
            "a2a_agents": len([a for a in agents_info if a['type'] == 'a2a']),
            "agents": agents_info
        }
        
    except Exception as e:
        logger.error(f"Error getting Phase 4 agents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting agent information: {str(e)}"
        )

@router.get("/status")
async def get_phase4_status():
    """
    Get detailed status of the Phase 4 multi-agent system.
    
    Returns:
        Dict: Detailed system status
    """
    try:
        status = manager.get_system_status()
        
        return {
            "system_status": "operational",
            "registry": status['registry'],
            "configuration": {
                "enhancement_threshold": status['enhancement_threshold'],
                "a2a_available": status['a2a_available']
            },
            "capabilities": {
                "supported_task_types": ["general", "mathematical", "logical", "causal"],
                "supported_approaches": ["local_only", "a2a_enhanced", "hybrid", "a2a_only"],
                "synthesis_methods": ["weighted_average", "consensus", "best_result", "hybrid"]
            },
            "performance": {
                "total_agents": status['registry']['total_agents'],
                "local_agents_available": len(status['registry']['local_agents']),
                "a2a_agents_available": len(status['registry'].get('a2a_agents', []))
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting Phase 4 status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting system status: {str(e)}"
        )

@router.post("/configure")
async def configure_phase4_system(request: Dict[str, Any]):
    """
    Configure the Phase 4 multi-agent system.
    
    Args:
        request: Configuration parameters
        
    Returns:
        Dict: Configuration result
    """
    try:
        # Set enhancement threshold if provided
        if 'enhancement_threshold' in request:
            threshold = float(request['enhancement_threshold'])
            manager.set_enhancement_threshold(threshold)
        
        # Get updated status
        status = manager.get_system_status()
        
        return {
            "status": "configured",
            "configuration": {
                "enhancement_threshold": status['enhancement_threshold'],
                "a2a_available": status['a2a_available']
            },
            "message": "Phase 4 system configured successfully"
        }
        
    except Exception as e:
        logger.error(f"Error configuring Phase 4 system: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error configuring system: {str(e)}"
        ) 