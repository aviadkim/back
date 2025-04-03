#!/bin/bash
echo "===== Starting Full Document Processing System ====="

# Check if API key is set
if [ ! -f .env ] || ! grep -q "OPENROUTER_API_KEY" .env; then
    echo "You need to set up API keys first. Running setup script..."
    ./setup_ai_integration.sh
fi

# Make all scripts executable
find . -name "*.sh" -exec chmod +x {} \;

# Start the application
echo "Starting the application..."
cd project_organized
./start_full_app.sh
