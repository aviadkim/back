#!/bin/bash

# =========================================================
# Basic dependencies installation script
# =========================================================

echo -e "\033[1;34m===== Installing basic dependencies for testing =====\033[0m"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "\033[1;33mCreating and activating virtual environment...\033[0m"
    python -m venv venv
    source venv/bin/activate
else
    echo -e "\033[1;32mVirtual environment already activated: $VIRTUAL_ENV\033[0m"
fi

# Install only the essential packages needed to run the app and tests
echo -e "\033[1;33mInstalling essential packages...\033[0m"
pip install Flask==3.1.0 flask-cors==4.0.0 python-dotenv==1.0.1 pytest==8.3.5 pytest-flask==1.3.0

echo -e "\033[1;32mBasic dependencies installed successfully!\033[0m"
echo -e "\033[1;33mYou can now run:\033[0m"
echo -e "  \033[1;36mpython vertical_slice_app.py\033[0m - to start the application"
echo -e "  \033[1;36mpython -m pytest tests/\033[0m - to run the tests"
