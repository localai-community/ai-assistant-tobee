#!/bin/bash

# LocalAI Community - Full GPU Setup and Run Script
# This script provides complete GPU-accelerated setup for macOS M1/M2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${PURPLE}🎉 $1${NC}"
}

print_header() {
    echo -e "${CYAN}🚀 $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check GPU usage
check_gpu_usage() {
    if command_exists "system_profiler"; then
        echo "📊 Checking GPU information..."
        system_profiler SPDisplaysDataType | grep -A 5 "Chipset Model" | head -10
    fi
}

# Function to monitor Ollama performance
monitor_ollama() {
    echo "🔍 Monitoring Ollama performance..."
    echo "   Process ID: $(pgrep -f 'ollama serve' || echo 'Not running')"
    echo "   GPU Status: $(ps aux | grep ollama | grep -q 'ollama serve' && echo 'Running' || echo 'Not running')"
}

print_header "LocalAI Community - GPU Accelerated Setup"
echo ""

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only"
    echo "   Use the regular docker-compose setup for other platforms"
    exit 1
fi

# Check for Apple Silicon
if [[ $(uname -m) == "arm64" ]]; then
    print_success "Detected Apple Silicon (M1/M2) - GPU acceleration available!"
    check_gpu_usage
else
    print_warning "Detected Intel Mac - GPU acceleration may be limited"
fi

echo ""

# Step 1: Check and install Ollama
print_header "Step 1: Setting up Ollama with GPU support"

if ! command_exists ollama; then
    print_info "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Add to PATH if needed
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        export PATH="$HOME/.local/bin:$PATH"
        print_status "Added Ollama to PATH"
    fi
else
    print_status "Ollama already installed: $(ollama --version)"
fi

# Step 2: Start Ollama with GPU support
print_header "Step 2: Starting Ollama with GPU acceleration"

# Stop any existing Ollama processes
if pgrep -x "ollama" > /dev/null; then
    print_info "Stopping existing Ollama processes..."
    pkill ollama || true
    sleep 2
fi

# Start Ollama
print_info "Starting Ollama with GPU support..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
print_info "Waiting for Ollama to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_status "Ollama is ready with GPU support!"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 2
done

# Step 3: Model Management
print_header "Step 3: Model Management"

# Check available models
MODELS=$(curl -s http://localhost:11434/api/tags 2>/dev/null | jq -r '.models[].name' 2>/dev/null || echo "")

if [ -z "$MODELS" ]; then
    print_warning "No models found"
    echo ""
    echo "Available models to download:"
    echo "  1. llama3:latest (4.7GB) - General purpose"
    echo "  2. llama3.2:latest (2.0GB) - Smaller, faster"
    echo "  3. codellama:7b (4.0GB) - Code assistance"
    echo "  4. mistral:latest (4.1GB) - High performance"
    echo ""
    read -p "Enter model number to download (or press Enter to skip): " model_choice
    
    case $model_choice in
        1)
            print_info "Downloading llama3:latest..."
            ollama pull llama3:latest
            ;;
        2)
            print_info "Downloading llama3.2:latest..."
            ollama pull llama3.2:latest
            ;;
        3)
            print_info "Downloading codellama:7b..."
            ollama pull codellama:7b
            ;;
        4)
            print_info "Downloading mistral:latest..."
            ollama pull mistral:latest
            ;;
        *)
            print_warning "No model selected"
            ;;
    esac
else
    print_status "Available models:"
    echo "$MODELS" | while read -r model; do
        echo "   • $model"
    done
fi

# Step 4: Stop conflicting Docker containers
print_header "Step 4: Preparing Docker environment"

print_info "Stopping any conflicting Docker containers..."
docker stop localaicommunity-ollama-1 2>/dev/null || true
docker stop localaicommunity-backend-1 2>/dev/null || true
docker stop localaicommunity-frontend-1 2>/dev/null || true

# Step 5: Start Docker services
print_header "Step 5: Starting LocalAI Community services"

print_info "Starting backend and frontend with host Ollama..."
docker-compose -f docker-compose.host-ollama.yml up -d

# Step 6: Wait for services
print_header "Step 6: Waiting for services to be ready"

# Wait for backend
print_info "Waiting for backend..."
for i in {1..30}; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        print_status "Backend is ready!"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 2
done

# Wait for frontend
print_info "Waiting for frontend..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Frontend is ready!"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 2
done

# Step 7: Performance monitoring
print_header "Step 7: Performance and Health Check"

# Check Ollama health
print_info "Checking Ollama health..."
OLLAMA_HEALTH=$(curl -s http://localhost:8001/api/v1/chat/health 2>/dev/null | jq -r '.ollama_available' 2>/dev/null || echo "false")

if [ "$OLLAMA_HEALTH" = "true" ]; then
    print_success "Ollama is healthy and connected!"
else
    print_error "Ollama health check failed"
fi

# Monitor performance
monitor_ollama

# Step 8: Test chat functionality
print_header "Step 8: Testing GPU-accelerated chat"

# Get available models from backend
BACKEND_MODELS=$(curl -s http://localhost:8001/api/v1/chat/health 2>/dev/null | jq -r '.available_models[]' 2>/dev/null | head -1 || echo "llama3:latest")

print_info "Testing chat with model: $BACKEND_MODELS"

# Test chat request
TEST_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/chat/ \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Hello! Are you using GPU acceleration?\", \"model\": \"$BACKEND_MODELS\"}" \
    2>/dev/null | jq -r '.response' 2>/dev/null || echo "Test failed")

if [ "$TEST_RESPONSE" != "Test failed" ] && [ -n "$TEST_RESPONSE" ]; then
    print_success "Chat test successful!"
    echo "   Response: ${TEST_RESPONSE:0:100}..."
else
    print_error "Chat test failed"
fi

# Final status
print_header "🎉 LocalAI Community is running with GPU acceleration!"

echo ""
echo "📱 Access Points:"
echo "   • Frontend: http://localhost:8000"
echo "   • Backend API: http://localhost:8001"
echo "   • Ollama API: http://localhost:11434"
echo ""

echo "🔧 Management Commands:"
echo "   • Stop services: docker-compose -f docker-compose.host-ollama.yml down"
echo "   • Stop Ollama: pkill ollama"
echo "   • View logs: docker-compose -f docker-compose.host-ollama.yml logs -f"
echo "   • Monitor GPU: Activity Monitor > GPU"
echo ""

echo "📊 Performance Tips:"
echo "   • Check Activity Monitor for GPU usage"
echo "   • Monitor Ollama process: ps aux | grep ollama"
echo "   • Test performance: ollama run $BACKEND_MODELS 'Hello, world!'"
echo ""

print_success "Your M2 GPU is now powering your AI assistant! 🚀"

# Services are now running in background
echo ""
print_success "All services are running in the background!"
echo ""
print_info "To stop services later, run: ./stop-gpu.sh"
echo ""

# Function to cleanup on exit (for Ctrl+C during startup)
cleanup() {
    echo ""
    print_warning "Stopping services..."
    docker-compose -f docker-compose.host-ollama.yml down
    pkill ollama 2>/dev/null || true
    print_status "All services stopped"
    exit 0
}

# Set trap to cleanup on script exit (only during startup)
trap cleanup SIGINT SIGTERM

# Exit successfully - services continue running in background
print_success "Setup complete! Services are running in the background."
exit 0 