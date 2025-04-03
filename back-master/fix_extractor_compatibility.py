def add_compatibility_functions():
    """Add compatibility functions to enhanced_financial_extractor.py"""
    with open('enhanced_financial_extractor.py', 'r') as f:
        content = f.read()
    
    # Check if functions already exist
    if 'def analyze_portfolio' in content and 'def generate_custom_table' in content:
        print("Compatibility functions already exist!")
        return
    
    # Add compatibility functions at the end of the file
    compatibility_functions = """
# Compatibility functions for enhanced_api_endpoints.py
def analyze_portfolio(document_id):
    \"\"\"Analyze portfolio data from a document
    This is a compatibility function that uses the EnhancedFinancialExtractor
    \"\"\"
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
    \"\"\"Generate a custom table from document data
    This is a compatibility function that uses the EnhancedFinancialExtractor
    \"\"\"
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
"""
    
    # Add compatibility functions to the end of the file
    with open('enhanced_financial_extractor.py', 'a') as f:
        f.write(compatibility_functions)
    
    print("Added compatibility functions to enhanced_financial_extractor.py!")

if __name__ == "__main__":
    add_compatibility_functions()
