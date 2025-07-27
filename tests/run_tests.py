#!/usr/bin/env python3
"""
Test Runner for AI Assistant

This script provides a convenient way to run tests from the organized test structure.
"""

import os
import sys
import unittest
import argparse
from pathlib import Path

# Set up paths for all test categories
def setup_test_paths():
    """Set up Python paths for all test categories."""
    # Backend paths - prioritize backend app directory
    backend_app_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')
    backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
    
    # Frontend paths - only add for frontend tests
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    
    # Add backend paths first (higher priority)
    for path in [backend_app_path, backend_path]:
        if path not in sys.path:
            sys.path.insert(0, path)

# Set up paths when module is imported
setup_test_paths()

def run_backend_tests():
    """Run all backend tests."""
    print("🧪 Running Backend Tests...")
    
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'backend')
    suite = loader.discover(start_dir, pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def run_frontend_tests():
    """Run all frontend tests."""
    print("🧪 Running Frontend Tests...")
    
    # Add frontend path for frontend tests
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    if frontend_path not in sys.path:
        sys.path.insert(0, frontend_path)
    
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    suite = loader.discover(start_dir, pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def run_integration_tests():
    """Run all integration tests."""
    print("🧪 Running Integration Tests...")
    
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'integration')
    suite = loader.discover(start_dir, pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def run_unit_tests():
    """Run all unit tests."""
    print("🧪 Running Unit Tests...")
    
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'unit')
    suite = loader.discover(start_dir, pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def run_all_tests():
    """Run all tests."""
    print("🚀 Running All Tests...")
    print("=" * 50)
    
    results = []
    
    # Run each test category
    results.append(("Backend", run_backend_tests()))
    results.append(("Frontend", run_frontend_tests()))
    results.append(("Integration", run_integration_tests()))
    results.append(("Unit", run_unit_tests()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for category, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{category:12} {status}")
        if not success:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED!")
    
    return all_passed

def run_specific_test(test_path):
    """Run a specific test file."""
    print(f"🧪 Running specific test: {test_path}")
    
    # Add the test directory to Python path
    test_dir = os.path.dirname(test_path)
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)
    
    # Run the specific test
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(test_path), pattern=os.path.basename(test_path))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def main():
    parser = argparse.ArgumentParser(description='Run AI Assistant tests')
    parser.add_argument('--category', choices=['backend', 'frontend', 'integration', 'unit', 'all'],
                       default='all', help='Test category to run')
    parser.add_argument('--test', help='Specific test file to run')
    
    args = parser.parse_args()
    
    if args.test:
        success = run_specific_test(args.test)
    elif args.category == 'backend':
        success = run_backend_tests()
    elif args.category == 'frontend':
        success = run_frontend_tests()
    elif args.category == 'integration':
        success = run_integration_tests()
    elif args.category == 'unit':
        success = run_unit_tests()
    else:  # all
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 