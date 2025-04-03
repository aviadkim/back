#!/bin/bash

# Create the basic structure
echo "Creating basic vertical slice architecture structure..."

# Make sure project_organized directory exists
mkdir -p project_organized

# Create core directories
mkdir -p project_organized/features
mkdir -p project_organized/shared
mkdir -p project_organized/config
mkdir -p project_organized/tests

# Create main feature directories
mkdir -p project_organized/features/pdf_processing
mkdir -p project_organized/features/financial_analysis
mkdir -p project_organized/features/document_upload
mkdir -p project_organized/features/document_qa
mkdir -p project_organized/features/portfolio_analysis

# Create shared utility directories
mkdir -p project_organized/shared/database
mkdir -p project_organized/shared/pdf
mkdir -p project_organized/shared/file_storage
mkdir -p project_organized/shared/ai

# Create example feature structure
mkdir -p project_organized/features/pdf_processing/tests
touch project_organized/features/pdf_processing/__init__.py
touch project_organized/features/pdf_processing/api.py
touch project_organized/features/pdf_processing/service.py

# Create main application file
cat > project_organized/app.py << 'EOL'
"""
Main application entry point with vertical slice architecture.
"""
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Service is healthy"})

@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "Vertical Slice Architecture Demo"})

# Import features here (when implemented)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
EOL

# Create a README
cat > project_organized/README.md << 'EOL'
# Vertical Slice Architecture Implementation

This is a reorganization of the existing codebase following vertical slice architecture principles.

## Structure

- `features/`: Contains business features as vertical slices
  - `pdf_processing/`: PDF text extraction
  - `financial_analysis/`: Financial data extraction
  - `document_upload/`: Document management
  - `document_qa/`: Question answering
  - `portfolio_analysis/`: Portfolio analysis
- `shared/`: Shared code used across features
- `config/`: Configuration files
- `tests/`: System-wide tests

## Migration Path

1. Copy files to new structure without deleting originals
2. Create adapters in old locations pointing to new code
3. Update app.py to use the new structure
4. Run tests to verify functionality
EOL

echo "✅ Basic vertical slice architecture structure created in project_organized/"
echo "Next steps:"
echo "1. Copy enhanced_pdf_processor.py to project_organized/features/pdf_processing/processor.py"
echo "2. Create adapters in the original files"
echo "3. Update imports in the new files"
