#!/bin/bash

# =========================================================
# Quickstart script for Financial Documents Analysis System
# =========================================================

echo -e "\033[1;34m===== Financial Document Analysis System - Quickstart (v5.0) =====\033[0m"

# Check if any arguments were provided
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo -e "\033[1;33mUsage:\033[0m"
    echo -e "  ./quickstart.sh [options]"
    echo -e "\033[1;33mOptions:\033[0m"
    echo -e "  --help, -h       Show this help message"
    echo -e "  --run            Run the application only"
    echo -e "  --test           Run tests only"
    echo -e "  --full           Install all dependencies (not just minimal set)"
    echo -e "  No options will run both the application and tests with minimal dependencies"
    exit 0
fi

# Make all scripts executable
chmod +x run.sh test_app.sh install_basic_deps.sh

# Create necessary directories
mkdir -p uploads logs

# If only running the application
if [ "$1" == "--run" ]; then
    echo -e "\033[1;33mRunning the application...\033[0m"
    ./run.sh ${@:2}
    exit 0
fi

# If only running tests
if [ "$1" == "--test" ]; then
    echo -e "\033[1;33mRunning tests...\033[0m"
    ./test_app.sh
    exit 0
fi

# Default: Install dependencies, run application and tests
echo -e "\033[1;33mInstalling dependencies...\033[0m"
if [ "$1" == "--full" ]; then
    ./install_basic_deps.sh --full
else
    ./install_basic_deps.sh
fi

echo -e "\033[1;33mStarting application in the background...\033[0m"
python vertical_slice_app.py > logs/app.log 2>&1 &
APP_PID=$!

# Store the PID for cleanup
echo $APP_PID > .app_pid

echo -e "\033[1;33mWaiting for the application to start...\033[0m"
for i in {1..20}; do
    if curl -s http://localhost:5001/health > /dev/null; then
        echo -e "\033[1;32mApplication started successfully!\033[0m"
        break
    fi
    if [ $i -eq 20 ]; then
        echo -e "\033[1;31mApplication failed to start. Check logs/app.log for details.\033[0m"
        if [ -f .app_pid ]; then
            kill $(cat .app_pid)
            rm .app_pid
        fi
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""

echo -e "\033[1;33mRunning tests...\033[0m"
python test_vertical_slice.py

# Get test exit code
TEST_EXIT_CODE=$?

# Clean up
if [ -f .app_pid ]; then
    echo -e "\033[1;33mStopping the application...\033[0m"
    kill $(cat .app_pid)
    rm .app_pid
fi

echo -e "\033[1;34m===== Quickstart complete! =====\033[0m"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "\033[1;32mAll tests passed! The application is working properly.\033[0m"
    echo -e "\033[1;33mTo run the application again, use: ./run.sh\033[0m"
else
    echo -e "\033[1;31mSome tests failed. Check the output above for details.\033[0m"
fi

exit $TEST_EXIT_CODE
