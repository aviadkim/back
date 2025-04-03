#!/bin/bash

echo "===== Setting Up Environment Variables ====="

# Check if .env already exists
if [ -f ".env" ]; then
    echo "An .env file already exists. Do you want to replace it? (y/n)"
    read answer
    if [ "$answer" != "y" ]; then
        echo "Keeping existing .env file."
        exit 0
    fi
fi

# Check if .env.example exists
if [ ! -f ".env.example" ]; then
    echo "Error: .env.example file not found."
    exit 1
fi

# Create .env from .env.example
cp .env.example .env
echo "Created .env file from template."

# Prompt for OpenRouter API key
echo ""
echo "You need an OpenRouter API key for AI functionality."
echo "Get a key at: https://openrouter.ai/"
echo ""
echo "Enter your OpenRouter API key (should start with sk-or-): "
read api_key

# Update the API key in .env
sed -i "s|your_openrouter_api_key_here|$api_key|" .env
echo ""

echo "✅ Environment setup complete!"
echo "You can now run the application with: ./run_with_setup.sh"
