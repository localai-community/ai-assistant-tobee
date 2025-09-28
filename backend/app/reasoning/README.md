# Unified Reasoning System

The Unified Reasoning System consolidates all three phases of reasoning into a single, easy-to-use interface. This system provides comprehensive reasoning capabilities for mathematical, logical, causal, and complex problem-solving scenarios.

## Overview

The system combines:

- **Phase 1**: Core components (base classes, validation, parsing, formatting)
- **Phase 2**: Basic reasoning engines (mathematical, logical, causal)
- **Phase 3**: Advanced reasoning strategies (Chain-of-Thought, Tree-of-Thoughts, prompt engineering)

## Quick Start

### Basic Usage

```python
from app.reasoning import create_unified_reasoner

# Create a unified reasoning system
system = create_unified_reasoner()

# Solve a problem (auto-selects best mode)
result = await system.reason("What is 15 * 23 + 45?")
print(f"Answer: {result.final_answer}")
```

### Quick Reasoning

For simple use cases:

```python
from app.reasoning import quick_reason

# One-liner for simple problems
result = quick_reason("What is 7 * 8 + 12?")
print(f"Answer: {result.final_answer}")
```

## Reasoning Modes

The system supports multiple reasoning modes:

- `MATHEMATICAL`: For numerical calculations and equations
- `LOGICAL`: For logical reasoning and inference
- `CAUSAL`: For cause-and-effect analysis
- `CHAIN_OF_THOUGHT`: For step-by-step complex reasoning
- `TREE_OF_THOUGHTS`: For exploring multiple solution paths
- `HYBRID`: Combines multiple reasoning approaches
- `AUTO`: Automatically selects the best mode (default)

### Using Specific Modes

```python
from app.reasoning import ReasoningMode

# Force a specific reasoning mode
result = await system.reason(
    "If all birds can fly and penguins are birds, can penguins fly?",
    mode=ReasoningMode.LOGICAL
)
```

## Configuration

### Basic Configuration

```python
from app.reasoning import UnifiedReasoningConfig

config = UnifiedReasoningConfig(
    default_mode=ReasoningMode.CHAIN_OF_THOUGHT,
    enable_validation=True,
    enable_parsing=True,
    enable_formatting=True,
    include_metadata=True,
    max_iterations=10,
    timeout_seconds=300
)

system = create_unified_reasoner(config)
```

### Advanced Configuration

```python
config = UnifiedReasoningConfig(
    # Core settings
    default_mode=ReasoningMode.AUTO,
    enable_validation=True,
    enable_parsing=True,
    enable_formatting=True,
    
    # Engine-specific configurations
    mathematical_config={
        "precision": 4,
        "show_work": True,
        "use_scientific_notation": False
    },
    logical_config={
        "strict_mode": True,
        "include_truth_tables": False
    },
    causal_config={
        "max_causal_depth": 3,
        "include_mediators": True
    },
    
    # Strategy-specific configurations
    cot_config={
        "max_steps": 10,
        "include_confidence": True,
        "detailed_explanations": True
    },
    tot_config={
        "max_branches": 5,
        "exploration_depth": 3,
        "enable_backtracking": True
    },
    
    # Output settings
    output_format=OutputFormat.STRUCTURED,
    include_metadata=True,
    include_validation_results=True,
    
    # Performance settings
    max_iterations=10,
    timeout_seconds=300,
    enable_caching=True
)
```

## Hybrid Reasoning

Create custom hybrid reasoners that combine multiple approaches:

```python
# Create a hybrid reasoner
hybrid_reasoner = system.reasoner_factory.create_hybrid_reasoner([
    ReasoningMode.MATHEMATICAL,
    ReasoningMode.LOGICAL,
    ReasoningMode.CHAIN_OF_THOUGHT
])

# Use for complex multi-faceted problems
result = await hybrid_reasoner.reason(complex_problem)
```

## Step-by-Step Reasoning

Access detailed reasoning steps:

