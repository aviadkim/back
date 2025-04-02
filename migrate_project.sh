#!/bin/bash
# Migrate the entire project to the vertical slice architecture

echo "===== Starting Full Project Migration ====="

# Check if project_organized directory exists
if [ ! -d "project_organized" ]; then
  echo "Creating base structure..."
  ./setup_vertical_slice.sh
fi

# Copy core PDF processor file
echo "Migrating PDF processor..."
cp enhanced_pdf_processor.py project_organized/features/pdf_processing/processor.py

# Copy financial extractor
echo "Migrating financial extractor..."
if [ -f "enhanced_financial_extractor.py" ]; then
  mkdir -p project_organized/features/financial_analysis/extractors
  cp enhanced_financial_extractor.py project_organized/features/financial_analysis/extractors/financial_extractor.py
fi

# Create shared utilities
echo "Setting up shared utilities..."
mkdir -p project_organized/shared/pdf
cat > project_organized/shared/pdf/__init__.py << 'EOL'
"""Shared PDF utilities"""
EOL

# Set up the document QA feature
echo "Setting up document QA feature..."
mkdir -p project_organized/features/document_qa
cat > project_organized/features/document_qa/__init__.py << 'EOL'
"""Document Q&A Feature

This feature provides question answering capabilities for documents.
"""
EOL

cat > project_organized/features/document_qa/api.py << 'EOL'
"""API endpoints for document Q&A feature."""
from flask import Blueprint, request, jsonify

qa_bp = Blueprint('qa', __name__, url_prefix='/api/qa')

def register_routes(app):
    """Register all routes for this feature"""
    app.register_blueprint(qa_bp)

@qa_bp.route('/ask', methods=['POST'])
def ask_question():
    """Ask a question about a document"""
    data = request.json
    
    if not data or 'question' not in data or 'document_id' not in data:
        return jsonify({'error': 'Question and document_id required'}), 400
    
    question = data['question']
    document_id = data['document_id']
    
    # This is a placeholder that would normally query an AI model
    answer = f"This is a placeholder answer for question: '{question}' about document {document_id}"
    
    return jsonify({
        'status': 'success',
        'question': question,
        'answer': answer,
        'document_id': document_id
    })
EOL

# Create a main script to run the new architecture
cat > run_vertical_slice_app.py << 'EOL'
#!/usr/bin/env python3
"""
Run the application with the vertical slice architecture.
This is a transition script that will run the new app structure
while keeping compatibility with the old structure.
"""
import os
import sys

def main():
    """Run the application with the vertical slice architecture"""
    print("Starting application with vertical slice architecture...")
    
    # Check if project_organized exists
    if not os.path.exists('project_organized'):
        print("Error: project_organized directory not found.")
        print("Run setup_vertical_slice.sh first to create the structure.")
        return 1
    
    # Change to the project_organized directory
    os.chdir('project_organized')
    
    # Run the app
    try:
        import app
        return 0
    except ImportError as e:
        print(f"Error importing app: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOL

# Make the script executable
chmod +x run_vertical_slice_app.py

echo "===== Migration Complete ====="
echo ""
echo "You can now run the application with the vertical slice architecture:"
echo "./run_vertical_slice_app.py"
echo ""
echo "Continue migrating more components by:"
echo "1. Adding more modules to project_organized/features/"
echo "2. Updating imports to use the new structure"
echo "3. Creating adapters for backward compatibility"
