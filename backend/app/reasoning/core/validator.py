"""
Validation framework for the reasoning system.

This module provides comprehensive validation capabilities for reasoning steps,
results, and inputs with support for rule-based, statistical, and domain-specific validation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
import re
import statistics
from enum import Enum

from .base import ValidationResult, ValidationLevel, ReasoningStep, ReasoningResult


class ValidationRuleType(Enum):
    """Types of validation rules."""
    INPUT = "input"
    STEP = "step"
    RESULT = "result"
    CROSS_VALIDATION = "cross_validation"


class ValidationRule(ABC):
    """Abstract base class for validation rules."""

    def __init__(self, name: str, rule_type: ValidationRuleType, priority: int = 0):
        self.name = name
        self.rule_type = rule_type
        self.priority = priority
        self.enabled = True

    @abstractmethod
    def validate(self, data: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate the given data.
        
        Args:
            data: The data to validate
            context: Additional context for validation
            
        Returns:
            ValidationResult indicating validation outcome
        """
        pass

    def __lt__(self, other: 'ValidationRule') -> bool:
        """Compare rules by priority."""
        return self.priority < other.priority


@dataclass
class ValidationContext:
    """Context for validation operations."""
    problem_statement: str = ""
    reasoning_type: str = ""
    step_history: List[ReasoningStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class InputValidationRule(ValidationRule):
    """Base class for input validation rules."""

    def __init__(self, name: str, priority: int = 0):
        super().__init__(name, ValidationRuleType.INPUT, priority)


class StepValidationRule(ValidationRule):
    """Base class for step validation rules."""

    def __init__(self, name: str, priority: int = 0):
        super().__init__(name, ValidationRuleType.STEP, priority)


class ResultValidationRule(ValidationRule):
    """Base class for result validation rules."""

    def __init__(self, name: str, priority: int = 0):
        super().__init__(name, ValidationRuleType.RESULT, priority)


class CrossValidationRule(ValidationRule):
    """Base class for cross-validation rules."""

    def __init__(self, name: str, priority: int = 0):
        super().__init__(name, ValidationRuleType.CROSS_VALIDATION, priority)


# Common validation rules
class NonEmptyInputRule(InputValidationRule):
    """Validates that input is not empty."""

    def __init__(self):
        super().__init__("non_empty_input", priority=1)

    def validate(self, data: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        if not data or not data.strip():
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Input cannot be empty"
            )
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="Input is not empty"
        )


class InputLengthRule(InputValidationRule):
    """Validates input length constraints."""

    def __init__(self, min_length: int = 1, max_length: int = 10000):
        super().__init__("input_length", priority=2)
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, data: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        length = len(data.strip())
        if length < self.min_length:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Input too short (minimum {self.min_length} characters)"
            )
        if length > self.max_length:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Input too long (maximum {self.max_length} characters)"
            )
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"Input length ({length}) is within acceptable range"
        )


class StepDescriptionRule(StepValidationRule):
    """Validates that reasoning steps have descriptions."""

    def __init__(self):
        super().__init__("step_description", priority=1)

    def validate(self, data: ReasoningStep, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        if not data.description or not data.description.strip():
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message="Step description is missing"
            )
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="Step has description"
        )


class StepConfidenceRule(StepValidationRule):
    """Validates confidence values for reasoning steps."""

    def __init__(self):
        super().__init__("step_confidence", priority=2)

    def validate(self, data: ReasoningStep, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        if data.confidence < 0.0 or data.confidence > 1.0:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Confidence must be between 0.0 and 1.0"
            )
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="Confidence value is valid"
        )


class ResultCompletenessRule(ResultValidationRule):
    """Validates that reasoning results are complete."""

    def __init__(self):
        super().__init__("result_completeness", priority=1)

    def validate(self, data: ReasoningResult, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        if not data.steps:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="No reasoning steps found"
            )
        
        completed_steps = [step for step in data.steps if step.status.value == "completed"]
        if not completed_steps:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message="No completed reasoning steps found"
            )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message=f"Result has {len(completed_steps)} completed steps"
        )


