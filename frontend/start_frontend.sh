#!/bin/bash

# LocalAI Community Frontend Starter
echo "Starting LocalAI Community Frontend..."

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

# Check if dependencies are installed
if ! python -c "import chainlit" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
    echo "Dependencies installed successfully!"
fi

# Check if backend is running
echo "Checking backend availability..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "⚠️  Backend not detected on http://localhost:8000"
    echo "   Make sure to start the backend first: cd ../backend && ./start_server.sh"
fi

# Start the frontend
echo "Starting Chainlit frontend on http://localhost:8001"
echo "Press Ctrl+C to stop the server"
echo ""

chainlit run app.py --host 0.0.0.0 --port 8001 