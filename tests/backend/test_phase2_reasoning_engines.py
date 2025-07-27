"""
Phase 2: Basic Reasoning Engines - Test Suite

This module tests the three basic reasoning engines implemented in Phase 2:
- Mathematical Reasoning Engine
- Logical Reasoning Engine
- Causal Reasoning Engine
"""

import sys
import os
import unittest
from typing import Dict, Any

# Path is set by the test runner

from app.reasoning.engines import (
    MathematicalReasoningEngine,
    LogicalReasoningEngine,
    CausalReasoningEngine
)
from app.reasoning.core.base import ReasoningResult, StepStatus


class TestMathematicalReasoningEngine(unittest.TestCase):
    """Test cases for the Mathematical Reasoning Engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = MathematicalReasoningEngine()
    
    def test_can_handle_algebraic_problems(self):
        """Test that the engine can handle algebraic problems."""
        problems = [
            "Solve 2x + 3 = 7",
            "Find the value of x in the equation x² - 4x + 3 = 0",
            "Solve for y: 3y - 5 = 10"
        ]
        
        for problem in problems:
            with self.subTest(problem=problem):
                self.assertTrue(self.engine.can_handle(problem))
    
    def test_can_handle_geometric_problems(self):
        """Test that the engine can handle geometric problems."""
        problems = [
            "Calculate the area of a circle with radius 5",
            "Find the perimeter of a rectangle with length 10 and width 5",
            "What is the area of a triangle with base 6 and height 4?"
        ]
        
        for problem in problems:
            with self.subTest(problem=problem):
                self.assertTrue(self.engine.can_handle(problem))
    
    def test_can_handle_calculus_problems(self):
        """Test that the engine can handle calculus problems."""
        problems = [
            "Find the derivative of f(x) = x³ + 2x² - 5x + 3",
            "Calculate the integral of x² dx",
            "Differentiate y = sin(x) + cos(x)"
        ]
        
        for problem in problems:
            with self.subTest(problem=problem):
                self.assertTrue(self.engine.can_handle(problem))
    
    def test_solve_algebraic_problem(self):
        """Test solving an algebraic problem."""
        problem = "Solve 2x + 3 = 7"
        result = self.engine.solve(problem)
        
        self.assertIsInstance(result, ReasoningResult)
        self.assertEqual(result.problem_statement, problem)
        self.assertEqual(result.reasoning_type.value, "mathematical")
        self.assertGreater(len(result.steps), 0)
        self.assertGreater(result.confidence, 0.0)
        
        # Check that all steps are completed
        for step in result.steps:
            self.assertIn(step.status, [StepStatus.COMPLETED, StepStatus.FAILED])
    
    def test_solve_geometric_problem(self):
        """Test solving a geometric problem."""
        problem = "Calculate the area of a circle with radius 5"
        result = self.engine.solve(problem)
        
        self.assertIsInstance(result, ReasoningResult)
        self.assertEqual(result.problem_statement, problem)
        self.assertEqual(result.reasoning_type.value, "mathematical")
        self.assertGreater(len(result.steps), 0)
        self.assertGreater(result.confidence, 0.0)
    
    def test_problem_classification(self):
        """Test problem type classification."""
        test_cases = [
            ("Solve 2x + 3 = 7", "algebraic"),
            ("Calculate the area of a circle", "geometric"),
            ("Find the derivative of f(x)", "calculus"),
            ("What is the mean of 1, 2, 3, 4, 5?", "statistical"),
            ("Calculate sin(30°)", "trigonometric"),
            ("Random text that's not mathematical", "unknown")
        ]
        
        for problem, expected_type in test_cases:
            with self.subTest(problem=problem):
                problem_type = self.engine.problem_classifier.classify(problem)
                self.assertEqual(problem_type.value, expected_type)


class TestLogicalReasoningEngine(unittest.TestCase):
    """Test cases for the Logical Reasoning Engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = LogicalReasoningEngine()
    
    def test_can_handle_propositional_problems(self):
        """Test that the engine can handle propositional logic problems."""
        problems = [
            "Evaluate P and Q where P is true and Q is false",
            "What is the truth value of A implies B?",
            "Create a truth table for P or Q"
        ]
        
        for problem in problems:
            with self.subTest(problem=problem):
                self.assertTrue(self.engine.can_handle(problem))
    
    def test_can_handle_syllogistic_problems(self):
        """Test that the engine can handle syllogistic reasoning problems."""
        problems = [
            "All roses are flowers. Some flowers are red. What can we conclude?",
            "Premise 1: All A are B. Premise 2: All B are C. Conclusion: All A are C",
            "If all mammals are animals and all dogs are mammals, then all dogs are animals"
        ]
        
        for problem in problems:
            with self.subTest(problem=problem):
                self.assertTrue(self.engine.can_handle(problem))
    
    def test_can_handle_inference_problems(self):
        """Test that the engine can handle logical inference problems."""
        problems = [
            "Given P implies Q and P is true, what can we infer?",
            "Use modus ponens to deduce the conclusion",
            "If A then B. A is true. Therefore B is true"
        ]
        
        for problem in problems:
            with self.subTest(problem=problem):
                self.assertTrue(self.engine.can_handle(problem))
    
    def test_solve_syllogistic_problem(self):
        """Test solving a syllogistic reasoning problem."""
        problem = "All roses are flowers. Some flowers are red. What can we conclude?"
        result = self.engine.solve(problem)
        
        self.assertIsInstance(result, ReasoningResult)
        self.assertEqual(result.problem_statement, problem)
        self.assertEqual(result.reasoning_type.value, "logical")
        self.assertGreater(len(result.steps), 0)
        self.assertGreater(result.confidence, 0.0)
        
        # Check that all steps are completed
        for step in result.steps:
            self.assertIn(step.status, [StepStatus.COMPLETED, StepStatus.FAILED])
    
    def test_extract_propositions(self):
        """Test proposition extraction."""
        problem = "P = It is raining. Q = The ground is wet. R = I will stay inside."
        propositions = self.engine._extract_propositions(problem)
        
        self.assertIn('P', propositions)
        self.assertIn('Q', propositions)
        self.assertIn('R', propositions)
        self.assertEqual(propositions['P'].description, "It is raining")
    
    def test_extract_premises(self):
        """Test premise extraction."""
        problem = "Given that all A are B. Assume that some B are C. Therefore, some A are C."
        premises = self.engine._extract_premises(problem)
        
        self.assertGreater(len(premises), 0)
        self.assertTrue(any("all A are B" in premise for premise in premises))
    
    def test_problem_classification(self):
        """Test problem type classification."""
        test_cases = [
            ("Evaluate P and Q", "propositional"),
            ("All A are B. Some B are C", "syllogistic"),
            ("Given P implies Q", "inference"),
            ("Prove that A implies B", "proof"),
            ("Check if the argument is consistent", "consistency"),
            ("Random text that's not logical", "unknown")
        ]
        
        for problem, expected_type in test_cases:
            with self.subTest(problem=problem):
                problem_type = self.engine.problem_classifier.classify(problem)
                self.assertEqual(problem_type.value, expected_type)