class ConfidenceConsistencyRule(CrossValidationRule):
    """Validates consistency of confidence values across steps."""

    def __init__(self, threshold: float = 0.3):
        super().__init__("confidence_consistency", priority=3)
        self.threshold = threshold

    def validate(self, data: ReasoningResult, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        if len(data.steps) < 2:
            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message="Not enough steps for confidence consistency check"
            )
        
        confidences = [step.confidence for step in data.steps if step.status.value == "completed"]
        if len(confidences) < 2:
            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message="Not enough completed steps for confidence consistency check"
            )
        
        confidence_std = statistics.stdev(confidences)
        if confidence_std > self.threshold:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message=f"High confidence variance ({confidence_std:.3f}) across steps"
            )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="Confidence values are consistent across steps"
        )


class StatisticalValidationRule(CrossValidationRule):
    """Performs statistical validation on reasoning results."""

    def __init__(self):
        super().__init__("statistical_validation", priority=4)

    def validate(self, data: ReasoningResult, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        if not data.steps:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="No steps to validate statistically"
            )
        
        # Calculate statistics
        confidences = [step.confidence for step in data.steps if step.status.value == "completed"]
        if not confidences:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message="No completed steps for statistical analysis"
            )
        
        avg_confidence = statistics.mean(confidences)
        confidence_std = statistics.stdev(confidences) if len(confidences) > 1 else 0
        
        # Check for outliers (confidence values more than 2 standard deviations from mean)
        outliers = []
        for step in data.steps:
            if step.status.value == "completed":
                z_score = abs(step.confidence - avg_confidence) / confidence_std if confidence_std > 0 else 0
                if z_score > 2:
                    outliers.append(step.step_number)
        
        details = {
            "average_confidence": avg_confidence,
            "confidence_std": confidence_std,
            "outlier_steps": outliers,
            "total_steps": len(data.steps),
            "completed_steps": len(confidences)
        }
        
        if outliers:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message=f"Found {len(outliers)} outlier confidence values",
                details=details
            )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="Statistical validation passed",
            details=details
        )


