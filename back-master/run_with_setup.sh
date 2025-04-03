#!/bin/bash

echo "===== Setting up Financial Document Processor ====="

# Create required directories
mkdir -p /workspaces/back/extractions
mkdir -p /workspaces/back/uploads
mkdir -p /workspaces/back/financial_data

# Create a sample extraction file for testing if one doesn't exist
if [ ! -f /workspaces/back/extractions/doc_c16be22a_sample_extraction.json ]; then
    echo "Creating sample extraction file for testing..."
    cat > /workspaces/back/extractions/doc_c16be22a_sample_extraction.json << 'EOL'
{
  "document_id": "doc_c16be22a",
  "filename": "sample_document.pdf",
  "page_count": 5,
  "content": "This is sample document content for testing the Q&A system. It contains financial information about several securities including Apple Inc. with ISIN US0378331005, Microsoft with ISIN US5949181045, and Amazon with ISIN US0231351067. The portfolio value is $1,500,000 as of March 15, 2025."
}
EOL
fi

# Check permissions
chmod -R 755 /workspaces/back/extractions
chmod -R 755 /workspaces/back/uploads
chmod -R 755 /workspaces/back/financial_data

# Check if the app is already running
echo "Checking if application is already running..."
RUNNING_APP=$(ps aux | grep "python app.py" | grep -v grep)
if [ -n "$RUNNING_APP" ]; then
    echo "Application is already running. Stopping it first..."
    APP_PID=$(echo "$RUNNING_APP" | awk '{print $2}')
    kill $APP_PID
    sleep 2
fi

# Now check all used ports to be sure
echo "Checking if ports are in use..."
for port in 5001 5002 5003; do
    PORT_IN_USE=$(lsof -i:$port)
    if [ -n "$PORT_IN_USE" ]; then
        PID=$(echo "$PORT_IN_USE" | awk 'NR>1 {print $2}' | uniq)
        echo "Port $port is in use by PID $PID. Attempting to terminate..."
        kill $PID
        sleep 2
    fi
done

# Start the application with specified port
cd /workspaces/back/project_organized
echo "Starting application on port 5003..."
export PORT=5003
python app.py

echo "Application stopped."
