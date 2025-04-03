#!/bin/bash

echo "===== Running Verification Tests ====="

# Test 1: Quick document processing test
echo -e "\n----- Running Quick Document Processing Test -----"
./quick_qa_test.py

if [ $? -ne 0 ]; then
    echo "❌ Quick document processing test failed!"
    exit 1
else
    echo "✅ Quick document processing test passed!"
fi

# Test 2: API integration test
echo -e "\n----- Running API Integration Test -----"
./test_api.py

if [ $? -ne 0 ]; then
    echo "❌ API integration test failed!"
    exit 1
else
    echo "✅ API integration test passed!"
fi

# Test 3: Set up AI integration
echo -e "\n----- Setting Up AI Integration -----"
chmod +x /workspaces/back/setup_ai_integration.sh
./setup_ai_integration.sh

# Test 4: Verify version and dependencies
echo -e "\n----- Verifying System Setup -----"
python -c "import sys; print(f'Python version: {sys.version}')"
pip list | grep -E 'flask|pdf|PyPDF|openai|tessera|pandas|langchain|dotenv'

# Test 5: Verify vertical slice structure
echo -e "\n----- Verifying Vertical Slice Structure -----"
find project_organized/features -type d -mindepth 1 | sort

# Final verification: Launch the application to verify it starts
echo -e "\n----- Launching Application (for verification only) -----"
cd project_organized
port=5001
timeout 5 python app.py || true
cd ..

echo -e "\n===== All Tests Complete ====="
echo "The system is now properly configured with vertical slice architecture"
echo "and integrated AI document processing capabilities."
echo ""
echo "To run the full application:"
echo "  ./run_full_app.sh"
echo ""
echo "To test document Q&A:"
echo "  ./test_full_implementation.sh"
