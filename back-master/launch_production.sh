#!/bin/bash

echo "===== Preparing for Production Deployment ====="

# 1. Kill any running Flask servers
echo "Stopping any running servers..."
pkill -f "python app.py" || true
sleep 2

# 2. Update permission for all script files
echo "Setting proper permissions on scripts..."
chmod +x /workspaces/back/*.sh
find /workspaces/back/project_organized -name "*.sh" -exec chmod +x {} \;

# 3. Ensure the necessary directories exist
echo "Creating required directories..."
mkdir -p /workspaces/back/{uploads,extractions,exports,qa_results,financial_data}

# 4. Create an optimized start script
echo "Creating optimized start script..."
cat > /workspaces/back/start_production.sh << 'EOL'
#!/bin/bash

# Set environment variables
export PYTHONPATH=/workspaces/back:$PYTHONPATH
export FLASK_ENV=production
export FLASK_DEBUG=0

# Change directory to project root
cd /workspaces/back/project_organized

# Try different ports in case one is already in use
for port in 5000 5001 5002 5003 5004; do
  echo "Trying to start server on port $port..."
  PORT=$port python app.py &
  SERVER_PID=$!
  
  # Wait briefly to see if the server starts successfully
  sleep 3
  if kill -0 $SERVER_PID 2>/dev/null; then
    echo "Server started successfully on port $port (PID: $SERVER_PID)"
    echo "$SERVER_PID" > /workspaces/back/.server_pid
    echo "To stop the server, run: ./stop_server.sh"
    exit 0
  fi
done

echo "Failed to start server on any port."
exit 1
EOL
chmod +x /workspaces/back/start_production.sh

# 5. Create a stop script
echo "Creating server stop script..."
cat > /workspaces/back/stop_server.sh << 'EOL'
#!/bin/bash
if [ -f /workspaces/back/.server_pid ]; then
  PID=$(cat /workspaces/back/.server_pid)
  if ps -p $PID > /dev/null; then
    echo "Stopping server (PID: $PID)..."
    kill $PID
    rm /workspaces/back/.server_pid
    echo "Server stopped."
  else
    echo "Server not running (stale PID file)."
    rm /workspaces/back/.server_pid
  fi
else
  pkill -f "python app.py" || echo "No running server found."
fi
EOL
chmod +x /workspaces/back/stop_server.sh

# 6. Create a simple dashboard script to see document progress
echo "Creating document processing dashboard..."
cat > /workspaces/back/document_dashboard.py << 'EOL'
#!/usr/bin/env python3
"""Simple dashboard to monitor document processing"""
import os
import sys
import json
from datetime import datetime

def list_documents():
    """List all processed documents"""
    documents = []
    
    # Check extractions directory
    extraction_dir = 'extractions'
    if os.path.exists(extraction_dir):
        for filename in os.listdir(extraction_dir):
            if filename.endswith('_extraction.json'):
                doc_id = filename.split('_')[0]
                doc_path = os.path.join(extraction_dir, filename)
                try:
                    size = os.path.getsize(doc_path)
                    mod_time = os.path.getmtime(doc_path)
                    documents.append({
                        'id': doc_id,
                        'filename': filename,
                        'type': 'Extraction',
                        'size': size,
                        'modified': datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
                    })
                except:
                    pass
    
    # Check qa_results directory
    qa_dir = 'qa_results'
    if os.path.exists(qa_dir):
        for filename in os.listdir(qa_dir):
            if filename.endswith('_qa.json'):
                doc_id = filename.split('_')[0]
                qa_path = os.path.join(qa_dir, filename)
                try:
                    size = os.path.getsize(qa_path)
                    mod_time = os.path.getmtime(qa_path)
                    
                    # Count QA pairs
                    try:
                        with open(qa_path, 'r') as f:
                            qa_data = json.load(f)
                            qa_count = len(qa_data)
                    except:
                        qa_count = "Error"
                        
                    documents.append({
                        'id': doc_id,
                        'filename': filename,
                        'type': 'Q&A',
                        'qa_count': qa_count,
                        'size': size,
                        'modified': datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
                    })
                except:
                    pass
    
    return documents

def print_dashboard():
    """Print dashboard of documents"""
    documents = list_documents()
    
    # Group by document ID
    docs_by_id = {}
    for doc in documents:
        if doc['id'] not in docs_by_id:
            docs_by_id[doc['id']] = []
        docs_by_id[doc['id']].append(doc)
    
    # Print dashboard
    print("=" * 80)
    print(" DOCUMENT PROCESSING DASHBOARD")
    print("=" * 80)
    print(f"Total documents: {len(docs_by_id)}")
    print("-" * 80)
    
    for doc_id, entries in sorted(docs_by_id.items()):
        print(f"Document ID: {doc_id}")
        
        # Find extraction data
        extraction = next((e for e in entries if e['type'] == 'Extraction'), None)
        if extraction:
            print(f"  Extraction: {extraction['filename']}, Size: {extraction['size']/1024:.1f} KB, Modified: {extraction['modified']}")
        else:
            print("  Extraction: None")
            
        # Find Q&A data
        qa = next((e for e in entries if e['type'] == 'Q&A'), None)
        if qa:
            print(f"  Q&A: {qa['filename']}, Questions: {qa['qa_count']}, Modified: {qa['modified']}")
        else:
            print("  Q&A: None")
            
        print("-" * 80)

if __name__ == "__main__":
    print_dashboard()
EOL
chmod +x /workspaces/back/document_dashboard.py

# 7. Update the README with final instructions
echo "Updating README with final instructions..."
cat >> /workspaces/back/README.md << 'EOL'

## Production Deployment

For production deployment, follow these steps:

1. Clean any development artifacts:
   ```bash
   ./prepare_for_github.sh
   ```

2. Set up the environment:
   ```bash
   ./setup_ai_integration.sh
   ```

3. Start the production server:
   ```bash
   ./start_production.sh
   ```

4. To monitor document processing:
   ```bash
   python document_dashboard.py
   ```

5. To stop the server:
   ```bash
   ./stop_server.sh
   ```

## Available Features

The system includes the following features:
- PDF Processing (extraction of text from PDF files)
- Document Upload (management of uploaded documents)
- Financial Analysis (extraction of financial data)
- Document Q&A (AI-powered question answering about documents)
- Document Export (export data to Excel and other formats)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/documents/upload` | POST | Upload a document |
| `/api/pdf/process` | POST | Process a PDF document |
| `/api/financial/analyze/{document_id}` | GET | Extract financial data |
| `/api/qa/ask` | POST | Ask questions about a document |
| `/api/export/excel/{document_id}` | GET | Export document data to Excel |
| `/health` | GET | Check system health status |
EOL

# 8. Make all scripts executable
chmod +x /workspaces/back/start_production.sh
chmod +x /workspaces/back/stop_server.sh
chmod +x /workspaces/back/document_dashboard.py

# 9. Run the environment setup
echo "Setting up environment..."
if [ -f "/workspaces/back/setup_ai_integration.sh" ]; then
    chmod +x /workspaces/back/setup_ai_integration.sh
    ./setup_ai_integration.sh
fi

echo -e "\n===== Production Deployment Ready ====="
echo "To launch the application in production mode:"
echo "  ./start_production.sh"
echo ""
echo "To monitor document processing:"
echo "  python document_dashboard.py"
echo ""
echo "To stop the server:"
echo "  ./stop_server.sh"
echo ""
echo "Congratulations! Your Financial Document Processing System with AI-powered Q&A"
echo "is now complete and ready for production use!"
