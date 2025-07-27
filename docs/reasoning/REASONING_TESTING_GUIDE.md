# Reasoning System Testing Guide

## Overview

This guide explains how to test the Phase 1 reasoning system through the frontend interface. The reasoning system provides step-by-step reasoning capabilities with parsing, validation, and formatting components.

## Quick Start

### 1. Start the Services

**Backend (Reasoning API):**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Streamlit Interface):**
```bash
cd frontend
source venv/bin/activate
streamlit run app.py --server.port 8501
```

### 2. Access the Interface

Open your browser and go to: **http://localhost:8501**

## Testing the Reasoning System

### Method 1: Frontend Interface (Recommended)

1. **Open the Frontend**: Navigate to http://localhost:8501
2. **Expand the Reasoning Section**: In the sidebar, click on "🧠 Reasoning System"
3. **Test Components**: Use the test buttons to try different features:
   - **🧪 Test Complete Workflow**: Tests the entire reasoning pipeline
   - **🔍 Test Problem Parsing**: Tests problem statement analysis
   - **📝 Test Step Parsing**: Tests step-by-step reasoning parsing
   - **🔄 Refresh Reasoning Status**: Updates the system status

### Method 2: API Testing

You can also test the API endpoints directly:

#### Health Check
```bash
curl -X GET "http://localhost:8000/reasoning/health"
```

#### Problem Parsing
```bash
curl -X POST "http://localhost:8000/reasoning/parse-problem" \
  -H "Content-Type: application/json" \
  -d '{"problem_statement": "Solve 2x + 3 = 7"}'
```

#### Step Parsing
```bash
curl -X POST "http://localhost:8000/reasoning/parse-steps" \
  -H "Content-Type: application/json" \
  -d '{"step_output": "Step 1: Identify the problem\nThis is a mathematical problem.\nConfidence: 0.9"}'
```

#### Validation
```bash
curl -X POST "http://localhost:8000/reasoning/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_statement": "Calculate the area of a circle with radius 5",
    "steps": [
      {
        "description": "Identify the formula",
        "reasoning": "The area of a circle is A = πr²",
        "confidence": 0.9
      }
    ],
    "final_answer": "The area is approximately 78.54 square units",
    "confidence": 0.95
  }'
```

#### Formatting
```bash
curl -X POST "http://localhost:8000/reasoning/format" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_statement": "Calculate the area of a circle with radius 5",
    "steps": [
      {
        "description": "Identify the formula",
        "reasoning": "The area of a circle is A = πr²",
        "confidence": 0.9
      }
    ],
    "final_answer": "The area is approximately 78.54 square units",
    "confidence": 0.95,
    "format_type": "json"
  }'
```

#### Complete Workflow Test
```bash
curl -X POST "http://localhost:8000/reasoning/test-workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_statement": "Calculate the area of a circle with radius 5",
    "format_type": "json"
  }'
```

### Method 3: Automated Test Script

Run the comprehensive test script:

```bash
# Activate backend virtual environment
cd backend && source venv/bin/activate && cd ..

# Run the test script
python test_reasoning_frontend.py
```

## Available Features

### 1. Problem Parsing
- **Input**: Natural language problem statements
- **Output**: Structured analysis including:
  - Problem type (mathematical, logical, general)
  - Extracted numbers and variables
  - Keywords and context
  - Word count and complexity metrics

### 2. Step Parsing
- **Input**: Step-by-step reasoning text
- **Output**: Structured steps with:
  - Step descriptions
  - Reasoning content
  - Confidence scores
  - Metadata

### 3. Validation Framework
- **Input**: Problem statement, steps, and final answer
- **Output**: Comprehensive validation including:
  - Input validation (format, completeness)
  - Step validation (logical consistency)
  - Result validation (reasonableness)
  - Validation summary with statistics

### 4. Output Formatting
- **Supported Formats**:
  - **JSON**: Structured data format
  - **Text**: Human-readable plain text
  - **Markdown**: Formatted markdown
  - **HTML**: Web-ready HTML
  - **Structured**: Custom structured format

### 5. Complete Workflow
- **End-to-End Testing**: Tests the entire pipeline
- **Sample Problems**: Automatically generates test cases
- **Validation**: Ensures all components work together
- **Formatting**: Outputs in the requested format

## Example Test Cases

### Mathematical Problems
```
"Solve 2x + 3 = 7"
"Calculate the area of a circle with radius 5"
"Find the derivative of f(x) = x² + 3x + 1"
```

### Logical Problems
```
"All humans are mortal. Socrates is human. Is Socrates mortal?"
"If it rains, the ground gets wet. The ground is wet. Did it rain?"
```

### General Problems
```
"What is the capital of France?"
"Explain the process of photosynthesis"
"How does a computer work?"
```

## Troubleshooting

### Common Issues

1. **Backend Not Available**
   - Check if the backend is running on port 8000
   - Verify the virtual environment is activated
   - Check for any error messages in the backend console

2. **Frontend Not Loading**
   - Check if Streamlit is running on port 8501
   - Verify the frontend virtual environment is activated
   - Check browser console for any JavaScript errors

3. **API Errors**
   - Check the backend logs for detailed error messages
   - Verify the request format matches the API specification
   - Ensure all required fields are provided

4. **Import Errors**
   - Make sure all dependencies are installed in the virtual environment
   - Check that the reasoning modules are properly imported
   - Verify the Python path includes the backend directory

### Debug Mode

To enable debug mode in the frontend:
1. Open the "⚙️ Settings" section in the sidebar
2. Check "🔍 Show Debug Info" for RAG statistics
3. Use the "🔄 Force Refresh All Data" button to reload all data

## Next Steps

After testing Phase 1, you can:

1. **Explore Phase 2**: Basic reasoning engines (mathematical, logical, causal)
2. **Test Advanced Features**: Chain-of-Thought and Tree-of-Thoughts implementations
3. **Integration Testing**: Test with the chat interface and RAG system
4. **Performance Testing**: Benchmark the system with larger datasets

## API Documentation

For detailed API documentation, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the backend and frontend logs
3. Test individual components using the API endpoints
4. Refer to the implementation documentation in `docs/reasoning/` 