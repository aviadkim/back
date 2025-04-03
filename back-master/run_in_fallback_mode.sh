#!/bin/bash

echo "===== Running in Fallback Mode (No API Keys) ====="

# Update .env file to use fallback mode
cat > /workspaces/back/.env << 'EOL'
# API Keys for External Services
# In fallback mode, we don't need actual API keys
HUGGINGFACE_API_KEY=hf_dummy_key_replace_with_valid_one
GEMINI_API_KEY=AIzaNotARealKey_ReplaceWithYourValidKey

# Model Configuration - Forcing fallback mode
DEFAULT_MODEL=fallback
HUGGINGFACE_MODEL=google/flan-t5-small
GEMINI_MODEL=gemini-pro

# Application Configuration
DEBUG=true
PORT=5001
MAX_UPLOAD_SIZE=100MB
DEFAULT_LANGUAGE=heb+eng
OCR_DPI=300
EOL

# Fix directory permissions
echo "Setting up directories with proper permissions..."
chmod +x /workspaces/back/fix_directory_permissions.sh
/workspaces/back/fix_directory_permissions.sh

# Setup AI module structure with fallback mode
echo "Setting up AI module with enhanced fallback capabilities..."
chmod +x /workspaces/back/setup_ai_module.sh
/workspaces/back/setup_ai_module.sh

# Create a test document
echo "Creating test document..."
mkdir -p /workspaces/back/extractions
cat > /workspaces/back/extractions/doc_test123_extraction.json << 'EOL'
{
  "document_id": "doc_test123",
  "filename": "test_document.pdf",
  "page_count": 3,
  "content": "This is a financial report for XYZ Corp dated March 15, 2025.\n\nThe company has assets worth $1,500,000 as of December 31, 2024.\nThe portfolio includes holdings in Apple Inc. (ISIN US0378331005) worth $250,000,\nMicrosoft Corp. (ISIN US5949181045) worth $300,000, and Tesla Inc. (ISIN US88160R1014) worth $150,000.\n\nThe portfolio allocation is:\n- Stocks: 75%\n- Bonds: 15%\n- Cash: 10%\n\nThe valuation date of this report is March 15, 2025."
}
EOL

# Run test to verify fallback mode works correctly
echo "Testing the fallback mode..."
python test_ai_integration.py

echo -e "\n✅ System has been configured to run in fallback mode."
echo "In this mode, the system will use rule-based responses instead of AI APIs."
echo "To use AI services, obtain valid API keys and update the .env file."
echo ""
echo "You can start the application with: ./run_with_setup.sh"
echo "The Q&A feature will function with basic extraction capabilities."
