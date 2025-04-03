from pdf_processor.extraction.text_extractor import PDFTextExtractor
from pdf_processor.tables.table_extractor import TableExtractor
import sys

def test_extraction(pdf_path):
    # Test text extraction
    text_extractor = PDFTextExtractor(language="heb+eng")
    try:
        document = text_extractor.extract_document(pdf_path)
        print(f"Successfully extracted text from {pdf_path}")
        print(f"Found {len(document)} pages")
        # Print sample from first page
        if document and 0 in document:
            print(f"Sample text from page 1: {document[0]['text'][:200]}...")
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
    
    # Test table extraction
    table_extractor = TableExtractor()
    try:
        tables = table_extractor.extract_tables(pdf_path)
        print(f"Successfully extracted tables from {pdf_path}")
        print(f"Found tables on {len(tables)} pages")
        # Print details of first table found
        if tables:
            first_page = next(iter(tables))
            print(f"Page {first_page} has {len(tables[first_page])} tables")
    except Exception as e:
        print(f"Error extracting tables: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_pdf_processing.py <path_to_pdf>")
        sys.exit(1)
    test_extraction(sys.argv[1])
