#!/bin/bash

# LocalAI Community - Main Startup Script
# This script provides options for different setup configurations

set -e

# Default values
INTERACTIVE_MODE=true
AUTO_CONFIRM=false
VERBOSE=false
SKIP_CHECKS=false





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



# Function to check if services are already running and restart them
check_services_running() {
    local backend_running=false
    local frontend_running=false
    
    # Check if backend is running
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        backend_running=true
    fi
    
    # Check if frontend is running
    if curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        frontend_running=true
    fi
    
    if [[ "$backend_running" == "true" || "$frontend_running" == "true" ]]; then
        print_info "Services are already running, restarting them..."
        echo ""
        if [[ "$backend_running" == "true" ]]; then
            print_info "   • Backend: http://localhost:8000 (stopping)"
        fi
        if [[ "$frontend_running" == "true" ]]; then
            print_info "   • Frontend: http://localhost:8501 (stopping)"
        fi
        echo ""
        
        # Stop existing services
        print_info "Stopping existing services..."
        ./scripts/stop-gpu-simple.sh 2>/dev/null || true
        pkill -f "run-with-gpu-simple.sh" 2>/dev/null || true
        pkill -f "run-no-gpu.sh" 2>/dev/null || true
        
        # Wait for services to stop
        sleep 3
        
        print_success "Existing services stopped, ready to restart"
        echo ""
    fi
    
    return 0
}

