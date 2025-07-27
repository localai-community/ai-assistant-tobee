#!/usr/bin/env python3
"""
LocalAI Community Backend - Dependency Import Test
Tests all required dependencies one by one and reports any failures.
"""

import sys
import traceback
from typing import List, Dict, Tuple

def test_import(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """
    Test importing a module and return success status and error message.
    
    Args:
        module_name: The module name to import
        package_name: Optional package name (if different from module_name)
    
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        __import__(module_name)
        return True, ""
    except ImportError as e:
        error_msg = f"ImportError: {e}"
        if package_name and package_name != module_name:
            error_msg += f" (Try: pip install {package_name})"
        return False, error_msg
    except Exception as e:
        return False, f"Unexpected error: {e}\n{traceback.format_exc()}"

def test_dependencies() -> Dict[str, List[Tuple[str, bool, str]]]:
    """
    Test all dependencies organized by category.
    
    Returns:
        Dictionary with categories and their test results
    """
    results = {}
    
    # Core web framework
    print("🔧 Testing Core Web Framework...")
    web_framework_deps = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn[standard]"),
        ("sqlalchemy", "sqlalchemy"),
        ("alembic", "alembic"),
    ]
    
    web_results = []
    for module, package in web_framework_deps:
        success, error = test_import(module, package)
        web_results.append((module, success, error))
        status = "✅" if success else "❌"
        print(f"  {status} {module}")
        if not success:
            print(f"    Error: {error}")
    
    results["web_framework"] = web_results
    
    # HTTP client
    print("\n🌐 Testing HTTP Client...")
    http_deps = [
        ("httpx", "httpx"),
    ]
    
    http_results = []
    for module, package in http_deps:
        success, error = test_import(module, package)
        http_results.append((module, success, error))
        status = "✅" if success else "❌"
        print(f"  {status} {module}")
        if not success:
            print(f"    Error: {error}")
    
    results["http_client"] = http_results
    
    # RAG and AI
    print("\n🤖 Testing RAG and AI...")
    rag_deps = [
        ("langchain", "langchain"),
        ("chromadb", "chromadb"),
        ("sentence_transformers", "sentence-transformers"),
    ]
    
    rag_results = []
    for module, package in rag_deps:
        success, error = test_import(module, package)
        rag_results.append((module, success, error))
        status = "✅" if success else "❌"
        print(f"  {status} {module}")
        if not success:
            print(f"    Error: {error}")
    
    results["rag_ai"] = rag_results
    
    # Document processing
    print("\n📄 Testing Document Processing...")
    doc_deps = [
        ("unstructured", "unstructured[pdf,docx]"),
        ("docx", "python-docx"),  # python-docx imports as docx
    ]
    
    doc_results = []
    for module, package in doc_deps:
        success, error = test_import(module, package)
        doc_results.append((module, success, error))
        status = "✅" if success else "❌"
        print(f"  {status} {module}")
        if not success:
            print(f"    Error: {error}")
    
    results["document_processing"] = doc_results
    
    # Additional utilities
    print("\n🛠️  Testing Additional Utilities...")
    util_deps = [
        ("pydantic", "pydantic"),
        ("pydantic_settings", "pydantic-settings"),
        ("dotenv", "python-dotenv"),
    ]
    
    util_results = []
    for module, package in util_deps:
        success, error = test_import(module, package)
        util_results.append((module, success, error))
        status = "✅" if success else "❌"
        print(f"  {status} {module}")
        if not success:
            print(f"    Error: {error}")
    
    results["utilities"] = util_results
    
    return results

def print_summary(results: Dict[str, List[Tuple[str, bool, str]]]):
    """Print a summary of all test results."""
    print("\n" + "="*60)
    print("📊 DEPENDENCY TEST SUMMARY")
    print("="*60)
    
    total_tests = 0
    total_passed = 0
    failed_modules = []
    
    for category, tests in results.items():
        category_passed = sum(1 for _, success, _ in tests if success)
        category_total = len(tests)
        total_tests += category_total
        total_passed += category_passed
        
        print(f"\n{category.replace('_', ' ').title()}:")
        for module, success, error in tests:
            status = "✅" if success else "❌"
            print(f"  {status} {module}")
            if not success:
                failed_modules.append((module, error))
    
    print(f"\n📈 Overall Results:")
    print(f"  Total: {total_tests}")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_tests - total_passed}")
    print(f"  Success Rate: {(total_passed/total_tests)*100:.1f}%")
    
    if failed_modules:
        print(f"\n❌ Failed Modules:")
        for module, error in failed_modules:
            print(f"  • {module}: {error}")
        
        print(f"\n🔧 To fix failed imports, run:")
        print(f"  pip install -r requirements.txt")
        print(f"  # Or install specific packages:")
        for module, error in failed_modules:
            if "ImportError" in error and "pip install" in error:
                # Extract package name from error message
                import re
                match = re.search(r'pip install ([^\s]+)', error)
                if match:
                    print(f"  pip install {match.group(1)}")
    else:
        print(f"\n🎉 All dependencies imported successfully!")
        print(f"   Your backend environment is ready to use!")

def main():
    """Main function to run the dependency tests."""
    print("🧪 LocalAI Community Backend - Dependency Import Test")
    print("="*60)
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.executable}")
    print("="*60)
    
    try:
        results = test_dependencies()
        print_summary(results)
        
        # Return appropriate exit code
        total_failed = sum(
            sum(1 for _, success, _ in tests if not success)
            for tests in results.values()
        )
        
        if total_failed > 0:
            print(f"\n❌ Test failed with {total_failed} import errors")
            sys.exit(1)
        else:
            print(f"\n✅ All tests passed!")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 