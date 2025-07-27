"""
Phase 2 Reasoning Engines API Endpoints
API routes for Phase 2 specialized reasoning engines.
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
from ..reasoning.engines import (
    MathematicalReasoningEngine,
    LogicalReasoningEngine,
    CausalReasoningEngine
)
from ..reasoning.core.base import ReasoningType

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/phase2-reasoning", tags=["phase2-reasoning"])

class Phase2ReasoningRequest(ChatRequest):
    """Phase 2 reasoning request with engine selection."""
    use_phase2_reasoning: bool = True
    engine_type: str = "auto"  # "auto", "mathematical", "logical", "causal"
    show_steps: bool = True
    output_format: str = "markdown"
    include_validation: bool = True

class Phase2ReasoningResponse(ChatResponse):
    """Phase 2 reasoning response with engine information."""
    engine_used: str
    reasoning_type: str
    steps_count: Optional[int] = None
    confidence: float = 0.0
    validation_summary: Optional[str] = None

# Initialize engines
mathematical_engine = MathematicalReasoningEngine()
logical_engine = LogicalReasoningEngine()
causal_engine = CausalReasoningEngine()

@router.post("/", response_model=Phase2ReasoningResponse)
async def phase2_reasoning_chat(request: Phase2ReasoningRequest, db: Session = Depends(get_db)):
    """
    Send a message and get a response using Phase 2 reasoning engines.
    
    Args:
        request: Phase 2 reasoning request containing message and engine selection
        db: Database session
        
    Returns:
        Phase2ReasoningResponse: AI response with engine-specific reasoning
    """
    try:
        # Create chat service with database
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        
        # Check if Ollama is available
        if not await chat_service.check_ollama_health():
            raise HTTPException(
                status_code=503,
                detail="Ollama service is not available. Please make sure Ollama is running."
            )
        
        # Determine which engine to use
        engine_used, reasoning_result = await select_and_use_engine(
            request.message, 
            request.engine_type,
            chat_service,
            request
        )
        
        # Generate enhanced response using the reasoning result
        enhanced_response = await generate_enhanced_response(
            chat_service,
            request.message,
            reasoning_result,
            request
        )
        
        # Create response with engine information
        response = Phase2ReasoningResponse(
            response=enhanced_response,
            model=request.model,
            conversation_id=reasoning_result.get("conversation_id") or "phase2-reasoning",
            engine_used=engine_used,
            reasoning_type=reasoning_result.get("reasoning_type", "unknown"),
            steps_count=reasoning_result.get("steps_count", 0),
            confidence=reasoning_result.get("confidence", 0.0),
            validation_summary=reasoning_result.get("validation_summary")
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Phase 2 reasoning chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def select_and_use_engine(
    message: str, 
    engine_type: str,
    chat_service: ChatService,
    request: Phase2ReasoningRequest
) -> tuple[str, Dict[str, Any]]:
    """Select and use the appropriate Phase 2 reasoning engine."""
    
    if engine_type == "auto":
        # Auto-detect which engine to use
        if mathematical_engine.can_handle(message):
            engine_used = "mathematical"
            reasoning_result = mathematical_engine.solve(message)
        elif logical_engine.can_handle(message):
            engine_used = "logical"
            reasoning_result = logical_engine.solve(message)
        elif causal_engine.can_handle(message):
            engine_used = "causal"
            reasoning_result = causal_engine.solve(message)
        else:
            # Fallback to mathematical engine for general problems
            engine_used = "mathematical"
            reasoning_result = mathematical_engine.solve(message)
    elif engine_type == "mathematical":
        engine_used = "mathematical"
        reasoning_result = mathematical_engine.solve(message)
    elif engine_type == "logical":
        engine_used = "logical"
        reasoning_result = logical_engine.solve(message)
    elif engine_type == "causal":
        engine_used = "causal"
        reasoning_result = causal_engine.solve(message)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown engine type: {engine_type}")
    
    # Convert reasoning result to dict format
    result_dict = {
        "problem_statement": reasoning_result.problem_statement,
        "reasoning_type": reasoning_result.reasoning_type.value,
        "final_answer": reasoning_result.final_answer,
        "confidence": reasoning_result.confidence,
        "steps": [step.to_dict() for step in reasoning_result.steps],
        "steps_count": len(reasoning_result.steps)
    }
    
    return engine_used, result_dict

async def generate_enhanced_response(
    chat_service: ChatService,
    message: str,
    reasoning_result: Dict[str, Any],
    request: Phase2ReasoningRequest
) -> str:
    """Generate an enhanced response using the reasoning result."""
    
    # Create a prompt that includes the reasoning steps
    steps_text = "\n".join([
        f"Step {i+1}: {step.get('description', '')}\n{step.get('reasoning', '')}"
        for i, step in enumerate(reasoning_result.get("steps", []))
    ])
    
    enhanced_prompt = f"""Based on the following step-by-step reasoning, provide a clear and comprehensive answer:

Problem: {message}

Reasoning Steps:
{steps_text}

Final Answer: {reasoning_result.get('final_answer', '')}

