#!/bin/bash
if [ -f /workspaces/back/.server_pid ]; then
  PID=$(cat /workspaces/back/.server_pid)
  if ps -p $PID > /dev/null; then
    echo "Stopping server (PID: $PID)..."
    kill $PID
    rm /workspaces/back/.server_pid
    echo "Server stopped."
  else
    echo "Server not running (stale PID file)."
    rm /workspaces/back/.server_pid
  fi
else
  pkill -f "python app.py" || echo "No running server found."
fi
