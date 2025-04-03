#!/bin/bash

echo "===== Fixing AI Integration Issues ====="

# 1. Fix directory permissions
echo "Creating required directories with proper permissions..."
mkdir -p /workspaces/back/extractions
mkdir -p /workspaces/back/uploads
mkdir -p /workspaces/back/exports
mkdir -p /workspaces/back/financial_data
chmod -R 755 /workspaces/back/extractions
chmod -R 755 /workspaces/back/uploads
chmod -R 755 /workspaces/back/exports
chmod -R 755 /workspaces/back/financial_data

# 2. Install required packages
echo "Installing required packages..."
pip install python-dotenv requests
pip install google-generativeai --quiet

# 3. Setup AI module structure
echo "Setting up AI module structure..."
mkdir -p /workspaces/back/project_organized/shared/ai
touch /workspaces/back/project_organized/shared/__init__.py
touch /workspaces/back/project_organized/shared/ai/__init__.py

# 4. Check if document_qa folder exists and create if needed
if [ ! -d "/workspaces/back/project_organized/features/document_qa" ]; then
    echo "Creating document_qa module..."
    mkdir -p /workspaces/back/project_organized/features/document_qa
    touch /workspaces/back/project_organized/features/document_qa/__init__.py
fi

# 5. Check simple_qa.py exists and create if needed
if [ ! -f "/workspaces/back/project_organized/features/document_qa/simple_qa.py" ]; then
    echo "Creating simple_qa.py file..."
    cat > /workspaces/back/project_organized/features/document_qa/simple_qa.py << 'EOL'
"""Simple question answering system for documents."""
import re

class SimpleQA:
    """Simple question answering system that provides basic responses"""
    
    def answer(self, question, document_content):
        """Answer a general question about a document"""
        question = question.lower().strip()
        
        # Check for page count questions
        if re.search(r'how many pages|page count', question):
            return self._get_page_count(document_content)
            
        # Check for document type questions
        if re.search(r'what (kind|type) of document|document type', question):
            return self._get_document_type(document_content)
            
        # Check for date questions
        if re.search(r'what date|when|date of', question):
            return self._find_date(document_content)
            
        # Simple full text search
        return self._search_document(question, document_content)
    
    def _get_page_count(self, document_content):
        """Extract page count information from document"""
        # Implementation for page count extraction
        match = re.search(r'page\s*(\d+)\s*of\s*(\d+)', document_content, re.IGNORECASE)
        if match:
            return f"This document has {match.group(2)} pages."
            
        return "I couldn't determine the exact page count from this document."
    
    def _get_document_type(self, document_content):
        """Try to determine the document type"""
        content = document_content.lower()
        
        if 'portfolio' in content:
            return "This appears to be a portfolio document."
        elif 'report' in content:
            return "This appears to be a report."
        else:
            return "This appears to be a general document."
    
    def _find_date(self, document_content):
        """Try to find a date in the document"""
        date_patterns = [r'\d{1,2}/\d{1,2}/\d{4}', r'\d{4}-\d{2}-\d{2}', r'[A-Za-z]+ \d{1,2}, \d{4}']
        
        for pattern in date_patterns:
            match = re.search(pattern, document_content)
            if match:
                return f"I found this date in the document: {match.group(0)}"
                
        return "I couldn't find a date in this document."
    
    def _search_document(self, question, document_content):
        """Search for relevant information in the document"""
        # Very simple implementation using keyword matching
        keywords = self._extract_keywords(question)
        for keyword in keywords:
            if keyword in document_content.lower():
                start = document_content.lower().find(keyword)
                snippet_start = max(0, start - 50)
                snippet_end = min(len(document_content), start + len(keyword) + 100)
                snippet = document_content[snippet_start:snippet_end]
                return f"I found relevant information: {snippet}"
        
        return "I couldn't find information related to your question in this document."
    
    def _extract_keywords(self, question):
        """Extract keywords from the question"""
        stop_words = ['what', 'where', 'when', 'who', 'how', 'is', 'are', 'the', 'in', 'of', 'and', 'to']
        words = question.lower().split()
        return [word for word in words if word not in stop_words and len(word) > 3]
EOL
fi

# 6. Test the AI models directly
echo "Running AI model test..."
python test_ai_models.py

echo "✅ All fixes applied"
echo "You can now run the AI integration with: python test_ai_integration.py"
echo "If you still encounter issues, try fixing your API keys in the .env file"
