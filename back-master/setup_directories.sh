#!/bin/bash

# Create necessary directories
mkdir -p /workspaces/back/extractions
mkdir -p /workspaces/back/uploads
mkdir -p /workspaces/back/financial_data
mkdir -p /workspaces/back/project_organized/static

# Create a sample extraction file for testing
cat > /workspaces/back/extractions/doc_c16be22a_sample_extraction.json << 'EOL'
{
  "document_id": "doc_c16be22a",
  "filename": "sample_document.pdf",
  "page_count": 5,
  "content": "This is sample document content for testing the Q&A system. It contains financial information about several securities including Apple Inc. with ISIN US0378331005, Microsoft with ISIN US5949181045, and Amazon with ISIN US0231351067. The portfolio value is $1,500,000 as of March 15, 2025."
}
EOL

echo "Created sample extraction for testing"

# Check if created successfully
if [ -f /workspaces/back/extractions/doc_c16be22a_sample_extraction.json ]; then
    echo "✅ Successfully created sample extraction file"
    ls -la /workspaces/back/extractions/
else
    echo "❌ Failed to create sample extraction file"
fi

echo "Directories created successfully"
