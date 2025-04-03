#!/bin/bash
# build.sh - Production build script

echo "Building production version..."

# Kill any running development servers
echo "Stopping any running development servers..."
pkill -f "flask run" || true
pkill -f "react-scripts start" || true
sleep 2 # Give processes a moment to stop

# Clean up previous build
echo "Cleaning up previous frontend build..."
rm -rf frontend/build

# Build frontend
echo "Building frontend..."
cd frontend
# Ensure dependencies are installed before building
npm install 
npm run build
cd ..

# Check if build was successful
if [ ! -f "frontend/build/index.html" ]; then
  echo "Frontend build failed. Exiting."
  exit 1
fi

echo "Frontend build successful."

# Start production server (assuming app.py is configured for production)
# Note: For a real production setup, consider using gunicorn or similar
echo "Starting production server..."
python app.py