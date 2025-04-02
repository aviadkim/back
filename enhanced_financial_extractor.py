import re
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("financial_extractor")

def extract_isin_numbers(text):
    """Extract ISIN numbers from text"""
    isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
    return list(set(re.findall(isin_pattern, text)))  # Remove duplicates

def extract_financial_metadata(all_text, isin_numbers):
    """Extract complete financial data for each security"""
    financial_data = {}
    
    # Common financial terms and their patterns
    patterns = {
        'security_types': {
            'bond': r'bond|debenture|note|treasury',
            'equity': r'equity|stock|share|common',
            'etf': r'ETF|fund|index fund',
            'structured': r'structured|certificate|note',
            'derivative': r'option|future|forward|swap'
        },
        'quantity': [
            r'(?:Nominal|Amount|Quantity|Qty)[:\s]+([0-9,\.]+)',
            r'([0-9,\.]+)[\s]+(?:units|shares)',
            r'(?:Position|Holding)[:\s]+([0-9,\.]+)'
        ],
        'price': [
            r'(?:Price|Rate)[:\s]+([0-9,\.]+)',
            r'(?:NAV|value per share)[:\s]+([0-9,\.]+)',
            r'([0-9,\.]+)[\s]+(?:per share|per unit)'
        ],
        'market_value': [
            r'(?:Market Value|Valuation|Value)[:\s]+([0-9,\.]+[KMB]?)',
            r'(?:Total)[:\s]+([0-9,\.]+[KMB]?)'
        ],
        'currency': r'\b(USD|EUR|GBP|CHF|JPY|ILS)\b',
        'percentage': [
            r'(?:Weight|Allocation|%)[:\s]+([0-9\.]+%)',
            r'(?:Weight|Allocation)[:\s]+([0-9\.]+)\s?%'
        ],
        'date': [
            r'\b(\d{1,2}[./]\d{1,2}[./]\d{2,4})\b',
            r'\b(\d{4}-\d{2}-\d{2})\b'
        ],
        'performance': [
            r'(?:YTD|Return|Performance)[:\s]+([\+\-]?[0-9\.]+%)',
            r'(?:YTD|Return|Performance)[:\s]+([\+\-]?[0-9\.]+)\s?%'
        ]
    }
    
    # Process each ISIN
    for isin in isin_numbers:
        # Get context around the ISIN
        context_pattern = r'(.{0,500}' + re.escape(isin) + r'.{0,500})'
        context_matches = re.findall(context_pattern, all_text, re.DOTALL)
        
        if not context_matches:
            financial_data[isin] = {'isin': isin, 'data_found': False}
            continue
            
        context = context_matches[0]
        
        # Initialize data structure for this ISIN
        data = {
            'isin': isin,
            'data_found': True,
            'context': context,
            'security_type': None,
            'name': None,
            'quantity': None,
            'price': None,
            'market_value': None,
            'currency': None,
            'percentage': None,
            'dates': [],
            'performance': None,
            'additional_metrics': {}
        }
        
        # Extract security name
        name_pattern = r'(?:' + re.escape(isin) + r'[^\n]*?([A-Z][A-Za-z\s\-\.\&0-9]{5,50}))'
        name_matches = re.findall(name_pattern, context)
        if name_matches:
            data['name'] = name_matches[0].strip()
            
        # Determine security type
        for sec_type, pattern in patterns['security_types'].items():
            if re.search(pattern, context, re.IGNORECASE):
                data['security_type'] = sec_type
                break
                
        # Extract each data point
        for metric, metric_patterns in patterns.items():
            if metric == 'security_types':  # Already handled
                continue
                
            if isinstance(metric_patterns, list):
                for pattern in metric_patterns:
                    matches = re.findall(pattern, context, re.IGNORECASE)
                    if matches:
                        # Handle special cases
                        if metric == 'dates':
                            data[metric].extend(matches)
                        else:
                            data[metric] = matches[0]
                            break
            else:
                # Single pattern (like currency)
                matches = re.findall(metric_patterns, context)
                if matches:
                    data[metric] = matches[0]
        
        financial_data[isin] = data
    
    return financial_data

