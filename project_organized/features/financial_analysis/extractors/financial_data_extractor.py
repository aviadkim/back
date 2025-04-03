# file: financial_data_extractor.py

import os
import re
import json
import sys
import logging
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"financial_extraction_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("financial_extractor")

def load_extracted_text(json_path):
    """Load OCR-extracted text from a JSON file"""
    with open(json_path, 'r', encoding='utf-8') as f:
        document = json.load(f)
    
    # Combine all text
    all_text = ""
    for page_num in sorted(document.keys()):
        all_text += document[page_num].get("text", "") + "\n\n"
    
    return all_text, document

def extract_isin_numbers(text):
    """Extract ISIN numbers from text"""
    isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
    return list(set(re.findall(isin_pattern, text)))  # Remove duplicates

def extract_currencies(text):
    """Extract currency mentions from text"""
    currency_pattern = r'\b(?:EUR|USD|CHF|GBP|JPY|ILS)\b'
    return list(set(re.findall(currency_pattern, text)))

def extract_amounts(text):
    """Extract monetary amounts from text"""
    # Match numbers with commas and decimal points
    # Examples: 1,234.56 or 1.234,56 or 1 234.56
    amount_patterns = [
        r'\b\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?\b',  # 1,234.56
        r'\b\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?\b',  # 1.234,56
        r'\b\d{1,3}(?:\s\d{3})*(?:\.\d{1,2})?\b',  # 1 234.56
    ]
    
    all_amounts = []
    for pattern in amount_patterns:
        matches = re.findall(pattern, text)
        all_amounts.extend(matches)
    
    return all_amounts

def find_associated_data(text, isin, page_contents=None):
    """Find data associated with an ISIN number"""
    # Look for the page where the ISIN appears
    isin_pages = []
    if page_contents:
        for page_num, page_data in page_contents.items():
            if isin in page_data.get("text", ""):
                isin_pages.append(int(page_num))
    
    # Look for context around the ISIN (50 chars before, 100 after)
    pattern = r'(.{0,100}' + re.escape(isin) + r'.{0,200})'
    matches = re.findall(pattern, text)
    
    if not matches:
        return None
    
    context = matches[0]
    
    # Extract potential quantity/nominal value
    # Look for patterns like "1,000" or "1,000.00" near words like "Nominal"
    quantity_patterns = [
        r'(?:Nominal|Amount|Quantity|Qty)[\s:]+([0-9,\.]+)(?:\s|$)',
        r'([0-9,\.]+)[\s]+(?:units|shares|bonds)',
        r'(?:Stk\.|Pcs\.?|Units?|Amount)[\s:]*([0-9,\.]+)'
    ]
    
    quantity = None
    for pattern in quantity_patterns:
        qty_matches = re.findall(pattern, context, re.IGNORECASE)
        if qty_matches:
            quantity = qty_matches[0]
            break
    
    # Extract potential price/value
    price_patterns = [
        r'(?:Price|Value|NAV|Rate)[\s:]+([0-9,\.]+)',
        r'([0-9,\.]+)[\s]+(?:per share|per unit)',
        r'(?:Price|Value|NAV|Rate)[^\n]*?([0-9,\.]+)(?:\s|$)'
    ]
    
    price = None
    for pattern in price_patterns:
        price_matches = re.findall(pattern, context, re.IGNORECASE)
        if price_matches:
            price = price_matches[0]
            break
    
    # Extract currency
    currency_pattern = r'\b(?:EUR|USD|CHF|GBP|JPY|ILS)\b'
    currency_matches = re.findall(currency_pattern, context)
    currency = currency_matches[0] if currency_matches else None
    
    # Extract dates (common formats)
    date_pattern = r'\d{1,2}[./]\d{1,2}[./]\d{2,4}|\d{4}-\d{2}-\d{2}'
    date_matches = re.findall(date_pattern, context)
    date = date_matches[0] if date_matches else None
    
    # Try to extract description/name
    name_pattern = r'(?:' + re.escape(isin) + r'[^\n]*?([A-Z][A-Za-z\s\-\.\&]{10,50}))|(?:([A-Z][A-Za-z\s\-\.\&]{10,50})[^\n]*?' + re.escape(isin) + r')'
    name_matches = re.findall(name_pattern, context)
    name = None
    if name_matches:
        for match_tuple in name_matches:
            for potential_name in match_tuple:
                if potential_name and len(potential_name.strip()) > 10:
                    name = potential_name.strip()
                    break
            if name:
                break
    
    return {
        "isin": isin,
        "context": context.strip(),
        "quantity": quantity,
        "price": price,
        "currency": currency,
        "date": date,
        "name": name,
        "pages": isin_pages if page_contents else []
    }

