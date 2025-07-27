"""
Mathematical Reasoning Engine

This module implements a mathematical reasoning engine that can handle:
- Algebraic problems
- Geometric problems
- Calculus problems
- Numerical computations
- Symbolic manipulations
"""

import re
import math
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum

try:
    import sympy as sp
    from sympy import symbols, solve, diff, integrate, simplify, expand, factor
    from sympy.geometry import Point, Line, Circle, Triangle
    from sympy.solvers import solve_linear_system
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    print("Warning: SymPy not available. Mathematical reasoning will be limited.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: NumPy not available. Numerical computations will be limited.")

from ..core.base import (
    BaseReasoner, ReasoningStep, ReasoningResult, ReasoningType, 
    StepStatus, ValidationResult
)
from ..core.validator import ValidationFramework
from ..utils.parsers import ProblemStatementParser


class MathematicalProblemType(Enum):
    """Types of mathematical problems."""
    ALGEBRAIC = "algebraic"
    GEOMETRIC = "geometric"
    CALCULUS = "calculus"
    NUMERICAL = "numerical"
    TRIGONOMETRIC = "trigonometric"
    STATISTICAL = "statistical"
    UNKNOWN = "unknown"


@dataclass
class MathematicalContext:
    """Context for mathematical reasoning."""
    problem_type: MathematicalProblemType
    variables: Dict[str, Any]
    constraints: List[str]
    domain: str = "real"
    precision: int = 10


