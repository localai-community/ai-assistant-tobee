"""
Comprehensive Auto-Detection Test Suite

This module tests the Phase 2 reasoning engine auto-detection mechanism with a variety of questions
to ensure proper routing to the correct engines.
"""

import sys
import os
import unittest
from typing import List, Tuple, Dict, Any

# Path is set by the test runner

from app.reasoning.engines import (
    MathematicalReasoningEngine,
    LogicalReasoningEngine,
    CausalReasoningEngine
)
from app.reasoning.core.base import ReasoningResult, StepStatus


class ComprehensiveAutoDetectionTest(unittest.TestCase):
    """Comprehensive test suite for auto-detection mechanism."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mathematical_engine = MathematicalReasoningEngine()
        self.logical_engine = LogicalReasoningEngine()
        self.causal_engine = CausalReasoningEngine()
        
        # Define test questions for each category
        self.test_questions = {
            "mathematical": [
                # Basic algebraic
                "Solve 2x + 3 = 7",
                "Find the value of x in the equation x² - 4x + 3 = 0",
                "Solve for y: 3y - 5 = 10",
                
                # Geometric
                "Calculate the area of a circle with radius 5",
                "Find the perimeter of a rectangle with length 10 and width 5",
                "What is the area of a triangle with base 6 and height 4?",
                
                # Calculus
                "Find the derivative of f(x) = x³ + 2x² - 5x + 3",
                "Calculate the integral of x² dx",
                "Differentiate y = sin(x) + cos(x)",
                
                # Complex mathematical
                "Evaluate the limit as x approaches 0 of (sin x)/x"
            ],
            
            "logical": [
                # Syllogistic reasoning
                "All A are B. Some B are C. What can we conclude?",
                "No mammals are fish. All whales are mammals. What follows?",
                "Some students are athletes. All athletes are healthy. What can we infer?",
                
                # Propositional logic
                "Evaluate the logical expression: (A AND B) OR (NOT A)",
                "What is the truth value of P AND (NOT P)?",
                "Simplify the expression: (A OR B) AND (A OR NOT B)",
                
                # Conditional reasoning
                "If P then Q. P is true. Is Q necessarily true?",
                "If it rains, the ground gets wet. The ground is wet. Did it rain?",
                "All squares are rectangles. This shape is a square. Is it a rectangle?",
                
                # Proof and inference
                "Prove that if x > 0 and y > 0, then x + y > 0"
            ],
            
            "causal": [
                # Health and medicine
                "Does smoking cause lung cancer? Assume S = smoking, L = lung cancer",
                "What is the causal effect of exercise on heart disease?",
                "Does diet affect diabetes risk?",
                
                # Education and economics
                "What is the causal effect of education on income?",
                "Does class size affect student performance?",
                "What causes inflation in the economy?",
                
                # Social and behavioral
                "Does social media use cause depression?",
                "What is the effect of sleep deprivation on cognitive function?",
                "Does parental involvement cause better academic outcomes?",
                
                # Environmental
                "Does carbon dioxide emissions cause global warming?"
            ],
            
            "ambiguous": [
                # Questions that could be interpreted multiple ways
                "What is the relationship between A and B?",
                "Analyze the effect of X on Y",
                "Find the connection between these variables",
                "What causes this outcome?",
                "Evaluate the impact of this factor",
                "Determine the relationship",
                "What is the effect?",
                "Find the correlation",
                "Analyze the pattern",
                "What is the connection?"
            ],
            
            "edge_cases": [
                # Edge cases and unusual questions
                "What is 2+2?",
                "Is this true or false?",
                "What do you think?",
                "Can you help me?",
                "I don't understand this",
                "Please explain",
                "What's the answer?",
                "How do I solve this?",
                "What should I do?",
                "Help me understand"
            ]
        }
    
    def test_mathematical_questions(self):
        """Test that mathematical questions are correctly identified."""
        print("\n🔢 Testing Mathematical Questions:")
        print("=" * 50)
        
        correct = 0
        total = len(self.test_questions["mathematical"])
        
        for i, question in enumerate(self.test_questions["mathematical"], 1):
            print(f"\n{i}. {question}")
            
            # Test individual engine capabilities
            math_can = self.mathematical_engine.can_handle(question)
            logic_can = self.logical_engine.can_handle(question)
            causal_can = self.causal_engine.can_handle(question)
            
            print(f"   Math: {math_can}, Logic: {logic_can}, Causal: {causal_can}")
            
            # Test auto-detection logic
            detected_engine = self._auto_detect_engine(question)
            print(f"   Auto-detected: {detected_engine}")
            
            if detected_engine == "mathematical":
                print("   ✅ CORRECT")
                correct += 1
            else:
                print(f"   ❌ INCORRECT - Expected: mathematical, Got: {detected_engine}")
            
            # Assert that mathematical engine can handle it
            self.assertTrue(math_can, f"Mathematical engine should handle: {question}")
        
        print(f"\n🎯 Mathematical Results: {correct}/{total} correct ({correct/total*100:.1f}%)")
        self.assertEqual(correct, total, f"All mathematical questions should be correctly detected")
    
    def test_logical_questions(self):
        """Test that logical questions are correctly identified."""
        print("\n🧮 Testing Logical Questions:")
        print("=" * 50)
        
        correct = 0
        total = len(self.test_questions["logical"])
        
        for i, question in enumerate(self.test_questions["logical"], 1):
            print(f"\n{i}. {question}")
            
            # Test individual engine capabilities
            math_can = self.mathematical_engine.can_handle(question)
            logic_can = self.logical_engine.can_handle(question)
            causal_can = self.causal_engine.can_handle(question)
            
            print(f"   Math: {math_can}, Logic: {logic_can}, Causal: {causal_can}")
            
            # Test auto-detection logic
            detected_engine = self._auto_detect_engine(question)
            print(f"   Auto-detected: {detected_engine}")
            
            if detected_engine == "logical":
                print("   ✅ CORRECT")
                correct += 1
            else:
                print(f"   ❌ INCORRECT - Expected: logical, Got: {detected_engine}")
            
            # Assert that logical engine can handle it
            self.assertTrue(logic_can, f"Logical engine should handle: {question}")
        
        print(f"\n🎯 Logical Results: {correct}/{total} correct ({correct/total*100:.1f}%)")
        self.assertEqual(correct, total, f"All logical questions should be correctly detected")
    
    def test_causal_questions(self):
        """Test that causal questions are correctly identified."""
        print("\n🔗 Testing Causal Questions:")
        print("=" * 50)
        
        correct = 0
        total = len(self.test_questions["causal"])
        
        for i, question in enumerate(self.test_questions["causal"], 1):
            print(f"\n{i}. {question}")
            
            # Test individual engine capabilities
            math_can = self.mathematical_engine.can_handle(question)
            logic_can = self.logical_engine.can_handle(question)
            causal_can = self.causal_engine.can_handle(question)
            
            print(f"   Math: {math_can}, Logic: {logic_can}, Causal: {causal_can}")
            
            # Test auto-detection logic
            detected_engine = self._auto_detect_engine(question)
            print(f"   Auto-detected: {detected_engine}")
            
            if detected_engine == "causal":
                print("   ✅ CORRECT")
                correct += 1
            else:
                print(f"   ❌ INCORRECT - Expected: causal, Got: {detected_engine}")
            
            # Assert that causal engine can handle it
            self.assertTrue(causal_can, f"Causal engine should handle: {question}")
        
        print(f"\n🎯 Causal Results: {correct}/{total} correct ({correct/total*100:.1f}%)")
        self.assertEqual(correct, total, f"All causal questions should be correctly detected")
    
    def test_ambiguous_questions(self):
        """Test how the system handles ambiguous questions."""
        print("\n❓ Testing Ambiguous Questions:")
        print("=" * 50)
        
        for i, question in enumerate(self.test_questions["ambiguous"], 1):
            print(f"\n{i}. {question}")
            
            # Test individual engine capabilities
            math_can = self.mathematical_engine.can_handle(question)
            logic_can = self.logical_engine.can_handle(question)
            causal_can = self.causal_engine.can_handle(question)
            
            print(f"   Math: {math_can}, Logic: {logic_can}, Causal: {causal_can}")
            
            # Test auto-detection logic
            detected_engine = self._auto_detect_engine(question)
            print(f"   Auto-detected: {detected_engine}")
            
            # For ambiguous questions, we just want to see the behavior
            print(f"   📊 Behavior observed")
        
        print(f"\n📊 Ambiguous questions tested - behavior documented")
    
    def test_edge_cases(self):
        """Test how the system handles edge cases and unusual questions."""
        print("\n🔍 Testing Edge Cases:")
        print("=" * 50)
        
        for i, question in enumerate(self.test_questions["edge_cases"], 1):
            print(f"\n{i}. {question}")
            
            # Test individual engine capabilities
            math_can = self.mathematical_engine.can_handle(question)
            logic_can = self.logical_engine.can_handle(question)
            causal_can = self.causal_engine.can_handle(question)
            
            print(f"   Math: {math_can}, Logic: {logic_can}, Causal: {causal_can}")
            
            # Test auto-detection logic
            detected_engine = self._auto_detect_engine(question)
            print(f"   Auto-detected: {detected_engine}")
            
            # For edge cases, we just want to see the behavior
            print(f"   📊 Behavior observed")
        
        print(f"\n📊 Edge cases tested - behavior documented")
    
    def test_engine_priority(self):
        """Test that engine priority is correctly implemented."""
        print("\n⚖️ Testing Engine Priority:")
        print("=" * 50)
        
        # Test questions that could be claimed by multiple engines
        priority_test_questions = [
            ("Does smoking cause lung cancer?", "causal"),  # Should be causal, not mathematical
            ("Evaluate the logical expression: (A AND B) OR (NOT A)", "logical"),  # Should be logical, not mathematical
            ("Calculate the causal effect of X on Y", "causal"),  # Should be causal, not mathematical
            ("Find the logical relationship between A and B", "logical"),  # Should be logical, not mathematical
            ("Prove that if X causes Y, then Y depends on X", "logical"),  # Should be logical, not causal
        ]
        
        correct = 0
        total = len(priority_test_questions)
        
        for question, expected in priority_test_questions:
            print(f"\nQuestion: {question}")
            print(f"Expected: {expected}")
            
            # Test individual engine capabilities
            math_can = self.mathematical_engine.can_handle(question)
            logic_can = self.logical_engine.can_handle(question)
            causal_can = self.causal_engine.can_handle(question)
            
            print(f"Math: {math_can}, Logic: {logic_can}, Causal: {causal_can}")
            
            # Test auto-detection logic
            detected_engine = self._auto_detect_engine(question)
            print(f"Auto-detected: {detected_engine}")
            
            if detected_engine == expected:
                print("✅ CORRECT")
                correct += 1
            else:
                print(f"❌ INCORRECT - Expected: {expected}, Got: {detected_engine}")
        
        print(f"\n🎯 Priority Results: {correct}/{total} correct ({correct/total*100:.1f}%)")
        self.assertGreaterEqual(correct, total * 0.8, f"At least 80% of priority tests should pass")
    
    def test_comprehensive_statistics(self):
        """Generate comprehensive statistics for all test questions."""
        print("\n📊 Comprehensive Statistics:")
        print("=" * 50)
        
        all_questions = []
        for category, questions in self.test_questions.items():
            for question in questions:
                all_questions.append((question, category))
        
        # Collect statistics
        stats = {
            "mathematical": {"correct": 0, "total": 0, "claimed_by_others": 0},
            "logical": {"correct": 0, "total": 0, "claimed_by_others": 0},
            "causal": {"correct": 0, "total": 0, "claimed_by_others": 0},
            "ambiguous": {"total": 0, "distribution": {}},
            "edge_cases": {"total": 0, "distribution": {}}
        }
        
        for question, expected_category in all_questions:
            detected_engine = self._auto_detect_engine(question)
            
            if expected_category in ["mathematical", "logical", "causal"]:
                stats[expected_category]["total"] += 1
                if detected_engine == expected_category:
                    stats[expected_category]["correct"] += 1
                else:
                    stats[expected_category]["claimed_by_others"] += 1
            else:
                stats[expected_category]["total"] += 1
                if expected_category not in stats[expected_category]["distribution"]:
                    stats[expected_category]["distribution"][detected_engine] = 0
                stats[expected_category]["distribution"][detected_engine] += 1
        
        # Print statistics
        for category in ["mathematical", "logical", "causal"]:
            if stats[category]["total"] > 0:
                accuracy = stats[category]["correct"] / stats[category]["total"] * 100
                print(f"\n{category.title()} Questions:")
                print(f"  Total: {stats[category]['total']}")
                print(f"  Correctly detected: {stats[category]['correct']}")
                print(f"  Incorrectly claimed by others: {stats[category]['claimed_by_others']}")
                print(f"  Accuracy: {accuracy:.1f}%")
        
        for category in ["ambiguous", "edge_cases"]:
            if stats[category]["total"] > 0:
                print(f"\n{category.title()} Questions:")
                print(f"  Total: {stats[category]['total']}")
                print(f"  Distribution: {stats[category]['distribution']}")
        
        # Overall accuracy
        total_correct = sum(stats[cat]["correct"] for cat in ["mathematical", "logical", "causal"])
        total_questions = sum(stats[cat]["total"] for cat in ["mathematical", "logical", "causal"])
        overall_accuracy = total_correct / total_questions * 100 if total_questions > 0 else 0
        
        print(f"\n🎯 Overall Accuracy: {overall_accuracy:.1f}% ({total_correct}/{total_questions})")
        
        # Assert minimum accuracy
        self.assertGreaterEqual(overall_accuracy, 90.0, f"Overall accuracy should be at least 90%, got {overall_accuracy:.1f}%")
    
    def _auto_detect_engine(self, message: str) -> str:
        """Replicate the auto-detection logic from the API."""
        message_lower = message.lower()
        
        # Causal keywords (highest priority)
        causal_keywords = ['cause', 'causes', 'causing', 'caused by', 'causal', 'effect', 'relationship', 'smoking', 'lung cancer', 'affect', 'affects', 'affecting']
        if any(keyword in message_lower for keyword in causal_keywords) and self.causal_engine.can_handle(message):
            return "causal"
        
        # Logical keywords (second priority)
        logical_keywords = ['logical expression', 'logical operator', 'and', 'or', 'not', 'implies', 'boolean', 'logic', 'proposition', 'truth table', 'if', 'then']
        if any(keyword in message_lower for keyword in logical_keywords) and self.logical_engine.can_handle(message):
            return "logical"
        
        # Mathematical engine (third priority)
        if self.mathematical_engine.can_handle(message):
            return "mathematical"
        
        # Logical engine (fallback for logical questions)
        if self.logical_engine.can_handle(message):
            return "logical"
        
        # Causal engine (fallback for causal questions)
        if self.causal_engine.can_handle(message):
            return "causal"
        
        # Default fallback
        return "mathematical"


def run_comprehensive_test():
    """Run the comprehensive auto-detection test."""
    print("🚀 Comprehensive Auto-Detection Test Suite")
    print("=" * 60)
    print("This test suite evaluates the Phase 2 reasoning engine")
    print("auto-detection mechanism with 50+ different questions.")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(ComprehensiveAutoDetectionTest)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    if not result.failures and not result.errors:
        print("\n🎉 ALL TESTS PASSED!")
        print("The auto-detection mechanism is working correctly.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 