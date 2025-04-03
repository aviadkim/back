#!/bin/bash

echo "===== Installing AI Integration Requirements ====="

# Install required packages
pip3 install requests python-dotenv google-generativeai huggingface_hub

echo "Creating necessary directories"
mkdir -p /workspaces/back/extractions
mkdir -p /workspaces/back/uploads

# Create a shared init file if needed
mkdir -p /workspaces/back/project_organized/shared
if [ ! -f "/workspaces/back/project_organized/shared/__init__.py" ]; then
    echo '"""Shared modules for the application."""' > /workspaces/back/project_organized/shared/__init__.py
fi

echo "✅ All requirements installed!"
echo "Now you can run: python test_ai_integration.py to test the AI integration"
