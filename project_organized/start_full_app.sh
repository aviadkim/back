#!/bin/bash
echo "Starting Financial Document Processor with vertical slice architecture..."

# Add the project root to PYTHONPATH
export PYTHONPATH=/workspaces/back:$PYTHONPATH

echo "Starting Flask application..."
# Try to run the app on port 5001
python app.py
