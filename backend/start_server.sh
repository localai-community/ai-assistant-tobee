#!/bin/bash

# LocalAI Community Backend Server Starter
echo "Starting LocalAI Community Backend Server..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Sync dependencies
echo "Syncing dependencies..."
uv sync

# Start the server
echo "Server starting on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
