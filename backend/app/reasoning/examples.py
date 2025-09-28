"""
Examples demonstrating the unified reasoning system.

This module provides practical examples of how to use the unified reasoning system
that consolidates all three phases of reasoning.
"""

import asyncio
from typing import Dict, Any

from .unified import (
    UnifiedReasoningSystem,
    UnifiedReasoningConfig,
    ReasoningMode,
    create_unified_reasoner,
    quick_reason
)


async def example_basic_usage():
    """Example of basic usage with auto-mode selection."""
    print("=== Basic Usage Example ===")
    
    # Create unified reasoning system with default configuration
    system = create_unified_reasoner()
    
    # Simple mathematical problem
    math_problem = "What is 15 * 23 + 45?"
    result = await system.reason(math_problem)
    
    print(f"Problem: {math_problem}")
    print(f"Mode: {result.reasoning_type}")
    print(f"Answer: {result.final_answer}")
    print(f"Steps: {len(result.steps)}")
    print()


async def example_specific_mode():
    """Example of using a specific reasoning mode."""
    print("=== Specific Mode Example ===")
    
    system = create_unified_reasoner()
    
    # Logical reasoning problem
    logic_problem = "If all birds can fly and penguins are birds, can penguins fly?"
    result = await system.reason(logic_problem, mode=ReasoningMode.LOGICAL)
    
    print(f"Problem: {logic_problem}")
    print(f"Mode: {result.reasoning_type}")
    print(f"Answer: {result.final_answer}")
    print()


async def example_custom_configuration():
    """Example of using custom configuration."""
    print("=== Custom Configuration Example ===")
    
    # Create custom configuration
    config = UnifiedReasoningConfig(
        default_mode=ReasoningMode.CHAIN_OF_THOUGHT,
        enable_validation=True,
        enable_parsing=True,
        enable_formatting=True,
        include_metadata=True,
        include_validation_results=True,
        max_iterations=5,
        timeout_seconds=60
    )
    
    system = create_unified_reasoner(config)
    
    # Complex problem that benefits from chain of thought
    complex_problem = """
    A company has 3 departments: Engineering (40 employees), Sales (25 employees), 
    and Marketing (15 employees). If 20% of Engineering, 30% of Sales, and 25% of 
    Marketing employees are working remotely, how many total employees are working 
    remotely across all departments?
    """
    
    result = await system.reason(complex_problem)
    
    print(f"Problem: {complex_problem.strip()}")
    print(f"Mode: {result.reasoning_type}")
    print(f"Answer: {result.final_answer}")
    print(f"Validation Results: {len(result.validation_results)}")
    print()


async def example_hybrid_reasoning():
    """Example of hybrid reasoning combining multiple modes."""
    print("=== Hybrid Reasoning Example ===")
    
    system = create_unified_reasoner()
    
    # Create hybrid reasoner
    hybrid_reasoner = system.reasoner_factory.create_hybrid_reasoner([
        ReasoningMode.MATHEMATICAL,
        ReasoningMode.LOGICAL,
        ReasoningMode.CHAIN_OF_THOUGHT
    ])
    
    # Multi-faceted problem
    hybrid_problem = """
    A store sells apples for $2.50 per pound and oranges for $3.00 per pound. 
    If a customer buys 2.5 pounds of apples and 1.8 pounds of oranges, 
    and there's a 10% discount on the total, what is the final price? 
    Also, explain the reasoning behind the calculation.
    """
    
    result = await hybrid_reasoner.reason(hybrid_problem)
    
    print(f"Problem: {hybrid_problem.strip()}")
    print(f"Mode: {result.reasoning_type}")
    print(f"Answer: {result.final_answer}")
    print()


def example_quick_reasoning():
    """Example of quick reasoning for simple use cases."""
    print("=== Quick Reasoning Example ===")
    
    # Simple mathematical calculation
    result = quick_reason("What is 7 * 8 + 12?")
    
    print(f"Problem: What is 7 * 8 + 12?")
    print(f"Answer: {result.final_answer}")
    print()


async def example_step_by_step_reasoning():
    """Example showing detailed step-by-step reasoning."""
    print("=== Step-by-Step Reasoning Example ===")
    
    system = create_unified_reasoner()
    
    problem = "Solve for x: 2x + 5 = 13"
    result = await system.reason(problem, mode=ReasoningMode.MATHEMATICAL)
    
    print(f"Problem: {problem}")
    print(f"Final Answer: {result.final_answer}")
    print("\nStep-by-step reasoning:")
    
    for i, step in enumerate(result.steps, 1):
        print(f"Step {i}: {step.description}")
        if step.reasoning:
            print(f"  Reasoning: {step.reasoning}")
        if step.result:
            print(f"  Result: {step.result}")
        print()


async def example_validation_and_errors():
    """Example showing validation and error handling."""
    print("=== Validation and Error Handling Example ===")
    
    system = create_unified_reasoner()
    
    # Empty problem (should trigger validation error)
    empty_result = await system.reason("")
    print(f"Empty problem result: {empty_result.validation_results[0].message}")
    
    # Invalid problem (should be handled gracefully)
    invalid_result = await system.reason("This is not a mathematical or logical problem")
    print(f"Invalid problem handled: {len(invalid_result.steps)} steps generated")
    print()


async def example_available_modes():
    """Example showing available reasoning modes."""
    print("=== Available Modes Example ===")
    
    system = create_unified_reasoner()
    
    print("Available reasoning modes:")
    for mode in system.get_available_modes():
        info = system.get_engine_info(mode)
        print(f"  {mode.value}: {info.get('name', 'Unknown')}")
    print()


async def example_mode_configuration():
    """Example of configuring specific modes."""
    print("=== Mode Configuration Example ===")
    
    system = create_unified_reasoner()
    
    # Configure mathematical engine
    math_config = {
        "precision": 4,
        "show_work": True,
        "use_scientific_notation": False
    }
    system.configure_mode(ReasoningMode.MATHEMATICAL, math_config)
    
    # Configure chain of thought strategy
    cot_config = {
        "max_steps": 10,
        "include_confidence": True,
        "detailed_explanations": True
    }
    system.configure_mode(ReasoningMode.CHAIN_OF_THOUGHT, cot_config)
    
    print("Configuration applied to mathematical and chain-of-thought modes")
    print()


async def run_all_examples():
    """Run all examples to demonstrate the unified reasoning system."""
    print("Unified Reasoning System Examples")
    print("=" * 50)
    print()
    
    await example_basic_usage()
    await example_specific_mode()
    await example_custom_configuration()
    await example_hybrid_reasoning()
    example_quick_reasoning()
    await example_step_by_step_reasoning()
    await example_validation_and_errors()
    await example_available_modes()
    await example_mode_configuration()
    
    print("All examples completed!")


if __name__ == "__main__":
    # Run examples
    asyncio.run(run_all_examples())

