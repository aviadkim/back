from pdf_processor.extraction.text_extractor import PDFTextExtractor
from pdf_processor.tables.table_extractor import TableExtractor
from pdf_processor.analysis.financial_analyzer import FinancialAnalyzer
import os

print("Testing PDF Processor components...")

# List test documents
test_docs = os.listdir("test_documents")
pdf_files = [f for f in test_docs if f.endswith('.pdf')]

if pdf_files:
    test_file = os.path.join("test_documents", pdf_files[0])
    print(f"Found test PDF: {test_file}")
    
    print("\nTesting Text Extractor...")
    extractor = PDFTextExtractor(language="heb+eng")
    try:
        print(f"Initialized extractor with language: heb+eng")
    except Exception as e:
        print(f"Error initializing extractor: {e}")
    
    print("\nTesting Table Extractor...")
    table_ext = TableExtractor()
    try:
        print("Initialized table extractor")
    except Exception as e:
        print(f"Error initializing table extractor: {e}")
    
    print("\nTesting Financial Analyzer...")
    analyzer = FinancialAnalyzer()
    try:
        print("Initialized financial analyzer")
    except Exception as e:
        print(f"Error initializing analyzer: {e}")
else:
    print("No test PDF files found in test_documents directory")