```python
result = await system.reason("Solve for x: 2x + 5 = 13")

print(f"Final Answer: {result.final_answer}")
print("\nStep-by-step reasoning:")

for i, step in enumerate(result.steps, 1):
    print(f"Step {i}: {step.description}")
    if step.reasoning:
        print(f"  Reasoning: {step.reasoning}")
    if step.result:
        print(f"  Result: {step.result}")
```

## Validation and Error Handling

The system includes comprehensive validation:

```python
# Empty problem (triggers validation error)
result = await system.reason("")
if not result.validation_results[0].is_valid:
    print(f"Error: {result.validation_results[0].message}")

# Invalid problem (handled gracefully)
result = await system.reason("This is not a mathematical problem")
print(f"Generated {len(result.steps)} steps")
```

## Available Modes and Information

```python
# Get all available modes
modes = system.get_available_modes()
print("Available modes:", [mode.value for mode in modes])

# Get information about a specific mode
info = system.get_engine_info(ReasoningMode.MATHEMATICAL)
print(f"Mathematical engine: {info['name']}")
```

## Mode Configuration

Configure specific reasoning modes:

```python
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
```

## Examples

See `examples.py` for comprehensive usage examples:

```python
from app.reasoning.examples import run_all_examples
import asyncio

# Run all examples
asyncio.run(run_all_examples())
```

## Architecture

### Core Components (Phase 1)
- `BaseReasoner`: Abstract base class for all reasoners
- `ReasoningResult`: Container for reasoning results
- `ReasoningStep`: Individual reasoning steps
- `ValidationFramework`: Input validation system
- `ParserFactory`: Problem statement parsing
- `FormatterFactory`: Output formatting

### Basic Engines (Phase 2)
- `MathematicalReasoningEngine`: Numerical calculations
- `LogicalReasoningEngine`: Logical inference
- `CausalReasoningEngine`: Cause-effect analysis

### Advanced Strategies (Phase 3)
- `ChainOfThoughtStrategy`: Step-by-step reasoning
- `TreeOfThoughtsStrategy`: Multi-path exploration
- `PromptEngineeringFramework`: Advanced prompt techniques

### Unified System
- `UnifiedReasoningSystem`: Main interface
- `ReasonerFactory`: Dynamic reasoner creation
- `HybridReasoner`: Multi-mode reasoning

## Best Practices

1. **Use AUTO mode** for most problems to let the system choose the best approach
2. **Enable validation** for production use to catch invalid inputs
3. **Use specific modes** when you know the problem type
4. **Configure timeouts** for long-running problems
5. **Use hybrid reasoning** for complex, multi-faceted problems
6. **Check validation results** to handle errors gracefully

## Performance Considerations

- The system automatically caches results when enabled
- Use appropriate timeouts for your use case
- Consider the complexity of your problems when setting max_iterations
- Hybrid reasoning may take longer but provides more comprehensive results

## Error Handling

The system provides robust error handling:

- Input validation catches invalid problems
- Graceful degradation when specific modes fail
- Comprehensive error messages in validation results
- Fallback to alternative reasoning approaches

## Extending the System

The unified system is designed to be extensible:

1. Create new reasoning engines by extending `BaseReasoner`
2. Add new validation plugins to the `ValidationFramework`
3. Implement custom formatters for different output formats
4. Create specialized hybrid reasoners for domain-specific problems

## Migration from Individual Phases

If you're currently using individual reasoning components:

```python
# Old way (individual components)
from app.reasoning.engines import MathematicalReasoningEngine
from app.reasoning.strategies import ChainOfThoughtStrategy

math_engine = MathematicalReasoningEngine()
cot_strategy = ChainOfThoughtStrategy()

# New way (unified system)
from app.reasoning import create_unified_reasoner

system = create_unified_reasoner()
result = await system.reason(problem, mode=ReasoningMode.MATHEMATICAL)
```

The unified system provides backward compatibility while offering a much simpler interface.

