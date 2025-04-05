#!/bin/bash
echo "Installing critical dependencies manually..."

# Install essential packages first
# pip install numpy==1.24.3 pandas==1.5.3 # Handled by requirements.txt

# Install specific LangChain packages
pip install langchain==0.3.21 langchain-community==0.3.20 langchain-openai==0.3.11 boto3

# Install other required packages
pip install sentence-transformers

# Install rest of requirements file without strict version pinning
pip install -r requirements.txt --no-deps

echo "Dependency installation complete."
