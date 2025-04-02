#!/bin/bash
# Run tests on the new architecture

echo "===== Testing New Architecture ====="

# Change to project directory
cd project_organized

# Run pytest
echo "Running tests..."
python -m pytest features/**/tests/ -v

# Test API endpoints
echo -e "\nTesting API endpoints..."
curl -s http://localhost:5001/health | python -m json.tool
curl -s http://localhost:5001/api/documents | python -m json.tool

echo -e "\nTests completed"
