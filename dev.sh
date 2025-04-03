#!/bin/bash
# dev.sh - Development mode with hot reloading

# Ensure FLASK_APP is set (adjust if your main app file is different)
export FLASK_APP=app.py 
export FLASK_ENV=development
export FLASK_DEBUG=1

echo "Starting frontend development server in the background..."
# Start frontend development server in the background
# Ensure you are in the correct directory if frontend is not in the root
(cd frontend && npm start) &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"

# Trap signals to ensure background process is killed on exit
trap "echo 'Stopping frontend server...'; kill $FRONTEND_PID; exit" SIGINT SIGTERM

echo "Starting Flask backend server with auto-reload..."
# Start Flask in debug mode (will auto-reload on Python file changes)
# Use port 5000 as specified in the instructions
flask run --host=0.0.0.0 --port=5000

# Wait for frontend process to finish if Flask exits normally (less likely in dev)
wait $FRONTEND_PID