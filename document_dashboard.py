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
