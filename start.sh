#!/bin/bash

# LocalAI Community - Main Startup Script
# This script provides options for different setup configurations

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
print_header() {
    echo -e "${CYAN}🚀 LocalAI Community - Setup Options${NC}"
    echo ""
}

print_option() {
    echo -e "${GREEN}$1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${PURPLE}🎉 $1${NC}"
}

# Function to check if we're on macOS
check_macos() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        return 0
    else
        return 1
    fi
}

# Function to check if we're on Apple Silicon
check_apple_silicon() {
    if [[ $(uname -m) == "arm64" ]]; then
        return 0
    else
        return 1
    fi
}

# Main menu
show_menu() {
    print_header
    
    echo "Choose your setup configuration:"
    echo ""
    
    if check_macos && check_apple_silicon; then
        print_option "1. 🍎 GPU Setup (Recommended for M1/M2)"
        echo "   • Uses native M1/M2 GPU acceleration"
        echo "   • Maximum performance and speed"
        echo "   • Installs Ollama on host system"
        echo "   • macOS Apple Silicon only"
        echo ""
    fi
    
    print_option "2. 🔒 No-GPU Setup (Cross-platform)"
    echo "   • Works on Linux, Windows, Intel Macs"
    echo "   • Uses Docker Ollama (CPU only)"
    echo "   • Simple Docker-only setup"
    echo "   • Compatible with all platforms"
    echo ""
    
    print_option "3. 🛑 Stop Services"
    echo "   • Stop all running services"
    echo "   • Clean shutdown"
    echo ""
    
    print_option "4. 📋 System Information"
    echo "   • Show system details"
    echo "   • Check GPU availability"
    echo ""
    
    print_option "5. ❌ Exit"
    echo "   • Exit without starting anything"
    echo ""
}

# Function to show system information
show_system_info() {
    print_header
    echo "System Information:"
    echo ""
    
    echo "Operating System:"
    echo "   • OS: $OSTYPE"
    echo "   • Architecture: $(uname -m)"
    
    if check_macos; then
        echo "   • Platform: macOS"
        if check_apple_silicon; then
            print_success "   • Apple Silicon detected (M1/M2)"
            echo "   • GPU acceleration available"
        else
            print_warning "   • Intel Mac detected"
            echo "   • Limited GPU acceleration"
        fi
    else
        echo "   • Platform: $(uname -s)"
        print_warning "   • GPU acceleration may be limited"
    fi
    
    echo ""
    echo "Docker Status:"
    if command -v docker &> /dev/null; then
        print_success "   • Docker is installed"
        if docker info &> /dev/null; then
            print_success "   • Docker is running"
        else
            print_error "   • Docker is not running"
        fi
    else
        print_error "   • Docker is not installed"
    fi
    
    echo ""
    echo "Ollama Status:"
    if command -v ollama &> /dev/null; then
        print_success "   • Ollama is installed: $(ollama --version)"
        if pgrep -x "ollama" > /dev/null; then
            print_success "   • Ollama is running"
        else
            print_warning "   • Ollama is not running"
        fi
    else
        print_warning "   • Ollama is not installed"
    fi
    
    echo ""
}

# Function to run GPU setup
run_gpu_setup() {
    print_header
    print_info "Starting GPU setup for macOS M1/M2..."
    echo ""
    
    if ! check_macos; then
        print_error "GPU setup is only available on macOS"
        return 1
    fi
    
    if ! check_apple_silicon; then
        print_warning "GPU setup is optimized for Apple Silicon (M1/M2)"
        print_info "You can still use it on Intel Mac, but performance may be limited"
        echo ""
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    fi
    
    print_success "Running GPU setup..."
    echo ""
    
    # Run the GPU setup script
    if ./scripts/run-with-gpu.sh; then
        print_success "GPU setup completed successfully!"
        echo ""
        print_info "Access your GPU-accelerated AI assistant at: http://localhost:8000"
    else
        print_error "GPU setup failed"
        return 1
    fi
}

# Function to run no-GPU setup
run_no_gpu_setup() {
    print_header
    print_info "Starting no-GPU setup (cross-platform)..."
    echo ""
    
    print_success "Running no-GPU setup..."
    echo ""
    
    # Run the no-GPU setup script
    if ./scripts/run-no-gpu.sh; then
        print_success "No-GPU setup completed successfully!"
        echo ""
        print_info "Access your AI assistant at: http://localhost:8000"
    else
        print_error "No-GPU setup failed"
        return 1
    fi
}

# Function to stop services
stop_services() {
    print_header
    print_info "Stopping all services..."
    echo ""
    
    # Stop Docker services
    print_info "Stopping Docker services..."
    docker-compose -f docker/docker-compose.yml down 2>/dev/null || true
docker-compose -f docker/docker-compose.host-ollama.yml down 2>/dev/null || true
    
    # Stop Ollama if running
    if pgrep -x "ollama" > /dev/null; then
        print_info "Stopping Ollama..."
        pkill ollama 2>/dev/null || true
    fi
    
    print_success "All services stopped!"
    echo ""
}

# Main script logic
main() {
    while true; do
        show_menu
        
        read -p "Enter your choice (1-5): " -n 1 -r
        echo ""
        echo ""
        
        case $REPLY in
            1)
                if check_macos && check_apple_silicon; then
                    run_gpu_setup
                else
                    print_error "GPU setup is only available on macOS M1/M2"
                    echo ""
                    print_info "Please choose option 2 for cross-platform setup"
                    echo ""
                fi
                ;;
            2)
                run_no_gpu_setup
                ;;
            3)
                stop_services
                ;;
            4)
                show_system_info
                ;;
            5)
                print_info "Exiting..."
                exit 0
                ;;
            *)
                print_error "Invalid option. Please choose 1-5."
                echo ""
                ;;
        esac
        
        if [[ $REPLY == 1 || $REPLY == 2 ]]; then
            echo ""
            print_success "Setup completed! You can now use your AI assistant."
            echo ""
            print_info "To stop services later, run: ./start.sh and choose option 3"
            echo ""
            break
        fi
        
        if [[ $REPLY != 4 ]]; then
            echo ""
            read -p "Press Enter to continue..."
            echo ""
        fi
    done
}

# Run main function
main 