class TestCausalReasoningEngine(unittest.TestCase):
    """Test cases for the Causal Reasoning Engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = CausalReasoningEngine()
    
    def test_can_handle_identification_problems(self):
        """Test that the engine can handle causal identification problems."""
        problems = [
            "Does smoking cause lung cancer?",
            "Identify the causal effect of education on income",
            "What is the causal relationship between exercise and health?"
        ]
        
        for problem in problems:
            with self.subTest(problem=problem):
                self.assertTrue(self.engine.can_handle(problem))
    
    def test_can_handle_intervention_problems(self):
        """Test that the engine can handle intervention analysis problems."""
        problems = [
            "What would happen if we implement a new policy?",
            "How would a treatment intervention affect the outcome?",
            "What is the effect of changing variable X?"
        ]
        
        for problem in problems:
            with self.subTest(problem=problem):
                self.assertTrue(self.engine.can_handle(problem))
    
    def test_can_handle_counterfactual_problems(self):
        """Test that the engine can handle counterfactual reasoning problems."""
        problems = [
            "What would have happened if the treatment was different?",
            "Counterfactual: What if the policy was not implemented?",
            "Would the outcome be different if we had intervened?"
        ]
        
        for problem in problems:
            with self.subTest(problem=problem):
                self.assertTrue(self.engine.can_handle(problem))
    
    def test_solve_identification_problem(self):
        """Test solving a causal identification problem."""
        problem = "Does smoking cause lung cancer? Assume S = smoking, L = lung cancer"
        result = self.engine.solve(problem)
        
        self.assertIsInstance(result, ReasoningResult)
        self.assertEqual(result.problem_statement, problem)
        self.assertEqual(result.reasoning_type.value, "causal")
        self.assertGreater(len(result.steps), 0)
        self.assertGreater(result.confidence, 0.0)
        
        # Check that all steps are completed
        for step in result.steps:
            self.assertIn(step.status, [StepStatus.COMPLETED, StepStatus.FAILED])
    
    def test_extract_variables(self):
        """Test variable extraction."""
        problem = "T = treatment, O = outcome, C = confounder"
        variables = self.engine._extract_variables(problem)
        
        self.assertIn('T', variables)
        self.assertIn('O', variables)
        self.assertIn('C', variables)
        self.assertEqual(variables['T'].description, "treatment")
    
    def test_extract_relationships(self):
        """Test causal relationship extraction."""
        problem = "T causes O. C affects O. T → O"
        relationships = self.engine._extract_relationships(problem)
        
        self.assertGreater(len(relationships), 0)
        self.assertTrue(any(rel.cause == 'T' and rel.effect == 'O' for rel in relationships))
    
    def test_extract_interventions(self):
        """Test intervention extraction."""
        problem = "What if we change the treatment? How would a policy intervention affect the outcome?"
        interventions = self.engine._extract_interventions(problem)
        
        self.assertGreater(len(interventions), 0)
        self.assertTrue(any("change" in intervention.lower() for intervention in interventions))
    
    def test_classify_variable_type(self):
        """Test variable type classification."""
        test_cases = [
            ("treatment", "treatment"),
            ("outcome", "outcome"),
            ("confounder", "confounder"),
            ("mediator", "mediator"),
            ("random variable", "variable")
        ]
        
        for description, expected_type in test_cases:
            with self.subTest(description=description):
                var_type = self.engine._classify_variable_type(description)
                self.assertEqual(var_type, expected_type)
    
    def test_problem_classification(self):
        """Test problem type classification."""
        test_cases = [
            ("Does X cause Y?", "identification"),
            ("What if we intervene on X?", "intervention"),
            ("What would have happened if...?", "counterfactual"),
            ("Estimate the causal effect", "effect_estimation"),
            ("Draw a causal graph", "graph_construction"),
            ("Random text that's not causal", "unknown")
        ]
        
        for problem, expected_type in test_cases:
            with self.subTest(problem=problem):
                problem_type = self.engine.problem_classifier.classify(problem)
                self.assertEqual(problem_type.value, expected_type)


class TestReasoningEngineIntegration(unittest.TestCase):
    """Test cases for reasoning engine integration."""
    
    def test_engine_selection(self):
        """Test that the appropriate engine is selected for different problem types."""
        mathematical_engine = MathematicalReasoningEngine()
        logical_engine = LogicalReasoningEngine()
        causal_engine = CausalReasoningEngine()
        
        # Test mathematical problems
        math_problems = [
            "Solve 2x + 3 = 7",
            "Calculate the area of a circle",
            "Find the derivative of f(x)"
        ]
        
        for problem in math_problems:
            with self.subTest(problem=problem):
                self.assertTrue(mathematical_engine.can_handle(problem))
                self.assertFalse(logical_engine.can_handle(problem))
                self.assertFalse(causal_engine.can_handle(problem))
        
        # Test logical problems
        logic_problems = [
            "All A are B. Some B are C",
            "Evaluate P and Q",
            "Use modus ponens"
        ]
        
        for problem in logic_problems:
            with self.subTest(problem=problem):
                self.assertFalse(mathematical_engine.can_handle(problem))
                self.assertTrue(logical_engine.can_handle(problem))
                self.assertFalse(causal_engine.can_handle(problem))
        
        # Test causal problems
        causal_problems = [
            "Does X cause Y?",
            "What if we intervene on X?",
            "What would have happened if...?"
        ]
        
        for problem in causal_problems:
            with self.subTest(problem=problem):
                self.assertFalse(mathematical_engine.can_handle(problem))
                self.assertFalse(logical_engine.can_handle(problem))
                self.assertTrue(causal_engine.can_handle(problem))
    
    def test_engine_consistency(self):
        """Test that engines produce consistent results."""
        mathematical_engine = MathematicalReasoningEngine()
        logical_engine = LogicalReasoningEngine()
        causal_engine = CausalReasoningEngine()
        
        # Test that all engines return ReasoningResult objects
        math_result = mathematical_engine.solve("Solve 2x + 3 = 7")
        logic_result = logical_engine.solve("All A are B. Some B are C")
        causal_result = causal_engine.solve("Does X cause Y?")
        
        self.assertIsInstance(math_result, ReasoningResult)
        self.assertIsInstance(logic_result, ReasoningResult)
        self.assertIsInstance(causal_result, ReasoningResult)
        
        # Test that all results have required attributes
        for result in [math_result, logic_result, causal_result]:
            self.assertIsInstance(result.problem_statement, str)
            self.assertIsInstance(result.steps, list)
            self.assertIsInstance(result.confidence, float)
            self.assertIsInstance(result.reasoning_type.value, str)


def run_phase2_tests():
    """Run all Phase 2 reasoning engine tests."""
    print("🧪 Running Phase 2: Basic Reasoning Engines Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestMathematicalReasoningEngine))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestLogicalReasoningEngine))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCausalReasoningEngine))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestReasoningEngineIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Phase 2 Test Results Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    if not result.failures and not result.errors:
        print("\n✅ All Phase 2 tests passed!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_phase2_tests()
    sys.exit(0 if success else 1) 