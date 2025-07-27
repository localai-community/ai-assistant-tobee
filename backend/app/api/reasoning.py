"""
API endpoints for the reasoning system.

This module provides REST API endpoints for testing and using the Phase 1
reasoning system components.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import time

from ..reasoning import (
    # Core classes
    ReasoningResult,
    ReasoningStep,
    ReasoningType,
    StepStatus,
    ValidationLevel,
    
    # Validation
    ValidationFramework,
    ValidationContext,
    
    # Parsing
    ProblemStatementParser,
    StepOutputParser,
    ParserFactory,
    InputSanitizer,
    
    # Formatting
    FormatterFactory,
    OutputFormat,
    FormatConfig
)

router = APIRouter(prefix="/reasoning", tags=["reasoning"])


class ProblemParseRequest(BaseModel):
    """Request model for problem parsing."""
    problem_statement: str


class ProblemParseResponse(BaseModel):
    """Response model for problem parsing."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    warnings: List[str] = []


class StepParseRequest(BaseModel):
    """Request model for step parsing."""
    step_output: str


class StepParseResponse(BaseModel):
    """Response model for step parsing."""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None
    warnings: List[str] = []


class ValidationRequest(BaseModel):
    """Request model for validation."""
    problem_statement: str
    steps: List[Dict[str, Any]]
    final_answer: Optional[Any] = None
    confidence: float = 0.0


class ValidationResponse(BaseModel):
    """Response model for validation."""
    input_validation: List[Dict[str, Any]]
    step_validation: List[List[Dict[str, Any]]]
    result_validation: List[Dict[str, Any]]
    summary: Dict[str, Any]


class FormatRequest(BaseModel):
    """Request model for formatting."""
    problem_statement: str
    steps: List[Dict[str, Any]]
    final_answer: Optional[Any] = None
    confidence: float = 0.0
    format_type: str = "json"
    include_metadata: bool = True
    include_validation: bool = True
    include_timestamps: bool = True


class FormatResponse(BaseModel):
    """Response model for formatting."""
    success: bool
    formatted_output: Optional[str] = None
    error_message: Optional[str] = None


class TestReasoningRequest(BaseModel):
    """Request model for testing the complete reasoning workflow."""
    problem_statement: str
    format_type: str = "json"


class TestReasoningResponse(BaseModel):
    """Response model for testing the complete reasoning workflow."""
    success: bool
    parsed_problem: Optional[Dict[str, Any]] = None
    validation_results: Optional[Dict[str, Any]] = None
    formatted_output: Optional[str] = None
    error_message: Optional[str] = None


