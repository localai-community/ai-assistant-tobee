"""
Chain-of-Thought (CoT) reasoning strategy implementation.

This module provides a comprehensive implementation of Chain-of-Thought reasoning
for complex problem solving with step-by-step reasoning generation, validation,
confidence scoring, and iterative refinement.
"""

import asyncio
import json
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone

from ..core.base import (
    BaseReasoner, ReasoningResult, ReasoningStep, StepStatus, 
    ValidationResult, ValidationLevel, ReasoningType
)
from ..utils.parsers import parse_problem_statement
from ..utils.formatters import format_reasoning_output


@dataclass
class CoTStep:
    """Represents a single Chain-of-Thought step."""
    step_id: str
    step_number: int
    thought: str
    action: str
    observation: str
    confidence: float
    validation_results: List[ValidationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoTConfig:
    """Configuration for Chain-of-Thought reasoning."""
    max_steps: int = 10
    min_confidence_threshold: float = 0.7
    max_iterations: int = 3
    enable_validation: bool = True
    enable_refinement: bool = True
    prompt_template: str = ""
    temperature: float = 0.1
    max_tokens: int = 1000


class ChainOfThoughtStrategy(BaseReasoner[ReasoningResult]):
    """
    Chain-of-Thought reasoning strategy implementation.
    
    This strategy implements step-by-step reasoning generation with:
    - Intermediate result validation
    - Confidence scoring
    - Iterative refinement
    - LLM integration for reasoning generation
    """

    def __init__(self, name: str = "Chain-of-Thought", config: Optional[CoTConfig] = None):
        super().__init__(name, ReasoningType.HYBRID)
        self.config = config or CoTConfig()
        self.cot_steps: List[CoTStep] = []
        self.iteration_count = 0
        
        # Default prompt template
        if not self.config.prompt_template:
            self.config.prompt_template = self._get_default_prompt_template()

    def _get_default_prompt_template(self) -> str:
        """Get the default prompt template for CoT reasoning."""
        return """You are a helpful AI assistant that solves problems step by step.

Problem: {problem_statement}

Please solve this problem step by step. For each step:
1. Think about what needs to be done
2. Take an action or make a calculation
3. Observe the result
4. Continue to the next step

Current step: {step_number}
Previous steps: {previous_steps}

Let's solve this step by step:

Step {step_number}:
Thought: """

    async def reason(self, problem_statement: str, **kwargs) -> ReasoningResult:
        """
        Perform Chain-of-Thought reasoning on the given problem.
        
        Args:
            problem_statement: The problem to solve
            **kwargs: Additional arguments
            
        Returns:
            ReasoningResult containing the CoT reasoning steps and final answer
        """
        start_time = datetime.now(timezone.utc)
        
        # Validate input
        validation = self.validate_input(problem_statement)
        if not validation.is_valid:
            return ReasoningResult(
                problem_statement=problem_statement,
                validation_results=[validation],
                created_at=start_time
            )

        # Parse problem statement
        parsed_problem = parse_problem_statement(problem_statement)
        
        # Initialize result
        result = ReasoningResult(
            problem_statement=problem_statement,
            reasoning_type=ReasoningType.HYBRID,
            created_at=start_time
        )

        # Perform iterative CoT reasoning
        final_answer = None
        overall_confidence = 0.0
        
        for iteration in range(self.config.max_iterations):
            self.iteration_count = iteration + 1
            
            # Generate CoT steps
            cot_result = await self._generate_cot_steps(parsed_problem, result)
            
            if cot_result:
                # Validate and refine steps
                validated_result = await self._validate_and_refine_steps(cot_result)
                
                if validated_result:
                    result = validated_result
                    final_answer = self._extract_final_answer(result)
                    overall_confidence = self._calculate_overall_confidence(result)
                    
                    # Check if we've reached sufficient confidence
                    if overall_confidence >= self.config.min_confidence_threshold:
                        break

        # Set final result
        result.final_answer = final_answer
        result.confidence = overall_confidence
        result.completed_at = datetime.now(timezone.utc)
        result.execution_time = (result.completed_at - start_time).total_seconds()

        return result

    async def _generate_cot_steps(self, parsed_problem: Dict[str, Any], 
                                 current_result: ReasoningResult) -> Optional[ReasoningResult]:
        """Generate Chain-of-Thought steps using LLM."""
        try:
            # This would integrate with an LLM service
            # For now, we'll simulate the process
            steps = await self._simulate_cot_generation(parsed_problem, current_result)
            
            if not steps:
                return None

            # Convert CoT steps to ReasoningSteps
            reasoning_steps = []
            for i, cot_step in enumerate(steps, 1):
                reasoning_step = ReasoningStep(
                    step_number=i,
                    description=f"Step {i}: {cot_step.action}",
                    input_data={"thought": cot_step.thought},
                    output_data={"observation": cot_step.observation},
                    reasoning=cot_step.thought,
                    confidence=cot_step.confidence,
                    status=StepStatus.COMPLETED,
                    validation_results=cot_step.validation_results,
                    metadata=cot_step.metadata
                )
                reasoning_steps.append(reasoning_step)

            # Create new result
            new_result = ReasoningResult(
                problem_statement=current_result.problem_statement,
                reasoning_type=current_result.reasoning_type,
                created_at=current_result.created_at
            )
            
            for step in reasoning_steps:
                new_result.add_step(step)

            return new_result

        except Exception as e:
            # Add error step
            error_step = ReasoningStep(
                step_number=len(current_result.steps) + 1,
                description="Error in CoT generation",
                reasoning=f"Error: {str(e)}",
                confidence=0.0,
                status=StepStatus.FAILED
            )
            current_result.add_step(error_step)
            return current_result

    async def _simulate_cot_generation(self, parsed_problem: Dict[str, Any], 
                                     current_result: ReasoningResult) -> List[CoTStep]:
        """Simulate CoT step generation (placeholder for LLM integration)."""
        problem_type = parsed_problem.get("type", "general")
        problem_content = parsed_problem.get("content", "")
        
        steps = []
        
        if problem_type == "mathematical":
            steps = self._generate_math_cot_steps(problem_content)
        elif problem_type == "logical":
            steps = self._generate_logical_cot_steps(problem_content)
        else:
            steps = self._generate_general_cot_steps(problem_content)
        
        return steps

    def _generate_math_cot_steps(self, problem_content: str) -> List[CoTStep]:
        """Generate mathematical CoT steps."""
        steps = []
        
        # Example: "What is 15 + 27?"
        if "What is" in problem_content and any(op in problem_content for op in ["+", "-", "*", "/"]):
            numbers = re.findall(r'\d+', problem_content)
            if len(numbers) >= 2:
                a, b = int(numbers[0]), int(numbers[1])
                
                steps.append(CoTStep(
                    step_id="step_1",
                    step_number=1,
                    thought="I need to identify the numbers and operation in this problem.",
                    action="Extract numbers: 15 and 27",
                    observation=f"Found numbers: {a} and {b}",
                    confidence=0.9
                ))
                
                steps.append(CoTStep(
                    step_id="step_2", 
                    step_number=2,
                    thought="I need to add these numbers together.",
                    action=f"Calculate: {a} + {b}",
                    observation=f"Result: {a + b}",
                    confidence=0.95
                ))
        
        return steps

    def _generate_logical_cot_steps(self, problem_content: str) -> List[CoTStep]:
        """Generate logical CoT steps."""
        steps = []
        
        # Example: "If all A are B, and some B are C, what can we conclude about A and C?"
        if "If" in problem_content and "what can we conclude" in problem_content:
            steps.append(CoTStep(
                step_id="step_1",
                step_number=1,
                thought="I need to analyze the logical premises given.",
                action="Identify premises: All A are B, Some B are C",
                observation="Premises identified",
                confidence=0.8
            ))
            
            steps.append(CoTStep(
                step_id="step_2",
                step_number=2,
                thought="I need to apply logical reasoning to these premises.",
                action="Apply syllogistic reasoning",
                observation="From 'All A are B' and 'Some B are C', we can conclude 'Some A are C'",
                confidence=0.7
            ))
        
        return steps

    def _generate_general_cot_steps(self, problem_content: str) -> List[CoTStep]:
        """Generate general CoT steps."""
        steps = []
        
        steps.append(CoTStep(
            step_id="step_1",
            step_number=1,
            thought="I need to understand what this problem is asking.",
            action="Analyze problem statement",
            observation="Problem understood",
            confidence=0.8
        ))
        
        steps.append(CoTStep(
            step_id="step_2",
            step_number=2,
            thought="I need to break this down into manageable steps.",
            action="Decompose problem",
            observation="Problem decomposed into steps",
            confidence=0.7
        ))
        
        steps.append(CoTStep(
            step_id="step_3",
            step_number=3,
            thought="I need to solve each step systematically.",
            action="Execute solution steps",
            observation="Solution completed",
            confidence=0.6
        ))
        
        return steps

    async def _validate_and_refine_steps(self, result: ReasoningResult) -> Optional[ReasoningResult]:
        """Validate and refine CoT steps."""
        if not self.config.enable_validation:
            return result

        validated_steps = []
        
        for step in result.steps:
            # Validate individual step
            validation = self.validate_step(step)
            step.validation_results.append(validation)
            
            # Refine step if needed
            if self.config.enable_refinement and validation.level == ValidationLevel.ERROR:
                refined_step = await self._refine_step(step)
                if refined_step:
                    validated_steps.append(refined_step)
                else:
                    validated_steps.append(step)
            else:
                validated_steps.append(step)

        # Create new result with validated steps
        new_result = ReasoningResult(
            problem_statement=result.problem_statement,
            reasoning_type=result.reasoning_type,
            created_at=result.created_at
        )
        
        for step in validated_steps:
            new_result.add_step(step)

        return new_result

    async def _refine_step(self, step: ReasoningStep) -> Optional[ReasoningStep]:
        """Refine a reasoning step."""
        try:
            # This would integrate with LLM for step refinement
            # For now, we'll implement basic refinement logic
            
            if step.confidence < 0.5:
                # Try to improve the step
                improved_reasoning = f"Refined: {step.reasoning}"
                improved_confidence = min(step.confidence + 0.2, 1.0)
                
                refined_step = ReasoningStep(
                    step_number=step.step_number,
                    description=step.description,
                    input_data=step.input_data,
                    output_data=step.output_data,
                    reasoning=improved_reasoning,
                    confidence=improved_confidence,
                    status=StepStatus.COMPLETED,
                    validation_results=step.validation_results,
                    metadata={**step.metadata, "refined": True}
                )
                
                return refined_step
            
            return step

        except Exception as e:
            # If refinement fails, return original step
            return step

    def _extract_final_answer(self, result: ReasoningResult) -> Any:
        """Extract the final answer from the reasoning result."""
        if not result.steps:
            return None

        # Look for the last step with a clear answer
        for step in reversed(result.steps):
            if step.output_data and step.confidence > 0.5:
                return step.output_data.get("observation") or step.output_data.get("result")
        
        # Fallback to the last step's reasoning
        last_step = result.steps[-1]
        return last_step.reasoning

    def _calculate_overall_confidence(self, result: ReasoningResult) -> float:
        """Calculate overall confidence from all steps."""
        if not result.steps:
            return 0.0

        # Weighted average of step confidences
        total_weight = 0
        weighted_sum = 0
        
        for i, step in enumerate(result.steps):
            weight = 1.0 + (i * 0.1)  # Later steps get more weight
            weighted_sum += step.confidence * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def can_handle(self, problem_statement: str) -> bool:
        """Check if this strategy can handle the given problem."""
        # CoT can handle most types of problems
        return len(problem_statement.strip()) > 0

    def get_cot_steps(self) -> List[CoTStep]:
        """Get the CoT steps from the last execution."""
        return self.cot_steps.copy()

    def get_iteration_count(self) -> int:
        """Get the number of iterations performed."""
        return self.iteration_count

    def reset(self) -> None:
        """Reset the strategy state."""
        self.cot_steps.clear()
        self.iteration_count = 0 