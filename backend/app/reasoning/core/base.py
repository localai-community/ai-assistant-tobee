"""
Base classes and interfaces for the reasoning system.

This module provides the foundational classes and interfaces that all reasoning
engines and components will inherit from and implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from datetime import datetime, timezone
import uuid
import json


class ReasoningType(Enum):
    """Enumeration of reasoning types."""
    MATHEMATICAL = "mathematical"
    LOGICAL = "logical"
    CAUSAL = "causal"
    HYBRID = "hybrid"


class StepStatus(Enum):
    """Enumeration of step statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ValidationLevel(Enum):
    """Enumeration of validation levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    level: ValidationLevel
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReasoningStep:
    """Represents a single reasoning step."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step_number: int = 0
    description: str = ""
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    reasoning: str = ""
    confidence: float = 0.0
    status: StepStatus = StepStatus.PENDING
    validation_results: List[ValidationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "step_number": self.step_number,
            "description": self.description,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "status": self.status.value,
            "validation_results": [
                {
                    "is_valid": vr.is_valid,
                    "level": vr.level.value,
                    "message": vr.message,
                    "details": vr.details,
                    "timestamp": vr.timestamp.isoformat()
                }
                for vr in self.validation_results
            ],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReasoningStep":
        """Create from dictionary representation."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            step_number=data.get("step_number", 0),
            description=data.get("description", ""),
            input_data=data.get("input_data"),
            output_data=data.get("output_data"),
            reasoning=data.get("reasoning", ""),
            confidence=data.get("confidence", 0.0),
            status=StepStatus(data.get("status", "pending")),
            validation_results=[
                ValidationResult(
                    is_valid=vr["is_valid"],
                    level=ValidationLevel(vr["level"]),
                    message=vr["message"],
                    details=vr.get("details"),
                    timestamp=datetime.fromisoformat(vr["timestamp"])
                )
                for vr in data.get("validation_results", [])
            ],
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
        )


@dataclass
class ReasoningResult:
    """Container for reasoning results with metadata."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    problem_statement: str = ""
    steps: List[ReasoningStep] = field(default_factory=list)
    final_answer: Optional[Any] = None
    confidence: float = 0.0
    reasoning_type: ReasoningType = ReasoningType.HYBRID
    validation_results: List[ValidationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None

    def add_step(self, step: ReasoningStep) -> None:
        """Add a reasoning step to the result."""
        step.step_number = len(self.steps) + 1
        self.steps.append(step)

    def get_step_by_id(self, step_id: str) -> Optional[ReasoningStep]:
        """Get a step by its ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_steps_by_status(self, status: StepStatus) -> List[ReasoningStep]:
        """Get all steps with a specific status."""
        return [step for step in self.steps if step.status == status]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "problem_statement": self.problem_statement,
            "steps": [step.to_dict() for step in self.steps],
            "final_answer": self.final_answer,
            "confidence": self.confidence,
            "reasoning_type": self.reasoning_type.value,
            "validation_results": [
                {
                    "is_valid": vr.is_valid,
                    "level": vr.level.value,
                    "message": vr.message,
                    "details": vr.details,
                    "timestamp": vr.timestamp.isoformat()
                }
                for vr in self.validation_results
            ],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_time": self.execution_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReasoningResult":
        """Create from dictionary representation."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            problem_statement=data.get("problem_statement", ""),
            steps=[ReasoningStep.from_dict(step_data) for step_data in data.get("steps", [])],
            final_answer=data.get("final_answer"),
            confidence=data.get("confidence", 0.0),
            reasoning_type=ReasoningType(data.get("reasoning_type", "hybrid")),
            validation_results=[
                ValidationResult(
                    is_valid=vr["is_valid"],
                    level=ValidationLevel(vr["level"]),
                    message=vr["message"],
                    details=vr.get("details"),
                    timestamp=datetime.fromisoformat(vr["timestamp"])
                )
                for vr in data.get("validation_results", [])
            ],
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            execution_time=data.get("execution_time")
        )


T = TypeVar('T', bound=ReasoningResult)


class BaseReasoner(ABC, Generic[T]):
    """Abstract base class for all reasoning engines."""

    def __init__(self, name: str, reasoning_type: ReasoningType):
        self.name = name
        self.reasoning_type = reasoning_type
        self.config: Dict[str, Any] = {}
        self.validation_rules: List[Any] = []

    @abstractmethod
    async def reason(self, problem_statement: str, **kwargs) -> T:
        """
        Perform reasoning on the given problem statement.
        
        Args:
            problem_statement: The problem to solve
            **kwargs: Additional arguments for the reasoning process
            
        Returns:
            ReasoningResult containing the reasoning steps and final answer
        """
        pass

    @abstractmethod
    def can_handle(self, problem_statement: str) -> bool:
        """
        Check if this reasoner can handle the given problem.
        
        Args:
            problem_statement: The problem to check
            
        Returns:
            True if the reasoner can handle this problem
        """
        pass

    def validate_input(self, problem_statement: str) -> ValidationResult:
        """
        Validate the input problem statement.
        
        Args:
            problem_statement: The problem to validate
            
        Returns:
            ValidationResult indicating if the input is valid
        """
        if not problem_statement or not problem_statement.strip():
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Problem statement cannot be empty"
            )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="Input validation passed"
        )

    def validate_step(self, step: ReasoningStep) -> ValidationResult:
        """
        Validate a reasoning step.
        
        Args:
            step: The step to validate
            
        Returns:
            ValidationResult indicating if the step is valid
        """
        if not step.description:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message="Step description is missing"
            )
        
        if step.confidence < 0.0 or step.confidence > 1.0:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Confidence must be between 0.0 and 1.0"
            )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="Step validation passed"
        )

    def validate_result(self, result: T) -> ValidationResult:
        """
        Validate a reasoning result.
        
        Args:
            result: The result to validate
            
        Returns:
            ValidationResult indicating if the result is valid
        """
        if not result.steps:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="No reasoning steps found"
            )
        
        if result.confidence < 0.0 or result.confidence > 1.0:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Overall confidence must be between 0.0 and 1.0"
            )
        
        return ValidationResult(
            is_valid=True,
            level=ValidationLevel.INFO,
            message="Result validation passed"
        )

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        return self.config.copy()

    def set_config(self, config: Dict[str, Any]) -> None:
        """Set the configuration."""
        self.config.update(config)

    def add_validation_rule(self, rule: Any) -> None:
        """Add a validation rule."""
        self.validation_rules.append(rule)


