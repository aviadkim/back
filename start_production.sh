#!/bin/bash

# Set environment variables
export PYTHONPATH=/workspaces/back:$PYTHONPATH
export FLASK_ENV=production
export FLASK_DEBUG=0

# Change directory to project root
cd /workspaces/back/project_organized

# Try different ports in case one is already in use
for port in 5000 5001 5002 5003 5004; do
  echo "Trying to start server on port $port..."
  PORT=$port python app.py &
  SERVER_PID=$!
  
  # Wait briefly to see if the server starts successfully
  sleep 3
  if kill -0 $SERVER_PID 2>/dev/null; then
    echo "Server started successfully on port $port (PID: $SERVER_PID)"
    echo "$SERVER_PID" > /workspaces/back/.server_pid
    echo "To stop the server, run: ./stop_server.sh"
    exit 0
  fi
done

echo "Failed to start server on any port."
exit 1
