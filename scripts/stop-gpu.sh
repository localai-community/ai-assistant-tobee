#!/bin/bash

# LocalAI Community - Stop GPU Services
# This script stops all services cleanly

set -e

echo "🛑 Stopping LocalAI Community GPU services..."

# Stop Docker services
echo "📦 Stopping Docker containers..."
docker-compose -f docker-compose.host-ollama.yml down 2>/dev/null || true

# Stop any other related containers
echo "🧹 Cleaning up any remaining containers..."
docker stop localaicommunity-ollama-1 2>/dev/null || true
docker stop localaicommunity-backend-1 2>/dev/null || true
docker stop localaicommunity-frontend-1 2>/dev/null || true

# Stop Ollama processes
echo "🤖 Stopping Ollama processes..."
pkill ollama 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Check if anything is still running
if pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Some Ollama processes may still be running"
    echo "   You can force stop them with: pkill -9 ollama"
else
    echo "✅ All Ollama processes stopped"
fi

if docker ps | grep -q "localai"; then
    echo "⚠️  Some Docker containers may still be running"
    echo "   You can force stop them with: docker stop \$(docker ps -q --filter name=localai)"
else
    echo "✅ All Docker containers stopped"
fi

echo ""
echo "🎉 All services stopped successfully!"
echo ""
echo "💡 To restart with GPU: ./run-with-gpu.sh" 