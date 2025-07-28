#!/usr/bin/env python3
"""
Phase 4 Evaluation Runner

This script runs the comprehensive Phase 4 evaluation to test the quality
of answers, agent selection, and reasoning across all categories.
"""

import sys
import os
import asyncio

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import the evaluation test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tests', 'backend'))
from test_phase4_comprehensive_evaluation import run_phase4_evaluation


def main():
    """Run the Phase 4 evaluation."""
    print("🚀 Phase 4 Multi-Agent System Evaluation")
    print("=" * 60)
    print("This will test:")
    print("✅ Mathematical problems (arithmetic, algebra, geometry)")
    print("✅ Logical problems (syllogistic, propositional logic)")
    print("✅ Causal problems (cause-effect analysis)")
    print("✅ Agent selection accuracy")
    print("✅ Answer quality and correctness")
    print("✅ Reasoning step quality")
    print("✅ Confidence score appropriateness")
    print("=" * 60)
    
    try:
        # Run the evaluation
        results = run_phase4_evaluation()
        
        print("\n✅ Evaluation completed successfully!")
        print("📄 Check the generated report file for detailed results.")
        
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 