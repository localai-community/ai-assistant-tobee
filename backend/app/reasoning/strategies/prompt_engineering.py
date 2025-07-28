"""
Prompt Engineering Framework for reasoning systems.

This module provides a comprehensive prompt engineering framework with:
- Prompt template management
- Context-aware prompt generation
- Prompt optimization tools
- A/B testing framework
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid

from ..core.base import (
    BaseReasoner, ReasoningResult, ReasoningStep, StepStatus,
    ValidationResult, ValidationLevel, ReasoningType
)
from ..utils.parsers import parse_problem_statement
from ..utils.formatters import format_reasoning_output


class PromptType(Enum):
    """Enumeration of prompt types."""
    REASONING = "reasoning"
    VALIDATION = "validation"
    REFINEMENT = "refinement"
    EVALUATION = "evaluation"
    GENERAL = "general"


class OptimizationStrategy(Enum):
    """Enumeration of optimization strategies."""
    GRADIENT_FREE = "gradient_free"
    GENETIC = "genetic"
    BAYESIAN = "bayesian"
    RANDOM = "random"


@dataclass
class PromptTemplate:
    """Represents a prompt template."""
    template_id: str
    name: str
    description: str
    template: str
    prompt_type: PromptType
    variables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    performance_metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "template": self.template,
            "prompt_type": self.prompt_type.value,
            "variables": self.variables,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "performance_metrics": self.performance_metrics
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptTemplate":
        """Create from dictionary representation."""
        return cls(
            template_id=data["template_id"],
            name=data["name"],
            description=data["description"],
            template=data["template"],
            prompt_type=PromptType(data["prompt_type"]),
            variables=data.get("variables", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            performance_metrics=data.get("performance_metrics", {})
        )


@dataclass
class PromptContext:
    """Represents context for prompt generation."""
    problem_statement: str
    problem_type: str
    reasoning_type: ReasoningType
    previous_steps: List[ReasoningStep] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    system_context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptResult:
    """Represents the result of prompt generation."""
    prompt_id: str
    generated_prompt: str
    template_used: PromptTemplate
    context: PromptContext
    performance_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ABTestConfig:
    """Configuration for A/B testing."""
    test_id: str
    template_a: PromptTemplate
    template_b: PromptTemplate
    traffic_split: float = 0.5  # Percentage of traffic to template B
    duration_days: int = 7
    success_metric: str = "accuracy"
    min_sample_size: int = 100


@dataclass
class ABTestResult:
    """Result of an A/B test."""
    test_id: str
    template_a_performance: Dict[str, float]
    template_b_performance: Dict[str, float]
    winner: Optional[str] = None
    confidence_level: float = 0.0
    p_value: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptEngineeringConfig:
    """Configuration for the prompt engineering framework."""
    enable_optimization: bool = True
    enable_ab_testing: bool = True
    enable_context_injection: bool = True
    max_templates_per_type: int = 10
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.GRADIENT_FREE
    performance_threshold: float = 0.7
    cache_size: int = 100


class PromptEngineeringFramework:
    """
    Comprehensive prompt engineering framework.
    
    This framework provides:
    - Template management system
    - Context-aware prompt generation
    - Prompt optimization tools
    - A/B testing framework
    """

    def __init__(self, config: Optional[PromptEngineeringConfig] = None):
        self.config = config or PromptEngineeringConfig()
        self.templates: Dict[str, PromptTemplate] = {}
        self.context_cache: Dict[str, PromptContext] = {}
        self.ab_tests: Dict[str, ABTestConfig] = {}
        self.ab_results: Dict[str, ABTestResult] = {}
        self.performance_history: List[Tuple[str, float, datetime]] = []
        
        # Initialize with default templates
        self._initialize_default_templates()

    def _initialize_default_templates(self) -> None:
        """Initialize the framework with default templates."""
        default_templates = [
            PromptTemplate(
                template_id="reasoning_basic",
                name="Basic Reasoning Template",
                description="Basic template for step-by-step reasoning",
                template="""You are a helpful AI assistant that solves problems step by step.

Problem: {problem_statement}

Please solve this problem step by step. For each step:
1. Think about what needs to be done
2. Take an action or make a calculation
3. Observe the result
4. Continue to the next step

