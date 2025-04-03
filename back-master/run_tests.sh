#!/bin/bash

# =========================================================
# Test runner for Financial Documents Analysis System
# =========================================================

echo -e "\033[1;34m===== Running Tests for Financial Documents Analysis System (v5.0) =====\033[0m"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "\033[1;31mPython is not installed. Please install Python 3.8 or higher.\033[0m"
    exit 1
fi

# Create necessary directories for testing
echo -e "\033[1;33mCreating test directories...\033[0m"
mkdir -p test_uploads test_data/embeddings test_data/templates test_logs

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo -e "\033[1;33mCreating virtual environment...\033[0m"
    python -m venv venv
    source venv/bin/activate
    echo -e "\033[1;32mVirtual environment created and activated.\033[0m"
else
    source venv/bin/activate
    echo -e "\033[1;32mVirtual environment activated.\033[0m"
fi

# Install test requirements
echo -e "\033[1;33mInstalling/updating test dependencies...\033[0m"
pip install pytest pytest-flask pytest-cov

# Run the tests
echo -e "\033[1;33mRunning tests...\033[0m"
python -m pytest tests/ -v

# Run tests with coverage report if requested
if [ "$1" == "--coverage" ]; then
    echo -e "\033[1;33mRunning tests with coverage report...\033[0m"
    python -m pytest tests/ --cov=features --cov=agent_framework --cov-report=term --cov-report=html
    echo -e "\033[1;32mCoverage report generated in htmlcov/ directory.\033[0m"
fi

# Deactivate virtual environment
deactivate

echo -e "\033[1;34m===== Tests completed =====\033[0m"