def analyze_portfolio(holdings_data):
    """Perform comprehensive portfolio analysis"""
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(holdings_data, orient='index')
    
    # Check if DataFrame is empty
    if df.empty:
        return {
            'total_value': 0,
            'security_count': 0,
            'asset_allocation': {},
            'currency_allocation': {},
            'top_holdings': [],
            'risk_metrics': {},
            'performance': {}
        }
    
    # Ensure numeric values
    numeric_columns = ['market_value', 'quantity', 'price', 'percentage']
    for col in numeric_columns:
        if col in df.columns:
            # Check if the column has any non-null values
            if df[col].notna().any():
                # Convert string percentages to floats
                if col == 'percentage':
                    # Handle percentage values with % symbol
                    df[col] = df[col].astype(str).str.replace('%', '', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce') / 100.0
                else:
                    # Handle numeric values with commas
                    df[col] = df[col].astype(str).str.replace(',', '', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Initialize results
    results = {
        'total_value': 0,
        'security_count': len(df),
        'asset_allocation': {},
        'currency_allocation': {},
        'top_holdings': [],
        'risk_metrics': {},
        'performance': {}
    }
    
    # Calculate total value
    if 'market_value' in df.columns and df['market_value'].notna().any():
        results['total_value'] = df['market_value'].sum()
    
    # Calculate asset allocation
    if 'security_type' in df.columns and df['security_type'].notna().any() and 'market_value' in df.columns:
        try:
            # Filter out rows with NaN values
            valid_rows = df[df['security_type'].notna() & df['market_value'].notna()]
            if not valid_rows.empty:
                asset_allocation = valid_rows.groupby('security_type')['market_value'].sum()
                asset_allocation_dict = asset_allocation.to_dict()
                
                # Calculate percentages
                for asset_type, value in asset_allocation_dict.items():
                    if asset_type and not pd.isna(asset_type):
                        results['asset_allocation'][asset_type] = {
                            'value': value,
                            'percentage': value / results['total_value'] * 100 if results['total_value'] else 0
                        }
        except Exception as e:
            print(f"Error calculating asset allocation: {e}")
    
    # Identify top holdings
    if 'market_value' in df.columns and df['market_value'].notna().any():
        try:
            # Filter valid rows and get top 10
            valid_rows = df[df['market_value'].notna()]
            if not valid_rows.empty:
                top_holdings = valid_rows.nlargest(10, 'market_value')
                
                for idx, row in top_holdings.iterrows():
                    holding_data = {
                        'isin': idx,
                        'market_value': row['market_value'],
                        'percentage': row['market_value'] / results['total_value'] * 100 if results['total_value'] else 0
                    }
                    
                    # Add name if available
                    if 'name' in row and not pd.isna(row['name']):
                        holding_data['name'] = row['name']
                    else:
                        holding_data['name'] = 'Unknown'
                    
                    results['top_holdings'].append(holding_data)
        except Exception as e:
            print(f"Error identifying top holdings: {e}")
    
    return results

def generate_custom_table(extracted_data, table_spec):
    """Generate a custom table based on user specifications"""
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame.from_dict(extracted_data, orient='index')
    
    # Apply filters
    if 'filters' in table_spec:
        for column, filter_value in table_spec['filters'].items():
            if column in df.columns:
                if isinstance(filter_value, dict):
                    # Complex filter with operators
                    if 'gt' in filter_value:
                        df = df[df[column] > filter_value['gt']]
                    if 'lt' in filter_value:
                        df = df[df[column] < filter_value['lt']]
                    if 'eq' in filter_value:
                        df = df[df[column] == filter_value['eq']]
                    if 'contains' in filter_value:
                        df = df[df[column].str.contains(filter_value['contains'], na=False)]
                else:
                    # Simple equality filter
                    df = df[df[column] == filter_value]
    
    # Sort data
    if 'sort_by' in table_spec and table_spec['sort_by'] in df.columns:
        ascending = table_spec.get('sort_order', 'asc') == 'asc'
        df = df.sort_values(by=table_spec['sort_by'], ascending=ascending)
    
    # Select columns
    if 'columns' in table_spec:
        columns = [col for col in table_spec['columns'] if col in df.columns]
        df = df[columns]
    
    return df

# Main function for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_financial_extractor.py <ocr_json_file>")
        sys.exit(1)
    
    # Load OCR text
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)
    
    # Combine all text
    all_text = ""
    for page_num, page_data in ocr_data.items():
        all_text += page_data.get("text", "") + "\n\n"
    
    # Extract ISIN numbers
    isin_numbers = extract_isin_numbers(all_text)
    print(f"Found {len(isin_numbers)} ISIN numbers")
    
    # Extract financial metadata
    financial_data = extract_financial_metadata(all_text, isin_numbers)
    
    # Save results
    output_file = sys.argv[1].replace("_ocr.json", "_enhanced_financial.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(financial_data, f, indent=2, ensure_ascii=False)
    
    print(f"Enhanced financial data saved to {output_file}")