Let's solve this step by step:""",
                prompt_type=PromptType.REASONING,
                variables=["problem_statement"]
            ),
            PromptTemplate(
                template_id="reasoning_advanced",
                name="Advanced Reasoning Template",
                description="Advanced template with detailed reasoning",
                template="""You are an expert problem solver with deep analytical skills.

Problem: {problem_statement}

Context: {context}

Please solve this problem using the following approach:
1. Analyze the problem structure and identify key components
2. Break down the problem into manageable sub-problems
3. Solve each sub-problem systematically
4. Synthesize the results into a final answer
5. Validate your solution

Previous steps: {previous_steps}

Let's solve this systematically:""",
                prompt_type=PromptType.REASONING,
                variables=["problem_statement", "context", "previous_steps"]
            ),
            PromptTemplate(
                template_id="validation_basic",
                name="Basic Validation Template",
                description="Basic template for validating reasoning steps",
                template="""Please validate the following reasoning step:

Step: {step_description}
Reasoning: {reasoning}
Result: {result}

Check for:
1. Logical consistency
2. Mathematical accuracy
3. Completeness of reasoning
4. Relevance to the problem

Validation:""",
                prompt_type=PromptType.VALIDATION,
                variables=["step_description", "reasoning", "result"]
            ),
            PromptTemplate(
                template_id="refinement_basic",
                name="Basic Refinement Template",
                description="Basic template for refining reasoning steps",
                template="""The following reasoning step needs improvement:

Original step: {original_step}
Issues identified: {issues}

Please provide an improved version that addresses these issues while maintaining the core logic.

Improved step:""",
                prompt_type=PromptType.REFINEMENT,
                variables=["original_step", "issues"]
            )
        ]
        
        for template in default_templates:
            self.add_template(template)

    def add_template(self, template: PromptTemplate) -> bool:
        """Add a prompt template to the framework."""
        try:
            # Validate template
            if not template.template_id or not template.template:
                return False
            
            # Check if template already exists
            if template.template_id in self.templates:
                # Update existing template
                template.updated_at = datetime.now(timezone.utc)
            
            self.templates[template.template_id] = template
            return True
            
        except Exception as e:
            return False

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)

    def get_templates_by_type(self, prompt_type: PromptType) -> List[PromptTemplate]:
        """Get all templates of a specific type."""
        return [t for t in self.templates.values() if t.prompt_type == prompt_type]

    def remove_template(self, template_id: str) -> bool:
        """Remove a template from the framework."""
        if template_id in self.templates:
            del self.templates[template_id]
            return True
        return False

    def generate_prompt(self, context: PromptContext, 
                       template_id: Optional[str] = None) -> Optional[PromptResult]:
        """Generate a prompt based on context and template."""
        try:
            # Select template
            template = self._select_template(context, template_id)
            if not template:
                return None
            
            # Generate prompt
            generated_prompt = self._fill_template(template, context)
            if not generated_prompt:
                return None
            
            # Create result
            result = PromptResult(
                prompt_id=str(uuid.uuid4()),
                generated_prompt=generated_prompt,
                template_used=template,
                context=context
            )
            
            return result
            
        except Exception as e:
            return None

    def _select_template(self, context: PromptContext, 
                        template_id: Optional[str] = None) -> Optional[PromptTemplate]:
        """Select the best template for the given context."""
        if template_id:
            return self.get_template(template_id)
        
        # Select based on context
        available_templates = self.get_templates_by_type(PromptType.REASONING)
        
        if not available_templates:
            return None
        
        # Simple selection based on problem type
        if context.problem_type == "mathematical":
            # Prefer templates with mathematical context
            for template in available_templates:
                if "mathematical" in template.name.lower():
                    return template
        
        # Default to first available template
        return available_templates[0]

    def _fill_template(self, template: PromptTemplate, 
                      context: PromptContext) -> Optional[str]:
        """Fill a template with context data."""
        try:
            filled_prompt = template.template
            
            # Replace variables
            variables = {
                "problem_statement": context.problem_statement,
                "problem_type": context.problem_type,
                "reasoning_type": context.reasoning_type.value,
                "context": self._format_context(context.system_context),
                "previous_steps": self._format_previous_steps(context.previous_steps),
                "user_preferences": self._format_user_preferences(context.user_preferences)
            }
            
            # Replace variables in template
            for var_name, var_value in variables.items():
                placeholder = "{" + var_name + "}"
                if placeholder in filled_prompt:
                    filled_prompt = filled_prompt.replace(placeholder, str(var_value))
            
            return filled_prompt
            
        except Exception as e:
            return None

    def _format_context(self, system_context: Dict[str, Any]) -> str:
        """Format system context for template insertion."""
        if not system_context:
            return "No additional context provided."
        
        context_parts = []
        for key, value in system_context.items():
            context_parts.append(f"{key}: {value}")
        
        return "; ".join(context_parts)

    def _format_previous_steps(self, previous_steps: List[ReasoningStep]) -> str:
        """Format previous steps for template insertion."""
        if not previous_steps:
            return "No previous steps."
        
        step_descriptions = []
        for step in previous_steps[-3:]:  # Last 3 steps
            step_descriptions.append(f"Step {step.step_number}: {step.description}")
        
        return "; ".join(step_descriptions)

    def _format_user_preferences(self, user_preferences: Dict[str, Any]) -> str:
        """Format user preferences for template insertion."""
        if not user_preferences:
            return "No specific preferences."
        
        preference_parts = []
        for key, value in user_preferences.items():
            preference_parts.append(f"{key}: {value}")
        
        return "; ".join(preference_parts)

    def optimize_template(self, template_id: str, 
                        performance_data: List[Tuple[str, float]]) -> Optional[PromptTemplate]:
        """Optimize a template based on performance data."""
        try:
            template = self.get_template(template_id)
            if not template:
                return None
            
            # Analyze performance data
            avg_performance = sum(score for _, score in performance_data) / len(performance_data)
            
            # Update template performance metrics
            template.performance_metrics["average_score"] = avg_performance
            template.performance_metrics["total_tests"] = len(performance_data)
            
            # Apply optimization based on strategy
            if self.config.optimization_strategy == OptimizationStrategy.GRADIENT_FREE:
                optimized_template = self._gradient_free_optimization(template, performance_data)
            elif self.config.optimization_strategy == OptimizationStrategy.GENETIC:
                optimized_template = self._genetic_optimization(template, performance_data)
            else:
                optimized_template = template
            
            return optimized_template
            
        except Exception as e:
            return None

    def _gradient_free_optimization(self, template: PromptTemplate, 
                                  performance_data: List[Tuple[str, float]]) -> PromptTemplate:
        """Apply gradient-free optimization to a template."""
        # Simple optimization: improve clarity and structure
        optimized_template = PromptTemplate(
            template_id=f"{template.template_id}_optimized",
            name=f"{template.name} (Optimized)",
            description=f"Optimized version of {template.name}",
            template=self._improve_template_text(template.template),
            prompt_type=template.prompt_type,
            variables=template.variables,
            metadata={**template.metadata, "optimized": True}
        )
        
        return optimized_template

    def _genetic_optimization(self, template: PromptTemplate, 
                            performance_data: List[Tuple[str, float]]) -> PromptTemplate:
        """Apply genetic optimization to a template."""
        # Simple genetic optimization: mutate template text
        mutated_template = PromptTemplate(
            template_id=f"{template.template_id}_genetic",
            name=f"{template.name} (Genetic)",
            description=f"Genetically optimized version of {template.name}",
            template=self._mutate_template_text(template.template),
            prompt_type=template.prompt_type,
            variables=template.variables,
            metadata={**template.metadata, "genetic_optimized": True}
        )
        
        return mutated_template

    def _improve_template_text(self, template_text: str) -> str:
        """Improve template text for better performance."""
        improvements = [
            ("You are", "You are an expert AI assistant that"),
            ("Please solve", "Please carefully solve"),
            ("step by step", "step by step with clear reasoning"),
            ("Let's solve", "Let's solve this systematically")
        ]
        
        improved_text = template_text
        for old, new in improvements:
            improved_text = improved_text.replace(old, new)
        
        return improved_text

    def _mutate_template_text(self, template_text: str) -> str:
        """Apply genetic mutation to template text."""
        mutations = [
            ("You are", "You are a highly skilled"),
            ("Please solve", "Please systematically solve"),
            ("step by step", "step by step with detailed explanations"),
            ("Let's solve", "Let's approach this methodically")
        ]
        
        mutated_text = template_text
        for old, new in mutations:
            if old in mutated_text:
                mutated_text = mutated_text.replace(old, new)
                break  # Apply only one mutation
        
        return mutated_text

    def create_ab_test(self, template_a_id: str, template_b_id: str, 
                      config: Optional[ABTestConfig] = None) -> Optional[str]:
        """Create an A/B test between two templates."""
        try:
            template_a = self.get_template(template_a_id)
            template_b = self.get_template(template_b_id)
            
            if not template_a or not template_b:
                return None
            
            test_config = config or ABTestConfig(
                test_id=str(uuid.uuid4()),
                template_a=template_a,
                template_b=template_b
            )
            
            self.ab_tests[test_config.test_id] = test_config
            return test_config.test_id
            
        except Exception as e:
            return None

    def record_ab_test_result(self, test_id: str, template_id: str, 
                            performance_score: float) -> bool:
        """Record a result for an A/B test."""
        try:
            if test_id not in self.ab_tests:
                return False
            
            test_config = self.ab_tests[test_id]
            
            # Initialize result if not exists
            if test_id not in self.ab_results:
                self.ab_results[test_id] = ABTestResult(
                    test_id=test_id,
                    template_a_performance={"scores": [], "count": 0},
                    template_b_performance={"scores": [], "count": 0}
                )
            
            result = self.ab_results[test_id]
            
            # Record score
            if template_id == test_config.template_a.template_id:
                result.template_a_performance["scores"].append(performance_score)
                result.template_a_performance["count"] += 1
            elif template_id == test_config.template_b.template_id:
                result.template_b_performance["scores"].append(performance_score)
                result.template_b_performance["count"] += 1
            
            return True
            
        except Exception as e:
            return False

    def get_ab_test_result(self, test_id: str) -> Optional[ABTestResult]:
        """Get the result of an A/B test."""
        if test_id not in self.ab_results:
            return None
        
        result = self.ab_results[test_id]
        
        # Calculate performance metrics
        if result.template_a_performance["scores"]:
            result.template_a_performance["average"] = (
                sum(result.template_a_performance["scores"]) / 
                len(result.template_a_performance["scores"])
            )
        
        if result.template_b_performance["scores"]:
            result.template_b_performance["average"] = (
                sum(result.template_b_performance["scores"]) / 
                len(result.template_b_performance["scores"])
            )
        
        # Determine winner
        a_avg = result.template_a_performance.get("average", 0.0)
        b_avg = result.template_b_performance.get("average", 0.0)
        
        if a_avg > b_avg:
            result.winner = "template_a"
            result.confidence_level = min((a_avg - b_avg) * 2, 1.0)
        elif b_avg > a_avg:
            result.winner = "template_b"
            result.confidence_level = min((b_avg - a_avg) * 2, 1.0)
        else:
            result.winner = None
            result.confidence_level = 0.0
        
        return result

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all templates."""
        stats = {
            "total_templates": len(self.templates),
            "templates_by_type": {},
            "average_performance": 0.0,
            "top_performers": []
        }
        
        total_performance = 0.0
        template_performances = []
        
        for template in self.templates.values():
            template_type = template.prompt_type.value
            if template_type not in stats["templates_by_type"]:
                stats["templates_by_type"][template_type] = 0
            stats["templates_by_type"][template_type] += 1
            
            if "average_score" in template.performance_metrics:
                performance = template.performance_metrics["average_score"]
                total_performance += performance
                template_performances.append((template.name, performance))
        
        if template_performances:
            stats["average_performance"] = total_performance / len(template_performances)
            stats["top_performers"] = sorted(template_performances, 
                                           key=lambda x: x[1], reverse=True)[:5]
        
        return stats

    def export_templates(self) -> Dict[str, Any]:
        """Export all templates to a dictionary."""
        return {
            "templates": [template.to_dict() for template in self.templates.values()],
            "ab_tests": [test_config.__dict__ for test_config in self.ab_tests.values()],
            "ab_results": [result.__dict__ for result in self.ab_results.values()],
            "exported_at": datetime.now(timezone.utc).isoformat()
        }

    def import_templates(self, data: Dict[str, Any]) -> bool:
        """Import templates from a dictionary."""
        try:
            # Import templates
            for template_data in data.get("templates", []):
                template = PromptTemplate.from_dict(template_data)
                self.add_template(template)
            
            # Import A/B tests
            for test_data in data.get("ab_tests", []):
                test_config = ABTestConfig(**test_data)
                self.ab_tests[test_config.test_id] = test_config
            
            # Import A/B results
            for result_data in data.get("ab_results", []):
                result = ABTestResult(**result_data)
                self.ab_results[result.test_id] = result
            
            return True
            
        except Exception as e:
            return False 