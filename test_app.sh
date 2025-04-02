#!/bin/bash

# =========================================================
# Test script for Financial Documents Analysis System
# =========================================================

echo -e "\033[1;34m===== Testing Financial Documents Analysis System (v5.0) =====\033[0m"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "\033[1;31mPython is not installed. Please install Python 3.8 or higher.\033[0m"
    exit 1
fi

# Create necessary directories
echo -e "\033[1;33mCreating necessary directories...\033[0m"
mkdir -p uploads logs

# Check if the application is running
if ! curl -s http://localhost:5001/health > /dev/null; then
    echo -e "\033[1;33mStarting the application...\033[0m"
    # Start the application in the background
    python vertical_slice_app.py > logs/app.log 2>&1 &
    APP_PID=$!
    
    echo -e "\033[1;32mApplication started with PID $APP_PID\033[0m"
    echo -e "\033[1;33mWaiting for the application to initialize...\033[0m"
    
    # Wait for the application to start
    for i in {1..20}; do
        if curl -s http://localhost:5001/health > /dev/null; then
            echo -e "\033[1;32mApplication is running!\033[0m"
            break
        fi
        if [ $i -eq 20 ]; then
            echo -e "\033[1;31mApplication failed to start. Check logs/app.log for details.\033[0m"
            exit 1
        fi
        sleep 1
        echo -n "."
    done
    echo ""
    
    # Store the PID for cleanup
    echo $APP_PID > .app_pid
else
    echo -e "\033[1;32mApplication is already running.\033[0m"
fi

# Install required packages for testing
echo -e "\033[1;33mInstalling test dependencies...\033[0m"
pip install requests

# Run the test script
echo -e "\033[1;33mRunning tests...\033[0m"
python test_vertical_slice.py

# Get test exit code
TEST_EXIT_CODE=$?

# Clean up if we started the application
if [ -f .app_pid ]; then
    APP_PID=$(cat .app_pid)
    echo -e "\033[1;33mStopping the application (PID $APP_PID)...\033[0m"
    kill $APP_PID
    rm .app_pid
    echo -e "\033[1;32mApplication stopped.\033[0m"
fi

exit $TEST_EXIT_CODE
