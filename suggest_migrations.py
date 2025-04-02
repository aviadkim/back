#!/usr/bin/env python3
"""Suggest migration destinations for files based on content analysis"""
import os
import re
import sys

def analyze_file(path):
    """Analyze a file's content to suggest a destination"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None
    
    # Check for common patterns
    features = {
        'pdf_processing': ['pdf', 'ocr', 'text extraction', 'document processing'],
        'document_upload': ['upload', 'document management', 'file handling'],
        'financial_analysis': ['financial', 'isin', 'portfolio', 'securities'],
        'document_qa': ['question', 'answer', 'qa', 'query'],
        'auth': ['auth', 'login', 'user', 'permission'],
        'portfolio_analysis': ['portfolio', 'allocation', 'analysis']
    }
    
    # Count matches for each feature
    matches = {}
    for feature, keywords in features.items():
        count = 0
        for keyword in keywords:
            count += len(re.findall(r'\b' + re.escape(keyword) + r'\b', content.lower()))
        matches[feature] = count
    
    # Find best match
    best_match = max(matches.items(), key=lambda x: x[1]) if matches else (None, 0)
    
    if best_match[1] > 0:
        return f"features/{best_match[0]}"
    
    # Check if it's a utility
    if 'util' in path.lower() or 'helper' in path.lower():
        return "shared/utils"
    
    # Check if it's a database related file
    if 'database' in path.lower() or 'db' in path.lower() or 'mongo' in path.lower():
        return "shared/database"
    
    return "not_sure"

def main():
    files = sys.argv[1:]
    if not files:
        print("Usage: python suggest_migrations.py file1.py file2.py ...")
        return
    
    for file in files:
        if not os.path.isfile(file):
            continue
            
        destination = analyze_file(file)
        print(f"{file} -> project_organized/{destination}")

if __name__ == "__main__":
    main()