Please provide a well-structured response that incorporates the reasoning steps and final answer."""

    # Generate response using the chat service
    response = await chat_service.generate_response(
        message=enhanced_prompt,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        conversation_id=request.conversation_id,
        k=request.k,
        filter_dict=request.filter_dict
    )
    
    return response.response

@router.get("/status")
async def phase2_status():
    """Get status of Phase 2 reasoning engines."""
    try:
        # Test each engine with a simple problem
        math_test = mathematical_engine.can_handle("Solve 2x + 3 = 7")
        logic_test = logical_engine.can_handle("All A are B. Some B are C.")
        causal_test = causal_engine.can_handle("Does X cause Y?")
        
        return {
            "status": "available",
            "engines": {
                "mathematical": {
                    "status": "available" if math_test else "limited",
                    "features": ["algebraic", "geometric", "calculus", "trigonometric", "statistical"],
                    "test_passed": math_test
                },
                "logical": {
                    "status": "available" if logic_test else "limited",
                    "features": ["propositional", "syllogistic", "inference", "consistency", "proof"],
                    "test_passed": logic_test
                },
                "causal": {
                    "status": "available" if causal_test else "limited",
                    "features": ["identification", "intervention", "counterfactual", "effect_estimation"],
                    "test_passed": causal_test
                }
            }
        }
    except Exception as e:
        logger.error(f"Phase 2 status error: {e}")
        return {
            "status": "unavailable",
            "error": str(e),
            "engines": {
                "mathematical": {"status": "unknown", "error": str(e)},
                "logical": {"status": "unknown", "error": str(e)},
                "causal": {"status": "unknown", "error": str(e)}
            }
        }

@router.get("/health")
async def phase2_health():
    """
    Health check endpoint for Phase 2 reasoning engines.
    
    Returns:
        Dict: Health status of Phase 2 reasoning engines
    """
    try:
        # Test each engine
        test_results = {}
        
        # Test mathematical engine
        try:
            math_result = mathematical_engine.can_handle("Solve 2x + 3 = 7")
            test_results["mathematical"] = "available" if math_result else "error"
        except Exception as e:
            test_results["mathematical"] = f"error: {str(e)}"
        
        # Test logical engine
        try:
            logic_result = logical_engine.can_handle("If all A are B and all B are C, then all A are C")
            test_results["logical"] = "available" if logic_result else "error"
        except Exception as e:
            test_results["logical"] = f"error: {str(e)}"
        
        # Test causal engine
        try:
            causal_result = causal_engine.can_handle("What is the causal effect of X on Y?")
            test_results["causal"] = "available" if causal_result else "error"
        except Exception as e:
            test_results["causal"] = f"error: {str(e)}"
        
        return {
            "status": "healthy" if all(status == "available" for status in test_results.values()) else "degraded",
            "engines": test_results,
            "service": "phase2-reasoning"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "phase2-reasoning"
        }


@router.post("/stream")
async def phase2_reasoning_stream(request: Phase2ReasoningRequest, db: Session = Depends(get_db)):
    """
    Send a message and get a streaming response using Phase 2 reasoning engines.
    
    Args:
        request: Phase 2 reasoning request containing message and engine selection
        db: Database session
        
    Returns:
        StreamingResponse: Streaming AI response with engine-specific reasoning
    """
    try:
        # Create chat service with database
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        
        # Check if Ollama is available
        if not await chat_service.check_ollama_health():
            raise HTTPException(
                status_code=503,
                detail="Ollama service is not available. Please make sure Ollama is running."
            )
        
        async def generate_stream():
            try:
                # Determine which engine to use
                engine_used, reasoning_result = await select_and_use_engine(
                    request.message, 
                    request.engine_type,
                    chat_service,
                    request
                )
                
                # Create enhanced prompt for streaming
                steps_text = "\n".join([
                    f"Step {i+1}: {step.get('description', '')}\n{step.get('reasoning', '')}"
                    for i, step in enumerate(reasoning_result.get("steps", []))
                ])
                
                enhanced_prompt = f"""Based on the following step-by-step reasoning, provide a clear and comprehensive answer:

Problem: {request.message}

Reasoning Steps:
{steps_text}

Final Answer: {reasoning_result.get('final_answer', '')}

Please provide a well-structured response that incorporates the reasoning steps and final answer."""
                
                # Stream the response using the chat service's streaming method
                full_response = ""
                async for chunk in chat_service.generate_streaming_response(
                    message=enhanced_prompt,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    conversation_id=request.conversation_id
                ):
                    full_response += chunk
                    data = {
                        "content": chunk,
                        "engine_used": engine_used,
                        "reasoning_type": reasoning_result.get("reasoning_type", "unknown"),
                        "steps_count": reasoning_result.get("steps_count", 0),
                        "confidence": reasoning_result.get("confidence", 0.0),
                        "validation_summary": reasoning_result.get("validation_summary")
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                
                # Send final metadata
                final_data = {
                    "content": "",
                    "conversation_id": reasoning_result.get("conversation_id") or "phase2-reasoning",
                    "engine_used": engine_used,
                    "reasoning_type": reasoning_result.get("reasoning_type", "unknown"),
                    "steps_count": reasoning_result.get("steps_count", 0),
                    "confidence": reasoning_result.get("confidence", 0.0),
                    "validation_summary": reasoning_result.get("validation_summary"),
                    "final": True
                }
                yield f"data: {json.dumps(final_data)}\n\n"
                
            except Exception as e:
                logger.error(f"Streaming error: {str(e)}")
                error_data = {"content": f"❌ Error: {str(e)}", "error": True}
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        logger.error(f"Phase 2 streaming request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 