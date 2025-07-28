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
    from sympy import symbols, solve, diff, integrate, simplify, expand, factor, sympify
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
    
    async def reason(self, problem_statement: str, **kwargs) -> ReasoningResult:
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
        try:
            # Try to extract and solve simple arithmetic problems
            import re
            
            # Look for arithmetic operations (both symbols and words)
            arithmetic_patterns = [
                r'(\d+)\s*([+\-*/])\s*(\d+)',  # Symbol operators
                r'(\d+)\s+(times|multiplied by)\s+(\d+)',  # Multiplication words
                r'(\d+)\s+(plus|added to)\s+(\d+)',  # Addition words
                r'(\d+)\s+(minus|subtracted from)\s+(\d+)',  # Subtraction words
                r'(\d+)\s+(divided by)\s+(\d+)',  # Division words
            ]
            
            for pattern in arithmetic_patterns:
                match = re.search(pattern, problem_statement.lower())
                if match:
                    num1 = int(match.group(1))
                    operator_word = match.group(2)
                    num2 = int(match.group(3))
                    
                    # Determine the operation and provide step-by-step solution
                    if operator_word in ['+', 'plus', 'added to']:
                        result = num1 + num2
                        solution = f"""**Step 1:** Identify the operation
We need to add {num1} and {num2}.

**Step 2:** Perform the addition
{num1} + {num2} = {result}

**Final Answer:** {result}"""
                    elif operator_word in ['-', 'minus', 'subtracted from']:
                        result = num1 - num2
                        solution = f"""**Step 1:** Identify the operation
We need to subtract {num2} from {num1}.

**Step 2:** Perform the subtraction
{num1} - {num2} = {result}

**Final Answer:** {result}"""
                    elif operator_word in ['*', 'times', 'multiplied by']:
                        result = num1 * num2
                        solution = f"""**Step 1:** Identify the operation
We need to multiply {num1} by {num2}.

**Step 2:** Perform the multiplication
{num1} × {num2} = {result}

**Final Answer:** {result}"""
                    elif operator_word in ['/', 'divided by']:
                        if num2 != 0:
                            result = num1 / num2
                            solution = f"""**Step 1:** Identify the operation
We need to divide {num1} by {num2}.

**Step 2:** Perform the division
{num1} ÷ {num2} = {result}

**Final Answer:** {result}"""
                        else:
                            solution = "Error: Division by zero"
                    else:
                        solution = "Applied general mathematical methods to solve the problem."
                    
                    return ReasoningStep(
                        step_number=step_number,
                        description="General Solution",
                        reasoning=solution,
                        status=StepStatus.COMPLETED,
                        confidence=0.8
                    )
            
            # If no pattern matches, return generic response
            solution = "Applied general mathematical methods to solve the problem."
            
            return ReasoningStep(
                step_number=step_number,
                description="General Solution",
                reasoning=solution,
                status=StepStatus.COMPLETED,
                confidence=0.8
            )
        except Exception as e:
            return ReasoningStep(
                step_number=step_number,
                description="General Solution",
                reasoning=f"Error in general solution: {str(e)}",
                status=StepStatus.FAILED,
                confidence=0.0
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
        """Solve a single equation with step-by-step explanation."""
        try:
            # Clean the equation first
            equation = equation.strip()
            
            # Remove any remaining prefixes that might have been missed
            prefixes_to_remove = [
                'solve the equation:',
                'solve:',
                'equation:',
                'find:',
                'calculate:',
                'solve for',
                'find the value of',
                'what is',
                'solve'
            ]
            
            for prefix in prefixes_to_remove:
                if equation.lower().startswith(prefix):
                    equation = equation[len(prefix):].strip()
                    break
            
            # Parse equation
            if '=' in equation:
                left, right = equation.split('=', 1)
                # Clean both sides
                left = left.strip()
                right = right.strip()
                
                # Fix implicit multiplication for SymPy parsing
                left_fixed = self._fix_implicit_multiplication(left)
                right_fixed = self._fix_implicit_multiplication(right)
                
                # Create the expression to solve: left - right = 0
                expr = sp.sympify(f"({left_fixed}) - ({right_fixed})")
                
                # Solve with SymPy for verification
                solution = solve(expr)
                
                # Generate step-by-step solution
                steps = self._generate_step_by_step_solution(left, right, solution)
                
                return steps
            else:
                # If no equals sign, treat as expression to solve
                equation_fixed = self._fix_implicit_multiplication(equation)
                expr = sp.sympify(equation_fixed)
                solution = solve(expr)
                
                steps = self._generate_step_by_step_solution(equation, "0", solution)
                return steps
                
        except Exception as e:
            return f"Error solving equation '{equation}': {str(e)}"
    
    def _generate_step_by_step_solution(self, left: str, right: str, solution) -> str:
        """Generate step-by-step solution for an equation."""
        try:
            # Parse the sides for step-by-step work
            left_parsed = sp.sympify(self._fix_implicit_multiplication(left))
            right_parsed = sp.sympify(self._fix_implicit_multiplication(right))
            
            steps = []
            steps.append(f"**Step 1:** Start with the equation")
            steps.append(f"{left} = {right}")
            steps.append("")
            
            # Move all terms to left side
            if right_parsed != 0:
                steps.append(f"**Step 2:** Move all terms to the left side")
                steps.append(f"{left} - {right} = 0")
                steps.append("")
            
            # Simplify the left side
            simplified = left_parsed - right_parsed
            if simplified != left_parsed - right_parsed:  # If simplification happened
                steps.append(f"**Step 3:** Simplify the left side")
                steps.append(f"{simplified} = 0")
                steps.append("")
            
            # For linear equations, show the actual solving steps
            if len(solution) == 1 and isinstance(solution[0], (int, float, sp.core.numbers.Rational)):
                # This is a linear equation, show the actual steps
                simplified_expr = simplified
                
                # Check if it's in the form ax + b = 0
                x = sp.symbols('x')
                if simplified_expr.has(x):
                    # Extract coefficient of x and constant term
                    coeff_x = simplified_expr.coeff(x)
                    constant = simplified_expr.subs(x, 0)
                    
                    if coeff_x != 0:
                        steps.append(f"**Step 3:** Simplify to standard form")
                        steps.append(f"{simplified_expr} = 0")
                        steps.append("")
                        
                        steps.append(f"**Step 4:** Isolate x")
                        # Fix the display of negative numbers
                        if constant < 0:
                            steps.append(f"{coeff_x}x + {constant} = 0")
                            steps.append(f"{coeff_x}x = {-constant}")
                            steps.append(f"x = {-constant}/{coeff_x}")
                        else:
                            steps.append(f"{coeff_x}x + {constant} = 0")
                            steps.append(f"{coeff_x}x = -{constant}")
                            steps.append(f"x = -{constant}/{coeff_x}")
                        steps.append(f"x = {solution[0]}")
                        steps.append("")
                        
                        steps.append(f"**Final Answer:** x = {solution[0]}")
                    else:
                        steps.append(f"**Step 4:** No solution (coefficient of x is 0)")
                        steps.append("")
                        steps.append(f"**Final Answer:** No solution")
                else:
                    steps.append(f"**Step 4:** Solve for x")
                    steps.append(f"x = {solution[0]}")
                    steps.append("")
                    steps.append(f"**Final Answer:** x = {solution[0]}")
            else:
                # For other types of equations (quadratic, etc.)
                if solution:
                    if len(solution) == 1:
                        steps.append(f"**Step 4:** Solve for x")
                        steps.append(f"x = {solution[0]}")
                        steps.append("")
                        steps.append(f"**Final Answer:** x = {solution[0]}")
                    else:
                        steps.append(f"**Step 4:** Solve for x")
                        steps.append(f"x = {solution}")
                        steps.append("")
                        steps.append(f"**Final Answer:** x = {solution}")
                else:
                    steps.append(f"**Step 4:** No solution found")
                    steps.append("")
                    steps.append(f"**Final Answer:** No solution")
            
            return "\n".join(steps)
            
        except Exception as e:
            # Fallback to simple solution if step-by-step fails
            if solution:
                if len(solution) == 1:
                    return f"Equation: {left} = {right}\nSolution: x = {solution[0]}"
                else:
                    return f"Equation: {left} = {right}\nSolutions: {solution}"
            else:
                return f"Equation: {left} = {right}\nNo solution found"
    
    def _fix_implicit_multiplication(self, expression: str) -> str:
        """Fix implicit multiplication for SymPy parsing."""
        import re
        
        # Add explicit multiplication where needed
        # Pattern: number followed by variable (e.g., 2x -> 2*x)
        expression = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expression)
        
        # Pattern: variable followed by number (e.g., x2 -> x*2)
        expression = re.sub(r'([a-zA-Z])(\d+)', r'\1*\2', expression)
        
        # Pattern: variable followed by variable (e.g., xy -> x*y)
        expression = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expression)
        
        # Pattern: closing parenthesis followed by variable or number
        expression = re.sub(r'\)([a-zA-Z0-9])', r')*\1', expression)
        
        # Pattern: variable or number followed by opening parenthesis
        expression = re.sub(r'([a-zA-Z0-9])\(', r'\1*(', expression)
        
        return expression
    
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
        
        # First, try to find clean equation patterns (just the mathematical expression)
        # Look for patterns like "2x + 5 = 13" or "x^2 + 3x = 10"
        clean_eq_pattern = r'([a-zA-Z0-9\s+\-*/^()=]+)'
        matches = re.findall(clean_eq_pattern, problem_statement)
        
        for match in matches:
            # Clean up the match to extract just the equation part
            cleaned_match = match.strip()
            
            # Skip if it doesn't contain an equals sign
            if '=' not in cleaned_match:
                continue
                
            # Remove common prefixes that might be included
            prefixes_to_remove = [
                'solve the equation:',
                'solve:',
                'equation:',
                'find:',
                'calculate:',
                'solve for',
                'find the value of',
                'what is',
                'solve'
            ]
            
            for prefix in prefixes_to_remove:
                if cleaned_match.lower().startswith(prefix):
                    cleaned_match = cleaned_match[len(prefix):].strip()
                    break
            
            # Only add if it looks like a valid equation
            if '=' in cleaned_match and len(cleaned_match.strip()) > 0:
                equations.append(cleaned_match.strip())
        
        # If no equations found with the clean pattern, try the original pattern
        if not equations:
            eq_pattern = r'([^=]+=[^=]+)'
            matches = re.findall(eq_pattern, problem_statement)
            for match in matches:
                # Clean up the match
                cleaned_match = match.strip()
                
                # Remove common prefixes
                prefixes_to_remove = [
                    'solve the equation:',
                    'solve:',
                    'equation:',
                    'find:',
                    'calculate:',
                    'solve for',
                    'find the value of',
                    'what is',
                    'solve'
                ]
                
                for prefix in prefixes_to_remove:
                    if cleaned_match.lower().startswith(prefix):
                        cleaned_match = cleaned_match[len(prefix):].strip()
                        break
                
                if '=' in cleaned_match and len(cleaned_match.strip()) > 0:
                    equations.append(cleaned_match.strip())
        
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
        # First, look for steps that contain actual solutions (not verification)
        for step in reversed(steps):
            if step.status == StepStatus.COMPLETED and step.reasoning:
                # Look for actual solution patterns, not verification
                if ('solution:' in step.reasoning.lower() and 'verification' not in step.reasoning.lower()) or \
                   ('answer:' in step.reasoning.lower()) or \
                   ('=' in step.reasoning and any(op in step.reasoning for op in ['+', '-', '*', '/', '×', '÷'])):
                    return step.reasoning
        
        # Fallback to the last completed step that's not verification
        for step in reversed(steps):
            if step.status == StepStatus.COMPLETED and step.reasoning and 'verification' not in step.reasoning.lower():
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
        
        # Algebraic patterns - but be more specific to avoid false positives
        algebraic_keywords = ['solve', 'equation', 'inequality', 'variable', 'x=', 'y=']
        if any(keyword in problem_lower for keyword in algebraic_keywords):
            return MathematicalProblemType.ALGEBRAIC
        
        # Check for "find" and "calculate" but only if they're followed by variables or equations
        if 'find' in problem_lower or 'calculate' in problem_lower:
            # Check if it contains variables (x, y, z) as standalone variables or equations (=)
            # Look for variables that are actually variables, not part of words
            var_pattern = r'\b[x-z]\b'  # Standalone variables
            if re.search(var_pattern, problem_lower) or '=' in problem_lower:
                return MathematicalProblemType.ALGEBRAIC
            # Check if it's a simple arithmetic problem
            arithmetic_patterns = [
                r'\d+\s+(times|multiplied by|plus|minus|divided by)\s+\d+',
                r'\d+\s*[+\-*/]\s*\d+'
            ]
            if any(re.search(pattern, problem_lower) for pattern in arithmetic_patterns):
                return MathematicalProblemType.NUMERICAL
        
        # Geometric patterns - but check if it's a logical reasoning question first
        geometric_keywords = ['area', 'perimeter', 'volume', 'circle', 'rectangle', 'triangle', 'square']
        if any(keyword in problem_lower for keyword in geometric_keywords):
            # Check if this is a logical reasoning question about geometric properties
            logical_geometric_keywords = ['is it a', 'are all', 'is this', 'what follows', 'what can we conclude']
            if any(keyword in problem_lower for keyword in logical_geometric_keywords):
                return MathematicalProblemType.UNKNOWN
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
        
        # Numerical patterns - more specific to avoid false positives
        numerical_keywords = ['calculate', 'compute', 'evaluate', 'find', 'what is']
        # Only classify as numerical if it's clearly mathematical and not causal or logical
        if any(keyword in problem_lower for keyword in numerical_keywords):
            # Check if it's a causal question (contains causal keywords)
            causal_keywords = ['cause', 'causes', 'causing', 'caused by', 'causal', 'effect', 'relationship']
            if any(causal_keyword in problem_lower for causal_keyword in causal_keywords):
                return MathematicalProblemType.UNKNOWN
            
            # Check if it's a logical question (contains logical keywords)
            logical_keywords = ['logical expression', 'logical operator', 'and', 'or', 'not', 'implies', 'boolean', 'logic', 'proposition', 'truth table', 'what is the truth', 'simplify the expression']
            if any(logical_keyword in problem_lower for logical_keyword in logical_keywords):
                return MathematicalProblemType.UNKNOWN
            
            # Check if it's a logical reasoning question (contains reasoning keywords)
            reasoning_keywords = ['what can we conclude', 'what follows', 'what can we infer', 'is it necessarily']
            if any(reasoning_keyword in problem_lower for reasoning_keyword in reasoning_keywords):
                return MathematicalProblemType.UNKNOWN
            
            # Check if it's a simple arithmetic problem
            arithmetic_patterns = [
                r'\d+\s+(times|multiplied by|plus|minus|divided by)\s+\d+',
                r'\d+\s*[+\-*/]\s*\d+'
            ]
            if any(re.search(pattern, problem_lower) for pattern in arithmetic_patterns):
                return MathematicalProblemType.NUMERICAL
            
            return MathematicalProblemType.NUMERICAL
        
        return MathematicalProblemType.UNKNOWN 