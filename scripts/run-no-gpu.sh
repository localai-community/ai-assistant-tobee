#!/bin/bash

# LocalAI Community - Startup Script
# This script starts the services and ensures models are available

set -e

echo "🚀 Starting LocalAI Community..."

# Start the services
echo "📦 Starting Docker services..."
docker-compose -f docker/docker-compose.yml up -d

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
    echo "   Waiting for Ollama service..."
    sleep 5
done

# Check if models are available
echo "🔍 Checking for available models..."
MODELS=$(curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "")

if [ -z "$MODELS" ]; then
    echo "📥 No models found. Downloading llama3.2:latest..."
    docker exec localaicommunity-ollama-1 ollama pull llama3.2:latest
    echo "✅ Model downloaded successfully!"
else
    echo "✅ Models already available:"
    echo "$MODELS" | while read -r model; do
        echo "   • $model"
    done
fi

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
while ! curl -s http://localhost:8001/health > /dev/null; do
    echo "   Waiting for backend service..."
    sleep 5
done

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
while ! curl -s http://localhost:8000/health > /dev/null; do
    echo "   Waiting for frontend service..."
    sleep 5
done

echo ""
echo "🎉 LocalAI Community is ready!"
echo ""
echo "📱 Frontend: http://localhost:8000"
echo "🔧 Backend API: http://localhost:8001"
echo "🤖 Ollama: http://localhost:11434"
echo ""
echo "💡 You can now open http://localhost:8000 in your browser to start chatting!" 