# Function to cleanup background processes on exit
cleanup_background_processes() {
    echo ""
    print_warning "Stopping all services..."
    
    # Stop all services cleanly
    ./scripts/stop-gpu-simple.sh 2>/dev/null || true
    
    # Kill any remaining setup processes
    pkill -f "run-with-gpu-simple.sh" 2>/dev/null || true
    pkill -f "run-no-gpu.sh" 2>/dev/null || true
    
    print_success "All services stopped!"
    exit 0
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

# Function to check if Ollama is running
check_ollama_running() {
    if pgrep -x "ollama" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to get Ollama status
get_ollama_status() {
    if check_ollama_running; then
        local ollama_pid=$(pgrep -x "ollama")
        local ollama_port=$(lsof -ti:11434 2>/dev/null | head -1)
        if [[ -n "$ollama_port" ]]; then
            # Check if Ollama is responding to API calls
            if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
                echo "running and healthy (PID: $ollama_pid, Port: 11434)"
            else
                echo "running but not responding (PID: $ollama_pid, Port: 11434)"
            fi
        else
            echo "running (PID: $ollama_pid, Port: unknown)"
        fi
    else
        echo "not running"
    fi
}

# Function to check Ollama status without starting it
ensure_ollama_running() {
    if ! check_ollama_running; then
        print_error "Ollama is not running"
        print_info "Please start Ollama manually: ollama serve"
        return 1
    else
        print_info "Using existing Ollama instance"
        return 0
    fi
}

# Function to check and kill processes using a specific port
check_and_kill_port() {
    local port=$1
    local service_name=$2
    
    if lsof -ti:$port > /dev/null 2>&1; then
        print_warning "Port $port is already in use by $service_name"
        
        # Get PIDs using the port
        local pids=$(lsof -ti:$port)
        
        # Check if this is Ollama and if it should be preserved
        if [[ "$service_name" == "Ollama" ]]; then
            print_info "Ollama is running on port $port"
            print_info "Keeping existing Ollama instance (user-managed)"
            return 0
        fi
        
        print_info "Killing processes using port $port..."
        
        # Kill each process gracefully first, then forcefully if needed
        for pid in $pids; do
            print_info "Stopping process $pid..."
            kill $pid 2>/dev/null || true
            
            # Wait a moment for graceful shutdown
            sleep 1
            
            # Check if process is still running
            if kill -0 $pid 2>/dev/null; then
                print_info "Process $pid still running, forcing termination..."
                kill -9 $pid 2>/dev/null || true
            fi
        done
        
        # Wait a moment for processes to terminate
        sleep 2
        
        # Verify port is free
        if lsof -ti:$port > /dev/null 2>&1; then
            print_error "Failed to free port $port"
            return 1
        else
            print_success "Port $port is now free"
        fi
    else
        print_success "Port $port is available"
    fi
}

# Function to show usage information
show_usage() {
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  gpu          Start GPU setup (macOS M1/M2 only)"
    echo "  nogpu        Start no-GPU setup (cross-platform)"
    echo "  quick        Auto-select best setup for your system"
    echo "  stop         Stop all services"
    echo "  status       Show system information"
    echo "  debug        Run diagnostics"
    echo "  menu         Show interactive menu (default)"
    echo ""
    echo "Options:"
    echo "  -y, --yes    Auto-confirm all prompts"
    echo "  -v, --verbose Enable verbose output"
    echo "  -q, --quiet  Disable interactive mode"
    echo "  --skip-checks Skip system compatibility checks"
    echo "  -h, --help   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Interactive menu"
    echo "  $0 quick              # Auto-select best setup"
    echo "  $0 gpu                # Start GPU setup"
    echo "  $0 nogpu -y           # Start no-GPU setup with auto-confirm"
    echo "  $0 stop               # Stop all services"
    echo "  $0 status             # Show system info"
    echo "  $0 debug              # Run diagnostics"
    echo ""
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            gpu)
                COMMAND="gpu"
                shift
                ;;
            nogpu)
                COMMAND="nogpu"
                shift
                ;;
            quick)
                COMMAND="quick"
                shift
                ;;
            stop)
                COMMAND="stop"
                shift
                ;;
            status)
                COMMAND="status"
                shift
                ;;
            debug)
                COMMAND="debug"
                shift
                ;;
            menu)
                COMMAND="menu"
                shift
                ;;
            -y|--yes)
                AUTO_CONFIRM=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -q|--quiet)
                INTERACTIVE_MODE=false
                shift
                ;;
            --skip-checks)
                SKIP_CHECKS=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
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
    
    print_option "5. 🔍 Debug GPU Setup"
    echo "   • Run comprehensive diagnostics"
    echo "   • Identify setup issues"
    echo ""
    
    print_option "6. ❌ Exit"
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
        local ollama_status=$(get_ollama_status)
        if [[ "$ollama_status" == "not running" ]]; then
            print_warning "   • Ollama is $ollama_status"
        else
            print_success "   • Ollama is $ollama_status"
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
        if [[ "$AUTO_CONFIRM" == "true" ]]; then
            print_info "Auto-confirming continuation..."
        else
            read -p "Continue anyway? (y/n): " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                return 1
            fi
        fi
    fi
    
    # Check if services are already running and restart them
    print_info "Checking if services are already running..."
    check_services_running
    
    # Check and free required ports before starting
    print_info "Checking port availability..."
    # Don't kill Ollama port - let user manage it
    check_and_kill_port 8000 "Backend"
    check_and_kill_port 8501 "Frontend"
    echo ""
    
    # Check if Ollama is running for GPU setup
    print_info "Checking Ollama status..."
    if ! ensure_ollama_running; then
        print_error "Ollama is not running. Please start it manually: ollama serve"
        return 1
    fi
    
    print_success "Running GPU setup..."
    echo ""
    
    # Run the simplified GPU setup script
    print_info "Starting GPU setup..."
    if ./scripts/run-with-gpu-simple.sh; then
        print_success "GPU setup completed successfully!"
        echo ""
        print_info "Access your GPU-accelerated AI assistant at: http://localhost:8501"
        echo ""
        print_info "Services are running in the background"
        print_info "Press Ctrl+C to stop all services"
        echo ""
        
        # Keep the script running to maintain services
        while true; do
            sleep 10
            # Check if services are still running
            if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
                print_warning "Backend service stopped"
                break
            fi
            if ! curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
                print_warning "Frontend service stopped"
                break
            fi
        done
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
    
    # Check if services are already running and restart them
    print_info "Checking if services are already running..."
    check_services_running
    
    # Check and free required ports before starting
    print_info "Checking port availability..."
    # Don't kill Ollama port - let user manage it
    check_and_kill_port 8000 "Backend"
    check_and_kill_port 8501 "Frontend"
    echo ""
    
    # For no-GPU setup, we can use existing Ollama if available
    print_info "Checking if host Ollama is available..."
    
    print_success "Running no-GPU setup..."
    echo ""
    
    # Run the no-GPU setup script
    print_info "Starting no-GPU setup..."
    if ./scripts/run-no-gpu.sh; then
        print_success "No-GPU setup completed successfully!"
        echo ""
        print_info "Access your AI assistant at: http://localhost:8501"
        echo ""
        print_info "Services are running in the background"
        print_info "Press Ctrl+C to stop all services"
        echo ""
        
        # Keep the script running to maintain services
        while true; do
            sleep 10
            # Check if services are still running
            if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
                print_warning "Backend service stopped"
                break
            fi
            if ! curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
                print_warning "Frontend service stopped"
                break
            fi
        done
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
    
    # Stop simplified GPU services
    print_info "Stopping simplified GPU services..."
    ./scripts/stop-gpu-simple.sh 2>/dev/null || true
    
    # Stop Docker services
    print_info "Stopping Docker services..."
    docker-compose -f docker/docker-compose.yml down 2>/dev/null || true
    docker-compose -f docker/docker-compose.host-ollama.yml down 2>/dev/null || true
    
    # Don't stop Ollama - let user manage it manually
    if check_ollama_running; then
        local ollama_status=$(get_ollama_status)
        print_info "Ollama is currently $ollama_status"
        print_info "Keeping Ollama running (managed by user)"
    else
        print_info "Ollama is not running"
    fi
    
    print_success "All services stopped!"
    echo ""
}

