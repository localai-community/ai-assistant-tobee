# Phase 4 Multi-Agent System Evaluation

This directory contains comprehensive evaluation tests for the Phase 4 multi-agent reasoning system.

## 📋 Test Files

### 1. `test_phase4_comprehensive_evaluation.py`
**Comprehensive evaluation test** that evaluates:
- Agent selection accuracy
- Answer quality and correctness  
- Reasoning step quality
- Confidence score appropriateness
- Response completeness

**Categories Tested:**
- 🔢 **Mathematical Problems**: Basic arithmetic, algebra, geometry, calculus
- 🧮 **Logical Problems**: Syllogistic reasoning, propositional logic, inference
- 🔗 **Causal Problems**: Cause-effect analysis, intervention studies

### 2. `test_phase4_simple.py` (in backend/)
**Quick verification test** for basic functionality testing.

## 🚀 How to Run

### Option 1: Run Comprehensive Evaluation
```bash
cd backend
python test_phase4_evaluation.py
```

### Option 2: Run Simple Test
```bash
cd backend
python test_phase4_simple.py
```

### Option 3: Run Directly
```bash
cd tests/backend
python test_phase4_comprehensive_evaluation.py
```

## 📊 Evaluation Criteria

The comprehensive evaluation uses weighted scoring across 4 criteria:

1. **Agent Selection Accuracy** (25% weight)
   - Checks if the correct specialized agent was selected
   - Expected vs actual agent comparison

2. **Answer Correctness** (35% weight)
   - Evaluates if the answer is correct
   - String matching for expected answers

3. **Reasoning Quality** (25% weight)
   - Checks for presence of reasoning steps
   - Evaluates step count and detail level
   - Validates confidence score reasonableness

4. **Confidence Appropriateness** (15% weight)
   - Compares actual vs expected confidence
   - Allows 30% deviation tolerance

## 📝 Sample Questions Tested

### Mathematical Problems
- "What is 15 + 27? Please explain step by step."
- "Solve the equation: 2x + 5 = 13"
- "Calculate the area of a circle with radius 5 units"
- "What is 5 times 8?"
- "Find the derivative of x² + 3x + 1"

### Logical Problems
- "If all A are B, and some B are C, what can we conclude about A and C?"
- "Three people are in a room. If Alice is older than Bob, and Bob is older than Charlie, who is the youngest?"
- "A train leaves station A at 2 PM and arrives at station B at 4 PM. Another train leaves station B at 1 PM and arrives at station A at 3 PM. When do they meet?"
- "Evaluate the logical expression: (A AND B) OR (NOT A)"
- "If P then Q. P is true. Is Q necessarily true?"

### Causal Problems
- "What causes inflation and how does it affect the economy?"
- "How does smoking affect lung cancer rates?"
- "What are the effects of climate change on biodiversity?"
- "Does exercise cause better health outcomes?"
- "What is the causal effect of education on income?"

## 📈 Expected Results

### Agent Selection
- **Mathematical problems** → `mathematical_agent`
- **Logical problems** → `logical_agent`  
- **Causal problems** → `causal_agent`

### Confidence Scores
- **Simple arithmetic**: 0.9
- **Basic algebra**: 0.9
- **Geometry**: 0.9
- **Calculus**: 0.8
- **Logical reasoning**: 0.8-0.9
- **Causal analysis**: 0.7-0.8

### Performance Targets
- **Overall Score**: ≥ 0.7 (Good), ≥ 0.8 (Excellent)
- **Agent Selection Accuracy**: ≥ 0.8
- **Answer Correctness**: ≥ 0.7
- **Reasoning Quality**: ≥ 0.6

## 📄 Output Files

The comprehensive evaluation generates:
- **Console output**: Real-time evaluation results
- **JSON report**: Detailed results saved as `phase4_evaluation_report_YYYYMMDD_HHMMSS.json`

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the backend directory
   cd backend
   python test_phase4_simple.py
   ```

2. **Agent Registration Issues**
   - Check that all local agents are properly initialized
   - Verify Ollama is running for local agents

3. **Low Scores**
   - Check agent selection logic
   - Verify expected answers match actual responses
   - Review confidence scoring

### Debug Mode
Add debug logging to see detailed agent interactions:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎯 Performance Benchmarks

Based on the logs you provided, the system should achieve:

- **Agent Selection**: 100% accuracy for mathematical problems
- **Confidence Scores**: 0.8-0.9 for mathematical problems
- **Approach**: "local_only" for current implementation
- **Response Time**: < 5 seconds per question

## 📝 Customization

To add new test questions:

1. Edit `test_questions` in `test_phase4_comprehensive_evaluation.py`
2. Add new questions with expected answers and agents
3. Run the evaluation to test

To modify evaluation criteria:

1. Adjust `evaluation_weights` in the test class
2. Modify evaluation functions as needed
3. Update expected confidence scores

## 🔄 Continuous Testing

For ongoing evaluation:

```bash
# Run daily evaluation
python test_phase4_evaluation.py > evaluation_log.txt 2>&1

# Check results
tail -f evaluation_log.txt
```

This comprehensive evaluation will help identify issues with:
- Agent selection accuracy
- Answer quality problems
- Reasoning step completeness
- Confidence score calibration
- Overall system performance 