# Phase 2: Update `start_server.sh`

## Current State

```bash
#!/bin/bash
# LocalAI Community Backend Server Starter
echo "Starting LocalAI Community Backend Server..."
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi
source venv/bin/activate
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi
echo "Server starting on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Target State

```bash
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
```

## Changes
- Remove `venv/` directory check
- Remove `source venv/bin/activate`
- Remove `pip install -r requirements.txt`
- Add `uv` availability check
- Replace with `uv sync` + `uv run uvicorn`

## File Modified
- `backend/start_server.sh`
