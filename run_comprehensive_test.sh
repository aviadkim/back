#!/bin/bash

echo "===== Running Comprehensive Document Q&A Test ====="

# Check if python is available
if ! command -v python &> /dev/null; then
    echo "Python is not available. Using python3 command instead."
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Check if the application is running
echo "Checking if application is running..."
curl -s http://localhost:5003/health > /dev/null
if [ $? -ne 0 ]; then
    echo "Application is not running at http://localhost:5003"
    echo "Starting application..."
    
    cd /workspaces/back/project_organized
    nohup $PYTHON_CMD app.py > /workspaces/back/app.log 2>&1 &
    APP_PID=$!
    
    # Wait for the application to start
    echo "Waiting for application to start..."
    for i in {1..30}; do
        echo -n "."
        sleep 1
        curl -s http://localhost:5003/health > /dev/null
        if [ $? -eq 0 ]; then
            echo " Application started!"
            break
        fi
        
        if [ $i -eq 30 ]; then
            echo " Failed to start application."
            echo "Check /workspaces/back/app.log for details."
            exit 1
        fi
    done
else
    echo "Application is running at http://localhost:5003"
fi

# Install required packages
echo "Installing required packages..."
pip install requests python-dotenv > /dev/null 2>&1

# Make the test script executable
chmod +x /workspaces/back/comprehensive_qa_test.py

# Create directory for test results
mkdir -p /workspaces/back/qa_test_results

echo -e "\nRunning comprehensive document Q&A test..."
$PYTHON_CMD /workspaces/back/comprehensive_qa_test.py --url http://localhost:5003

echo -e "\nTest completed! Results are saved in the qa_test_results directory."
echo "To view the results: ls -la /workspaces/back/qa_test_results"
