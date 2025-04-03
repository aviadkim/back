import fitz  # PyMuPDF
import os

def analyze_pdf(filepath):
    """Analyze PDF document and extract information"""
    try:
        doc = fitz.open(filepath)
        results = {
            'filename': os.path.basename(filepath),
            'pages': {},
            'total_pages': len(doc),
            'metadata': doc.metadata
        }
        
        # Analyze each page
        for page_num, page in enumerate(doc):
            text = page.get_text()
            tables = page.find_tables()
            
            results['pages'][str(page_num)] = {
                'text': text,
                'tables': [table.extract() for table in tables],
                'financial_data': extract_financial_data(text)
            }
        
        return results
    except Exception as e:
        raise Exception(f"Error analyzing PDF: {str(e)}")

def extract_financial_data(text):
    """Extract financial information from text"""
    # Basic financial data extraction
    return {
        'isins': find_isins(text),
        'dates': find_dates(text),
        'amounts': find_amounts(text),
    }

def find_isins(text):
    """Find ISIN codes in text"""
    # Basic ISIN pattern: 12 characters, letters and numbers
    import re
    isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
    return list(set(re.findall(isin_pattern, text)))

def find_dates(text):
    """Find dates in text"""
    import re
    # Add your date patterns here
    date_patterns = [
        r'\d{2}/\d{2}/\d{4}',
        r'\d{2}\.\d{2}\.\d{4}'
    ]
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text))
    return list(set(dates))

def find_amounts(text):
    """Find monetary amounts in text"""
    import re
    # Add your amount patterns here
    amount_pattern = r'[\$€₪]?\s*\d+(?:,\d{3})*(?:\.\d{2})?'
    return list(set(re.findall(amount_pattern, text)))