# Main script logic
main() {
    # Set up cleanup trap for Ctrl+C
    trap 'cleanup_background_processes' SIGINT SIGTERM
    
    # Parse command line arguments
    parse_arguments "$@"
    

    
    # If a specific command was provided, execute it directly
    if [[ -n "$COMMAND" ]]; then
        case $COMMAND in
            gpu)
                if [[ "$SKIP_CHECKS" == "true" ]] || (check_macos && check_apple_silicon); then
                    run_gpu_setup
                else
                    print_error "GPU setup is only available on macOS M1/M2"
                    print_info "Use --skip-checks to override this check"
                    exit 1
                fi
                ;;
            nogpu)
                run_no_gpu_setup
                ;;
            quick)
                print_header
                print_info "Auto-selecting best setup for your system..."
                echo ""
                if check_macos && check_apple_silicon; then
                    print_success "Detected macOS M1/M2 - using GPU setup"
                    run_gpu_setup
                else
                    print_info "Using cross-platform no-GPU setup"
                    run_no_gpu_setup
                fi
                ;;
            stop)
                stop_services
                ;;
            status)
                show_system_info
                ;;
            debug)
                print_info "Running GPU setup diagnostics..."
                ./scripts/debug-gpu-setup.sh
                ;;
            menu)
                # Fall through to interactive menu
                ;;
        esac
        
        # Exit after executing command (unless it's menu)
        if [[ "$COMMAND" != "menu" ]]; then
            exit 0
        fi
    fi
    
    # Interactive menu mode
    while true; do
        show_menu
        
        # Set default choice based on system compatibility
        DEFAULT_CHOICE=""
        if check_macos && check_apple_silicon; then
            DEFAULT_CHOICE="1"
            read -p "Enter your choice (1-6) [default: 1]: " -n 1 -r
        else
            DEFAULT_CHOICE="2"
            read -p "Enter your choice (1-6) [default: 2]: " -n 1 -r
        fi
        
        # Use default if no input provided
        if [[ -z "$REPLY" ]]; then
            REPLY="$DEFAULT_CHOICE"
        fi
        
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
                print_info "Running GPU setup diagnostics..."
                ./scripts/debug-gpu-setup.sh
                ;;
            6)
                print_info "Exiting..."
                exit 0
                ;;
            *)
                print_error "Invalid option. Please choose 1-6."
                echo ""
                ;;
        esac
        
        if [[ $REPLY == 1 || $REPLY == 2 ]]; then
            # The setup functions now handle their own monitoring
            # No need to break out of the loop as they will exit when done
            break
        fi
        
        if [[ $REPLY != 4 ]]; then
            echo ""
            read -p "Press Enter to continue..."
            echo ""
        fi
    done
}

# Run main function with all arguments
main "$@" 