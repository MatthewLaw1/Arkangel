#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${BLUE}[Arkangel]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[Success]${NC} $1"
}

print_error() {
    echo -e "${RED}[Error]${NC} $1"
}

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    print_message "Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_message "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Install/upgrade pip
print_message "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_message "Installing requirements..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install requirements"
    exit 1
fi
print_success "Requirements installed"

# Function to check if a port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Check if port 5000 is already in use
if check_port 5000; then
    print_error "Port 5000 is already in use. Please free up the port and try again."
    exit 1
fi

# Function to run tests
run_tests() {
    print_message "Running tests..."
    
    # Test 1: Check if main.py can start
    print_message "Test 1: Starting main.py..."
    python main.py &
    MAIN_PID=$!
    sleep 5
    
    if ! check_port 5000; then
        print_error "Test 1 failed: main.py failed to start"
        kill $MAIN_PID 2>/dev/null
        exit 1
    fi
    print_success "Test 1 passed: main.py started successfully"
    
    # Test 2: Check if browser_controller.py can start
    print_message "Test 2: Starting browser_controller.py..."
    python browser_controller.py &
    CONTROLLER_PID=$!
    sleep 5
    
    if ! ps -p $CONTROLLER_PID > /dev/null; then
        print_error "Test 2 failed: browser_controller.py failed to start"
        kill $MAIN_PID $CONTROLLER_PID 2>/dev/null
        exit 1
    fi
    print_success "Test 2 passed: browser_controller.py started successfully"
    
    # Cleanup test processes
    kill $MAIN_PID $CONTROLLER_PID 2>/dev/null
    print_success "All tests passed!"
}

# Function to start the system
start_system() {
    print_message "Starting Arkangel system..."
    
    # Start main.py in the background
    python main.py &
    MAIN_PID=$!
    print_message "Started focus monitoring (PID: $MAIN_PID)"
    
    # Wait for the API to be ready
    sleep 5
    
    # Start browser_controller.py in the background
    python browser_controller.py &
    CONTROLLER_PID=$!
    print_message "Started browser controller (PID: $CONTROLLER_PID)"
    
    # Save PIDs to a file for later cleanup
    echo "$MAIN_PID $CONTROLLER_PID" > .arkangel_pids
    
    print_success "Arkangel system is running!"
    print_message "Press Ctrl+C to stop the system"
    
    # Wait for user interrupt
    trap 'cleanup' INT
    wait
}

# Function to cleanup processes
cleanup() {
    print_message "Cleaning up..."
    if [ -f .arkangel_pids ]; then
        read MAIN_PID CONTROLLER_PID < .arkangel_pids
        kill $MAIN_PID $CONTROLLER_PID 2>/dev/null
        rm .arkangel_pids
    fi
    print_success "Cleanup complete"
    exit 0
}

# Main menu
while true; do
    echo -e "\n${BLUE}Arkangel Control Panel${NC}"
    echo "1. Run tests"
    echo "2. Start system"
    echo "3. Exit"
    read -p "Select an option (1-3): " choice
    
    case $choice in
        1)
            run_tests
            ;;
        2)
            start_system
            ;;
        3)
            cleanup
            exit 0
            ;;
        *)
            print_error "Invalid option"
            ;;
    esac
done 