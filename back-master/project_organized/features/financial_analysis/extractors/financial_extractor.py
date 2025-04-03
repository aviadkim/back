import re
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedFinancialExtractor:
    """Enhanced extractor for financial data from documents"""
    
    def __init__(self):
        # ISIN pattern: 2 letters followed by 10 digits/letters
        self.isin_pattern = r'\b([A-Z]{2}[A-Z0-9]{10})\b'
        
        # Currency patterns
        self.currency_symbols = r'[$€£₪]'
        self.currency_codes = r'\b(USD|EUR|GBP|ILS)\b'
        
        # Number patterns
        self.number_pattern = r'[\d,]+\.?\d*'
        
        # Percentage pattern
        self.percentage_pattern = r'(\d+\.?\d*)[ ]?%'
    
    def process_document(self, document_id):
        """Process a document to extract all financial information"""
        # Get the document content (assuming extraction file exists)
        extraction_path = self._get_extraction_path(document_id)
        
        if not os.path.exists(extraction_path):
            logger.error(f"Extraction file not found: {extraction_path}")
            return None
        
        # Read the extraction file
        try:
            with open(extraction_path, 'r') as f:
                extraction_data = json.load(f)
                content = extraction_data.get('content', '')
        except Exception as e:
            logger.error(f"Error reading extraction file: {e}")
            return None
        
        # Extract financial data
        result = self.extract_data(content)
        
        # Save the enhanced extraction
        enhanced_path = self._get_enhanced_path(document_id)
        with open(enhanced_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result
    
    def extract_data(self, text):
        """Extract all financial data from text"""
        result = {
            'isins': self._extract_isins(text),
            'currencies': self._extract_currencies(text),
            'percentages': self._extract_percentages(text),
            'securities': self._extract_securities(text),
            'tables': self._extract_table_data(text)
        }
        return result
    
    def _extract_isins(self, text):
        """Extract ISIN numbers from text"""
        isins = re.findall(self.isin_pattern, text)
        logger.info(f"Extracted {len(isins)} ISINs")
        return isins
    
    def _extract_currencies(self, text):
        """Extract currency amounts from text"""
        # Look for currency symbol followed by number
        symbol_amounts = re.findall(f'{self.currency_symbols}[ ]?({self.number_pattern})', text)
        
        # Look for number followed by currency code
        code_amounts = re.findall(f'({self.number_pattern})[ ]?{self.currency_codes}', text)
        
        currencies = []
        
        # Process symbol amounts
        for amount in symbol_amounts:
            currencies.append({
                'amount': amount,
                'type': 'symbol_amount'
            })
        
        # Process code amounts
        for amount in code_amounts:
            currencies.append({
                'amount': amount,
                'type': 'code_amount'
            })
        
        logger.info(f"Extracted {len(currencies)} currency amounts")
        return currencies
    
    def _extract_percentages(self, text):
        """Extract percentage values from text"""
        percentages = re.findall(self.percentage_pattern, text)
        logger.info(f"Extracted {len(percentages)} percentages")
        return percentages
    
    def _extract_securities(self, text):
        """Extract securities information (ISIN with associated data)"""
        securities = []
        
        # Find all ISINs
        isins = re.findall(self.isin_pattern, text)
        
        for isin in isins:
            # Get a window of text around the ISIN (100 chars before and after)
            isin_index = text.find(isin)
            start = max(0, isin_index - 100)
            end = min(len(text), isin_index + 100)
            context = text[start:end]
            
            # Look for numbers in this context
            numbers = re.findall(self.number_pattern, context)
            
            # Look for currency symbols in this context
            currencies = re.findall(self.currency_symbols, context)
            
            # Look for possible security names (capital letters followed by text)
            name_match = re.search(r'\b([A-Z][A-Za-z\.\, ]{2,30})(Inc|Corp|Ltd|AG|SA|NV|Plc|Group|ETF)?', context)
            name = name_match.group(0) if name_match else None
            
            security = {
                'isin': isin,
                'name': name,
                'numbers': numbers[:5],  # Limit to first 5 numbers
                'currencies': currencies
            }
            
            securities.append(security)
        
        logger.info(f"Extracted data for {len(securities)} securities")
        return securities
    
    def _extract_table_data(self, text):
        """Attempt to extract table structures from text"""
        tables = []
        
        # Look for potential tables (lines with consistent delimiters)
        lines = text.split("\n")
        current_table = []
        
        for line in lines:
            # If line contains multiple tab or multiple space sequences
            if "\t" in line or "  " in line:
                # Check if this is a data line
                if re.search(self.isin_pattern, line) or re.search(self.number_pattern, line):
                    current_table.append(line)
            elif current_table:
                # End of table
                if len(current_table) > 1:  # At least 2 lines to be a table
                    tables.append(current_table)
                current_table = []
        
        # Don't forget to add the last table if we ended on a table line
        if current_table and len(current_table) > 1:
            tables.append(current_table)
        
        processed_tables = []
        
        # Process each potential table
        for table_lines in tables:
            # Try to determine columns based on spacing
            header = table_lines[0]
            
            # Check if we can split by tabs
            if "\t" in header:
                columns = header.split("\t")
                rows = [line.split("\t") for line in table_lines[1:]]
            else:
                # Try to split based on multiple spaces
                columns = re.split(r'\s{2,}', header.strip())
                rows = [re.split(r'\s{2,}', line.strip()) for line in table_lines[1:]]
            
            # Only keep tables with at least 2 columns
            if len(columns) >= 2:
                processed_tables.append({
                    'columns': columns,
                    'rows': rows
                })
        
        logger.info(f"Extracted {len(processed_tables)} potential tables")
        return processed_tables
    
    def _get_extraction_path(self, document_id):
        """Get the path to the extraction file"""
        return f"extractions/{document_id}_extraction.json"
    
    def _get_enhanced_path(self, document_id):
        """Get the path to the enhanced extraction file"""
        # Create the directory if it doesn't exist
        os.makedirs("enhanced_extractions", exist_ok=True)
        return f"enhanced_extractions/{document_id}_enhanced.json"

# Create a function to use this class with an existing document
def enhance_document_extraction(document_id):
    """Enhance the extraction for an existing document"""
    extractor = EnhancedFinancialExtractor()
    result = extractor.process_document(document_id)
    if result:
        print(f"Enhanced extraction completed for document {document_id}")
        print(f"Found {len(result['isins'])} ISINs")
        print(f"Found {len(result['securities'])} securities with contextual data")
        print(f"Found {len(result['tables'])} potential tables")
        return True
    else:
        print(f"Failed to enhance extraction for document {document_id}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        document_id = sys.argv[1]
        enhance_document_extraction(document_id)
    else:
        print("Please provide a document ID")

# Compatibility functions for enhanced_api_endpoints.py
def analyze_portfolio(document_id):
    """Analyze portfolio data from a document
    This is a compatibility function that uses the EnhancedFinancialExtractor
    """
    extractor = EnhancedFinancialExtractor()
    result = extractor.process_document(document_id)
    
    if not result:
        return {
            'security_count': 0,
            'total_value': 0,
            'asset_allocation': {},
            'currency_allocation': {},
            'performance': {},
            'risk_metrics': {},
            'top_holdings': []
        }
    
    # Extract securities info
    securities = result.get('securities', [])
    
    # Count securities
    security_count = len(securities)
    
    # Placeholder for more sophisticated analysis
    # In a real implementation, this would extract more data
    
    analysis = {
        'security_count': security_count,
        'total_value': 0,  # Would calculate total portfolio value
        'asset_allocation': {},  # Would calculate asset allocation
        'currency_allocation': {},  # Would analyze currencies
        'performance': {},  # Would analyze performance metrics 
        'risk_metrics': {},  # Would calculate risk metrics
        'top_holdings': []  # Would identify top holdings
    }
    
    return analysis

def generate_custom_table(document_id, columns=None):
    """Generate a custom table from document data
    This is a compatibility function that uses the EnhancedFinancialExtractor
    """
    if columns is None:
        columns = ['isin', 'name', 'currency']
    
    extractor = EnhancedFinancialExtractor()
    result = extractor.process_document(document_id)
    
    if not result:
        return {
            'columns': columns,
            'rows': [],
            'document_id': document_id
        }
    
    # Extract securities info
    securities = result.get('securities', [])
    
    # Transform securities into rows
    rows = []
    for security in securities:
        row = {}
        if 'isin' in columns:
            row['isin'] = security.get('isin', '')
        if 'name' in columns:
            row['name'] = security.get('name', '')
        if 'currency' in columns:
            # Use the first currency found in the security context
            currencies = security.get('currencies', [])
            row['currency'] = currencies[0] if currencies else ''
        
        rows.append(row)
    
    return {
        'columns': columns,
        'rows': rows,
        'document_id': document_id
    }