@router.post("/parse-problem", response_model=ProblemParseResponse)
async def parse_problem(request: ProblemParseRequest):
    """Parse and analyze a problem statement."""
    try:
        # Sanitize input
        sanitizer = InputSanitizer()
        sanitized_input = sanitizer.sanitize(request.problem_statement)
        
        # Parse problem
        parser = ProblemStatementParser()
        parse_result = parser.parse(sanitized_input)
        
        return ProblemParseResponse(
            success=parse_result.success,
            data=parse_result.data,
            error_message=parse_result.error_message,
            warnings=parse_result.warnings
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing problem: {str(e)}")


@router.post("/parse-steps", response_model=StepParseResponse)
async def parse_steps(request: StepParseRequest):
    """Parse step-by-step reasoning output."""
    try:
        # Sanitize input
        sanitizer = InputSanitizer()
        sanitized_input = sanitizer.sanitize(request.step_output)
        
        # Parse steps
        parser = StepOutputParser()
        parse_result = parser.parse(sanitized_input)
        
        return StepParseResponse(
            success=parse_result.success,
            data=parse_result.data,
            error_message=parse_result.error_message,
            warnings=parse_result.warnings
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing steps: {str(e)}")


@router.post("/validate", response_model=ValidationResponse)
async def validate_reasoning(request: ValidationRequest):
    """Validate reasoning input, steps, and result."""
    try:
        # Create validation framework
        framework = ValidationFramework()
        
        # Set context
        context = ValidationContext(
            problem_statement=request.problem_statement,
            reasoning_type="hybrid"
        )
        framework.set_context(context)
        
        # Create reasoning result for validation
        result = ReasoningResult(
            problem_statement=request.problem_statement,
            reasoning_type=ReasoningType.HYBRID,
            final_answer=request.final_answer,
            confidence=request.confidence
        )
        
        # Add steps to result
        for step_data in request.steps:
            step = ReasoningStep(
                description=step_data.get("description", ""),
                reasoning=step_data.get("reasoning", ""),
                confidence=step_data.get("confidence", 0.0),
                status=StepStatus.COMPLETED
            )
            result.add_step(step)
        
        # Perform validation
        validation_results = framework.validate_all(
            request.problem_statement,
            result.steps,
            result
        )
        
        # Get summary
        summary = framework.get_validation_summary(validation_results["result"])
        
        return ValidationResponse(
            input_validation=[vr.__dict__ for vr in validation_results["input"]],
            step_validation=[[vr.__dict__ for vr in step_results] for step_results in validation_results["steps"]],
            result_validation=[vr.__dict__ for vr in validation_results["result"]],
            summary=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating reasoning: {str(e)}")


@router.post("/format", response_model=FormatResponse)
async def format_reasoning(request: FormatRequest):
    """Format reasoning result in the specified format."""
    try:
        # Create reasoning result
        result = ReasoningResult(
            problem_statement=request.problem_statement,
            reasoning_type=ReasoningType.HYBRID,
            final_answer=request.final_answer,
            confidence=request.confidence
        )
        
        # Add steps to result
        for step_data in request.steps:
            step = ReasoningStep(
                description=step_data.get("description", ""),
                reasoning=step_data.get("reasoning", ""),
                confidence=step_data.get("confidence", 0.0),
                status=StepStatus.COMPLETED
            )
            result.add_step(step)
        
        # Create formatter
        try:
            format_type = OutputFormat(request.format_type.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported format type: {request.format_type}")
        
        formatter = FormatterFactory.create_formatter(format_type)
        if not formatter:
            raise HTTPException(status_code=400, detail=f"Could not create formatter for: {request.format_type}")
        
        # Configure formatter
        config = FormatConfig(
            include_metadata=request.include_metadata,
            include_validation=request.include_validation,
            include_timestamps=request.include_timestamps
        )
        formatter.set_config(config)
        
        # Format result
        formatted_output = formatter.format(result)
        
        return FormatResponse(
            success=True,
            formatted_output=formatted_output
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error formatting reasoning: {str(e)}")


@router.post("/test-workflow", response_model=TestReasoningResponse)
async def test_workflow(request: TestReasoningRequest):
    """Test the complete reasoning workflow (parse -> validate -> format)."""
    try:
        # Step 1: Parse problem
        sanitizer = InputSanitizer()
        sanitized_input = sanitizer.sanitize(request.problem_statement)
        
        problem_parser = ProblemStatementParser()
        parse_result = problem_parser.parse(sanitized_input)
        
        if not parse_result.success:
            return TestReasoningResponse(
                success=False,
                error_message=f"Problem parsing failed: {parse_result.error_message}"
            )
        
        # Step 2: Create a simple test result
        result = ReasoningResult(
            problem_statement=request.problem_statement,
            reasoning_type=ReasoningType.HYBRID,
            final_answer="This is a test answer",
            confidence=0.8
        )
        
        # Add test steps
        step1 = ReasoningStep(
            description="Analyze the problem",
            reasoning="This is a test reasoning step",
            confidence=0.7,
            status=StepStatus.COMPLETED
        )
        step2 = ReasoningStep(
            description="Generate answer",
            reasoning="Based on analysis, here is the answer",
            confidence=0.9,
            status=StepStatus.COMPLETED
        )
        result.add_step(step1)
        result.add_step(step2)
        
        # Step 3: Validate
        framework = ValidationFramework()
        validation_results = framework.validate_result(result)
        validation_summary = framework.get_validation_summary(validation_results)
        
        # Step 4: Format
        try:
            format_type = OutputFormat(request.format_type.lower())
        except ValueError:
            format_type = OutputFormat.JSON
        
        formatter = FormatterFactory.create_formatter(format_type)
        if formatter:
            formatted_output = formatter.format(result)
        else:
            formatted_output = "Formatting failed"
        
        return TestReasoningResponse(
            success=True,
            parsed_problem=parse_result.data,
            validation_results={
                "validation_summary": validation_summary,
                "validation_count": len(validation_results)
            },
            formatted_output=formatted_output
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in workflow test: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for the reasoning system."""
    return {
        "status": "healthy",
        "components": {
            "parsers": ["ProblemStatementParser", "StepOutputParser", "JSONParser"],
            "formatters": ["JSON", "Text", "Markdown", "HTML", "Structured"],
            "validation": "ValidationFramework with rule-based and statistical validation"
        },
        "phase": "Phase 1 - Core Infrastructure Complete"
    }


@router.get("/available-formats")
async def get_available_formats():
    """Get list of available output formats."""
    formats = FormatterFactory.get_available_formats()
    return {
        "formats": [format.value for format in formats],
        "default": "json"
    }


@router.get("/available-parsers")
async def get_available_parsers():
    """Get list of available parsers."""
    parsers = ParserFactory.get_available_parsers()
    return {
        "parsers": parsers,
        "default": "problem_statement"
    } 