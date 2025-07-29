#!/bin/bash

# LocalAI Community - Simplified GPU Setup Script
# This script runs services directly without Docker to avoid dependency issues

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

# Function to check and kill processes using a specific port
check_and_kill_port() {
    local port=$1
    local service_name=$2
    
    if lsof -ti:$port > /dev/null 2>&1; then
        print_warning "Port $port is already in use by $service_name"
        print_info "Killing processes using port $port..."
        
        # Get PIDs using the port
        local pids=$(lsof -ti:$port)
        
        # Kill each process
        for pid in $pids; do
            print_info "Killing process $pid..."
            kill -9 $pid 2>/dev/null || true
        done
        
        # Wait a moment for processes to terminate
        sleep 2
        
        # Verify port is free
        if lsof -ti:$port > /dev/null 2>&1; then
            print_error "Failed to free port $port"
            return 1
        else
            print_status "Port $port is now free"
        fi
    else
        print_status "Port $port is available"
    fi
}

print_header "LocalAI Community - Simplified GPU Setup"
echo ""

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only"
    exit 1
fi

# Check for Apple Silicon
if [[ $(uname -m) == "arm64" ]]; then
    print_success "Detected Apple Silicon (M1/M2) - GPU acceleration available!"
else
    print_warning "Detected Intel Mac - GPU acceleration may be limited"
fi

echo ""

# Step 1: Check and install Ollama
print_header "Step 1: Setting up Ollama with GPU support"

if ! command -v ollama &> /dev/null; then
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

# Check and free port 11434 (Ollama)
check_and_kill_port 11434 "Ollama"

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

# Step 3: Check for models
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

# Step 4: Start Backend
print_header "Step 4: Starting Backend"

cd backend

# Activate virtual environment
if [ -d "venv" ]; then
    print_info "Activating virtual environment..."
    source venv/bin/activate
else
    print_error "Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check and free port 8000 (Backend)
check_and_kill_port 8000 "Backend"

# Start backend
print_info "Starting backend server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to be ready
print_info "Waiting for backend..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Backend is ready!"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 2
done

if [ $i -eq 30 ]; then
    print_error "Backend failed to start within 60 seconds"
    exit 1
fi

# Step 5: Start Frontend
print_header "Step 5: Starting Frontend"

cd ../frontend

# Check if frontend virtual environment exists
if [ ! -d "venv" ]; then
    print_info "Creating frontend virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check and free port 8501 (Frontend)
check_and_kill_port 8501 "Frontend"

# Start frontend
print_info "Starting frontend server..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!

# Wait for frontend to be ready
print_info "Waiting for frontend..."
for i in {1..30}; do
    if curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        print_status "Frontend is ready!"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 2
done

if [ $i -eq 30 ]; then
    print_error "Frontend failed to start within 60 seconds"
    exit 1
fi

# Step 6: Test the setup
print_header "Step 6: Testing the Setup"

# Test backend health
print_info "Testing backend health..."
BACKEND_HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo "failed")

if [ "$BACKEND_HEALTH" = "healthy" ]; then
    print_success "Backend health check passed!"
else
    print_error "Backend health check failed"
fi

# Test Ollama connection
print_info "Testing Ollama connection..."
OLLAMA_HEALTH=$(curl -s http://localhost:8000/api/v1/chat/health 2>/dev/null | jq -r '.ollama_available' 2>/dev/null || echo "false")

if [ "$OLLAMA_HEALTH" = "true" ]; then
    print_success "Ollama is connected and ready!"
else
    print_error "Ollama connection failed"
fi

# Final status
print_header "🎉 LocalAI Community is running with GPU acceleration!"

echo ""
echo "📱 Access Points:"
echo "   • Frontend: http://localhost:8501"
echo "   • Backend API: http://localhost:8000"
echo "   • Ollama API: http://localhost:11434"
echo ""

echo "🔧 Management Commands:"
echo "   • Stop all services: pkill -f 'uvicorn\|streamlit\|ollama'"
echo "   • Stop Ollama: pkill ollama"
echo "   • View backend logs: tail -f backend/logs/app.log"
echo "   • Monitor GPU: Activity Monitor > GPU"
echo ""

echo "📊 Performance Tips:"
echo "   • Check Activity Monitor for GPU usage"
echo "   • Monitor Ollama process: ps aux | grep ollama"
echo "   • Test performance: ollama run llama3:latest 'Hello, world!'"
echo ""

print_success "Your M2 GPU is now powering your AI assistant! 🚀"

# Save PIDs for cleanup
echo $OLLAMA_PID > /tmp/ollama.pid
echo $BACKEND_PID > /tmp/backend.pid
echo $FRONTEND_PID > /tmp/frontend.pid

# Function to cleanup on exit
cleanup() {
    echo ""
    print_warning "Stopping services..."
    pkill -f "uvicorn.*app.main:app" 2>/dev/null || true
    pkill -f "streamlit.*app.py" 2>/dev/null || true
    pkill ollama 2>/dev/null || true
    rm -f /tmp/ollama.pid /tmp/backend.pid /tmp/frontend.pid
    print_status "All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

print_success "Setup complete! Services are running in the background."
echo ""
print_info "Press Ctrl+C to stop all services"
echo ""

# Keep script running to maintain services
while true; do
    sleep 10
    # Check if services are still running
    if ! pgrep -f "ollama serve" > /dev/null; then
        print_error "Ollama process died"
        cleanup
    fi
    if ! pgrep -f "uvicorn.*app.main:app" > /dev/null; then
        print_error "Backend process died"
        cleanup
    fi
    if ! pgrep -f "streamlit.*app.py" > /dev/null; then
        print_error "Frontend process died"
        cleanup
    fi
done 