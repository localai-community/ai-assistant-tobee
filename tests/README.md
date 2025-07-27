# AI Assistant Test Suite

This directory contains the organized test suite for the AI Assistant project.

## Directory Structure

```
tests/
├── backend/           # Backend-specific tests
│   ├── test_auto_detection_comprehensive.py
│   ├── test_chat.py
│   ├── test_imports.py
│   ├── test_phase1_reasoning.py
│   ├── test_phase2_reasoning_engines.py
│   ├── test_phase2_simple.py
│   ├── test_phase3_complete.py
│   └── test_rag.py
├── frontend/          # Frontend-specific tests
│   ├── test_frontend.py
│   └── test_frontend_chat.py
├── integration/       # Integration tests (multiple components)
│   ├── test_advanced_rag.py
│   ├── test_advanced_rag_frontend.py
│   ├── test_llm_context_detection.py
│   ├── test_mcp_integration.py
│   ├── test_phase2_streaming.py
│   ├── test_phase2_ui.py
│   ├── test_reasoning_chat.py
│   ├── test_reasoning_frontend.py
│   ├── test_streaming_reasoning.py
│   └── test_streaming_timing.py
├── unit/              # Unit tests (single components)
│   ├── test_frontend_reasoning.py
│   ├── test_frontend_streaming.py
│   └── test_ui_streaming.py
├── run_tests.py       # Test runner script
└── README.md          # This file
```

## Test Categories

### Backend Tests (`backend/`)
Tests for backend components including:
- Reasoning engines (mathematical, logical, causal)
- Chat services
- RAG (Retrieval-Augmented Generation) functionality
- API endpoints
- Core reasoning infrastructure

### Frontend Tests (`frontend/`)
Tests for frontend components including:
- Streamlit UI components
- Frontend chat functionality
- User interface interactions

### Integration Tests (`integration/`)
Tests that verify multiple components work together:
- Backend-frontend integration
- RAG system integration
- MCP (Model Context Protocol) integration
- Streaming functionality
- Phase 2 reasoning system integration

### Unit Tests (`unit/`)
Tests for individual components in isolation:
- Individual UI components
- Single functionality modules
- Isolated feature testing

## Running Tests

### Using the Test Runner Script

The `run_tests.py` script provides a convenient way to run tests:

```bash
# Run all tests
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py --category backend
python tests/run_tests.py --category frontend
python tests/run_tests.py --category integration
python tests/run_tests.py --category unit

# Run a specific test file
python tests/run_tests.py --test tests/backend/test_auto_detection_comprehensive.py
```

### Running Tests Directly

You can also run tests directly using Python's unittest module:

```bash
# Run all backend tests
python -m unittest discover tests/backend

# Run all frontend tests
python -m unittest discover tests/frontend

# Run all integration tests
python -m unittest discover tests/integration

# Run all unit tests
python -m unittest discover tests/unit

# Run a specific test file
python -m unittest tests.backend.test_auto_detection_comprehensive
```

### Running from Project Root

From the project root directory:

```bash
# Run all tests
python tests/run_tests.py

# Run backend tests only
python tests/run_tests.py --category backend

# Run a specific test
python tests/run_tests.py --test tests/backend/test_auto_detection_comprehensive.py
```

## Test Configuration

### Environment Setup

Before running tests, ensure you have:

1. **Virtual Environment Activated:**
   ```bash
   source backend/venv/bin/activate  # or frontend/venv/bin/activate
   ```

2. **Dependencies Installed:**
   ```bash
   pip install -r backend/requirements.txt
   pip install -r frontend/requirements.txt
   ```

3. **Backend Server Running** (for integration tests):
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

### Test Data

Some tests may require specific test data or configuration:
- RAG tests may need sample documents
- Integration tests may need a running backend server
- MCP tests may need MCP servers running

## Writing New Tests

### Test File Naming Convention

- All test files should start with `test_`
- Use descriptive names that indicate what is being tested
- Follow the pattern: `test_<component>_<feature>.py`

### Test Class Naming Convention

- Test classes should inherit from `unittest.TestCase`
- Use descriptive class names: `Test<Component><Feature>`

### Example Test Structure

```python
import unittest
import sys
import os

# Add the appropriate path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app'))

from app.some_module import SomeClass

class TestSomeFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.test_instance = SomeClass()
    
    def test_some_functionality(self):
        """Test some specific functionality."""
        result = self.test_instance.some_method()
        self.assertEqual(result, expected_value)
    
    def tearDown(self):
        """Clean up after tests."""
        pass

if __name__ == '__main__':
    unittest.main()
```

## Continuous Integration

Tests are automatically run in CI/CD pipelines. The test runner script returns appropriate exit codes:
- `0` for success
- `1` for failure

This allows CI systems to detect test failures and take appropriate action.

## Troubleshooting

### Import Errors

If you encounter import errors, ensure:
1. The correct path is added to `sys.path`
2. The virtual environment is activated
3. All dependencies are installed

### Path Issues

Test files use relative paths to import modules. If you move test files, update the `sys.path.insert()` calls accordingly.

### Backend Server Issues

For integration tests that require a running backend:
1. Ensure the backend server is running
2. Check that the correct port is being used
3. Verify the server is healthy before running tests 