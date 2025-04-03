#!/bin/bash

# Install frontend dependencies
echo "==== Installing frontend dependencies ===="
cd frontend
npm install react-bootstrap @mui/material @emotion/react @emotion/styled
cd ..

# Fix configuration file if needed
echo "==== Checking configuration file ===="
if ! grep -q "MAX_FILE_SIZE" config/configuration.py; then
    echo "Adding MAX_FILE_SIZE to configuration"
    echo "MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB file size limit" >> config/configuration.py
fi

# Build the frontend
echo "==== Building frontend ===="
cd frontend
npm run build
cd ..

# Check for successful build
if [ ! -d "frontend/build" ]; then
    echo "Frontend build failed!"
    exit 1
fi

# Start the application
echo "==== Starting application ===="
python app.py