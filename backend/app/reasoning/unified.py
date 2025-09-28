"""
Unified Reasoning System

This module provides a consolidated interface that combines:
- Phase 1: Core reasoning components (base classes, validation, parsing, formatting)
- Phase 2: Basic reasoning engines (mathematical, logical, causal)
- Phase 3: Advanced reasoning strategies (CoT, ToT, prompt engineering)

The unified system provides a single entry point for all reasoning capabilities.
"""

from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone

# Phase 1: Core components
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

# Phase 2: Basic reasoning engines
from .engines.mathematical import MathematicalReasoningEngine
from .engines.logical import LogicalReasoningEngine
from .engines.causal import CausalReasoningEngine

# Phase 3: Advanced reasoning strategies
from .strategies.chain_of_thought import ChainOfThoughtStrategy
from .strategies.tree_of_thoughts import TreeOfThoughtsStrategy
from .strategies.prompt_engineering import PromptEngineeringFramework


class ReasoningMode(Enum):
    """Enumeration of available reasoning modes."""
    MATHEMATICAL = "mathematical"
    LOGICAL = "logical"
    CAUSAL = "causal"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    HYBRID = "hybrid"
    AUTO = "auto"


@dataclass
class UnifiedReasoningConfig:
    """Configuration for the unified reasoning system."""
    
    # Core configuration
    default_mode: ReasoningMode = ReasoningMode.AUTO
    enable_validation: bool = True
    enable_parsing: bool = True
    enable_formatting: bool = True
    
    # Engine-specific configurations
    mathematical_config: Optional[Dict[str, Any]] = None
    logical_config: Optional[Dict[str, Any]] = None
    causal_config: Optional[Dict[str, Any]] = None
    
    # Strategy-specific configurations
    cot_config: Optional[Dict[str, Any]] = None
    tot_config: Optional[Dict[str, Any]] = None
    prompt_engineering_config: Optional[Dict[str, Any]] = None
    
    # Output configuration
    output_format: OutputFormat = OutputFormat.STRUCTURED
    include_metadata: bool = True
    include_validation_results: bool = True
    
    # Performance configuration
    max_iterations: int = 10
    timeout_seconds: int = 300
    enable_caching: bool = True


