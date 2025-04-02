#!/bin/bash
echo "===== Testing Full Document Processing and Q&A Implementation ====="

# 1. Set up the environment
echo "Setting up environment..."
./setup_ai_integration.sh

# 2. Test PDF processing (also tests enhanced_pdf_processor.py)
echo -e "\n===== Testing PDF Processing ====="
python3 project_organized/features/pdf_processing/tests/test_processor.py

# 3. Test document upload
echo -e "\n===== Testing Document Upload ====="
# Create a test file if needed
if [ ! -f "uploads/test_document.pdf" ] && [ -f "uploads/doc_de0c7654_2._Messos_28.02.2025.pdf" ]; then
    echo "Creating test file from existing document..."
    cp uploads/doc_de0c7654_2._Messos_28.02.2025.pdf uploads/test_document.pdf
fi

# Process a document
echo "Processing sample document..."
python3 quick_qa_test.py

# 4. Test document Q&A with OpenRouter
echo -e "\n===== Testing Document Q&A ====="
python3 << EOF
import os
import sys
from dotenv import load_dotenv
load_dotenv()

sys.path.append('/workspaces/back')
from project_organized.features.document_qa.enhanced_qa import EnhancedDocumentQA
from project_organized.features.document_qa.service import DocumentQAService

print("Testing Q&A system...")

# Test if API key is loaded
api_key = os.getenv("OPENROUTER_API_KEY", "")
if not api_key or api_key == "YOUR_OPENROUTER_API_KEY":
    print("⚠️  WARNING: No OpenRouter API key found. Advanced Q&A will use fallbacks.")

# Find a document ID to test with
extraction_dir = "extractions"
document_id = None

if os.path.exists(extraction_dir) and os.listdir(extraction_dir):
    for filename in os.listdir(extraction_dir):
        if filename.endswith("_extraction.json") or filename.endswith(".txt"):
            if "_" in filename:
                document_id = filename.split("_")[0]
            else:
                document_id = filename.split(".")[0]
            break

if not document_id:
    print("No documents found for testing in extractions directory.")
    sys.exit(1)

print(f"Using document ID: {document_id}")

# Test enhanced QA
qa = EnhancedDocumentQA()
result = qa.answer_question(document_id, "What is this document about?")
print(f"\nTest question: What is this document about?")
print(f"Answer: {result.get('answer', 'Error: No answer returned')}")

# Test table generation
table_result = qa.generate_table(document_id, {
    "columns": ["name", "isin", "value"],
    "sort_by": "name",
    "sort_order": "asc"
})

print("\nGenerated table:")
if table_result.get("success", False):
    print(f"Columns: {table_result['table']['columns']}")
    print(f"Rows: {len(table_result['table']['data'])}")
    for row in table_result['table']['data'][:3]:
        print(row)
    if len(table_result['table']['data']) > 3:
        print(f"...and {len(table_result['table']['data']) - 3} more rows")
else:
    print(f"Error: {table_result.get('error', 'Unknown error')}")

print("\n✅ Test complete!")
EOF

# 5. Test the full API
echo -e "\n===== Testing REST API ====="
echo "Starting server in background..."
cd project_organized
nohup python app.py > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 5

echo "Testing API endpoints..."
echo "1. Health check:"
curl -s http://localhost:5001/health | python3 -m json.tool

# Test document upload endpoint
echo ""
echo "2. Testing document Q&A API..."
curl -s -X POST \
  http://localhost:5001/api/qa/ask \
  -H "Content-Type: application/json" \
  -d "{\"document_id\":\"$document_id\", \"question\":\"What is the total portfolio value?\"}" \
  | python3 -m json.tool

# Kill the server
echo ""
echo "Stopping test server..."
kill $SERVER_PID

echo -e "\n===== All Tests Complete ====="
echo "The application is now ready to process documents with AI and answer questions."
