"""
Reasoning System Module

This module provides a comprehensive step-by-step reasoning system with support for
multiple reasoning types, validation, and various output formats.

Phase 2: Basic Reasoning Engines
- Mathematical Reasoning Engine
- Logical Reasoning Engine  
- Causal Reasoning Engine

Phase 3: Advanced Reasoning Strategies
- Chain-of-Thought (CoT) Reasoning Strategy
- Tree-of-Thoughts (ToT) Reasoning Strategy
- Prompt Engineering Framework
"""

from .core.base import (
    BaseReasoner,
    ReasoningChain,
    ReasoningResult,
    ReasoningStep,
    ReasoningType,
    StepStatus,
    ValidationLevel,
    ValidationResult
)

from .core.validator import (
    ValidationFramework,
    ValidationRule,
    ValidationRuleType,
    ValidationContext,
    DomainValidationPlugin,
    MathematicalValidationPlugin
)

from .utils.parsers import (
    BaseParser,
    ProblemStatementParser,
    StepOutputParser,
    JSONParser,
    ParserFactory,
    InputSanitizer,
    ParseResult
)

from .utils.formatters import (
    BaseFormatter,
    JSONFormatter,
    TextFormatter,
    MarkdownFormatter,
    HTMLFormatter,
    StructuredFormatter,
    FormatterFactory,
    FormatConverter,
    OutputFormat,
    FormatConfig
)

# Phase 2: Basic Reasoning Engines
from .engines import (
    MathematicalReasoningEngine,
    LogicalReasoningEngine,
    CausalReasoningEngine
)

# Phase 3: Advanced Reasoning Strategies
from .strategies import (
    ChainOfThoughtStrategy,
    TreeOfThoughtsStrategy,
    PromptEngineeringFramework
)

__version__ = "2.0.0"

__all__ = [
    # Core classes
    "BaseReasoner",
    "ReasoningChain", 
    "ReasoningResult",
    "ReasoningStep",
    "ReasoningType",
    "StepStatus",
    "ValidationLevel",
    "ValidationResult",
    
    # Validation
    "ValidationFramework",
    "ValidationRule",
    "ValidationRuleType", 
    "ValidationContext",
    "DomainValidationPlugin",
    "MathematicalValidationPlugin",
    
    # Parsing
    "BaseParser",
    "ProblemStatementParser",
    "StepOutputParser",
    "JSONParser",
    "ParserFactory",
    "InputSanitizer",
    "ParseResult",
    
    # Formatting
    "BaseFormatter",
    "JSONFormatter",
    "TextFormatter",
    "MarkdownFormatter",
    "HTMLFormatter",
    "StructuredFormatter",
    "FormatterFactory",
    "FormatConverter",
    "OutputFormat",
    "FormatConfig",
    
    # Phase 2: Basic Reasoning Engines
    "MathematicalReasoningEngine",
    "LogicalReasoningEngine",
    "CausalReasoningEngine",
    
    # Phase 3: Advanced Reasoning Strategies
    "ChainOfThoughtStrategy",
    "TreeOfThoughtsStrategy",
    "PromptEngineeringFramework"
]
