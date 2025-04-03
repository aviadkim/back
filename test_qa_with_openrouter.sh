#!/bin/bash

echo "===== Testing Q&A Feature with OpenRouter Integration ====="

# Make sure the test script is executable
chmod +x /workspaces/back/test_qa_feature.py

# Ensure directories exist and have proper permissions
mkdir -p /workspaces/back/extractions
chmod 755 /workspaces/back/extractions

# Verify OpenRouter setup first
echo "Verifying OpenRouter configuration..."
python /workspaces/back/debug_api_keys.py --quick > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ OpenRouter configuration issue detected. Running fix script first..."
    ./fix_openrouter.sh
else
    echo "✅ OpenRouter configuration is valid."
fi

# Run the test
echo -e "\nRunning Q&A test with OpenRouter..."
python /workspaces/back/test_qa_feature.py

echo -e "\n===== Test Complete ====="
echo "If tests pass, you now have a working document Q&A system with AI integration!"
echo "You can use it in your application by importing: from project_organized.features.document_qa.service import DocumentQAService"