class ReasoningChain(ABC):
    """Abstract base class for reasoning chains."""

    def __init__(self, name: str):
        self.name = name
        self.steps: List[ReasoningStep] = []
        self.config: Dict[str, Any] = {}

    @abstractmethod
    async def execute(self, problem_statement: str, **kwargs) -> ReasoningResult:
        """
        Execute the reasoning chain.
        
        Args:
            problem_statement: The problem to solve
            **kwargs: Additional arguments
            
        Returns:
            ReasoningResult containing the chain execution results
        """
        pass

    def add_step(self, step: ReasoningStep) -> None:
        """Add a step to the chain."""
        step.step_number = len(self.steps) + 1
        self.steps.append(step)

    def get_step(self, step_number: int) -> Optional[ReasoningStep]:
        """Get a step by number."""
        if 1 <= step_number <= len(self.steps):
            return self.steps[step_number - 1]
        return None

    def remove_step(self, step_number: int) -> bool:
        """Remove a step by number."""
        if 1 <= step_number <= len(self.steps):
            del self.steps[step_number - 1]
            # Renumber remaining steps
            for i, step in enumerate(self.steps, 1):
                step.step_number = i
            return True
        return False

    def clear_steps(self) -> None:
        """Clear all steps."""
        self.steps.clear()

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        return self.config.copy()

    def set_config(self, config: Dict[str, Any]) -> None:
        """Set the configuration."""
        self.config.update(config) 