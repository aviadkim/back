#!/bin/bash

echo "===== Running Quick Document Q&A Test ====="

# Number of questions to test (default: 5)
QUESTIONS=5
if [ -n "$1" ]; then
    QUESTIONS=$1
fi

# Create necessary directories
mkdir -p /workspaces/back/extractions
mkdir -p /workspaces/back/qa_test_results
chmod 755 /workspaces/back/extractions
chmod 755 /workspaces/back/qa_test_results

# Make sure the test script is executable
chmod +x /workspaces/back/quick_qa_test.py

# Check if the application is running
curl -s http://localhost:5003/health > /dev/null
if [ $? -ne 0 ]; then
    echo "The application is not running at http://localhost:5003"
    echo "Starting application..."
    
    cd /workspaces/back/project_organized
    python app.py > /dev/null 2>&1 &
    APP_PID=$!
    
    echo "Waiting for application to start..."
    for i in {1..10}; do
        echo -n "."
        sleep 1
        curl -s http://localhost:5003/health > /dev/null
        if [ $? -eq 0 ]; then
            echo " Started!"
            break
        fi
        
        if [ $i -eq 10 ]; then
            echo " Failed to start application."
            echo "Check app.py for errors"
            exit 1
        fi
    done
else
    echo "Application is already running at http://localhost:5003"
fi

# Run the quick test
echo -e "\nRunning quick test with $QUESTIONS questions..."
python /workspaces/back/quick_qa_test.py --questions $QUESTIONS

# Show results
echo -e "\nLatest test results:"
ls -lt /workspaces/back/qa_test_results/quick_qa_test_*.txt | head -n 1 | xargs cat

echo -e "\nTest complete! To run with more questions, use: ./run_quick_test.sh [number]"
