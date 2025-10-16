#!/bin/bash

# Next.js Frontend Starter
echo "Starting Next.js Frontend..."

# Check if we're in the frontend-nextjs directory
if [ ! -f "package.json" ]; then
    echo "Error: package.json not found. Please run this script from the frontend-nextjs directory."
    echo "Current directory: $(pwd)"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
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
echo "Starting Next.js frontend on http://localhost:3000"
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
