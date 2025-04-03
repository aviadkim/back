
import os
from enhanced_pdf_processor import EnhancedPDFProcessor

pdf_path = 'uploads/doc_de0c7654_2._Messos_28.02.2025.pdf'
if os.path.exists(pdf_path):
    processor = EnhancedPDFProcessor()
    document_id = 'doc_de0c7654'
    result = processor.process_document(pdf_path, document_id)
    print(f"Processed document: {result}")
    
    filename = os.path.basename(pdf_path)
    
    # Check either of the possible correct output paths
    expected_path1 = f'extractions/doc_de0c7654_2._Messos_28.02.2025_extraction.json'
    expected_path2 = f'extractions/2._Messos_28.02.2025_extraction.json'
    
    if os.path.exists(expected_path1):
        print(f"SUCCESS: Extraction file created at {expected_path1}")
        exit(0)
    elif os.path.exists(expected_path2):
        print(f"SUCCESS: Extraction file created at {expected_path2}")
        exit(0)
    else:
        print(f"ERROR: Extraction file not found at expected paths")
        print(f"Files in extractions directory: {os.listdir('extractions')}")
        exit(1)
else:
    print(f"ERROR: Test PDF not found at {pdf_path}")
    exit(1)
