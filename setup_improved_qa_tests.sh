#!/bin/bash

echo "===== Setting up Improved Q&A Test Scripts ====="

# Make scripts executable
chmod +x /workspaces/back/quick_qa_test.py
chmod +x /workspaces/back/run_quick_test.sh
chmod +x /workspaces/back/comprehensive_qa_test.py
chmod +x /workspaces/back/run_comprehensive_test.sh

# Create necessary directories
mkdir -p /workspaces/back/extractions
mkdir -p /workspaces/back/qa_test_results
chmod 755 /workspaces/back/extractions
chmod 755 /workspaces/back/qa_test_results

# Install required packages
pip install requests python-dotenv > /dev/null 2>&1

echo -e "\n✅ Setup complete!"
echo "To run a quick test (5 questions): ./run_quick_test.sh"
echo "To run a quick test with more questions: ./run_quick_test.sh 10"
echo "To run the comprehensive test: ./run_comprehensive_test.sh"
echo "After running tests, results are saved in /workspaces/back/qa_test_results/"
