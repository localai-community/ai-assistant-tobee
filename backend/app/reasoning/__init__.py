"""
Reasoning System Module

This module provides a comprehensive step-by-step reasoning system with support for
multiple reasoning types, validation, and various output formats.
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

__version__ = "1.0.0"

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
    "FormatConfig"
]
