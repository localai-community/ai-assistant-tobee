#!/bin/bash

# LocalAI Community Backend Server Stopper
echo "Stopping LocalAI Community Backend Server..."

# Find and kill uvicorn processes
pkill -f uvicorn

if [ $? -eq 0 ]; then
    echo "Server stopped successfully"
else
    echo "No server was running"
fi 