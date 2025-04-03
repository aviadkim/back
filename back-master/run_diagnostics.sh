#!/bin/bash

echo "===== Running API Diagnostics ====="

# First, make sure the directories are set up
chmod +x /workspaces/back/setup_directories.sh
/workspaces/back/setup_directories.sh

# Check if the application is running
echo "Checking if application is running..."
curl -s http://localhost:5001/health > /dev/null
if [ $? -ne 0 ]; then
    echo "Application is not running, starting it now..."
    cd /workspaces/back/project_organized
    python app.py > /dev/null 2>&1 &
    APP_PID=$!
    
    # Wait for app to start
    echo "Waiting for application to start..."
    for i in {1..10}; do
        sleep 1
        curl -s http://localhost:5001/health > /dev/null
        if [ $? -eq 0 ]; then
            echo "Application started successfully."
            break
        fi
        if [ $i -eq 10 ]; then
            echo "Failed to start application. Please check logs."
            exit 1
        fi
    done
else
    echo "Application is already running."
fi

# Run the diagnostics
echo "Running API diagnostics..."
python /workspaces/back/api_diagnostic.py

# Print summary
echo -e "\nNOTE: If some endpoints fail, try running the fix_all_issues.sh script:"
echo "chmod +x /workspaces/back/fix_all_issues.sh"
echo "./fix_all_issues.sh"
