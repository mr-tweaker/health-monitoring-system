#!/bin/bash
#
# Health Monitoring System - Startup Script (Shell Wrapper)
# This script provides a simple shell interface to start the system
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Python is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    print_success "Using Python: $PYTHON_CMD"
}

# Function to check if virtual environment exists
check_venv() {
    if [ -d "venv" ]; then
        print_status "Virtual environment found, activating..."
        source venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_warning "No virtual environment found"
        print_status "You may want to create one: python -m venv venv"
    fi
}

# Function to show usage
show_usage() {
    echo "Health Monitoring System - Startup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -s, --setup             Run setup first (install dependencies, generate data)"
    echo "  -d, --dashboard-only    Start only the Streamlit dashboard"
    echo "  -a, --api-only          Start only the FastAPI backend"
    echo "  -c, --check             Check system status only"
    echo ""
    echo "Examples:"
    echo "  $0                      # Start both API and dashboard"
    echo "  $0 --setup              # Run setup then start system"
    echo "  $0 --dashboard-only     # Start only dashboard"
    echo "  $0 --api-only           # Start only API"
    echo "  $0 --check              # Check system status"
}

# Function to run setup
run_setup() {
    print_status "Running system setup..."
    
    if [ -f "setup.py" ]; then
        $PYTHON_CMD setup.py
        if [ $? -eq 0 ]; then
            print_success "Setup completed successfully"
        else
            print_error "Setup failed"
            exit 1
        fi
    else
        print_error "setup.py not found"
        exit 1
    fi
}

# Function to check system status
check_status() {
    print_status "Checking system status..."
    
    # Check if API is running
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "FastAPI backend is running"
    else
        print_warning "FastAPI backend is not running"
    fi
    
    # Check if Streamlit is running
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        print_success "Streamlit dashboard is running"
    else
        print_warning "Streamlit dashboard is not running"
    fi
    
    # Check database
    if [ -f "data/health_monitoring.db" ]; then
        print_success "Database exists"
    else
        print_warning "Database not found"
    fi
}

# Main function
main() {
    print_status "Health Monitoring System - Startup Script"
    echo "================================================"
    
    # Check Python
    check_python
    
    # Check virtual environment
    check_venv
    
    # Parse command line arguments
    case "${1:-}" in
        -h|--help)
            show_usage
            exit 0
            ;;
        -s|--setup)
            run_setup
            print_status "Starting system after setup..."
            $PYTHON_CMD start_system.py
            ;;
        -d|--dashboard-only)
            print_status "Starting Streamlit dashboard only..."
            $PYTHON_CMD -c "
import sys
import types

# Create mock imghdr module
imghdr = types.ModuleType('imghdr')
def mock_what(file, h=None): return None
imghdr.what = mock_what
imghdr.test_jpeg = lambda h, f: None
imghdr.test_png = lambda h, f: None
imghdr.test_gif = lambda h, f: None
imghdr.test_bmp = lambda h, f: None
sys.modules['imghdr'] = imghdr

# Now import and run streamlit
import streamlit.web.cli as stcli
sys.argv = ['streamlit', 'run', 'frontend/dashboard.py', '--server.port', '8501', '--server.address', '0.0.0.0']
stcli.main()
"
            ;;
        -a|--api-only)
            print_status "Starting FastAPI backend only..."
            $PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
            ;;
        -c|--check)
            check_status
            exit 0
            ;;
        "")
            print_status "Starting complete system..."
            $PYTHON_CMD start_system.py
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
