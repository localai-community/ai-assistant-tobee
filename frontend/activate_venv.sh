#!/bin/bash

# LocalAI Community Frontend - Virtual Environment Activator
echo "Activating LocalAI Community Frontend Virtual Environment..."

# Check if we're in the frontend directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found. Please run this script from the frontend directory."
    echo "Current directory: $(pwd)"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating new virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully!"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if activation was successful
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated successfully!"
echo "📍 Virtual environment: $VIRTUAL_ENV"
echo "🐍 Python version: $(python --version)"
echo "📦 Pip version: $(pip --version)"

# Check if dependencies are installed
if ! python -c "import chainlit" 2>/dev/null; then
    echo ""
    echo "⚠️  Dependencies not installed. Installing now..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully!"
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🚀 Ready to work! You can now:"
echo "   • Start frontend: ./start_frontend.sh"
echo "   • Install new packages: pip install <package>"
echo "   • Deactivate: deactivate"
echo ""

# Start a new shell with the virtual environment activated
echo "Starting new shell with virtual environment activated..."
echo "Type 'exit' to return to the original shell"
echo ""

exec $SHELL 