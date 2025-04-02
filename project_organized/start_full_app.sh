#!/bin/bash
echo "Starting Financial Document Processor with vertical slice architecture..."

<<<<<<< HEAD
# Make sure we're in the correct directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Make sure environment variables are loaded
if [ -f ../.env ]; then
    export $(grep -v '^#' ../.env | xargs)
fi

echo "Starting Flask application..."
=======
# Add the project root to PYTHONPATH
export PYTHONPATH=/workspaces/back:$PYTHONPATH

echo "Starting Flask application..."
# Try to run the app on port 5001
>>>>>>> main
python app.py