class UnifiedReasoningSystem:
    """
    Unified reasoning system that consolidates all three phases of reasoning.
    
    This class provides a single interface to access:
    - Core reasoning components (Phase 1)
    - Basic reasoning engines (Phase 2) 
    - Advanced reasoning strategies (Phase 3)
    """
    
    def __init__(self, config: Optional[UnifiedReasoningConfig] = None):
        """
        Initialize the unified reasoning system.
        
        Args:
            config: Configuration for the unified system
        """
        self.config = config or UnifiedReasoningConfig()
        
        # Initialize core components (Phase 1)
        self._init_core_components()
        
        # Initialize reasoning engines (Phase 2)
        self._init_reasoning_engines()
        
        # Initialize reasoning strategies (Phase 3)
        self._init_reasoning_strategies()
        
        # Initialize factory components
        self._init_factories()
    
    def _init_core_components(self):
        """Initialize Phase 1 core components."""
        self.validation_framework = ValidationFramework()
        self.parser_factory = ParserFactory()
        self.formatter_factory = FormatterFactory()
        
        # Add domain-specific validation plugins
        self.validation_framework.add_plugin(MathematicalValidationPlugin())
        self.validation_framework.add_plugin(DomainValidationPlugin())
    
    def _init_reasoning_engines(self):
        """Initialize Phase 2 reasoning engines."""
        self.engines = {
            ReasoningMode.MATHEMATICAL: MathematicalReasoningEngine(
                config=self.config.mathematical_config or {}
            ),
            ReasoningMode.LOGICAL: LogicalReasoningEngine(
                config=self.config.logical_config or {}
            ),
            ReasoningMode.CAUSAL: CausalReasoningEngine(
                config=self.config.causal_config or {}
            )
        }
    
    def _init_reasoning_strategies(self):
        """Initialize Phase 3 reasoning strategies."""
        self.strategies = {
            ReasoningMode.CHAIN_OF_THOUGHT: ChainOfThoughtStrategy(
                config=self.config.cot_config or {}
            ),
            ReasoningMode.TREE_OF_THOUGHTS: TreeOfThoughtsStrategy(
                config=self.config.tot_config or {}
            )
        }
        
        # Initialize prompt engineering framework
        self.prompt_engineering = PromptEngineeringFramework(
            config=self.config.prompt_engineering_config or {}
        )
    
    def _init_factories(self):
        """Initialize factory components for dynamic creation."""
        self.reasoner_factory = ReasonerFactory(self)
    
    async def reason(
        self,
        problem_statement: str,
        mode: Optional[ReasoningMode] = None,
        **kwargs
    ) -> ReasoningResult:
        """
        Perform reasoning on the given problem statement.
        
        Args:
            problem_statement: The problem to solve
            mode: Specific reasoning mode to use (defaults to auto-selection)
            **kwargs: Additional arguments for the reasoning process
            
        Returns:
            ReasoningResult containing the reasoning steps and final answer
        """
        # Determine reasoning mode
        if mode is None:
            mode = self._auto_select_mode(problem_statement)
        
        # Validate input if enabled
        if self.config.enable_validation:
            validation_result = self._validate_input(problem_statement)
            if not validation_result.is_valid:
                return self._create_error_result(problem_statement, validation_result)
        
        # Parse problem statement if enabled
        if self.config.enable_parsing:
            parsed_problem = self._parse_problem(problem_statement)
        else:
            parsed_problem = {"original": problem_statement}
        
        # Select appropriate reasoner
        reasoner = self._get_reasoner(mode)
        
        # Perform reasoning
        try:
            result = await reasoner.reason(problem_statement, **kwargs)
            
            # Format output if enabled
            if self.config.enable_formatting:
                result = self._format_result(result)
            
            return result
            
        except Exception as e:
            return self._create_error_result(
                problem_statement,
                ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Reasoning failed: {str(e)}"
                )
            )
    
    def _auto_select_mode(self, problem_statement: str) -> ReasoningMode:
        """
        Automatically select the best reasoning mode for the problem.
        
        Args:
            problem_statement: The problem to analyze
            
        Returns:
            Selected reasoning mode
        """
        problem_lower = problem_statement.lower()
        
        # Check for mathematical indicators
        math_indicators = ['calculate', 'solve', 'equation', 'formula', 'number', 'math']
        if any(indicator in problem_lower for indicator in math_indicators):
            return ReasoningMode.MATHEMATICAL
        
        # Check for logical indicators
        logic_indicators = ['if', 'then', 'therefore', 'because', 'implies', 'logical']
        if any(indicator in problem_lower for indicator in logic_indicators):
            return ReasoningMode.LOGICAL
        
        # Check for causal indicators
        causal_indicators = ['cause', 'effect', 'why', 'how', 'result', 'consequence']
        if any(indicator in problem_lower for indicator in causal_indicators):
            return ReasoningMode.CAUSAL
        
        # Default to chain of thought for complex problems
        if len(problem_statement.split()) > 20:
            return ReasoningMode.CHAIN_OF_THOUGHT
        
        # Default to mathematical for shorter problems
        return ReasoningMode.MATHEMATICAL
    
    def _validate_input(self, problem_statement: str) -> ValidationResult:
        """Validate the input problem statement."""
        return self.validation_framework.validate(
            problem_statement,
            ValidationContext(
                problem_type="general",
                validation_level=ValidationLevel.INFO
            )
        )
    
    def _parse_problem(self, problem_statement: str) -> Dict[str, Any]:
        """Parse the problem statement."""
        parser = self.parser_factory.create_parser("problem_statement")
        return parser.parse(problem_statement)
    
    def _get_reasoner(self, mode: ReasoningMode) -> BaseReasoner:
        """Get the appropriate reasoner for the given mode."""
        if mode in self.engines:
            return self.engines[mode]
        elif mode in self.strategies:
            return self.strategies[mode]
        else:
            # Default to chain of thought
            return self.strategies[ReasoningMode.CHAIN_OF_THOUGHT]
    
    def _format_result(self, result: ReasoningResult) -> ReasoningResult:
        """Format the reasoning result according to configuration."""
        formatter = self.formatter_factory.create_formatter(
            self.config.output_format.value
        )
        
        # Apply formatting while preserving the original result structure
        formatted_steps = []
        for step in result.steps:
            formatted_step = ReasoningStep(
                step_number=step.step_number,
                description=step.description,
                reasoning=step.reasoning,
                result=step.result,
                status=step.status,
                metadata=step.metadata.copy()
            )
            
            # Add formatting metadata
            if self.config.include_metadata:
                formatted_step.metadata.update({
                    "formatted_at": datetime.now(timezone.utc).isoformat(),
                    "output_format": self.config.output_format.value
                })
            
            formatted_steps.append(formatted_step)
        
        # Create new result with formatted steps
        formatted_result = ReasoningResult(
            problem_statement=result.problem_statement,
            steps=formatted_steps,
            final_answer=result.final_answer,
            reasoning_type=result.reasoning_type,
            validation_results=result.validation_results if self.config.include_validation_results else [],
            metadata=result.metadata.copy(),
            created_at=result.created_at,
            completed_at=result.completed_at
        )
        
        return formatted_result
    
    def _create_error_result(
        self,
        problem_statement: str,
        validation_result: ValidationResult
    ) -> ReasoningResult:
        """Create an error result."""
        return ReasoningResult(
            problem_statement=problem_statement,
            steps=[],
            final_answer="",
            reasoning_type=ReasoningType.UNKNOWN,
            validation_results=[validation_result],
            metadata={"error": True},
            created_at=datetime.now(timezone.utc)
        )
    
    def get_available_modes(self) -> List[ReasoningMode]:
        """Get list of available reasoning modes."""
        return list(ReasoningMode)
    
    def get_engine_info(self, mode: ReasoningMode) -> Dict[str, Any]:
        """Get information about a specific reasoning engine."""
        if mode in self.engines:
            engine = self.engines[mode]
            return {
                "name": engine.name,
                "type": engine.reasoning_type.value,
                "can_handle": "general" if hasattr(engine, 'can_handle') else "unknown"
            }
        elif mode in self.strategies:
            strategy = self.strategies[mode]
            return {
                "name": strategy.name,
                "type": strategy.reasoning_type.value,
                "can_handle": "general" if hasattr(strategy, 'can_handle') else "unknown"
            }
        else:
            return {"error": f"Unknown mode: {mode}"}
    
    def configure_mode(self, mode: ReasoningMode, config: Dict[str, Any]) -> None:
        """Configure a specific reasoning mode."""
        if mode in self.engines:
            self.engines[mode].config.update(config)
        elif mode in self.strategies:
            self.strategies[mode].config.update(config)
        else:
            raise ValueError(f"Cannot configure unknown mode: {mode}")


