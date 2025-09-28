"""
Unified Reasoning System Module

This module provides a comprehensive step-by-step reasoning system that consolidates
all three phases of reasoning into a unified interface:

Phase 1: Core Components (base classes, validation, parsing, formatting)
Phase 2: Basic Reasoning Engines (mathematical, logical, causal)
Phase 3: Advanced Reasoning Strategies (CoT, ToT, prompt engineering)

The unified system provides a single entry point for all reasoning capabilities.
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

# Unified Reasoning System (consolidates all phases)
from .unified import (
    UnifiedReasoningSystem,
    UnifiedReasoningConfig,
    ReasoningMode,
    ReasonerFactory,
    HybridReasoner,
    create_unified_reasoner,
    quick_reason
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
    "PromptEngineeringFramework",
    
    # Unified Reasoning System
    "UnifiedReasoningSystem",
    "UnifiedReasoningConfig",
    "ReasoningMode",
    "ReasonerFactory",
    "HybridReasoner",
    "create_unified_reasoner",
    "quick_reason"
]
