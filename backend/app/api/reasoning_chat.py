"""
Reasoning-Enhanced Chat API Endpoints
API routes for chat functionality with integrated reasoning system.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import json
import logging
import os
import asyncio
import re

from ..services.chat import ChatService, ChatRequest, ChatResponse, Conversation
from ..core.database import get_db
from ..core.models import ErrorResponse
from ..reasoning import (
    ProblemStatementParser,
    ValidationFramework,
    FormatterFactory,
    OutputFormat,
    ReasoningResult,
    ReasoningStep,
    ReasoningType,
    StepStatus
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/reasoning-chat", tags=["reasoning-chat"])

class ReasoningChatRequest(ChatRequest):
    """Enhanced chat request with reasoning options."""
    use_reasoning: bool = True
    show_steps: bool = True
    output_format: str = "markdown"
    include_validation: bool = True

class ReasoningChatResponse(ChatResponse):
    """Enhanced chat response with reasoning information."""
    reasoning_result: Optional[Dict[str, Any]] = None
    steps_count: Optional[int] = None
    validation_summary: Optional[Dict[str, Any]] = None
    reasoning_used: bool = False
    model: Optional[str] = None

@router.post("/", response_model=ReasoningChatResponse)
async def reasoning_chat(request: ReasoningChatRequest, db: Session = Depends(get_db)):
    """
    Send a message and get a response with step-by-step reasoning.
    
    Args:
        request: Reasoning chat request containing message and reasoning options
        db: Database session
        
    Returns:
        ReasoningChatResponse: AI response with reasoning steps and validation
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
        
        # Parse the problem to determine if reasoning should be used
        problem_parser = ProblemStatementParser()
        parse_result = problem_parser.parse(request.message)
        
        # Determine if this is a reasoning-worthy problem
        should_use_reasoning = (
            request.use_reasoning and 
            parse_result.success and
            parse_result.data.get("problem_type") in ["mathematical", "logical", "general"]
        )
        
        if should_use_reasoning:
            # Generate reasoning-enhanced response
            response = await generate_reasoning_response(
                chat_service, request, parse_result.data, db
            )
        else:
            # Generate regular response
            response = await chat_service.generate_response(
                message=request.message,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                conversation_id=request.conversation_id,
                k=request.k,
                filter_dict=request.filter_dict
            )
            # Convert to reasoning response format
            response = ReasoningChatResponse(
                response=response.response,
                conversation_id=response.conversation_id,
                reasoning_used=False
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Reasoning chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def reasoning_chat_stream(request: ReasoningChatRequest, db: Session = Depends(get_db)):
    """
    Send a message and get a streaming response with step-by-step reasoning.
    
    Args:
        request: Reasoning chat request containing message and reasoning options
        db: Database session
        
    Returns:
        StreamingResponse: Stream of AI response chunks with reasoning
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
        
        # Parse the problem to determine if reasoning should be used
        problem_parser = ProblemStatementParser()
        parse_result = problem_parser.parse(request.message)
        
        # Determine if this is a reasoning-worthy problem
        should_use_reasoning = (
            request.use_reasoning and 
            parse_result.success and
            parse_result.data.get("problem_type") in ["mathematical", "logical", "general"]
        )
        
        if should_use_reasoning:
            # Generate streaming reasoning response
            async def generate_reasoning_stream():
                async for chunk in generate_reasoning_streaming_response(
                    chat_service, request, parse_result.data, db
                ):
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            return StreamingResponse(
                generate_reasoning_stream(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )
        else:
            # Generate regular streaming response
            async def generate_stream():
                async for chunk in chat_service.generate_streaming_response(
                    message=request.message,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    conversation_id=request.conversation_id
                ):
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )
        
    except Exception as e:
        logger.error(f"Reasoning chat stream error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_reasoning_response(
    chat_service: ChatService, 
    request: ReasoningChatRequest, 
    parsed_problem: Dict[str, Any],
    db: Session
) -> ReasoningChatResponse:
    """Generate a response with step-by-step reasoning."""
    
    # Create reasoning prompt
    reasoning_prompt = create_reasoning_prompt(request.message, parsed_problem)
    
    # Generate step-by-step reasoning
    reasoning_response = await chat_service.generate_response(
        message=reasoning_prompt,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        conversation_id=request.conversation_id,
        k=request.k,
        filter_dict=request.filter_dict
    )
    
    # Parse the reasoning response into steps
    reasoning_steps = parse_reasoning_response(reasoning_response.response)
    
    # Create reasoning result
    reasoning_result = ReasoningResult(
        problem_statement=request.message,
        reasoning_type=ReasoningType.HYBRID,
        final_answer="",  # AI response already contains the final answer
        confidence=0.8
    )
    
    # Add steps to reasoning result
    for i, step_data in enumerate(reasoning_steps, 1):
        step = ReasoningStep(
            step_number=i,
            description=step_data.get("description", f"Step {i}"),
            reasoning=step_data.get("reasoning", ""),
            confidence=step_data.get("confidence", 0.8),
            status=StepStatus.COMPLETED
        )
        reasoning_result.add_step(step)
    
    # Validate the reasoning
    validation_framework = ValidationFramework()
    validation_results = validation_framework.validate_result(reasoning_result)
    validation_summary = validation_framework.get_validation_summary(validation_results)
    
    # Use the actual AI response instead of the formatter
    # The AI response already contains the step-by-step reasoning
    ai_response = reasoning_response.response
    
    # Create final response - AI response already contains the final answer
    final_response = f"""## Step-by-Step Reasoning

{ai_response}
"""
    
    return ReasoningChatResponse(
        response=final_response,
        conversation_id=reasoning_response.conversation_id,
        reasoning_result=reasoning_result.__dict__,
        steps_count=len(reasoning_steps),
        validation_summary=validation_summary,
        reasoning_used=True
    )

async def generate_reasoning_streaming_response(
    chat_service: ChatService, 
    request: ReasoningChatRequest, 
    parsed_problem: Dict[str, Any],
    db: Session
):
    """Generate a streaming response with step-by-step reasoning."""
    
    # Create reasoning prompt
    reasoning_prompt = create_reasoning_prompt(request.message, parsed_problem)
    
    # Stream the reasoning response
    async for chunk in chat_service.generate_streaming_response(
        message=reasoning_prompt,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        conversation_id=request.conversation_id
    ):
        yield chunk

def create_reasoning_prompt(problem: str, parsed_problem: Dict[str, Any]) -> str:
    """Create a prompt that encourages step-by-step reasoning."""
    
    problem_type = parsed_problem.get("problem_type", "general")
    
    if problem_type == "mathematical":
        # Check if it's an equation solving problem or other mathematical problem
        equation_keywords = ["solve", "equation", "=", "find x", "solve for x", "value of x"]
        is_equation_problem = any(keyword in problem.lower() for keyword in equation_keywords)
        
        if is_equation_problem:
            return f"""Please solve this mathematical problem step by step:

Problem: {problem}

Please provide your solution in the following EXACT format:

**Step 1:** [Brief description of what you're doing]

[Explanation of why you're doing this step]

[Show your work and calculations with clear line breaks]

[Result of this step]

**Step 2:** [Brief description of what you're doing]

[Explanation of why you're doing this step]

[Show your work and calculations with clear line breaks]

[Result of this step]

[Continue with more steps as needed]

**Final Answer:** [Your final answer]

EXACT FORMATTING RULES:
1. Use "**Step 1:**" (with bold)
2. Use "**Final Answer:**" (with bold)
3. Show clear step-by-step work with proper line breaks
4. Include explanations for each step
5. Separate equations and calculations from text with line breaks
6. Use clear, readable formatting"""
        else:
            return f"""Please solve this mathematical problem step by step:

Problem: {problem}

Please provide your solution in the following EXACT format:

**Step 1:** [Brief description of what you're doing]

[Explanation of why you're doing this step]

[Show your work and calculations with clear line breaks]

[Result of this step]

**Step 2:** [Brief description of what you're doing]

[Explanation of why you're doing this step]

[Show your work and calculations with clear line breaks]

[Result of this step]

[Continue with more steps as needed]

**Final Answer:** [Your final answer]

EXACT FORMATTING RULES:
1. Use "**Step 1:**" (with bold)
2. Use "**Final Answer:**" (with bold)
3. Show clear step-by-step work with proper line breaks
4. Include explanations for each step
5. Separate equations and calculations from text with line breaks
6. Use clear, readable formatting"""
    
    elif problem_type == "logical":
        return f"""Please solve this logical problem step by step:

Problem: {problem}

Please provide your solution in the following structured format:

**Step 1:** [Brief description of what you're analyzing]
[Explanation of your logical reasoning]
[Show the logical statements/conditions]
[Apply logical rules]
[Show the result]

**Step 2:** [Brief description of what you're analyzing]
[Explanation of your logical reasoning]
[Show the logical statements/conditions]
[Apply logical rules]
[Show the result]

[Continue with more steps as needed]

**Final Answer:** [Your conclusion]

Keep each step concise and focused. Show your logical thinking clearly."""
    
    else:
        return f"""Please answer this question step by step:

Question: {problem}

Please provide your answer in the following structured format:

**Step 1:** [Brief description of what you're thinking about]
[Explanation of your reasoning]
[Show the key information/facts]
[Apply your analysis]
[Show the result]

**Step 2:** [Brief description of what you're thinking about]
[Explanation of your reasoning]
[Show the key information/facts]
[Apply your analysis]
[Show the result]

[Continue with more steps as needed]

**Final Answer:** [Your comprehensive answer]

Keep each step concise and focused. Break down your thinking process clearly."""

def parse_reasoning_response(response: str) -> List[Dict[str, Any]]:
    """Parse the AI response into structured reasoning steps."""
    steps = []
    lines = response.split('\n')
    current_step = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for step headers
        if line.lower().startswith('step ') and ':' in line:
            # Save previous step if exists
            if current_step:
                steps.append(current_step)
            
            # Start new step
            step_num = line.split(':')[0].strip()
            description = line.split(':', 1)[1].strip() if ':' in line else ""
            current_step = {
                "description": description,
                "reasoning": "",
                "confidence": 0.8
            }
        
        elif current_step and line:
            # Add to current step's reasoning
            if current_step["reasoning"]:
                current_step["reasoning"] += "\n" + line
            else:
                current_step["reasoning"] = line
    
    # Add the last step
    if current_step:
        steps.append(current_step)
    
    return steps



@router.get("/health")
async def reasoning_chat_health():
    """Health check for reasoning chat service."""
    return {
        "status": "healthy",
        "service": "reasoning-chat",
        "features": {
            "step_by_step_reasoning": "enabled",
            "problem_parsing": "enabled",
            "validation": "enabled",
            "multiple_formats": "enabled"
        }
    } 