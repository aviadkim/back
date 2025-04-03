#!/bin/bash

echo "===== Setting up Comprehensive Document Q&A Test ====="

# Make scripts executable
chmod +x /workspaces/back/comprehensive_qa_test.py
chmod +x /workspaces/back/run_comprehensive_test.sh
chmod +x /workspaces/back/analyze_qa_results.py

# Create directory for test results
mkdir -p /workspaces/back/qa_test_results

# Install required packages
pip install requests python-dotenv reportlab > /dev/null 2>&1

echo -e "\n✅ Setup complete!"
echo "To run the comprehensive test: ./run_comprehensive_test.sh"
echo "After running the test, analyze the results with: python analyze_qa_results.py"
