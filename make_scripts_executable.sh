#!/bin/bash
echo "Making all scripts executable..."
chmod +x /workspaces/back/start_production.sh
chmod +x /workspaces/back/stop_server.sh
chmod +x /workspaces/back/document_dashboard.py
chmod +x /workspaces/back/launch_production.sh
chmod +x /workspaces/back/make_scripts_executable.sh

echo "All scripts are now executable."
echo "You can now run ./launch_production.sh to set up everything."
