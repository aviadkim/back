#!/bin/bash

# Script to check, start, or stop the Financial Document Processor

function check_status() {
    echo "Checking application status..."
    APP_PROCESS=$(ps aux | grep "python app.py" | grep -v grep)
    
    if [ -n "$APP_PROCESS" ]; then
        echo "✅ Application is running:"
        echo "$APP_PROCESS"
        
        # Check which ports are being used
        echo -e "\nPorts in use:"
        for port in 5001 5002 5003 5004 5005; do
            PORT_IN_USE=$(lsof -i:$port 2>/dev/null)
            if [ -n "$PORT_IN_USE" ]; then
                echo "Port $port: In use by PID $(echo "$PORT_IN_USE" | awk 'NR>1 {print $2}' | uniq)"
            fi
        done
        
        return 0
    else
        echo "❌ Application is not running"
        return 1
    fi
}

function start_app() {
    echo "Starting application..."
    cd /workspaces/back/project_organized
    python app.py &
    echo "Application started in background. Run $0 status to check status."
}

function stop_app() {
    echo "Stopping application..."
    APP_PROCESS=$(ps aux | grep "python app.py" | grep -v grep)
    
    if [ -n "$APP_PROCESS" ]; then
        PID=$(echo "$APP_PROCESS" | awk '{print $2}')
        echo "Stopping application with PID $PID"
        kill $PID
        echo "Application stopped"
    else
        echo "No running application found"
    fi
    
    # Also check for any processes using the ports
    for port in 5001 5002 5003 5004 5005; do
        PORT_IN_USE=$(lsof -i:$port 2>/dev/null)
        if [ -n "$PORT_IN_USE" ]; then
            PID=$(echo "$PORT_IN_USE" | awk 'NR>1 {print $2}' | uniq)
            echo "Found process using port $port (PID: $PID). Stopping it..."
            kill $PID
        fi
    done
}

function show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  status    Check if the application is running"
    echo "  start     Start the application"
    echo "  stop      Stop the application"
    echo "  restart   Restart the application"
    echo ""
    echo "Example: $0 status"
}

# Main logic
case "$1" in
    status)
        check_status
        ;;
    start)
        # Check if already running
        if check_status; then
            echo "Application is already running. Use '$0 restart' to restart it."
        else
            start_app
        fi
        ;;
    stop)
        stop_app
        ;;
    restart)
        stop_app
        sleep 2
        start_app
        ;;
    *)
        show_help
        ;;
esac
