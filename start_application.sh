#!/bin/bash

echo "===== Starting Financial Document Processor ====="

# Check if frontend build exists
if [ ! -d "frontend/build" ]; then
  echo "❌ Error: Frontend build not found. Run 'cd frontend && npm run build' first."
  exit 1
fi

# Start the application in the correct directory
cd project_organized
echo "Starting API server..."
python app.py &
API_PID=$!

echo "Application is running!"
echo "Access the frontend at: http://localhost:5001"
echo "API endpoints available at: http://localhost:5001/api/*"
echo "Press CTRL+C to stop the application"

# Wait for the API server process
wait $API_PID
