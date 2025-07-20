#!/usr/bin/env python3
"""
LocalAI Community Frontend - Dependency Import Test
Tests all required dependencies for the frontend.
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
    Test all frontend dependencies organized by category.
    
    Returns:
        Dictionary with categories and their test results
    """
    results = {}
    
    # Streamlit framework
    print("🤖 Testing Streamlit Framework...")
    streamlit_deps = [
        ("streamlit", "streamlit"),
    ]
    
    streamlit_results = []
    for module, package in streamlit_deps:
        success, error = test_import(module, package)
        streamlit_results.append((module, success, error))
        status = "✅" if success else "❌"
        print(f"  {status} {module}")
        if not success:
            print(f"    Error: {error}")
    
    results["streamlit_framework"] = streamlit_results
    
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
    
    # Utilities
    print("\n🛠️  Testing Utilities...")
    util_deps = [
        ("dotenv", "python-dotenv"),
        ("pydantic", "pydantic"),
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

def test_backend_connectivity():
    """Test connectivity to the backend."""
    print("\n🔗 Testing Backend Connectivity...")
    
    try:
        import httpx
        import asyncio
        
        async def check_backend():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://localhost:8000/health", timeout=5.0)
                    if response.status_code == 200:
                        print("  ✅ Backend is reachable on http://localhost:8000")
                        return True
                    else:
                        print(f"  ❌ Backend responded with status: {response.status_code}")
                        return False
            except Exception as e:
                print(f"  ❌ Backend connection failed: {e}")
                return False
        
        # Run the async check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(check_backend())
        loop.close()
        
        return result
        
    except ImportError:
        print("  ⚠️  httpx not available, skipping backend connectivity test")
        return False
    except Exception as e:
        print(f"  ❌ Connectivity test error: {e}")
        return False

def print_summary(results: Dict[str, List[Tuple[str, bool, str]]], backend_ok: bool):
    """Print a summary of all test results."""
    print("\n" + "="*60)
    print("📊 FRONTEND DEPENDENCY TEST SUMMARY")
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
    
    print(f"\n🔗 Backend Connectivity:")
    status = "✅" if backend_ok else "❌"
    print(f"  {status} Backend reachable")
    
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
                import re
                match = re.search(r'pip install ([^\s]+)', error)
                if match:
                    print(f"  pip install {match.group(1)}")
    else:
        print(f"\n🎉 All frontend dependencies imported successfully!")
        
        if backend_ok:
            print(f"   Your frontend environment is ready to use!")
            print(f"   Start with: ./start_frontend.sh")
        else:
            print(f"   ⚠️  Frontend ready, but backend not reachable")
            print(f"   Start backend first: cd ../backend && ./start_server.sh")

def main():
    """Main function to run the dependency tests."""
    print("🧪 LocalAI Community Frontend - Dependency Import Test")
    print("="*60)
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.executable}")
    print("="*60)
    
    try:
        results = test_dependencies()
        backend_ok = test_backend_connectivity()
        print_summary(results, backend_ok)
        
        # Return appropriate exit code
        total_failed = sum(
            sum(1 for _, success, _ in tests if not success)
            for tests in results.values()
        )
        
        if total_failed > 0:
            print(f"\n❌ Test failed with {total_failed} import errors")
            sys.exit(1)
        else:
            print(f"\n✅ All frontend tests passed!")
            if not backend_ok:
                print(f"⚠️  Backend connectivity test failed")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 