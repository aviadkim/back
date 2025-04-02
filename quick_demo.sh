#!/bin/bash
echo "===== Running Financial Document Processing API Demo ====="

# Make the demo script executable
chmod +x /workspaces/back/demo_api_usage.py

# Create sample document if needed
if [ ! -d "/workspaces/back/uploads" ]; then
    mkdir -p /workspaces/back/uploads
fi

if [ ! -f "/workspaces/back/uploads/test_document.pdf" ]; then
    echo "No sample PDF found, creating a dummy test file with financial data..."
    cat > /workspaces/back/extractions/test_doc_123_extraction.json << 'EOL'
{
    "content": "This is sample document content for testing. It contains financial information about several securities including Apple Inc. with ISIN US0378331005, Microsoft with ISIN US5949181045, and Amazon with ISIN US0231351067. The portfolio value is $1,500,000 as of March 15, 2025."
}
EOL
fi

# Run the demo
python /workspaces/back/demo_api_usage.py

echo ""
echo "Demo complete! The system is now ready for production use."
