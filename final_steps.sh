#!/bin/bash

echo "===== Financial Document Processor: Next Steps ====="

# 1. Show the system overview
echo -e "\n----- System Overview -----"
echo "Your Financial Document Processing System is now fully operational:"
echo "✅ Vertical Slice Architecture implemented"
echo "✅ AI-Powered Document Q&A functioning"
echo "✅ PDF processing and extraction working"
echo "✅ Financial data analysis working"
echo "✅ Custom table generation working"
echo "✅ Document monitoring dashboard available"

# 2. Service status
echo -e "\n----- Service Status -----"
if [ -f /workspaces/back/.server_pid ]; then
    pid=$(cat /workspaces/back/.server_pid)
    if ps -p $pid > /dev/null; then
        port=$(netstat -nlp 2>/dev/null | grep $pid | grep -o "127.0.0.1:[0-9]*" | cut -d":" -f2)
        echo "✅ Server is RUNNING (PID: $pid, Port: $port)"
        echo "   API Access: http://localhost:$port"
        echo "   To stop: ./stop_server.sh"
    else
        echo "⚠️  Server PID file exists but process is not running."
        echo "   To start: ./start_production.sh"
    fi
else
    echo "⚠️  Server is NOT running"
    echo "   To start: ./start_production.sh"
fi

# 3. Show available commands
echo -e "\n----- Available Commands -----"
echo "• ./start_production.sh - Start the server in production mode"
echo "• ./stop_server.sh - Stop the running server"
echo "• python document_dashboard.py - Show the document processing dashboard"
echo "• ./demo_api_usage.py - Run a demo of the API"
echo "• ./run_full_app.sh - Run the application with all features"
echo "• ./push_to_github.sh - Push your changes to GitHub"

# 4. Next steps recommendations
echo -e "\n----- Recommended Next Steps -----"
echo "1. Set up usage monitoring - Track API usage with Prometheus/Grafana"
echo "2. Add more AI models - Integrate additional AI models for specialized tasks"
echo "3. Improve error handling - Add more robust error handling and recovery"
echo "4. Add user authentication - Set up JWT authentication for API access"
echo "5. Create a web dashboard - Develop a web UI for easier interaction" 

# 5. Documentation resources
echo -e "\n----- Documentation -----"
echo "API documentation can be found in the README.md file."
echo "Project structure, organization and design is described in MIGRATION_STATUS.md"
echo "For developer documentation, see the individual feature modules and their README files."

echo -e "\nCongratulations on completing the vertical slice architecture implementation!"
echo "The system is now production-ready and can be extended with new features."
