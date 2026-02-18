#!/bin/bash

# LocalAI Community Backend - Virtual Environment Activator
echo "Activating LocalAI Community Backend Virtual Environment..."

# Check if we're in the backend directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found. Please run this script from the backend directory."
    echo "Current directory: $(pwd)"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create virtual environment and sync dependencies if .venv doesn't exist
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating and syncing..."
    uv sync
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created and dependencies synced!"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if activation was successful
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

echo "Virtual environment activated successfully!"
echo "Virtual environment: $VIRTUAL_ENV"
echo "Python version: $(python --version)"
echo "uv version: $(uv --version)"

# Check if dependencies are synced
if ! python -c "import fastapi" 2>/dev/null; then
    echo ""
    echo "Dependencies not synced. Syncing now..."
    uv sync
    if [ $? -eq 0 ]; then
        echo "Dependencies synced successfully!"
    else
        echo "Failed to sync dependencies"
        exit 1
    fi
else
    echo "Dependencies already synced"
fi

echo ""
echo "Ready to work! You can now:"
echo "   - Start server: ./start_server.sh"
echo "   - Run tests: uv run pytest"
echo "   - Add packages: uv add <package>"
echo "   - Deactivate: deactivate"
echo ""

# Start a new shell with the virtual environment activated
echo "Starting new shell with virtual environment activated..."
echo "Type 'exit' to return to the original shell"
echo ""

exec $SHELL
