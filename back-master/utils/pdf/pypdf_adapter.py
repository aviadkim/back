"""
Adapter for different PyPDF2 versions to provide a unified interface.
"""
import sys

try:
    import PyPDF2
    
    # Check which version of PyPDF2 we're using
    if hasattr(PyPDF2, 'PdfReader'):
        # PyPDF2 3.0+
        def get_pdf_reader(file_obj):
            return PyPDF2.PdfReader(file_obj)
            
        def get_page_count(reader):
            return len(reader.pages)
            
        def get_page(reader, page_num):
            return reader.pages[page_num]
            
        def extract_text(page):
            return page.extract_text()
            
    else:
        # PyPDF2 < 3.0
        def get_pdf_reader(file_obj):
            return PyPDF2.PdfFileReader(file_obj)
            
        def get_page_count(reader):
            return reader.getNumPages()
            
        def get_page(reader, page_num):
            return reader.getPage(page_num)
            
        def extract_text(page):
            return page.extractText()
            
except ImportError:
    print("PyPDF2 is not installed. Please install it with 'pip install PyPDF2'", file=sys.stderr)
    sys.exit(1)
