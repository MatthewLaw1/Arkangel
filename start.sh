#!/bin/bash

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
    return $?
}

# Function to check Python version
check_python_version() {
    if command -v python3.11 &> /dev/null; then
        echo "python3.11"
    else
        echo "Please install Python 3.11: brew install python@3.11"
        exit 1
    fi
}

# Function to create and activate virtual environment
setup_venv() {
    echo "Setting up Python virtual environment..."
    PYTHON_CMD=$(check_python_version)
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install core dependencies first
    pip install python-dotenv
    pip install openai
    pip install gradio==5.23.1
    pip install "pandas<2.2.0"  # Use older pandas version
    pip install langchain-core
    pip install langchain
}

# Check if Chrome debugging is already enabled
if ! port_in_use 9222; then
    echo "Starting Chrome with remote debugging..."
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
        --remote-debugging-port=9222 \
        --user-data-dir="$HOME/Library/Application Support/Google/Chrome" \
        --no-first-run \
        --no-default-browser-check \
        --start-maximized &

    echo "Waiting for Chrome to start..."
    sleep 2
else
    echo "Chrome debugging already enabled on port 9222"
fi

# Set up virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    setup_venv
else
    source venv/bin/activate
fi

cd web-ui

echo "Installing remaining dependencies..."
# Remove problematic version constraint for langchain-ibm
sed -i '' 's/langchain-ibm==0.3.10/langchain-ibm>=0.3.5/g' requirements.txt
pip install --no-deps -r requirements.txt

# Install any missing dependencies
pip install -r <(pip freeze | grep -i "langchain")

# Verify installations
python -c "import gradio; import openai; import pandas; import langchain_core; print('All core packages installed successfully!')"

# Start the webUI
echo "Starting webUI..."
python webui.py