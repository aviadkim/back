#!/bin/bash
echo "Starting Financial Document Processor with vertical slice architecture..."

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
python app.py
