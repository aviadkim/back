#!/bin/bash

echo "===== Running AI Integration Setup and Test ====="

# Make sure the script is executable
chmod +x /workspaces/back/setup_ai_module.sh

# Run the setup script
./setup_ai_module.sh

# Run the test
echo -e "\nRunning AI integration test..."
python test_ai_integration.py

echo -e "\n===== Integration Test Complete ====="
echo "You now have a working AI integration!"
echo "The AI module is available at: project_organized/shared/ai"
echo "You can import it with: from project_organized.shared.ai.service import AIService"
