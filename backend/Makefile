# Makefile for Local Lambda Testing

.PHONY: test test-all test-simple test-chat test-health test-status help

# Default target
help:
	@echo "Available commands:"
	@echo "  make test-all      - Run comprehensive Lambda handler tests"
	@echo "  make test-simple   - Run simple test handler"
	@echo "  make test-chat     - Test chat endpoint"
	@echo "  make test-health   - Test health endpoint"
	@echo "  make test-status   - Test API status endpoint"
	@echo "  make test-root     - Test root endpoint"
	@echo "  make help          - Show this help"

# Activate virtual environment
venv:
	@echo "Activating virtual environment..."
	@source venv/bin/activate || echo "Virtual environment not found. Please create one first."

# Run comprehensive tests
test-all: venv
	@echo "🧪 Running comprehensive Lambda handler tests..."
	@python test_lambda_local.py

# Test simple handler
test-simple: venv
	@echo "🧪 Testing simple handler..."
	@python invoke_lambda.py /test

# Test chat endpoint
test-chat: venv
	@echo "🧪 Testing chat endpoint..."
	@python invoke_lambda.py /chat POST '{"message": "Hello, test message"}'

# Test health endpoint
test-health: venv
	@echo "🧪 Testing health endpoint..."
	@python invoke_lambda.py /health

# Test API status endpoint
test-status: venv
	@echo "🧪 Testing API status endpoint..."
	@python invoke_lambda.py /api/v1/status

# Test root endpoint
test-root: venv
	@echo "🧪 Testing root endpoint..."
	@python invoke_lambda.py /

# Test with custom endpoint
test-custom:
	@echo "Usage: make test-custom ENDPOINT=/your/endpoint [METHOD=GET] [BODY='{\"key\":\"value\"}']"
	@if [ -n "$(ENDPOINT)" ]; then \
		echo "🧪 Testing custom endpoint: $(ENDPOINT)"; \
		python invoke_lambda.py $(ENDPOINT) $(METHOD) $(BODY); \
	else \
		echo "Please specify ENDPOINT parameter"; \
	fi

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete 