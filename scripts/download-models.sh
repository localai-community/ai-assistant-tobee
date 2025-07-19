#!/bin/sh

# Download models for local-only operation
# This script downloads all necessary models for offline use

set -e

echo "🚀 Starting model download for local-only operation..."

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
while ! wget -q --spider http://ollama:11434/api/tags; do
    echo "   Waiting for Ollama service..."
    sleep 5
done

echo "✅ Ollama is ready!"

# Download chat models
echo "📥 Downloading chat models..."

echo "   • Downloading Llama 3.2 (main chat model)..."
ollama pull llama3.2:latest

echo "   • Downloading CodeLlama (for code tasks)..."
ollama pull codellama:7b

echo "   • Downloading Llama 3.2 1B (lightweight model)..."
ollama pull llama3.2:1b

# Download embedding models
echo "📥 Downloading embedding models..."

echo "   • Downloading Nomic Embed Text (for RAG)..."
ollama pull nomic-embed-text:latest

echo "   • Downloading BGE Small (alternative embeddings)..."
ollama pull bge-small:latest

# List downloaded models
echo "📋 Downloaded models:"
ollama list

echo "✅ All models downloaded successfully!"
echo "🔒 System is now ready for fully offline operation."

# Create a marker file to indicate models are downloaded
touch /tmp/models-downloaded

echo "🎉 Local-only setup complete!"
echo ""
echo "Available models:"
echo "  • llama3.2:latest      - Main chat model"
echo "  • codellama:7b         - Code assistance"
echo "  • llama3.2:1b          - Lightweight model"
echo "  • nomic-embed-text     - Document embeddings"
echo "  • bge-small            - Alternative embeddings"
echo ""
echo "📖 Your AI assistant can now run completely offline!" 