def extract_tables_from_text(text):
    """Attempt to extract tables from text based on structure"""
    lines = text.split('\n')
    tables = []
    
    current_table = []
    in_table = False
    
    for line in lines:
        # Check if line looks like it could be part of a table
        # Tables typically have consistent spacing or multiple whitespace separators
        stripped = line.strip()
        if not stripped:
            if in_table and current_table:
                # Empty line after a table - end of table
                if len(current_table) >= 3:  # Require at least 3 rows to consider it a table
                    tables.append(current_table)
                current_table = []
                in_table = False
            continue
        
        # Detect table rows based on multiple spaces between fields or consistent patterns
        if '  ' in stripped and len(stripped) > 15:
            if not in_table:
                in_table = True
            current_table.append(stripped)
        elif in_table:
            # This line doesn't match table pattern, but we were in a table
            # Check if it might be a continuation of the previous line
            if current_table and len(stripped) < 40:
                # Might be a continuation - append to the last line
                current_table[-1] += " " + stripped
            else:
                # End of table
                if len(current_table) >= 3:  # Require at least 3 rows
                    tables.append(current_table)
                current_table = []
                in_table = False
    
    # Don't forget the last table
    if in_table and len(current_table) >= 3:
        tables.append(current_table)
    
    return tables

def convert_tables_to_dataframes(tables):
    """Convert extracted text tables to pandas DataFrames"""
    dataframes = []
    
    for table in tables:
        # Try to determine headers (usually the first row)
        headers = table[0].split()
        
        # Try to parse the rest as rows
        rows = []
        for i in range(1, len(table)):
            # Split by multiple spaces
            cells = re.split(r'\s{2,}', table[i])
            rows.append(cells)
        
        # Create DataFrame
        try:
            # Make sure we have consistent number of columns
            max_cols = max(len(row) for row in rows)
            padded_rows = []
            for row in rows:
                padded_rows.append(row + [''] * (max_cols - len(row)))
            
            df = pd.DataFrame(padded_rows)
            dataframes.append(df)
        except Exception as e:
            logger.error(f"Error creating DataFrame: {str(e)}")
    
    return dataframes

def main():
    if len(sys.argv) < 2:
        print("Usage: python financial_data_extractor.py <ocr_json_file> [output_format]")
        print("Example: python financial_data_extractor.py '2. Messos 28.02.2025_ocr.json' [json|csv]")
        return
    
    json_path = sys.argv[1]
    output_format = sys.argv[2].lower() if len(sys.argv) > 2 else "json"
    
    if not os.path.exists(json_path):
        logger.error(f"File not found: {json_path}")
        return
    
    # Load text
    all_text, page_contents = load_extracted_text(json_path)
    
    # Extract ISIN numbers
    isin_numbers = extract_isin_numbers(all_text)
    
    if not isin_numbers:
        logger.warning("No ISIN numbers found.")
    else:
        logger.info(f"Found {len(isin_numbers)} ISIN numbers.")
    
    # Extract currencies
    currencies = extract_currencies(all_text)
    logger.info(f"Found currencies: {', '.join(currencies)}")
    
    # Extract amounts
    amounts = extract_amounts(all_text)
    logger.info(f"Found {len(amounts)} potential monetary amounts")
    
    # Extract tables
    tables = extract_tables_from_text(all_text)
    logger.info(f"Found {len(tables)} potential tables")
    
    # Try to convert tables to DataFrames
    dataframes = convert_tables_to_dataframes(tables)
    logger.info(f"Converted {len(dataframes)} tables to DataFrames")
    
    # Extract associated data for each ISIN
    results = []
    for isin in isin_numbers:
        data = find_associated_data(all_text, isin, page_contents)
        if data:
            results.append(data)
    
    # Print results
    print("\n=== Financial Data Extraction Results ===")
    print(f"Document: {os.path.basename(json_path)}")
    print(f"ISINs found: {len(isin_numbers)}")
    print(f"Tables found: {len(tables)}")
    
    print("\n=== ISIN Details ===")
    for i, data in enumerate(results):
        print(f"\n{i+1}. ISIN: {data['isin']}")
        if data['name']:
            print(f"   Name: {data['name']}")
        if data['quantity']:
            print(f"   Quantity: {data['quantity']}")
        if data['price']:
            print(f"   Price: {data['price']}")
        if data['currency']:
            print(f"   Currency: {data['currency']}")
        if data['date']:
            print(f"   Date: {data['date']}")
        if data['pages']:
            print(f"   Pages: {', '.join(map(str, data['pages']))}")
    
    # Save results
    base_name = os.path.splitext(json_path)[0]
    
    if output_format == "json" or output_format == "both":
        # Save ISIN data as JSON
        isin_output = f"{base_name}_isin_data.json"
        with open(isin_output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nISIN data saved to {isin_output}")
    
    if output_format == "csv" or output_format == "both":
        # Save ISIN data as CSV
        isin_csv = f"{base_name}_isin_data.csv"
        df = pd.DataFrame(results)
        df.to_csv(isin_csv, index=False, encoding='utf-8')
        print(f"\nISIN data saved to {isin_csv}")
    
    # Save tables
    if tables and (output_format == "json" or output_format == "both"):
        tables_output = f"{base_name}_tables.json"
        with open(tables_output, 'w', encoding='utf-8') as f:
            json.dump(tables, f, indent=2, ensure_ascii=False)
        print(f"Tables saved to {tables_output}")
    
    if dataframes:
        # Save each DataFrame to a CSV file
        for i, df in enumerate(dataframes):
            df_output = f"{base_name}_table_{i+1}.csv"
            df.to_csv(df_output, index=False, encoding='utf-8')
            print(f"Table {i+1} saved to {df_output}")

if __name__ == "__main__":
    main()