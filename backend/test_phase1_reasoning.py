#!/usr/bin/env python3
"""
Test script for Phase 1 reasoning system implementation.

This script tests the core infrastructure including base classes, validation framework,
parsing utilities, and formatting utilities.
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timezone

# Add the backend directory to the path
sys.path.insert(0, '.')

from app.reasoning import (
    # Core classes
    BaseReasoner,
    ReasoningResult,
    ReasoningStep,
    ReasoningType,
    StepStatus,
    ValidationLevel,
    ValidationResult,
    
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


class SimpleTestReasoner(BaseReasoner[ReasoningResult]):
    """Simple test reasoner for demonstration."""
    
    def __init__(self):
        super().__init__("SimpleTestReasoner", ReasoningType.HYBRID)
    
    async def reason(self, problem_statement: str, **kwargs) -> ReasoningResult:
        """Perform simple reasoning."""
        start_time = time.time()
        
        # Create result
        result = ReasoningResult(
            problem_statement=problem_statement,
            reasoning_type=self.reasoning_type
        )
        
        # Create steps
        step1 = ReasoningStep(
            description="Analyze the problem statement",
            reasoning="The problem appears to be a general reasoning task.",
            confidence=0.8,
            status=StepStatus.COMPLETED,
            completed_at=datetime.now(timezone.utc)
        )
        
        step2 = ReasoningStep(
            description="Generate a simple response",
            reasoning="Based on the analysis, I can provide a basic response.",
            confidence=0.9,
            status=StepStatus.COMPLETED,
            completed_at=datetime.now(timezone.utc)
        )
        
        # Add steps to result
        result.add_step(step1)
        result.add_step(step2)
        
        # Set final answer
        result.final_answer = f"Processed: {problem_statement}"
        result.confidence = 0.85
        result.completed_at = datetime.now(timezone.utc)
        result.execution_time = time.time() - start_time
        
        return result
    
    def can_handle(self, problem_statement: str) -> bool:
        """Check if this reasoner can handle the problem."""
        return len(problem_statement) > 0


async def test_core_classes():
    """Test core classes functionality."""
    print("Testing core classes...")
    
    # Test ReasoningStep
    step = ReasoningStep(
        description="Test step",
        reasoning="This is a test reasoning step",
        confidence=0.8,
        status=StepStatus.COMPLETED
    )
    
    # Test serialization/deserialization
    step_dict = step.to_dict()
    step_from_dict = ReasoningStep.from_dict(step_dict)
    
    assert step.description == step_from_dict.description
    assert step.confidence == step_from_dict.confidence
    print("✓ ReasoningStep serialization/deserialization works")
    
    # Test ReasoningResult
    result = ReasoningResult(
        problem_statement="Test problem",
        reasoning_type=ReasoningType.HYBRID
    )
    result.add_step(step)
    
    result_dict = result.to_dict()
    result_from_dict = ReasoningResult.from_dict(result_dict)
    
    assert result.problem_statement == result_from_dict.problem_statement
    assert len(result.steps) == len(result_from_dict.steps)
    print("✓ ReasoningResult serialization/deserialization works")
    
    # Test BaseReasoner
    reasoner = SimpleTestReasoner()
    test_result = await reasoner.reason("Test problem statement")
    
    assert isinstance(test_result, ReasoningResult)
    assert len(test_result.steps) == 2
    assert test_result.final_answer is not None
    print("✓ BaseReasoner functionality works")


def test_validation_framework():
    """Test validation framework."""
    print("\nTesting validation framework...")
    
    # Create validation framework
    framework = ValidationFramework()
    
    # Test input validation
    input_results = framework.validate_input("Valid problem statement")
    assert len(input_results) > 0
    print("✓ Input validation works")
    
    # Test step validation
    step = ReasoningStep(
        description="Valid step",
        reasoning="Valid reasoning",
        confidence=0.8
    )
    step_results = framework.validate_step(step)
    assert len(step_results) > 0
    print("✓ Step validation works")
    
    # Test result validation
    result = ReasoningResult(
        problem_statement="Test problem",
        reasoning_type=ReasoningType.HYBRID
    )
    result.add_step(step)
    result_results = framework.validate_result(result)
    assert len(result_results) > 0
    print("✓ Result validation works")
    
    # Test validation summary
    summary = framework.get_validation_summary(result_results)
    assert "total" in summary
    assert "valid" in summary
    print("✓ Validation summary works")


def test_parsing_utilities():
    """Test parsing utilities."""
    print("\nTesting parsing utilities...")
    
    # Test ProblemStatementParser
    parser = ProblemStatementParser()
    parse_result = parser.parse("Solve the equation: 2x + 3 = 7")
    
    assert parse_result.success
    assert parse_result.data["problem_type"] == "mathematical"
    assert "numbers" in parse_result.data["extracted_info"]
    print("✓ ProblemStatementParser works")
    
    # Test StepOutputParser
    step_parser = StepOutputParser()
    step_output = """
    Step 1: Analyze the equation
    This is a linear equation with one variable.
    Confidence: 0.9
    
    Step 2: Solve for x
    Subtract 3 from both sides: 2x = 4
    Divide by 2: x = 2
    Confidence: 0.95
    """
    
    step_parse_result = step_parser.parse(step_output)
    assert step_parse_result.success
    assert len(step_parse_result.data) == 2
    print("✓ StepOutputParser works")
    
    # Test ParserFactory
    factory = ParserFactory()
    available_parsers = factory.get_available_parsers()
    assert "problem_statement" in available_parsers
    assert "step_output" in available_parsers
    print("✓ ParserFactory works")
    
    # Test InputSanitizer
    sanitizer = InputSanitizer()
    sanitized = sanitizer.sanitize("<script>alert('test')</script>Hello World")
    assert "<script>" not in sanitized
    assert "Hello World" in sanitized
    print("✓ InputSanitizer works")


def test_formatting_utilities():
    """Test formatting utilities."""
    print("\nTesting formatting utilities...")
    
    # Create a test result
    result = ReasoningResult(
        problem_statement="Test formatting",
        reasoning_type=ReasoningType.HYBRID
    )
    
    step = ReasoningStep(
        description="Test step",
        reasoning="This is a test step",
        confidence=0.8,
        status=StepStatus.COMPLETED
    )
    result.add_step(step)
    result.final_answer = "Test answer"
    result.confidence = 0.8
    
    # Test JSON formatter
    json_formatter = FormatterFactory.create_formatter(OutputFormat.JSON)
    json_output = json_formatter.format(result)
    assert '"problem_statement": "Test formatting"' in json_output
    print("✓ JSON formatter works")
    
    # Test Text formatter
    text_formatter = FormatterFactory.create_formatter(OutputFormat.TEXT)
    text_output = text_formatter.format(result)
    assert "REASONING RESULT" in text_output
    assert "Test formatting" in text_output
    print("✓ Text formatter works")
    
    # Test Markdown formatter
    md_formatter = FormatterFactory.create_formatter(OutputFormat.MARKDOWN)
    md_output = md_formatter.format(result)
    assert "# Reasoning Result" in md_output
    print("✓ Markdown formatter works")
    
    # Test Structured formatter
    struct_formatter = FormatterFactory.create_formatter(OutputFormat.STRUCTURED)
    struct_output = struct_formatter.format(result)
    assert "summary" in struct_output
    assert "steps" in struct_output
    print("✓ Structured formatter works")
    
    # Test FormatterFactory
    factory = FormatterFactory()
    available_formats = factory.get_available_formats()
    assert OutputFormat.JSON in available_formats
    assert OutputFormat.TEXT in available_formats
    print("✓ FormatterFactory works")


def test_integration():
    """Test integration of all components."""
    print("\nTesting integration...")
    
    # Create a complete workflow
    problem = "Calculate the area of a circle with radius 5"
    
    # Parse the problem
    parser = ProblemStatementParser()
    parse_result = parser.parse(problem)
    assert parse_result.success
    
    # Create a reasoner and get result
    async def get_result():
        reasoner = SimpleTestReasoner()
        return await reasoner.reason(problem)
    
    result = asyncio.run(get_result())
    
    # Validate the result
    framework = ValidationFramework()
    validation_results = framework.validate_result(result)
    summary = framework.get_validation_summary(validation_results)
    
    # Format the result
    formatter = FormatterFactory.create_formatter(OutputFormat.JSON)
    formatted_output = formatter.format(result)
    
    # Verify the complete workflow
    assert result.problem_statement == problem
    assert len(result.steps) > 0
    assert result.final_answer is not None
    assert len(validation_results) > 0
    assert len(formatted_output) > 0
    
    print("✓ Complete integration workflow works")


def main():
    """Run all tests."""
    print("Phase 1 Reasoning System Tests")
    print("=" * 40)
    
    try:
        # Test core classes
        asyncio.run(test_core_classes())
        
        # Test validation framework
        test_validation_framework()
        
        # Test parsing utilities
        test_parsing_utilities()
        
        # Test formatting utilities
        test_formatting_utilities()
        
        # Test integration
        test_integration()
        
        print("\n" + "=" * 40)
        print("🎉 All Phase 1 tests passed!")
        print("Phase 1 implementation is complete and working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 