#!/bin/bash

# LocalAI Community Frontend Stopper
echo "Stopping LocalAI Community Frontend..."

# Find and kill streamlit processes
pkill -f streamlit

if [ $? -eq 0 ]; then
    echo "Frontend stopped successfully"
else
    echo "No frontend was running"
fi 