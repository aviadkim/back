#!/bin/bash
echo "Stopping any running Python processes..."
# Use pkill to find and kill processes running python app.py or similar
# The || true prevents the script from exiting if no processes are found
pkill -f "python app.py" || true
pkill -f "flask run" || true 

# Give processes a moment to shut down
sleep 2

echo "Rebuilding frontend..."
cd frontend
# Ensure dependencies are installed before building
npm install 
npm run build
cd ..

# Check if build was successful by looking for index.html
if [ ! -f "frontend/build/index.html" ]; then
  echo "Frontend build failed. Exiting."
  exit 1
fi

echo "Starting application..."
python app.py