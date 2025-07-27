# Phase 2 Streaming Test Guide

## Prerequisites
- Backend server running on port 8000
- Frontend server running on port 8501
- Ollama running with llama3:latest model

## How to Test Phase 2 Streaming

### 1. Open the Frontend
Open your browser and go to: http://localhost:8501

### 2. Enable Phase 2 Reasoning
1. In the sidebar, expand the "🚀 Phase 2: Advanced Reasoning Engines" section
2. Toggle on "Enable Phase 2 Reasoning"
3. Select an engine (e.g., "Mathematical" or "Auto")

### 3. Enable Streaming
1. In the sidebar, expand the "⚙️ Settings" section
2. Check "Enable Streaming Responses"

### 4. Test with Sample Questions
1. In the Phase 2 section, click on one of the sample questions:
   - **Mathematical**: "Solve 2x + 3 = 7"
   - **Logical**: "If all A are B and all B are C, then all A are C"
   - **Causal**: "What is the causal effect of X on Y?"

### 5. Test with Custom Questions
1. Type a question in the chat input, such as:
   - "What is 5 + 3?"
   - "Solve the equation 3x - 2 = 7"
   - "If it rains, the ground gets wet. The ground is wet. Did it rain?"

## Expected Behavior

### With Streaming Enabled:
- You should see "🚀 Starting Phase 2 reasoning streaming..." message
- The response should appear in real-time, character by character
- You should see a blinking cursor (▌) at the end while streaming
- At the end, you should see Phase 2 engine information

### With Streaming Disabled:
- You should see a spinner "🚀 Using Phase 2 reasoning engine..."
- The response should appear all at once
- You should see Phase 2 engine information

## Troubleshooting

### If streaming doesn't work:
1. Check that both backend and frontend are running
2. Verify that Phase 2 reasoning is enabled in the sidebar
3. Verify that streaming is enabled in settings
4. Check the browser console for any JavaScript errors
5. Check the frontend terminal for debug output (🔍 messages)

### Debug Output
The frontend now includes debug logging. Look for messages starting with 🔍 in the terminal where the frontend is running.

### Backend Test
You can test the backend directly:
```bash
curl -X POST "http://localhost:8000/api/v1/phase2-reasoning/stream" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 5 + 3?", "model": "llama3:latest", "engine_type": "auto"}' \
  --no-buffer
```

## Sample Questions for Testing

### Mathematical:
- "What is 5 + 3?"
- "Solve 2x + 3 = 7"
- "What is the derivative of x²?"
- "Calculate the area of a circle with radius 5"

### Logical:
- "If all A are B and all B are C, then all A are C"
- "If it rains, the ground gets wet. The ground is wet. Did it rain?"
- "All humans are mortal. Socrates is human. Is Socrates mortal?"

### Causal:
- "What is the causal effect of X on Y?"
- "Does smoking cause lung cancer?"
- "What would happen if we increased the minimum wage?"

## Expected Output Format

The response should include:
1. Step-by-step reasoning
2. Final answer
3. Phase 2 engine information:
   - Engine used
   - Reasoning type
   - Confidence score
   - Number of steps generated
   - Validation summary (if available) 