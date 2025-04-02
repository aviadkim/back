#!/bin/bash

echo "===== Running Financial Document Processor Simulation ====="

# First make sure the app is running
echo "Checking if application is running..."
curl -s http://localhost:5001/health > /dev/null
if [ $? -ne 0 ]; then
    echo "Application is not running. Starting it now..."
    cd /workspaces/back/project_organized
    python app.py > /dev/null 2>&1 &
    APP_PID=$!
    echo "Waiting for application to start..."
    sleep 3
    # Check again
    curl -s http://localhost:5001/health > /dev/null
    if [ $? -ne 0 ]; then
        echo "Failed to start application. Please run it manually with:"
        echo "cd /workspaces/back/project_organized && python app.py"
        exit 1
    fi
    echo "Application started with PID: $APP_PID"
else
    echo "Application is already running"
fi

# Fix issues first
echo "Applying fixes to issues..."
python simulation_test.py --fix

# Run the simulation test
echo -e "\nRunning simulation test..."
python simulation_test.py

TEST_STATUS=$?
if [ $TEST_STATUS -eq 0 ]; then
    echo -e "\n✅ All tests passed! The application is working correctly."
else
    echo -e "\n❌ Some tests failed. Please check the logs above for details."
fi

echo -e "\nYou can now access the application at http://localhost:5001"
echo "To stop the application, find its PID with 'ps aux | grep app.py' and run 'kill <PID>'"

exit $TEST_STATUS
