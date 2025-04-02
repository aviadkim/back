#!/bin/bash
# Start both backend and frontend

echo "Starting backend with vertical slice architecture..."
cd project_organized
python app.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "Backend started with PID $BACKEND_PID"
echo "Application is running at http://localhost:5001"

# Trap Ctrl+C to clean up processes
trap "echo 'Shutting down...'; kill $BACKEND_PID; exit" INT TERM

# Wait for Ctrl+C
echo "Press Ctrl+C to stop the application"
wait
