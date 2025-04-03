import re
import json
import os
import logging
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedFinancialExtractor:
    """Advanced extractor for financial data from documents"""
    
    def __init__(self):
        # ISIN pattern: 2 letters followed by 10 digits/letters
        self.isin_pattern = r'\b([A-Z]{2}[A-Z0-9]{10})\b'
        
        # Currency patterns
        self.currency_symbols = r'[$€£₪]'
        self.currency_codes = r'\b(USD|EUR|GBP|ILS|NIS)\b'
        
        # Number patterns - handles different formats including thousands separators
        self.number_pattern = r'((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)'
        
        # Percentage pattern
        self.percentage_pattern = r'(\d+\.?\d*)[ ]?%'
        
        # Date patterns
        self.date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # 31/12/2023
            r'\d{1,2}-\d{1,2}-\d{2,4}',  # 31-12-2023
            r'\d{1,2}\.\d{1,2}\.\d{2,4}', # 31.12.2023
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'  # February 28, 2023
        ]
        
        # Financial terms for context extraction
        self.financial_terms = [
            'total', 'sum', 'balance', 'value', 'price', 'quantity', 'amount',
            'shares', 'bonds', 'equity', 'asset', 'liability', 'capital',
            'interest', 'dividend', 'yield', 'profit', 'loss', 'revenue',
            'expense', 'cost', 'fee', 'tax', 'payment', 'allocation'
        ]
    
    def extract_from_document(self, document_id, extraction_dir='extractions', output_dir='financial_data'):
        """Extract financial data from a document extraction"""
        logger.info(f"Extracting financial data from document: {document_id}")
        
        # Get the extraction file
        extraction_path = os.path.join(extraction_dir, f"{document_id}_extraction.json")
        
        if not os.path.exists(extraction_path):
            logger.error(f"Extraction file not found: {extraction_path}")
            return None
        
        # Load the extraction
        try:
            with open(extraction_path, 'r', encoding='utf-8') as f:
                extraction = json.load(f)
        except Exception as e:
            logger.error(f"Error reading extraction file: {e}")
            return None
        
        # Extract content
        content = extraction.get('content', '')
        pages = extraction.get('pages', [])
        page_texts = [page.get('text', '') for page in pages]
        
        # Extract financial data
        result = self.extract_data(content, page_texts)
        result['document_id'] = document_id
        
        # Save the result
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{document_id}_financial.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Financial data extraction completed and saved to {output_path}")
        
        return result
    
    def extract_data(self, text, page_texts=None):
        """Extract all financial data from text"""
        if page_texts is None:
            page_texts = [text]
        
        # Basic extraction
        isins = self._extract_isins(text)
        currencies = self._extract_currencies(text)
        percentages = self._extract_percentages(text)
        dates = self._extract_dates(text)
        
        # Advanced extraction
        securities = self._extract_securities(text, page_texts)
        tables = self._extract_table_data(text)
        summary_data = self._extract_summary_data(text)
        financial_metrics = self._extract_financial_metrics(text)
        
        # Create structured result
        result = {
            'isins': isins,
            'securities': securities,
            'currencies': currencies,
            'percentages': percentages,
            'dates': dates,
            'tables': tables,
            'summary': summary_data,
            'metrics': financial_metrics,
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def _extract_isins(self, text):
        """Extract ISIN numbers from text"""
        isins = re.findall(self.isin_pattern, text)
        unique_isins = list(set(isins))  # Remove duplicates
        logger.info(f"Extracted {len(unique_isins)} unique ISINs")
        return unique_isins
    
    def _extract_currencies(self, text):
        """Extract currency amounts from text"""
        # Look for currency symbol followed by number
        symbol_amounts = re.findall(f'{self.currency_symbols}\s*{self.number_pattern}', text)
        
        # Look for number followed by currency code
        code_amounts = re.findall(f'{self.number_pattern}\s*{self.currency_codes}', text)
        
        currencies = []
        
        # Process symbol amounts
        for match in symbol_amounts:
            if isinstance(match, tuple):
                amount = match[-1]  # Last group in the tuple is usually the number
            else:
                amount = re.search(self.number_pattern, match).group(0)
            
            symbol = re.search(self.currency_symbols, match).group(0)
            
            currencies.append({
                'amount': amount,
                'symbol': symbol,
                'type': 'symbol_amount'
            })
        
        # Process code amounts
        for match in code_amounts:
            if isinstance(match, tuple):
                amount = match[0]  # First group in the tuple is usually the number
                code_match = re.search(self.currency_codes, match[-1])
            else:
                amount = re.search(self.number_pattern, match).group(0)
                code_match = re.search(self.currency_codes, match)
            
            code = code_match.group(0) if code_match else ""
            
            currencies.append({
                'amount': amount,
                'code': code,
                'type': 'code_amount'
            })
        
        logger.info(f"Extracted {len(currencies)} currency amounts")
        return currencies
    
    def _extract_percentages(self, text):
        """Extract percentage values from text"""
        percentages = []
        
        for match in re.finditer(self.percentage_pattern, text):
            # Get the percentage value
            percentage_value = match.group(1)
            
            # Get context (20 chars before and after)
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end]
            
            percentages.append({
                'value': percentage_value,
                'context': context
            })
        
        logger.info(f"Extracted {len(percentages)} percentages")
        return percentages
    
    def _extract_dates(self, text):
        """Extract dates from text"""
        dates = []
        
        for pattern in self.date_patterns:
            for match in re.finditer(pattern, text):
                date_str = match.group(0)
                
                # Get context (30 chars before and after)
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end]
                
                # Try to identify date type from context
                date_type = self._identify_date_type(context)
                
                dates.append({
                    'date': date_str,
                    'type': date_type,
                    'context': context
                })
        
        logger.info(f"Extracted {len(dates)} dates")
        return dates
    
    def _identify_date_type(self, context):
        """Try to identify what type of date this is from context"""
        context_lower = context.lower()
        
        if any(term in context_lower for term in ['valuation', 'as of', 'as at']):
            return 'valuation_date'
        elif any(term in context_lower for term in ['report', 'statement']):
            return 'report_date'
        elif any(term in context_lower for term in ['transaction', 'trade']):
            return 'transaction_date'
        elif any(term in context_lower for term in ['maturity', 'expires']):
            return 'maturity_date'
        elif any(term in context_lower for term in ['issue', 'issuance']):
            return 'issue_date'
        else:
            return 'unknown'
    
    def _extract_securities(self, text, page_texts):
        """Extract securities information (ISIN with associated data)"""
        securities = []
        
        # Find all ISINs
        isins = re.findall(self.isin_pattern, text)
        unique_isins = list(set(isins))  # Remove duplicates
        
        for isin in unique_isins:
            # Find all occurrences of this ISIN
            security_data = self._extract_security_data(isin, text, page_texts)
            securities.append(security_data)
        
        logger.info(f"Extracted data for {len(securities)} securities")
        return securities
    
    def _extract_security_data(self, isin, text, page_texts):
        """Extract data for a specific security (ISIN)"""
        # Find occurrences across all pages
        occurrences = []
        
        for i, page_text in enumerate(page_texts):
            positions = [m.start() for m in re.finditer(re.escape(isin), page_text)]
            for pos in positions:
                # Get context (100 chars before and after)
                start = max(0, pos - 100)
                end = min(len(page_text), pos + 100)
                context = page_text[start:end]
                
                occurrences.append({
                    'page_index': i,
                    'position': pos,
                    'context': context
                })
        
        # Extract name
        name = self._extract_security_name(isin, text, occurrences)
        
        # Extract quantities
        quantities = self._extract_security_quantities(isin, text, occurrences)
        
        # Extract prices
        prices = self._extract_security_prices(isin, text, occurrences)
        
        # Extract currency
        currency = self._extract_security_currency(isin, text, occurrences)
        
        # Create security data
        security_data = {
            'isin': isin,
            'name': name,
            'quantities': quantities,
            'prices': prices,
            'currency': currency,
            'occurrences': occurrences
        }
        
        return security_data
    
    def _extract_security_name(self, isin, text, occurrences):
        """Extract security name based on ISIN occurrences"""
        # Try different approaches to find the name
        
        # Look for patterns like "NAME (ISIN: XX0000000000)" or "NAME, ISIN XX0000000000"
        name_pattern1 = r'([A-Z][A-Za-z0-9\.\, ]{2,50})[\s\(](?:ISIN:?\s*)?' + re.escape(isin)
        name_pattern2 = re.escape(isin) + r'(?:\s*:)?\s*([A-Z][A-Za-z0-9\.\, ]{2,50})'
        
        # Try to find name in occurrences contexts
        for occurrence in occurrences:
            context = occurrence['context']
            
            # Try pattern 1
            match = re.search(name_pattern1, context)
            if match:
                return match.group(1).strip()
            
            # Try pattern 2
            match = re.search(name_pattern2, context)
            if match:
                return match.group(1).strip()
            
            # Try to find a capitalized name near the ISIN
            isin_pos = context.find(isin)
            if isin_pos > 0:
                # Look at text before ISIN
                before_text = context[:isin_pos].strip()
                words = before_text.split()
                
                # If we have words before the ISIN
                if words:
                    # Take the last 1-4 words that start with uppercase
                    name_words = []
                    for word in reversed(words):
                        if re.match(r'^[A-Z]', word) and len(name_words) < 4:
                            name_words.insert(0, word)
                    
                    if name_words:
                        return ' '.join(name_words)
        
        # If no name found in occurrences, try searching in the whole text
        for pattern in [name_pattern1, name_pattern2]:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        # Default response if no name found
        return "Unknown"
    
    def _extract_security_quantities(self, isin, text, occurrences):
        """Extract quantities associated with this security"""
        quantities = []
        
        # Quantity-related terms
        quantity_terms = ['quantity', 'shares', 'units', 'volume', 'amount', 'balance', 'holding']
        
        # Look in contexts for quantities
        for occurrence in occurrences:
            context = occurrence['context'].lower()
            
            # Look for quantity terms followed by numbers
            for term in quantity_terms:
                # Pattern: term followed by number
                pattern = r'(?i)' + re.escape(term) + r'\s*[:=]?\s*' + self.number_pattern
                for match in re.finditer(pattern, context):
                    if isinstance(match.group(1), tuple):
                        quantity = match.group(1)[0]  # First capture group
                    else:
                        quantity = match.group(1)
                    
                    quantities.append({
                        'value': quantity,
                        'term': term,
                        'context': match.group(0)
                    })
        
        return quantities
    
    def _extract_security_prices(self, isin, text, occurrences):
        """Extract prices associated with this security"""
        prices = []
        
        # Price-related terms
        price_terms = ['price', 'rate', 'value', 'cost', 'nav', 'market value']
        
        # Look in contexts for prices
        for occurrence in occurrences:
            context = occurrence['context'].lower()
            
            # Look for price terms with currency and numbers
            for term in price_terms:
                # Pattern: term followed by currency symbol/code and number
                currency_pattern = f'(?:{self.currency_symbols}|{self.currency_codes})'
                
                # Term followed by currency and number
                pattern1 = r'(?i)' + re.escape(term) + r'\s*[:=]?\s*' + currency_pattern + r'\s*' + self.number_pattern
                
                # Term followed by number and currency
                pattern2 = r'(?i)' + re.escape(term) + r'\s*[:=]?\s*' + self.number_pattern + r'\s*' + currency_pattern
                
                # Check both patterns
                for pattern in [pattern1, pattern2]:
                    for match in re.finditer(pattern, context):
                        match_text = match.group(0)
                        
                        # Extract the number
                        number_match = re.search(self.number_pattern, match_text)
                        if number_match:
                            price_value = number_match.group(0)
                            
                            # Extract the currency
                            currency_symbol_match = re.search(self.currency_symbols, match_text)
                            currency_code_match = re.search(self.currency_codes, match_text)
                            
                            currency = None
                            if currency_symbol_match:
                                currency = currency_symbol_match.group(0)
                            elif currency_code_match:
                                currency = currency_code_match.group(0)
                            
                            prices.append({
                                'value': price_value,
                                'currency': currency,
                                'term': term,
                                'context': match_text
                            })
        
        return prices
    
    def _extract_security_currency(self, isin, text, occurrences):
        """Extract currency associated with this security"""
        currencies = set()
        
        # Get currencies from prices
        prices = self._extract_security_prices(isin, text, occurrences)
        for price in prices:
            if price.get('currency'):
                currencies.add(price['currency'])
        
        # If no currency found in prices, look in contexts
        if not currencies:
            for occurrence in occurrences:
                context = occurrence['context']
                
                # Look for currency symbols
                symbol_matches = re.findall(self.currency_symbols, context)
                for symbol in symbol_matches:
                    currencies.add(symbol)
                
                # Look for currency codes
                code_matches = re.findall(self.currency_codes, context)
                for code in code_matches:
                    currencies.add(code)
        
        return list(currencies)
    
    def _extract_table_data(self, text):
        """Extract and process table data from text"""
        # Split text into lines
        lines = text.split('\n')
        
        # Find potential tables (consecutive lines with similar structure)
        tables = []
        current_table = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                if current_table:
                    if len(current_table) >= 3:  # Minimum 3 rows for a table
                        tables.append(current_table)
                    current_table = []
                continue
            
            # Check if line has a table-like structure
            if self._is_potential_table_row(line):
                current_table.append(line)
            elif current_table:
                if len(current_table) >= 3:  # Minimum 3 rows for a table
                    tables.append(current_table)
                current_table = []
        
        # Don't forget the last table
        if current_table and len(current_table) >= 3:
            tables.append(current_table)
        
        # Process each potential table
        processed_tables = []
        for table_lines in tables:
            # Try different parsing approaches
            table_data = self._parse_table(table_lines)
            if table_data:
                processed_tables.append(table_data)
        
        logger.info(f"Extracted {len(processed_tables)} potential tables")
        return processed_tables
    
    def _is_potential_table_row(self, line):
        """Check if a line might be part of a table"""
        # Check for multiple spaces (column separators)
        if '  ' in line and line.count('  ') >= 2:
            return True
        
        # Check for tab separators
        if '\t' in line:
            return True
        
        # Check for consistent separators like | or ;
        for sep in ['|', ';']:
            if sep in line and line.count(sep) >= 2:
                return True
        
        # Check for potential comma-separated data
        if ',' in line:
            # Avoid interpreting normal text as CSV
            comma_count = line.count(',')
            word_count = len(line.split())
            # If commas are more frequent than in normal text
            if comma_count >= 2 and comma_count >= word_count / 5:
                return True
        
        return False
    
    def _parse_table(self, table_lines):
        """Parse a potential table into structured data"""
        # Try different parsing strategies
        
        # Strategy 1: Split by multiple spaces
        if all('  ' in line for line in table_lines[:3]):
            header = re.split(r'\s{2,}', table_lines[0].strip())
            rows = [re.split(r'\s{2,}', line.strip()) for line in table_lines[1:]]
            
            # Check if columns are consistent
            if all(len(row) == len(header) for row in rows):
                return {
                    'headers': header,
                    'rows': rows,
                    'parsing_method': 'space_separated'
                }
        
        # Strategy 2: Split by tabs
        if all('\t' in line for line in table_lines[:3]):
            header = [col.strip() for col in table_lines[0].split('\t')]
            rows = [[col.strip() for col in line.split('\t')] for line in table_lines[1:]]
            
            # Check if columns are consistent
            if all(len(row) == len(header) for row in rows):
                return {
                    'headers': header,
                    'rows': rows,
                    'parsing_method': 'tab_separated'
                }
        
        # Strategy 3: Split by separator characters
        for sep in ['|', ';', ',']:
            if all(sep in line for line in table_lines[:3]):
                header = [col.strip() for col in table_lines[0].split(sep)]
                rows = [[col.strip() for col in line.split(sep)] for line in table_lines[1:]]
                
                # Check if columns are consistent
                if all(len(row) == len(header) for row in rows):
                    return {
                        'headers': header,
                        'rows': rows,
                        'parsing_method': f'{sep}_separated'
                    }
        
        # If no parsing method worked, try a fallback approach
        # Analyze the first few lines to find a consistent structure
        if len(table_lines) >= 3:
            # Try to deduce delimiters from data
            potential_delimiters = [' ', ',', ';', '\t', '|']
            best_delimiter = None
            max_consistency = 0
            
            for delimiter in potential_delimiters:
                # Check consistency of column counts
                col_counts = [len(line.split(delimiter)) for line in table_lines[:min(5, len(table_lines))]]
                
                if col_counts and min(col_counts) > 1:  # At least 2 columns
                    consistency = col_counts.count(col_counts[0]) / len(col_counts)
                    
                    if consistency > max_consistency:
                        max_consistency = consistency
                        best_delimiter = delimiter
            
            if best_delimiter and max_consistency >= 0.7:  # At least 70% consistent
                # Parse with best delimiter
                header = [col.strip() for col in table_lines[0].split(best_delimiter) if col.strip()]
                rows = []
                
                for line in table_lines[1:]:
                    cols = [col.strip() for col in line.split(best_delimiter) if col.strip()]
                    if cols:
                        # Align with header if needed
                        while len(cols) < len(header):
                            cols.append("")
                        rows.append(cols[:len(header)])  # Truncate if too long
                
                return {
                    'headers': header,
                    'rows': rows,
                    'parsing_method': 'adaptive'
                }
        
        # No suitable parsing found
        return None
    
    def _extract_summary_data(self, text):
        """Extract summary financial data from text"""
        summary = {}
        
        # Look for common summary data patterns
        
        # Total portfolio value
        portfolio_value_patterns = [
            r'(?i)total\s+(?:portfolio|asset|holding|fund)?\s*value\s*[:=]?\s*' + 
            f'(?:{self.currency_symbols})?\s*{self.number_pattern}',
            
            r'(?i)(?:portfolio|asset|holding|fund)?\s*total\s*[:=]?\s*' + 
            f'(?:{self.currency_symbols})?\s*{self.number_pattern}'
        ]
        
        for pattern in portfolio_value_patterns:
            match = re.search(pattern, text)
            if match:
                value_match = re.search(self.number_pattern, match.group(0))
                currency_match = re.search(self.currency_symbols, match.group(0))
                
                if value_match:
                    summary['total_portfolio_value'] = {
                        'value': value_match.group(0),
                        'currency': currency_match.group(0) if currency_match else None,
                        'context': match.group(0)
                    }
                    break
        
        # Account number
        account_patterns = [
            r'(?i)account\s*(?:number|no|#)?\s*[:=]?\s*([A-Za-z0-9\-]+)',
            r'(?i)(?:a/c|acct)\.?\s*(?:number|no|#)?\s*[:=]?\s*([A-Za-z0-9\-]+)'
        ]
        
        for pattern in account_patterns:
            match = re.search(pattern, text)
            if match:
                summary['account_number'] = {
                    'value': match.group(1),
                    'context': match.group(0)
                }
                break
        
        # Client name
        client_patterns = [
            r'(?i)client\s*(?:name)?\s*[:=]?\s*([A-Z][A-Za-z\.\, ]{2,50})',
            r'(?i)(?:name|account holder)\s*[:=]?\s*([A-Z][A-Za-z\.\, ]{2,50})'
        ]
        
        for pattern in client_patterns:
            match = re.search(pattern, text)
            if match:
                summary['client_name'] = {
                    'value': match.group(1),
                    'context': match.group(0)
                }
                break
        
        # Valuation date
        date_patterns = [
            r'(?i)(?:valuation|statement|as of|as at)\s*date\s*[:=]?\s*(' + 
            '|'.join(self.date_patterns) + ')'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_match = None
                for date_pattern in self.date_patterns:
                    date_match = re.search(date_pattern, match.group(1))
                    if date_match:
                        summary['valuation_date'] = {
                            'value': date_match.group(0),
                            'context': match.group(0)
                        }
                        break
                if date_match:
                    break
        
        logger.info(f"Extracted {len(summary)} summary data points")
        return summary
    
    def _extract_financial_metrics(self, text):
        """Extract financial metrics and ratios from text"""
        metrics = {}
        
        # Asset allocation
        allocation_section = self._extract_section(text, 
                                                ['asset allocation', 'allocation by asset', 'allocation by class'], 
                                                ['performance', 'holdings', 'securities'])
        
        if allocation_section:
            allocation_data = self._extract_allocation_data(allocation_section)
            if allocation_data:
                metrics['asset_allocation'] = allocation_data
        
        # Currency breakdown
        currency_section = self._extract_section(text, 
                                                ['currency allocation', 'currency breakdown', 'allocation by currency'], 
                                                ['asset allocation', 'performance', 'holdings'])
        
        if currency_section:
            currency_data = self._extract_allocation_data(currency_section)
            if currency_data:
                metrics['currency_allocation'] = currency_data
        
        # Performance metrics
        performance_section = self._extract_section(text, 
                                                 ['performance', 'return', 'yield', 'growth'], 
                                                 ['holdings', 'securities', 'allocation'])
        
        if performance_section:
            performance_data = self._extract_performance_data(performance_section)
            if performance_data:
                metrics['performance'] = performance_data
        
        logger.info(f"Extracted {len(metrics)} financial metric categories")
        return metrics
    
    def _extract_section(self, text, section_headers, end_markers):
        """Extract a section of text based on headers and end markers"""
        text_lower = text.lower()
        
        # Find section start
        start_pos = -1
        for header in section_headers:
            pos = text_lower.find(header)
            if pos >= 0:
                start_pos = pos
                break
        
        if start_pos < 0:
            return None
        
        # Find section end
        end_pos = len(text)
        for marker in end_markers:
            pos = text_lower.find(marker, start_pos + 1)
            if pos >= 0 and pos < end_pos:
                end_pos = pos
        
        # Extract the section (with reasonable max length)
        max_length = 2000  # Avoid extremely long sections
        section_length = min(end_pos - start_pos, max_length)
        
        return text[start_pos:start_pos + section_length]
    
    def _extract_allocation_data(self, section_text):
        """Extract allocation data (asset class or currency)"""
        allocation_data = []
        
        # Look for percentage patterns in the section
        for match in re.finditer(self.percentage_pattern, section_text):
            percentage = match.group(1)
            
            # Get context before the percentage (likely the category name)
            start = max(0, match.start() - 50)
            context_before = section_text[start:match.start()].strip()
            
            # Try to identify the category name
            category = self._identify_category(context_before)
            
            if category:
                allocation_data.append({
                    'category': category,
                    'percentage': percentage
                })
        
        return allocation_data
    
    def _identify_category(self, text):
        """Identify a category name from text"""
        # Look for the last word or phrase that could be a category
        words = text.split()
        
        if not words:
            return None
        
        # Check for common asset classes or currency names
        asset_classes = ['equity', 'equities', 'stocks', 'shares', 'bonds', 'fixed income', 
                      'cash', 'money market', 'commodities', 'alternatives', 'real estate',
                      'property', 'hedge funds', 'private equity']
        
        currencies = ['usd', 'eur', 'gbp', 'jpy', 'chf', 'cad', 'aud', 'nzd', 'ils', 'nis']
        
        # Try to find asset classes
        for asset_class in asset_classes:
            if asset_class.lower() in text.lower():
                # Find the position and extract the full name
                pos = text.lower().find(asset_class.lower())
                
                # Get some context around the match
                start = max(0, pos - 10)
                end = min(len(text), pos + len(asset_class) + 10)
                
                # Extract the full category name with potential modifiers
                category_text = text[start:end].strip()
                
                # Clean up the category text
                category = re.sub(r'[-:;,.]', ' ', category_text).strip()
                category = re.sub(r'\s+', ' ', category)
                
                return category
        
        # Try to find currencies
        for currency in currencies:
            if currency.lower() in text.lower():
                return currency.upper()
        
        # If no specific category found, try to get the last 1-3 words
        last_words = words[-min(3, len(words)):]
        category = ' '.join(last_words)
        
        # Clean up the category
        category = re.sub(r'[-:;,.]', ' ', category).strip()
        category = re.sub(r'\s+', ' ', category)
        
        return category
    
    def _extract_performance_data(self, section_text):
        """Extract performance metrics data"""
        performance_data = {}
        
        # Look for common performance metrics
        metrics = {
            'ytd': r'(?i)(?:ytd|year[\s\-]to[\s\-]date)[\s:]+([+-]?\d+\.?\d*%?)',
            '1_year': r'(?i)(?:1[- ]year?|one[- ]year|12[- ]month)[\s:]+([+-]?\d+\.?\d*%?)',
            '3_year': r'(?i)(?:3[- ]year?|three[- ]year)[\s:]+([+-]?\d+\.?\d*%?)',
            '5_year': r'(?i)(?:5[- ]year?|five[- ]year)[\s:]+([+-]?\d+\.?\d*%?)',
            'inception': r'(?i)(?:since[\s\-]inception)[\s:]+([+-]?\d+\.?\d*%?)'
        }
        
        for metric_name, pattern in metrics.items():
            match = re.search(pattern, section_text)
            if match:
                value = match.group(1)
                
                # Add % if not present
                if '%' not in value:
                    value = value + '%'
                
                performance_data[metric_name] = value
        
        return performance_data
    
    def to_dataframe(self, data):
        """Convert extracted data to pandas DataFrame for analysis"""
        if not data or 'securities' not in data:
            return None
        
        # Create a DataFrame from securities data
        securities = data['securities']
        
        df_data = []
        for security in securities:
            row = {
                'isin': security['isin'],
                'name': security['name'],
                'currency': security['currency'][0] if security['currency'] else None
            }
            
            # Add quantity if available
            if security['quantities']:
                # Use the first quantity value
                row['quantity'] = security['quantities'][0]['value']
            
            # Add price if available
            if security['prices']:
                # Use the first price value
                row['price'] = security['prices'][0]['value']
                
                # Add price currency if different from security currency
                if security['prices'][0].get('currency'):
                    row['price_currency'] = security['prices'][0]['currency']
            
            df_data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(df_data)
        
        return df

# Usage example
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python advanced_financial_extractor.py <document_id>")
        sys.exit(1)
    
    document_id = sys.argv[1]
    extractor = AdvancedFinancialExtractor()
    result = extractor.extract_from_document(document_id)
    
    if result:
        print(f"Processed document: {document_id}")
        print(f"Found {len(result['isins'])} ISINs")
        print(f"Extracted {len(result['securities'])} securities")
        print(f"Detected {len(result['tables'])} tables")
        
        # Convert to DataFrame and display
        df = extractor.to_dataframe(result)
        if df is not None:
            print("\nSecurities DataFrame:")
            print(df.head())
