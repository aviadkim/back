#!/bin/bash

echo "===== Setting Up and Running Financial Document Processor ====="

# Make scripts executable
chmod +x /workspaces/back/setup_directories.sh
chmod +x /workspaces/back/fix_all_issues.sh
chmod +x /workspaces/back/run_simulation.sh
chmod +x /workspaces/back/run_diagnostics.sh
chmod +x /workspaces/back/run_with_setup.sh

# Create necessary directories and test files
./setup_directories.sh

# Fix issues and check
./fix_all_issues.sh

# Run diagnostics to verify everything is working
./run_diagnostics.sh

echo -e "\n===== Setup Complete ====="
echo "You can now use the system with the following commands:"
echo "  ./run_with_setup.sh          # Start the application"
echo "  ./run_simulation.sh          # Test all features"
echo "  ./run_diagnostics.sh         # Check API status"
echo "  python api_diagnostic.py     # Run API diagnostics directly"