class ValidationFramework:
    """Main validation framework for the reasoning system."""

    def __init__(self):
        self.rules: Dict[ValidationRuleType, List[ValidationRule]] = {
            ValidationRuleType.INPUT: [],
            ValidationRuleType.STEP: [],
            ValidationRuleType.RESULT: [],
            ValidationRuleType.CROSS_VALIDATION: []
        }
        self.context: Optional[ValidationContext] = None
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Set up default validation rules."""
        # Input validation rules
        self.add_rule(NonEmptyInputRule())
        self.add_rule(InputLengthRule())
        
        # Step validation rules
        self.add_rule(StepDescriptionRule())
        self.add_rule(StepConfidenceRule())
        
        # Result validation rules
        self.add_rule(ResultCompletenessRule())
        
        # Cross-validation rules
        self.add_rule(ConfidenceConsistencyRule())
        self.add_rule(StatisticalValidationRule())

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule."""
        if rule.enabled:
            self.rules[rule.rule_type].append(rule)
            # Sort by priority
            self.rules[rule.rule_type].sort()

    def remove_rule(self, rule_name: str, rule_type: ValidationRuleType) -> bool:
        """Remove a validation rule by name."""
        rules = self.rules[rule_type]
        for i, rule in enumerate(rules):
            if rule.name == rule_name:
                del rules[i]
                return True
        return False

    def enable_rule(self, rule_name: str, rule_type: ValidationRuleType) -> bool:
        """Enable a validation rule."""
        for rule in self.rules[rule_type]:
            if rule.name == rule_name:
                rule.enabled = True
                return True
        return False

    def disable_rule(self, rule_name: str, rule_type: ValidationRuleType) -> bool:
        """Disable a validation rule."""
        for rule in self.rules[rule_type]:
            if rule.name == rule_name:
                rule.enabled = False
                return True
        return False

    def set_context(self, context: ValidationContext) -> None:
        """Set the validation context."""
        self.context = context

    def validate_input(self, problem_statement: str) -> List[ValidationResult]:
        """Validate input problem statement."""
        results = []
        for rule in self.rules[ValidationRuleType.INPUT]:
            if rule.enabled:
                result = rule.validate(problem_statement, self._get_context_dict())
                results.append(result)
        return results

    def validate_step(self, step: ReasoningStep) -> List[ValidationResult]:
        """Validate a reasoning step."""
        results = []
        for rule in self.rules[ValidationRuleType.STEP]:
            if rule.enabled:
                result = rule.validate(step, self._get_context_dict())
                results.append(result)
        return results

    def validate_result(self, result: ReasoningResult) -> List[ValidationResult]:
        """Validate a reasoning result."""
        results = []
        
        # Apply result validation rules
        for rule in self.rules[ValidationRuleType.RESULT]:
            if rule.enabled:
                result_validation = rule.validate(result, self._get_context_dict())
                results.append(result_validation)
        
        # Apply cross-validation rules
        for rule in self.rules[ValidationRuleType.CROSS_VALIDATION]:
            if rule.enabled:
                cross_validation = rule.validate(result, self._get_context_dict())
                results.append(cross_validation)
        
        return results

    def validate_all(self, problem_statement: str, steps: List[ReasoningStep], 
                    result: ReasoningResult) -> Dict[str, List[ValidationResult]]:
        """Validate input, steps, and result comprehensively."""
        return {
            "input": self.validate_input(problem_statement),
            "steps": [self.validate_step(step) for step in steps],
            "result": self.validate_result(result)
        }

    def _get_context_dict(self) -> Optional[Dict[str, Any]]:
        """Get context as dictionary."""
        if self.context is None:
            return None
        
        return {
            "problem_statement": self.context.problem_statement,
            "reasoning_type": self.context.reasoning_type,
            "step_history": self.context.step_history,
            "metadata": self.context.metadata,
            "created_at": self.context.created_at
        }

    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Get a summary of validation results."""
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        invalid = total - valid
        
        by_level = {}
        for level in ValidationLevel:
            by_level[level.value] = sum(1 for r in results if r.level == level)
        
        return {
            "total": total,
            "valid": valid,
            "invalid": invalid,
            "validity_rate": valid / total if total > 0 else 0,
            "by_level": by_level
        }

    def get_failed_validations(self, results: List[ValidationResult]) -> List[ValidationResult]:
        """Get all failed validation results."""
        return [r for r in results if not r.is_valid]

    def get_critical_validations(self, results: List[ValidationResult]) -> List[ValidationResult]:
        """Get all critical validation results."""
        return [r for r in results if r.level == ValidationLevel.CRITICAL]


# Domain-specific validation plugins
class DomainValidationPlugin(ABC):
    """Abstract base class for domain-specific validation plugins."""

    def __init__(self, domain: str):
        self.domain = domain
        self.rules: List[ValidationRule] = []

    @abstractmethod
    def setup_rules(self) -> None:
        """Set up domain-specific validation rules."""
        pass

    def get_rules(self) -> List[ValidationRule]:
        """Get all rules for this domain."""
        return self.rules.copy()

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a rule to this domain."""
        self.rules.append(rule)


class MathematicalValidationPlugin(DomainValidationPlugin):
    """Validation plugin for mathematical reasoning."""

    def __init__(self):
        super().__init__("mathematical")
        self.setup_rules()

    def setup_rules(self) -> None:
        """Set up mathematical validation rules."""
        self.add_rule(MathematicalExpressionRule())
        self.add_rule(NumericalRangeRule())


class MathematicalExpressionRule(StepValidationRule):
    """Validates mathematical expressions in reasoning steps."""

    def __init__(self):
        super().__init__("mathematical_expression", priority=5)

    def validate(self, data: ReasoningStep, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        # Simple check for mathematical symbols in reasoning
        math_symbols = r'[\+\-\*/=\^√∫∑∏∞≤≥≠≈]'
        if re.search(math_symbols, data.reasoning):
            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message="Mathematical expressions detected"
            )
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="No mathematical expressions detected"
        )


class NumericalRangeRule(StepValidationRule):
    """Validates numerical values are within reasonable ranges."""

    def __init__(self):
        super().__init__("numerical_range", priority=6)

    def validate(self, data: ReasoningStep, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        # Extract numbers from reasoning text
        numbers = re.findall(r'-?\d+\.?\d*', data.reasoning)
        if not numbers:
            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.INFO,
                message="No numerical values found"
            )
        
        # Check for extreme values
        extreme_values = []
        for num_str in numbers:
            try:
                num = float(num_str)
                if abs(num) > 1e10:  # Very large numbers
                    extreme_values.append(num)
            except ValueError:
                continue
        
        if extreme_values:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message=f"Found {len(extreme_values)} extreme numerical values",
                details={"extreme_values": extreme_values}
            )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="All numerical values are within reasonable range"
        ) 