class ReasonerFactory:
    """Factory for creating reasoners dynamically."""
    
    def __init__(self, unified_system: UnifiedReasoningSystem):
        self.unified_system = unified_system
    
    def create_reasoner(
        self,
        mode: ReasoningMode,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> BaseReasoner:
        """
        Create a reasoner with custom configuration.
        
        Args:
            mode: The reasoning mode to create
            custom_config: Custom configuration for the reasoner
            
        Returns:
            Configured reasoner instance
        """
        if mode in self.unified_system.engines:
            reasoner_class = type(self.unified_system.engines[mode])
            config = custom_config or {}
            return reasoner_class(config=config)
        elif mode in self.unified_system.strategies:
            reasoner_class = type(self.unified_system.strategies[mode])
            config = custom_config or {}
            return reasoner_class(config=config)
        else:
            raise ValueError(f"Cannot create reasoner for unknown mode: {mode}")
    
    def create_hybrid_reasoner(
        self,
        modes: List[ReasoningMode],
        config: Optional[Dict[str, Any]] = None
    ) -> 'HybridReasoner':
        """
        Create a hybrid reasoner that combines multiple modes.
        
        Args:
            modes: List of reasoning modes to combine
            config: Configuration for the hybrid reasoner
            
        Returns:
            Hybrid reasoner instance
        """
        return HybridReasoner(modes, config or {}, self.unified_system)


class HybridReasoner(BaseReasoner):
    """Reasoner that combines multiple reasoning modes."""
    
    def __init__(
        self,
        modes: List[ReasoningMode],
        config: Dict[str, Any],
        unified_system: UnifiedReasoningSystem
    ):
        super().__init__("HybridReasoner", ReasoningType.HYBRID)
        self.modes = modes
        self.config = config
        self.unified_system = unified_system
        self.reasoners = [
            self.unified_system._get_reasoner(mode) for mode in modes
        ]
    
    async def reason(self, problem_statement: str, **kwargs) -> ReasoningResult:
        """Perform hybrid reasoning using multiple modes."""
        results = []
        
        for reasoner in self.reasoners:
            try:
                result = await reasoner.reason(problem_statement, **kwargs)
                results.append(result)
            except Exception as e:
                # Log error but continue with other reasoners
                continue
        
        # Combine results (simplified implementation)
        if results:
            # Use the first successful result for now
            # In a more sophisticated implementation, you might combine insights
            return results[0]
        else:
            return self.unified_system._create_error_result(
                problem_statement,
                ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="All reasoning modes failed"
                )
            )
    
    def can_handle(self, problem_statement: str) -> bool:
        """Check if any of the hybrid reasoners can handle the problem."""
        return any(
            reasoner.can_handle(problem_statement) for reasoner in self.reasoners
        )


# Convenience functions for easy access
def create_unified_reasoner(
    config: Optional[UnifiedReasoningConfig] = None
) -> UnifiedReasoningSystem:
    """
    Create a unified reasoning system with optional configuration.
    
    Args:
        config: Optional configuration for the system
        
    Returns:
        Configured UnifiedReasoningSystem instance
    """
    return UnifiedReasoningSystem(config)


def quick_reason(
    problem_statement: str,
    mode: Optional[ReasoningMode] = None,
    config: Optional[UnifiedReasoningConfig] = None
) -> ReasoningResult:
    """
    Quick reasoning function for simple use cases.
    
    Args:
        problem_statement: The problem to solve
        mode: Optional reasoning mode
        config: Optional system configuration
        
    Returns:
        ReasoningResult
    """
    system = create_unified_reasoner(config)
    import asyncio
    return asyncio.run(system.reason(problem_statement, mode))

