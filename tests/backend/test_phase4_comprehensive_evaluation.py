#!/usr/bin/env python3
"""
Comprehensive Phase 4 Multi-Agent System Evaluation Test

This test file evaluates the quality of Phase 4 reasoning responses, agent selection,
and answer accuracy across all three categories: mathematical, logical, and causal.

Test Categories:
1. Mathematical Problems - Basic arithmetic, algebra, geometry
2. Logical Problems - Syllogistic reasoning, propositional logic, inference
3. Causal Problems - Cause-effect analysis, intervention studies

Evaluation Criteria:
- Agent Selection Accuracy
- Answer Quality and Correctness
- Reasoning Step Quality
- Confidence Score Appropriateness
- Response Completeness
"""

import unittest
import asyncio
import json
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.reasoning.agents import (
    SimplifiedHybridManager,
    create_all_local_agents,
    AgentTask,
    AgentResult
)
from app.reasoning.agents.base import LocalAgent


class Phase4ComprehensiveEvaluationTest(unittest.TestCase):
    """Comprehensive evaluation of Phase 4 multi-agent system."""
    
    def setUp(self):
        """Set up the test environment."""
        self.manager = SimplifiedHybridManager()
        
        # Register all local agents
        agents = create_all_local_agents()
        for agent in agents:
            self.manager.register_local_agent(agent)
        
        # Define comprehensive test questions for each category
        self.test_questions = {
            "mathematical": [
                {
                    "question": "What is 15 + 27? Please explain step by step.",
                    "expected_answer": "42",
                    "expected_agent": "mathematical_agent",
                    "expected_confidence": 0.8,
                    "category": "basic_arithmetic"
                },
                {
                    "question": "Solve the equation: 2x + 5 = 13",
                    "expected_answer": "x = 4",
                    "expected_agent": "mathematical_agent", 
                    "expected_confidence": 0.9,
                    "category": "algebra"
                },
                {
                    "question": "Calculate the area of a circle with radius 5 units",
                    "expected_answer": "78.54",  # π * 5² ≈ 78.54
                    "expected_agent": "mathematical_agent",
                    "expected_confidence": 0.9,
                    "category": "geometry"
                },
                {
                    "question": "What is 5 times 8?",
                    "expected_answer": "40",
                    "expected_agent": "mathematical_agent",
                    "expected_confidence": 0.9,
                    "category": "multiplication"
                },
                {
                    "question": "Find the derivative of x² + 3x + 1",
                    "expected_answer": "2x + 3",
                    "expected_agent": "mathematical_agent",
                    "expected_confidence": 0.8,
                    "category": "calculus"
                }
            ],
            "logical": [
                {
                    "question": "If all A are B, and some B are C, what can we conclude about A and C?",
                    "expected_answer": "Some A are C",
                    "expected_agent": "logical_agent",
                    "expected_confidence": 0.8,
                    "category": "syllogistic"
                },
                {
                    "question": "Three people are in a room. If Alice is older than Bob, and Bob is older than Charlie, who is the youngest?",
                    "expected_answer": "Charlie",
                    "expected_agent": "logical_agent",
                    "expected_confidence": 0.9,
                    "category": "transitive_reasoning"
                },
                {
                    "question": "A train leaves station A at 2 PM and arrives at station B at 4 PM. Another train leaves station B at 1 PM and arrives at station A at 3 PM. When do they meet?",
                    "expected_answer": "2:30 PM",
                    "expected_agent": "logical_agent",
                    "expected_confidence": 0.7,
                    "category": "time_logic"
                },
                {
                    "question": "Evaluate the logical expression: (A AND B) OR (NOT A)",
                    "expected_answer": "True when A is false or B is true",
                    "expected_agent": "logical_agent",
                    "expected_confidence": 0.8,
                    "category": "propositional_logic"
                },
                {
                    "question": "If P then Q. P is true. Is Q necessarily true?",
                    "expected_answer": "No, Q is not necessarily true",
                    "expected_agent": "logical_agent",
                    "expected_confidence": 0.9,
                    "category": "conditional_logic"
                }
            ],
            "causal": [
                {
                    "question": "What causes inflation and how does it affect the economy?",
                    "expected_answer": "Inflation is caused by...",
                    "expected_agent": "causal_agent",
                    "expected_confidence": 0.7,
                    "category": "economic_causality"
                },
                {
                    "question": "How does smoking affect lung cancer rates?",
                    "expected_answer": "Smoking increases lung cancer rates...",
                    "expected_agent": "causal_agent",
                    "expected_confidence": 0.8,
                    "category": "health_causality"
                },
                {
                    "question": "What are the effects of climate change on biodiversity?",
                    "expected_answer": "Climate change affects biodiversity by...",
                    "expected_agent": "causal_agent",
                    "expected_confidence": 0.7,
                    "category": "environmental_causality"
                },
                {
                    "question": "Does exercise cause better health outcomes?",
                    "expected_answer": "Exercise is associated with better health...",
                    "expected_agent": "causal_agent",
                    "expected_confidence": 0.8,
                    "category": "health_intervention"
                },
                {
                    "question": "What is the causal effect of education on income?",
                    "expected_answer": "Education has a positive causal effect on income...",
                    "expected_agent": "causal_agent",
                    "expected_confidence": 0.7,
                    "category": "social_causality"
                }
            ]
        }
        
        # Evaluation criteria weights
        self.evaluation_weights = {
            "agent_selection": 0.25,
            "answer_correctness": 0.35,
            "reasoning_quality": 0.25,
            "confidence_appropriateness": 0.15
        }
    
    def evaluate_agent_selection(self, result: Dict[str, Any], expected_agent: str) -> Dict[str, Any]:
        """Evaluate if the correct agent was selected."""
        actual_agent = result.get("agent_used", "unknown")
        is_correct = actual_agent == expected_agent
        
        return {
            "score": 1.0 if is_correct else 0.0,
            "expected": expected_agent,
            "actual": actual_agent,
            "is_correct": is_correct,
            "details": f"Expected {expected_agent}, got {actual_agent}"
        }
    
    def evaluate_answer_correctness(self, result: Dict[str, Any], expected_answer: str) -> Dict[str, Any]:
        """Evaluate if the answer is correct."""
        actual_answer = result.get("answer", "")
        
        # Simple string matching for now (could be enhanced with semantic similarity)
        is_correct = expected_answer.lower() in actual_answer.lower() or actual_answer.lower() in expected_answer.lower()
        
        return {
            "score": 1.0 if is_correct else 0.0,
            "expected": expected_answer,
            "actual": actual_answer,
            "is_correct": is_correct,
            "details": f"Expected answer contains '{expected_answer}', actual: '{actual_answer}'"
        }
    
    def evaluate_reasoning_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the quality of reasoning steps."""
        steps = result.get("reasoning_steps", [])
        confidence = result.get("confidence", 0.0)
        
        # Check if steps are present and detailed
        has_steps = len(steps) > 0
        step_quality = len(steps) >= 2  # At least 2 steps for good reasoning
        
        # Check confidence is reasonable
        confidence_reasonable = 0.0 <= confidence <= 1.0
        
        score = 0.0
        if has_steps and step_quality and confidence_reasonable:
            score = 1.0
        elif has_steps and confidence_reasonable:
            score = 0.7
        elif has_steps:
            score = 0.5
        else:
            score = 0.0
        
        return {
            "score": score,
            "has_steps": has_steps,
            "step_count": len(steps),
            "step_quality": step_quality,
            "confidence_reasonable": confidence_reasonable,
            "details": f"Steps: {len(steps)}, Quality: {step_quality}, Confidence: {confidence}"
        }
    
    def evaluate_confidence_appropriateness(self, result: Dict[str, Any], expected_confidence: float) -> Dict[str, Any]:
        """Evaluate if the confidence score is appropriate."""
        actual_confidence = result.get("confidence", 0.0)
        
        # Check if confidence is within reasonable range of expected
        confidence_diff = abs(actual_confidence - expected_confidence)
        is_appropriate = confidence_diff <= 0.3  # Allow 30% deviation
        
        return {
            "score": 1.0 if is_appropriate else 0.5,
            "expected": expected_confidence,
            "actual": actual_confidence,
            "difference": confidence_diff,
            "is_appropriate": is_appropriate,
            "details": f"Expected {expected_confidence}, got {actual_confidence} (diff: {confidence_diff})"
        }
    
    def calculate_overall_score(self, evaluations: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall evaluation score."""
        total_score = 0.0
        total_weight = 0.0
        
        for criterion, weight in self.evaluation_weights.items():
            if criterion in evaluations:
                total_score += evaluations[criterion]["score"] * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    async def test_mathematical_problems(self):
        """Test mathematical problem solving."""
        print("\n🔢 Testing Mathematical Problems")
        print("=" * 50)
        
        results = []
        for i, test_case in enumerate(self.test_questions["mathematical"]):
            print(f"\nTest {i+1}: {test_case['question']}")
            
            # Solve the problem
            result = await self.manager.solve_problem(
                test_case["question"], 
                task_type="mathematical"
            )
            
            # Evaluate the result
            evaluations = {
                "agent_selection": self.evaluate_agent_selection(result, test_case["expected_agent"]),
                "answer_correctness": self.evaluate_answer_correctness(result, test_case["expected_answer"]),
                "reasoning_quality": self.evaluate_reasoning_quality(result),
                "confidence_appropriateness": self.evaluate_confidence_appropriateness(result, test_case["expected_confidence"])
            }
            
            overall_score = self.calculate_overall_score(evaluations)
            
            # Store results
            test_result = {
                "question": test_case["question"],
                "category": test_case["category"],
                "result": result,
                "evaluations": evaluations,
                "overall_score": overall_score
            }
            results.append(test_result)
            
            # Print evaluation
            print(f"  Agent Selection: {evaluations['agent_selection']['score']:.2f} ({evaluations['agent_selection']['details']})")
            print(f"  Answer Correctness: {evaluations['answer_correctness']['score']:.2f} ({evaluations['answer_correctness']['details']})")
            print(f"  Reasoning Quality: {evaluations['reasoning_quality']['score']:.2f} ({evaluations['reasoning_quality']['details']})")
            print(f"  Confidence: {evaluations['confidence_appropriateness']['score']:.2f} ({evaluations['confidence_appropriateness']['details']})")
            print(f"  Overall Score: {overall_score:.2f}")
        
        # Calculate average score
        avg_score = sum(r["overall_score"] for r in results) / len(results)
        print(f"\n📊 Mathematical Problems Average Score: {avg_score:.2f}")
        
        return results
    
    async def test_logical_problems(self):
        """Test logical problem solving."""
        print("\n🧮 Testing Logical Problems")
        print("=" * 50)
        
        results = []
        for i, test_case in enumerate(self.test_questions["logical"]):
            print(f"\nTest {i+1}: {test_case['question']}")
            
            # Solve the problem
            result = await self.manager.solve_problem(
                test_case["question"], 
                task_type="logical"
            )
            
            # Evaluate the result
            evaluations = {
                "agent_selection": self.evaluate_agent_selection(result, test_case["expected_agent"]),
                "answer_correctness": self.evaluate_answer_correctness(result, test_case["expected_answer"]),
                "reasoning_quality": self.evaluate_reasoning_quality(result),
                "confidence_appropriateness": self.evaluate_confidence_appropriateness(result, test_case["expected_confidence"])
            }
            
            overall_score = self.calculate_overall_score(evaluations)
            
            # Store results
            test_result = {
                "question": test_case["question"],
                "category": test_case["category"],
                "result": result,
                "evaluations": evaluations,
                "overall_score": overall_score
            }
            results.append(test_result)
            
            # Print evaluation
            print(f"  Agent Selection: {evaluations['agent_selection']['score']:.2f} ({evaluations['agent_selection']['details']})")
            print(f"  Answer Correctness: {evaluations['answer_correctness']['score']:.2f} ({evaluations['answer_correctness']['details']})")
            print(f"  Reasoning Quality: {evaluations['reasoning_quality']['score']:.2f} ({evaluations['reasoning_quality']['details']})")
            print(f"  Confidence: {evaluations['confidence_appropriateness']['score']:.2f} ({evaluations['confidence_appropriateness']['details']})")
            print(f"  Overall Score: {overall_score:.2f}")
        
        # Calculate average score
        avg_score = sum(r["overall_score"] for r in results) / len(results)
        print(f"\n📊 Logical Problems Average Score: {avg_score:.2f}")
        
        return results
    
    async def test_causal_problems(self):
        """Test causal problem solving."""
        print("\n🔗 Testing Causal Problems")
        print("=" * 50)
        
        results = []
        for i, test_case in enumerate(self.test_questions["causal"]):
            print(f"\nTest {i+1}: {test_case['question']}")
            
            # Solve the problem
            result = await self.manager.solve_problem(
                test_case["question"], 
                task_type="causal"
            )
            
            # Evaluate the result
            evaluations = {
                "agent_selection": self.evaluate_agent_selection(result, test_case["expected_agent"]),
                "answer_correctness": self.evaluate_answer_correctness(result, test_case["expected_answer"]),
                "reasoning_quality": self.evaluate_reasoning_quality(result),
                "confidence_appropriateness": self.evaluate_confidence_appropriateness(result, test_case["expected_confidence"])
            }
            
            overall_score = self.calculate_overall_score(evaluations)
            
            # Store results
            test_result = {
                "question": test_case["question"],
                "category": test_case["category"],
                "result": result,
                "evaluations": evaluations,
                "overall_score": overall_score
            }
            results.append(test_result)
            
            # Print evaluation
            print(f"  Agent Selection: {evaluations['agent_selection']['score']:.2f} ({evaluations['agent_selection']['details']})")
            print(f"  Answer Correctness: {evaluations['answer_correctness']['score']:.2f} ({evaluations['answer_correctness']['details']})")
            print(f"  Reasoning Quality: {evaluations['reasoning_quality']['score']:.2f} ({evaluations['reasoning_quality']['details']})")
            print(f"  Confidence: {evaluations['confidence_appropriateness']['score']:.2f} ({evaluations['confidence_appropriateness']['details']})")
            print(f"  Overall Score: {overall_score:.2f}")
        
        # Calculate average score
        avg_score = sum(r["overall_score"] for r in results) / len(results)
        print(f"\n📊 Causal Problems Average Score: {avg_score:.2f}")
        
        return results
    
    async def test_agent_capabilities(self):
        """Test agent capabilities and availability."""
        print("\n🤖 Testing Agent Capabilities")
        print("=" * 50)
        
        # Get system status
        status = self.manager.get_system_status()
        
        print(f"Total Agents: {status['registry']['total_agents']}")
        print(f"Local Agents: {len(status['registry']['local_agents'])}")
        print(f"A2A Agents: {len(status['registry'].get('a2a_agents', []))}")
        
        # Test each agent type
        agent_tests = [
            ("mathematical", "mathematical_agent"),
            ("logical", "logical_agent"),
            ("causal", "causal_agent"),
            ("cot", "cot_agent"),
            ("tot", "tot_agent"),
            ("prompt_engineering", "prompt_engineering_agent"),
            ("general", "general_reasoning_agent")
        ]
        
        for task_type, expected_agent in agent_tests:
            agents = self.manager.registry.get_agents_for_task(task_type)
            available_agents = [agent.agent_id for agent in agents]
            
            print(f"\n{task_type.upper()} Task Type:")
            print(f"  Expected Agent: {expected_agent}")
            print(f"  Available Agents: {available_agents}")
            print(f"  Expected Agent Available: {expected_agent in available_agents}")
    
    async def test_general_problem_solving(self):
        """Test general problem solving with auto-detection."""
        print("\n🔄 Testing General Problem Solving (Auto-detection)")
        print("=" * 50)
        
        general_questions = [
            "What is 15 + 27?",
            "If all A are B and some B are C, what can we conclude?",
            "How does smoking affect health?",
            "Solve 2x + 3 = 7",
            "What causes inflation?"
        ]
        
        results = []
        for i, question in enumerate(general_questions):
            print(f"\nTest {i+1}: {question}")
            
            # Solve with general task type
            result = await self.manager.solve_problem(question, task_type="general")
            
            print(f"  Agent Used: {result.get('agent_used', 'unknown')}")
            print(f"  Confidence: {result.get('confidence', 0.0):.2f}")
            print(f"  Approach: {result.get('approach', 'unknown')}")
            
            results.append({
                "question": question,
                "result": result
            })
        
        return results
    
    def generate_evaluation_report(self, all_results: Dict[str, List[Dict[str, Any]]]):
        """Generate a comprehensive evaluation report."""
        print("\n" + "=" * 80)
        print("📊 PHASE 4 COMPREHENSIVE EVALUATION REPORT")
        print("=" * 80)
        
        # Calculate overall statistics
        total_tests = 0
        total_score = 0.0
        category_scores = {}
        
        for category, results in all_results.items():
            if results and len(results) > 0:
                category_score = sum(r["overall_score"] for r in results) / len(results)
                category_scores[category] = category_score
                total_tests += len(results)
                total_score += sum(r["overall_score"] for r in results)
        
        overall_score = total_score / total_tests if total_tests > 0 else 0.0
        
        # Print summary
        print(f"\n📈 OVERALL PERFORMANCE")
        print(f"Total Tests: {total_tests}")
        print(f"Overall Score: {overall_score:.2f}")
        
        print(f"\n📊 CATEGORY BREAKDOWN")
        for category, score in category_scores.items():
            print(f"{category.title()}: {score:.2f}")
        
        # Detailed analysis
        print(f"\n🔍 DETAILED ANALYSIS")
        for category, results in all_results.items():
            if results:
                print(f"\n{category.upper()} CATEGORY:")
                for i, result in enumerate(results):
                    score = result.get("overall_score", 0.0)
                    question = result["question"][:60] + "..." if len(result["question"]) > 60 else result["question"]
                    print(f"  {i+1}. Score: {score:.2f} - {question}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        if overall_score >= 0.8:
            print("✅ Excellent performance! Phase 4 system is working well.")
        elif overall_score >= 0.6:
            print("⚠️ Good performance with room for improvement.")
        else:
            print("❌ Performance needs significant improvement.")
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"phase4_evaluation_report_{timestamp}.json"
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": overall_score,
            "total_tests": total_tests,
            "category_scores": category_scores,
            "detailed_results": all_results,
            "evaluation_criteria": self.evaluation_weights
        }
        
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_filename}")
    
    async def run_comprehensive_evaluation(self):
        """Run the complete comprehensive evaluation."""
        print("🚀 Starting Phase 4 Comprehensive Evaluation")
        print("=" * 80)
        
        all_results = {}
        
        # Test agent capabilities first
        await self.test_agent_capabilities()
        
        # Test each category
        all_results["mathematical"] = await self.test_mathematical_problems()
        all_results["logical"] = await self.test_logical_problems()
        all_results["causal"] = await self.test_causal_problems()
        
        # Test general problem solving
        all_results["general"] = await self.test_general_problem_solving()
        
        # Generate comprehensive report
        self.generate_evaluation_report(all_results)
        
        return all_results


def run_phase4_evaluation():
    """Run the Phase 4 evaluation."""
    test = Phase4ComprehensiveEvaluationTest()
    test.setUp()
    
    # Run the evaluation
    asyncio.run(test.run_comprehensive_evaluation())


if __name__ == "__main__":
    run_phase4_evaluation() 