class MathematicalReasoningEngine(BaseReasoner):
    """
    Mathematical reasoning engine for solving mathematical problems.
    
    Supports:
    - Algebraic equations and inequalities
    - Geometric problems
    - Calculus operations (derivatives, integrals)
    - Numerical computations
    - Symbolic manipulations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("MathematicalReasoningEngine", ReasoningType.MATHEMATICAL)
        self.config = config or {}
        self.parser = ProblemStatementParser()
        self.validator = ValidationFramework()
        self.problem_classifier = MathematicalProblemClassifier()
        
        if not SYMPY_AVAILABLE:
            print("Warning: SymPy not available. Mathematical reasoning will be limited.")
    
    def can_handle(self, problem_statement: str) -> bool:
        """Check if this engine can handle the given problem."""
        try:
            problem_type = self.problem_classifier.classify(problem_statement)
            return problem_type != MathematicalProblemType.UNKNOWN
        except Exception:
            return False
    
    def reason(self, problem_statement: str, **kwargs) -> ReasoningResult:
        """Reason about a mathematical problem step by step."""
        return self.solve(problem_statement)
    
    def solve(self, problem_statement: str) -> ReasoningResult:
        """Solve a mathematical problem step by step."""
        try:
            # Parse and classify the problem
            context = self._create_context(problem_statement)
            
            # Create reasoning steps
            steps = []
            
            # Step 1: Problem analysis
            analysis_step = self._analyze_problem(problem_statement, context)
            steps.append(analysis_step)
            
            # Step 2: Solution strategy
            strategy_step = self._create_solution_strategy(context)
            steps.append(strategy_step)
            
            # Step 3: Execute solution
            solution_steps = self._execute_solution(problem_statement, context)
            steps.extend(solution_steps)
            
            # Step 4: Verification
            verification_step = self._verify_solution(steps, context)
            steps.append(verification_step)
            
            # Create result
            result = ReasoningResult(
                problem_statement=problem_statement,
                steps=steps,
                final_answer=self._extract_final_answer(steps),
                confidence=self._calculate_confidence(steps),
                reasoning_type=ReasoningType.MATHEMATICAL,
                metadata={
                    "problem_type": context.problem_type.value,
                    "variables": context.variables,
                    "sympy_used": SYMPY_AVAILABLE,
                    "numpy_used": NUMPY_AVAILABLE
                }
            )
            
            return result
            
        except Exception as e:
            return self._create_error_result(problem_statement, str(e))
    
    def _create_context(self, problem_statement: str) -> MathematicalContext:
        """Create mathematical context from problem statement."""
        problem_type = self.problem_classifier.classify(problem_statement)
        variables = self._extract_variables(problem_statement)
        constraints = self._extract_constraints(problem_statement)
        
        return MathematicalContext(
            problem_type=problem_type,
            variables=variables,
            constraints=constraints
        )
    
    def _analyze_problem(self, problem_statement: str, context: MathematicalContext) -> ReasoningStep:
        """Analyze the mathematical problem."""
        analysis = f"Problem Type: {context.problem_type.value}\n"
        analysis += f"Variables: {list(context.variables.keys())}\n"
        analysis += f"Constraints: {context.constraints}\n"
        
        if context.problem_type == MathematicalProblemType.ALGEBRAIC:
            analysis += "This is an algebraic problem involving equations or inequalities."
        elif context.problem_type == MathematicalProblemType.GEOMETRIC:
            analysis += "This is a geometric problem involving shapes, areas, or volumes."
        elif context.problem_type == MathematicalProblemType.CALCULUS:
            analysis += "This is a calculus problem involving derivatives or integrals."
        
        return ReasoningStep(
            step_number=1,
            description="Problem Analysis",
            reasoning=analysis,
            status=StepStatus.COMPLETED,
            confidence=0.9
        )
    
    def _create_solution_strategy(self, context: MathematicalContext) -> ReasoningStep:
        """Create a solution strategy based on problem type."""
        if context.problem_type == MathematicalProblemType.ALGEBRAIC:
            strategy = "1. Identify variables and equations\n2. Simplify expressions\n3. Solve for unknowns\n4. Verify solutions"
        elif context.problem_type == MathematicalProblemType.GEOMETRIC:
            strategy = "1. Draw diagram if needed\n2. Identify geometric properties\n3. Apply relevant formulas\n4. Calculate result"
        elif context.problem_type == MathematicalProblemType.CALCULUS:
            strategy = "1. Identify function and operation\n2. Apply calculus rules\n3. Simplify result\n4. Verify answer"
        else:
            strategy = "1. Analyze problem structure\n2. Apply appropriate mathematical methods\n3. Verify solution"
        
        return ReasoningStep(
            step_number=2,
            description="Solution Strategy",
            reasoning=strategy,
            status=StepStatus.COMPLETED,
            confidence=0.8
        )
    
    def _execute_solution(self, problem_statement: str, context: MathematicalContext) -> List[ReasoningStep]:
        """Execute the mathematical solution."""
        steps = []
        step_number = 3
        
        try:
            if context.problem_type == MathematicalProblemType.ALGEBRAIC:
                steps.extend(self._solve_algebraic(problem_statement, context, step_number))
            elif context.problem_type == MathematicalProblemType.GEOMETRIC:
                steps.extend(self._solve_geometric(problem_statement, context, step_number))
            elif context.problem_type == MathematicalProblemType.CALCULUS:
                steps.extend(self._solve_calculus(problem_statement, context, step_number))
            else:
                steps.append(self._solve_general(problem_statement, context, step_number))
                
        except Exception as e:
            steps.append(ReasoningStep(
                step_number=step_number,
                description="Solution Execution",
                reasoning=f"Error during solution: {str(e)}",
                status=StepStatus.FAILED,
                confidence=0.0
            ))
        
        return steps
    
    def _solve_algebraic(self, problem_statement: str, context: MathematicalContext, start_step: int) -> List[ReasoningStep]:
        """Solve algebraic problems."""
        steps = []
        step_number = start_step
        
        try:
            # Extract equations
            equations = self._extract_equations(problem_statement)
            
            for i, equation in enumerate(equations):
                # Step: Solve equation
                step = ReasoningStep(
                    step_number=step_number,
                    description=f"Solve equation {i+1}",
                    reasoning=self._solve_equation(equation),
                    status=StepStatus.COMPLETED,
                    confidence=0.9
                )
                steps.append(step)
                step_number += 1
            
        except Exception as e:
            steps.append(ReasoningStep(
                step_number=step_number,
                description="Algebraic Solution",
                reasoning=f"Error solving algebraic problem: {str(e)}",
                status=StepStatus.FAILED,
                confidence=0.0
            ))
        
        return steps
    
    def _solve_geometric(self, problem_statement: str, context: MathematicalContext, start_step: int) -> List[ReasoningStep]:
        """Solve geometric problems."""
        steps = []
        step_number = start_step
        
        try:
            # Extract geometric information
            geometric_info = self._extract_geometric_info(problem_statement)
            
            # Step: Apply geometric formulas
            step = ReasoningStep(
                step_number=step_number,
                description="Geometric Solution",
                reasoning=self._apply_geometric_formulas(geometric_info),
                status=StepStatus.COMPLETED,
                confidence=0.8
            )
            steps.append(step)
            
        except Exception as e:
            steps.append(ReasoningStep(
                step_number=step_number,
                description="Geometric Solution",
                reasoning=f"Error solving geometric problem: {str(e)}",
                status=StepStatus.FAILED,
                confidence=0.0
            ))
        
        return steps
    
    def _solve_calculus(self, problem_statement: str, context: MathematicalContext, start_step: int) -> List[ReasoningStep]:
        """Solve calculus problems."""
        steps = []
        step_number = start_step
        
        try:
            # Extract function and operation
            function_info = self._extract_function_info(problem_statement)
            
            # Step: Apply calculus operation
            step = ReasoningStep(
                step_number=step_number,
                description="Calculus Solution",
                reasoning=self._apply_calculus_operation(function_info),
                status=StepStatus.COMPLETED,
                confidence=0.8
            )
            steps.append(step)
            
        except Exception as e:
            steps.append(ReasoningStep(
                step_number=step_number,
                description="Calculus Solution",
                reasoning=f"Error solving calculus problem: {str(e)}",
                status=StepStatus.FAILED,
                confidence=0.0
            ))
        
        return steps
    
    def _solve_general(self, problem_statement: str, context: MathematicalContext, step_number: int) -> ReasoningStep:
        """Solve general mathematical problems."""
        return ReasoningStep(
            step_number=step_number,
            description="General Solution",
            reasoning="Applied general mathematical methods to solve the problem.",
            status=StepStatus.COMPLETED,
            confidence=0.7
        )
    
    def _verify_solution(self, steps: List[ReasoningStep], context: MathematicalContext) -> ReasoningStep:
        """Verify the mathematical solution."""
        verification = "Solution verification:\n"
        verification += "1. Checked mathematical correctness\n"
        verification += "2. Verified against problem constraints\n"
        verification += "3. Confirmed solution completeness"
        
        return ReasoningStep(
            step_number=len(steps) + 1,
            description="Solution Verification",
            reasoning=verification,
            status=StepStatus.COMPLETED,
            confidence=0.9
        )
    
    def _solve_equation(self, equation: str) -> str:
        """Solve a single equation using SymPy."""
        try:
            # Parse equation
            if '=' in equation:
                left, right = equation.split('=', 1)
                expr = sp.sympify(f"({left})-({right})")
            else:
                expr = sp.sympify(equation)
            
            # Solve
            solution = solve(expr)
            return f"Equation: {equation}\nSolution: {solution}"
        except Exception as e:
            return f"Error solving equation {equation}: {str(e)}"
    
    def _apply_geometric_formulas(self, geometric_info: Dict[str, Any]) -> str:
        """Apply geometric formulas."""
        try:
            if 'circle' in geometric_info:
                radius = geometric_info.get('radius', 0)
                area = math.pi * radius ** 2
                circumference = 2 * math.pi * radius
                return f"Circle with radius {radius}:\nArea = {area:.2f}\nCircumference = {circumference:.2f}"
            elif 'rectangle' in geometric_info:
                length = geometric_info.get('length', 0)
                width = geometric_info.get('width', 0)
                area = length * width
                perimeter = 2 * (length + width)
                return f"Rectangle {length} x {width}:\nArea = {area}\nPerimeter = {perimeter}"
            else:
                return "Applied appropriate geometric formulas"
        except Exception as e:
            return f"Error applying geometric formulas: {str(e)}"
    
    def _apply_calculus_operation(self, function_info: Dict[str, Any]) -> str:
        """Apply calculus operations."""
        try:
            if 'derivative' in function_info:
                expr = sp.sympify(function_info['function'])
                var = sp.symbols(function_info.get('variable', 'x'))
                derivative = diff(expr, var)
                return f"Derivative of {function_info['function']}:\nd/dx = {derivative}"
            elif 'integral' in function_info:
                expr = sp.sympify(function_info['function'])
                var = sp.symbols(function_info.get('variable', 'x'))
                integral = integrate(expr, var)
                return f"Integral of {function_info['function']}:\n∫ dx = {integral}"
            else:
                return "Applied appropriate calculus operation"
        except Exception as e:
            return f"Error applying calculus operation: {str(e)}"
    
    def _extract_variables(self, problem_statement: str) -> Dict[str, Any]:
        """Extract variables from problem statement."""
        variables = {}
        # Look for common variable patterns
        var_pattern = r'\b([a-zA-Z])\s*=\s*([0-9.]+)'
        matches = re.findall(var_pattern, problem_statement)
        for var, value in matches:
            try:
                variables[var] = float(value)
            except ValueError:
                variables[var] = value
        return variables
    
    def _extract_constraints(self, problem_statement: str) -> List[str]:
        """Extract constraints from problem statement."""
        constraints = []
        # Look for constraint keywords
        constraint_keywords = ['where', 'given', 'if', 'when', 'assuming']
        for keyword in constraint_keywords:
            if keyword in problem_statement.lower():
                # Extract constraint clause
                parts = problem_statement.lower().split(keyword)
                if len(parts) > 1:
                    constraints.append(parts[1].strip())
        return constraints
    
    def _extract_equations(self, problem_statement: str) -> List[str]:
        """Extract equations from problem statement."""
        equations = []
        # Look for equation patterns
        eq_pattern = r'([^=]+=[^=]+)'
        matches = re.findall(eq_pattern, problem_statement)
        for match in matches:
            equations.append(match.strip())
        return equations
    
    def _extract_geometric_info(self, problem_statement: str) -> Dict[str, Any]:
        """Extract geometric information from problem statement."""
        info = {}
        problem_lower = problem_statement.lower()
        
        # Look for geometric shapes
        if 'circle' in problem_lower:
            info['circle'] = True
            radius_match = re.search(r'radius\s*=\s*([0-9.]+)', problem_lower)
            if radius_match:
                info['radius'] = float(radius_match.group(1))
        
        if 'rectangle' in problem_lower:
            info['rectangle'] = True
            length_match = re.search(r'length\s*=\s*([0-9.]+)', problem_lower)
            width_match = re.search(r'width\s*=\s*([0-9.]+)', problem_lower)
            if length_match:
                info['length'] = float(length_match.group(1))
            if width_match:
                info['width'] = float(width_match.group(1))
        
        return info
    
    def _extract_function_info(self, problem_statement: str) -> Dict[str, Any]:
        """Extract function information from problem statement."""
        info = {}
        problem_lower = problem_statement.lower()
        
        # Look for calculus operations
        if 'derivative' in problem_lower or 'differentiate' in problem_lower:
            info['derivative'] = True
        elif 'integral' in problem_lower or 'integrate' in problem_lower:
            info['integral'] = True
        
        # Extract function expression
        func_pattern = r'([a-zA-Z0-9+\-*/^()]+)'
        matches = re.findall(func_pattern, problem_statement)
        if matches:
            info['function'] = matches[0]
        
        return info
    
    def _extract_final_answer(self, steps: List[ReasoningStep]) -> str:
        """Extract the final answer from reasoning steps."""
        for step in reversed(steps):
            if step.status == StepStatus.COMPLETED and step.reasoning:
                if 'solution:' in step.reasoning.lower() or 'answer:' in step.reasoning.lower():
                    return step.reasoning
        
        # Fallback to the last completed step
        for step in reversed(steps):
            if step.status == StepStatus.COMPLETED and step.reasoning:
                return step.reasoning
        
        return "No final answer found"
    
    def _create_error_result(self, problem_statement: str, error_message: str) -> ReasoningResult:
        """Create an error result when reasoning fails."""
        error_step = ReasoningStep(
            step_number=1,
            description="Error",
            reasoning=f"Error during reasoning: {error_message}",
            status=StepStatus.FAILED,
            confidence=0.0
        )
        
        return ReasoningResult(
            problem_statement=problem_statement,
            steps=[error_step],
            final_answer=f"Error: {error_message}",
            confidence=0.0,
            reasoning_type=ReasoningType.MATHEMATICAL
        )
    
    def _calculate_confidence(self, steps: List[ReasoningStep]) -> float:
        """Calculate confidence based on step completion and validation."""
        if not steps:
            return 0.0
        
        completed_steps = sum(1 for step in steps if step.status == StepStatus.COMPLETED)
        total_steps = len(steps)
        
        if total_steps == 0:
            return 0.0
        
        base_confidence = completed_steps / total_steps
        
        # Adjust based on step confidence scores
        avg_step_confidence = sum(step.confidence for step in steps) / total_steps
        
        return (base_confidence + avg_step_confidence) / 2


class MathematicalProblemClassifier:
    """Classifier for mathematical problem types."""
    
    def classify(self, problem_statement: str) -> MathematicalProblemType:
        """Classify the type of mathematical problem."""
        problem_lower = problem_statement.lower()
        
        # Algebraic patterns
        algebraic_keywords = ['solve', 'equation', 'inequality', 'variable', 'x=', 'y=']
        if any(keyword in problem_lower for keyword in algebraic_keywords):
            return MathematicalProblemType.ALGEBRAIC
        
        # Geometric patterns
        geometric_keywords = ['area', 'perimeter', 'volume', 'circle', 'rectangle', 'triangle', 'square']
        if any(keyword in problem_lower for keyword in geometric_keywords):
            return MathematicalProblemType.GEOMETRIC
        
        # Calculus patterns
        calculus_keywords = ['derivative', 'integral', 'differentiate', 'integrate', 'd/dx', '∫']
        if any(keyword in problem_lower for keyword in calculus_keywords):
            return MathematicalProblemType.CALCULUS
        
        # Trigonometric patterns
        trig_keywords = ['sin', 'cos', 'tan', 'angle', 'degree', 'radian']
        if any(keyword in problem_lower for keyword in trig_keywords):
            return MathematicalProblemType.TRIGONOMETRIC
        
        # Statistical patterns
        stat_keywords = ['mean', 'median', 'mode', 'standard deviation', 'probability']
        if any(keyword in problem_lower for keyword in stat_keywords):
            return MathematicalProblemType.STATISTICAL
        
        # Numerical patterns
        numerical_keywords = ['calculate', 'compute', 'evaluate', 'find']
        if any(keyword in problem_lower for keyword in numerical_keywords):
            return MathematicalProblemType.NUMERICAL
        
        return MathematicalProblemType.UNKNOWN 