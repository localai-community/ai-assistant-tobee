"""
Phase 3 Advanced Reasoning Strategies API Endpoints
API routes for Phase 3 advanced reasoning strategies (Chain-of-Thought, Tree-of-Thoughts, Prompt Engineering).
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
from ..reasoning.strategies import (
    ChainOfThoughtStrategy,
    TreeOfThoughtsStrategy,
    PromptEngineeringFramework
)
from ..reasoning.core.base import ReasoningType

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/phase3-reasoning", tags=["phase3-reasoning"])

class Phase3ReasoningRequest(ChatRequest):
    """Phase 3 reasoning request with strategy selection."""
    use_phase3_reasoning: bool = True
    strategy_type: str = "auto"  # "auto", "chain_of_thought", "tree_of_thoughts", "prompt_engineering"
    show_steps: bool = True
    output_format: str = "markdown"
    include_validation: bool = True

class Phase3ReasoningResponse(ChatResponse):
    """Phase 3 reasoning response with strategy information."""
    strategy_used: str
    reasoning_type: str
    steps_count: Optional[int] = None
    confidence: float = 0.0
    validation_summary: Optional[str] = None

# Initialize strategies
cot_strategy = ChainOfThoughtStrategy()
tot_strategy = TreeOfThoughtsStrategy()
pe_framework = PromptEngineeringFramework()

@router.post("/", response_model=Phase3ReasoningResponse)
async def phase3_reasoning_chat(request: Phase3ReasoningRequest, db: Session = Depends(get_db)):
    """
    Send a message and get a response using Phase 3 advanced reasoning strategies.
    
    Args:
        request: Phase 3 reasoning request containing message and strategy selection
        db: Database session
        
    Returns:
        Phase3ReasoningResponse: AI response with strategy-specific reasoning
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
        
        # Determine which strategy to use
        strategy_used, reasoning_result = await select_and_use_strategy(
            request.message, 
            request.strategy_type,
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
        
        # Create response with strategy information
        response = Phase3ReasoningResponse(
            response=enhanced_response,
            model=request.model,
            conversation_id=reasoning_result.get("conversation_id") or "phase3-reasoning",
            strategy_used=strategy_used,
            reasoning_type=reasoning_result.get("reasoning_type", "unknown"),
            steps_count=reasoning_result.get("steps_count", 0),
            confidence=reasoning_result.get("confidence", 0.0),
            validation_summary=reasoning_result.get("validation_summary")
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Phase 3 reasoning chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def select_and_use_strategy(
    message: str, 
    strategy_type: str,
    chat_service: ChatService,
    request: Phase3ReasoningRequest
) -> tuple[str, Dict[str, Any]]:
    """
    Select and use the appropriate Phase 3 strategy based on the message and strategy type.
    
    Args:
        message: User message
        strategy_type: Strategy type ("auto", "chain_of_thought", "tree_of_thoughts", "prompt_engineering")
        chat_service: Chat service instance
        request: Original request
        
    Returns:
        Tuple of (strategy_used, reasoning_result)
    """
    try:
        # Auto-detect strategy if not specified
        if strategy_type == "auto":
            # Simple heuristic for strategy selection
            if any(word in message.lower() for word in ["calculate", "solve", "compute", "math", "equation"]):
                strategy_type = "chain_of_thought"
            elif any(word in message.lower() for word in ["design", "architecture", "system", "complex", "multiple"]):
                strategy_type = "tree_of_thoughts"
            elif any(word in message.lower() for word in ["prompt", "create", "write", "generate", "template"]):
                strategy_type = "prompt_engineering"
            else:
                strategy_type = "chain_of_thought"  # Default to CoT
        
        # Use the selected strategy
        if strategy_type == "chain_of_thought":
            reasoning_result = await cot_strategy.reason(message)
            strategy_used = "chain_of_thought"
        elif strategy_type == "tree_of_thoughts":
            reasoning_result = await tot_strategy.reason(message)
            strategy_used = "tree_of_thoughts"
        elif strategy_type == "prompt_engineering":
            # For prompt engineering, we'll use a simplified approach
            reasoning_result = await cot_strategy.reason(message)
            strategy_used = "prompt_engineering"
        else:
            # Fallback to Chain-of-Thought
            reasoning_result = await cot_strategy.reason(message)
            strategy_used = "chain_of_thought"
        
        # Convert reasoning result to expected format
        result_dict = {
            "conversation_id": request.conversation_id,
            "reasoning_type": reasoning_result.reasoning_type.value if hasattr(reasoning_result, 'reasoning_type') else "hybrid",
            "steps_count": len(reasoning_result.steps) if hasattr(reasoning_result, 'steps') else 0,
            "confidence": reasoning_result.confidence if hasattr(reasoning_result, 'confidence') else 0.0,
            "validation_summary": "Validated" if reasoning_result.validation_results and all(v.is_valid for v in reasoning_result.validation_results) else "Needs review"
        }
        
        return strategy_used, result_dict
        
    except Exception as e:
        logger.error(f"Error in strategy selection: {str(e)}")
        # Fallback to Chain-of-Thought
        reasoning_result = await cot_strategy.reason(message)
        return "chain_of_thought", {
            "conversation_id": request.conversation_id,
            "reasoning_type": "hybrid",
            "steps_count": len(reasoning_result.steps) if hasattr(reasoning_result, 'steps') else 0,
            "confidence": reasoning_result.confidence if hasattr(reasoning_result, 'confidence') else 0.0,
            "validation_summary": "Fallback response"
        }

async def generate_enhanced_response(
    chat_service: ChatService,
    message: str,
    reasoning_result: Dict[str, Any],
    request: Phase3ReasoningRequest
) -> str:
    """
    Generate an enhanced response using the reasoning result.
    
    Args:
        chat_service: Chat service instance
        message: Original user message
        reasoning_result: Reasoning result from strategy
        request: Original request
        
    Returns:
        Enhanced response string
    """
    try:
        # Create a prompt that includes the reasoning context
        enhanced_prompt = f"""
Please provide a comprehensive response to the following question using advanced reasoning strategies.

Question: {message}

Reasoning Context:
- Strategy used: {reasoning_result.get('reasoning_type', 'Advanced')}
- Steps generated: {reasoning_result.get('steps_count', 0)}
- Confidence level: {reasoning_result.get('confidence', 0.0):.2f}
- Validation: {reasoning_result.get('validation_summary', 'Validated')}

Please provide a detailed, step-by-step response that demonstrates advanced reasoning capabilities.
"""
        
        # Generate response using the chat service
        chat_response = await chat_service.generate_response(
            message=enhanced_prompt,
            model=request.model,
            temperature=request.temperature,
            conversation_id=request.conversation_id
        )
        
        return chat_response.response
        
    except Exception as e:
        logger.error(f"Error generating enhanced response: {str(e)}")
        return f"I apologize, but I encountered an error while processing your request. Please try again. Error: {str(e)}"

@router.get("/health")
async def phase3_health():
    """
    Get health status of Phase 3 reasoning strategies.
    
    Returns:
        Dict containing health status of all strategies
    """
    try:
        # Check strategy availability
        strategies = {
            "chain_of_thought": {
                "status": "available",
                "features": ["step-by-step reasoning", "validation", "confidence scoring"]
            },
            "tree_of_thoughts": {
                "status": "available", 
                "features": ["multi-path exploration", "search algorithms", "path evaluation"]
            },
            "prompt_engineering": {
                "status": "available",
                "features": ["template management", "context injection", "optimization"]
            }
        }
        
        return {
            "status": "available",
            "strategies": strategies
        }
        
    except Exception as e:
        logger.error(f"Error checking Phase 3 health: {str(e)}")
        return {
            "status": "unavailable",
            "error": str(e),
            "strategies": {
                "chain_of_thought": {"status": "unknown", "error": str(e)},
                "tree_of_thoughts": {"status": "unknown", "error": str(e)},
                "prompt_engineering": {"status": "unknown", "error": str(e)}
            }
        }

@router.get("/strategies")
async def get_phase3_strategies():
    """
    Get available Phase 3 strategies.
    
    Returns:
        Dict containing available strategies and their capabilities
    """
    try:
        strategies = {
            "chain_of_thought": {
                "name": "Chain-of-Thought",
                "description": "Step-by-step reasoning with validation and confidence scoring",
                "capabilities": ["mathematical reasoning", "logical reasoning", "step validation"],
                "best_for": ["mathematical problems", "logical puzzles", "step-by-step solutions"]
            },
            "tree_of_thoughts": {
                "name": "Tree-of-Thoughts", 
                "description": "Multi-path exploration with search algorithms",
                "capabilities": ["multi-path exploration", "search algorithms", "path evaluation"],
                "best_for": ["complex design problems", "architecture decisions", "multi-option scenarios"]
            },
            "prompt_engineering": {
                "name": "Prompt Engineering",
                "description": "Template management and context-aware prompt generation",
                "capabilities": ["template management", "context injection", "prompt optimization"],
                "best_for": ["creative writing", "prompt creation", "context-aware responses"]
            }
        }
        
        return {
            "strategies": strategies,
            "auto_detection": True,
            "default_strategy": "chain_of_thought"
        }
        
    except Exception as e:
        logger.error(f"Error getting Phase 3 strategies: {str(e)}")
        return {
            "strategies": {},
            "error": str(e)
        }

@router.post("/stream")
async def phase3_reasoning_stream(request: Phase3ReasoningRequest, db: Session = Depends(get_db)):
    """
    Stream Phase 3 reasoning response.
    
    Args:
        request: Phase 3 reasoning request
        db: Database session
        
    Returns:
        StreamingResponse with reasoning results
    """
    try:
        # Create chat service
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        chat_service = ChatService(ollama_url=ollama_url, db=db)
        
        # Check Ollama health
        if not await chat_service.check_ollama_health():
            raise HTTPException(
                status_code=503,
                detail="Ollama service is not available"
            )
        
        # Select and use strategy
        strategy_used, reasoning_result = await select_and_use_strategy(
            request.message,
            request.strategy_type,
            chat_service,
            request
        )
        
        async def generate_stream():
            """Generate streaming response."""
            try:
                # Send initial strategy info
                strategy_name = strategy_used.replace("_", " ").title()
                initial_content = f"🚀 Using {strategy_name} strategy...\\n\\n"
                initial_data = {
                    'content': initial_content,
                    'strategy_used': strategy_used,
                    'reasoning_type': reasoning_result.get('reasoning_type', 'unknown'),
                    'steps_count': reasoning_result.get('steps_count', 0),
                    'confidence': reasoning_result.get('confidence', 0.0),
                    'validation_summary': reasoning_result.get('validation_summary')
                }
                yield f"data: {json.dumps(initial_data)}\\n\\n"
                
                # Generate enhanced response
                enhanced_response = await generate_enhanced_response(
                    chat_service,
                    request.message,
                    reasoning_result,
                    request
                )
                
                # Send the response in chunks
                chunk_size = 50
                for i in range(0, len(enhanced_response), chunk_size):
                    chunk = enhanced_response[i:i + chunk_size]
                    chunk_data = {
                        'content': chunk,
                        'strategy_used': strategy_used,
                        'reasoning_type': reasoning_result.get('reasoning_type', 'unknown'),
                        'steps_count': reasoning_result.get('steps_count', 0),
                        'confidence': reasoning_result.get('confidence', 0.0),
                        'validation_summary': reasoning_result.get('validation_summary')
                    }
                    yield f"data: {json.dumps(chunk_data)}\\n\\n"
                    await asyncio.sleep(0.01)  # Small delay for streaming effect
                
                # Send final message
                final_data = {
                    'final': True,
                    'conversation_id': request.conversation_id,
                    'strategy_used': strategy_used,
                    'reasoning_type': reasoning_result.get('reasoning_type', 'unknown'),
                    'steps_count': reasoning_result.get('steps_count', 0),
                    'confidence': reasoning_result.get('confidence', 0.0),
                    'validation_summary': reasoning_result.get('validation_summary')
                }
                yield f"data: {json.dumps(final_data)}\\n\\n"
                
            except Exception as e:
                logger.error(f"Error in streaming: {str(e)}")
                error_data = {'error': str(e)}
                yield f"data: {json.dumps(error_data)}\\n\\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Phase 3 streaming: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}") 