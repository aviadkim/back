import pandas as pd
import re
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
import os
import json

class FinancialAnalyzer:
    """Analyze financial data extracted from documents.
    
    This class provides methods to recognize, categorize and analyze
    financial information from document text and tables.
    With enhanced support for multilingual financial documents and ISIN detection.
    """
    
    def __init__(self):
        """Initialize the financial analyzer with language-specific financial terms."""
        self.logger = logging.getLogger(__name__)
        
        # Load financial terms (English and Hebrew)
        self.financial_terms = self._load_financial_terms()
        
        # Initialize ISIN database if available
        self.isin_database = self._load_isin_database()
    
    def _load_financial_terms(self) -> Dict[str, List[str]]:
        """Load financial terms in multiple languages.
        
        Returns:
            Dictionary with financial term categories and their keywords
        """
        return {
            'income_statement': [
                # English terms
                'revenue', 'sales', 'income', 'expense', 'cost of goods', 'gross profit',
                'operating income', 'ebitda', 'net income', 'earnings per share', 'eps',
                'profit', 'loss', 'margin', 'tax', 'depreciation', 'amortization',
                # Hebrew terms
                'הכנסות', 'מכירות', 'רווח', 'הוצאות', 'עלות המכר', 'רווח גולמי',
                'רווח תפעולי', 'רווח נקי', 'רווח למניה', 'הפסד', 'מרווח', 'מס',
                'פחת', 'הפחתות'
            ],
            'balance_sheet': [
                # English terms
                'assets', 'liabilities', 'equity', 'cash', 'accounts receivable',
                'inventory', 'property', 'equipment', 'debt', 'loans', 'capital',
                'retained earnings', 'shares outstanding', 'book value',
                # Hebrew terms
                'נכסים', 'התחייבויות', 'הון', 'מזומנים', 'לקוחות', 'מלאי',
                'רכוש קבוע', 'ציוד', 'חוב', 'הלוואות', 'הון', 'עודפים',
                'מניות', 'ערך בספרים'
            ],
            'cash_flow': [
                # English terms
                'cash flow', 'operating activities', 'investing activities',
                'financing activities', 'capital expenditure', 'capex', 'dividend',
                'repurchase', 'issuance', 'free cash flow', 'fcf',
                # Hebrew terms
                'תזרים מזומנים', 'פעילות שוטפת', 'פעילות השקעה',
                'פעילות מימון', 'השקעות הוניות', 'דיבידנד',
                'רכישה עצמית', 'הנפקה', 'תזרים חופשי'
            ],
            'investment_portfolio': [
                # English terms
                'portfolio', 'holdings', 'securities', 'stocks', 'bonds', 'etf',
                'fund', 'investment', 'allocation', 'diversification', 'position',
                'weight', 'sector', 'asset class', 'maturity', 'yield', 'coupon',
                # Hebrew terms
                'תיק השקעות', 'אחזקות', 'ניירות ערך', 'מניות', 'אגרות חוב', 'אג״ח',
                'קרן', 'קרנות', 'השקעה', 'הקצאה', 'פיזור', 'פוזיציה',
                'משקל', 'סקטור', 'ענף', 'סוג נכס', 'מועד פירעון', 'תשואה', 'קופון'
            ],
            'ratios': [
                # English terms
                'ratio', 'return on', 'roe', 'roa', 'roi', 'eps', 'p/e', 'price to earnings',
                'debt to equity', 'current ratio', 'quick ratio', 'profit margin',
                'operating margin', 'net margin',
                # Hebrew terms
                'יחס', 'תשואה על', 'רווח למניה', 'מכפיל רווח',
                'יחס חוב להון', 'יחס שוטף', 'יחס מהיר', 'שולי רווח',
                'מרווח תפעולי', 'מרווח נקי'
            ]
        }
    
    def _load_isin_database(self) -> Dict[str, Dict[str, Any]]:
        """Load ISIN database if available.
        
        Returns:
            Dictionary with ISIN numbers as keys and security information as values
        """
        isin_db = {}
        
        # Try to load from file if it exists
        isin_db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'isin_database.json')
        if os.path.exists(isin_db_path):
            try:
                with open(isin_db_path, 'r', encoding='utf-8') as f:
                    isin_db = json.load(f)
                self.logger.info(f"Loaded {len(isin_db)} ISIN records from database")
            except Exception as e:
                self.logger.warning(f"Failed to load ISIN database: {str(e)}")
        
        return isin_db
    
    def classify_table(self, df: pd.DataFrame) -> str:
        """Classify a table based on its content with improved language support.
        
        Args:
            df: DataFrame containing table data
            
        Returns:
            Classification of the table (income_statement, balance_sheet, etc.)
        """
        if df.empty:
            return "unknown"
            
        # Convert dataframe to string for term matching
        table_text = ' '.join([' '.join(map(str, row)) for row in df.values])
        table_text = table_text.lower()
        
        # Count matches for each category
        scores = {}
        for category, terms in self.financial_terms.items():
            count = sum(1 for term in terms if term.lower() in table_text)
            scores[category] = count
            
        # Return the category with the highest score, if any terms matched
        max_category = max(scores.items(), key=lambda x: x[1])
        if max_category[1] > 0:
            return max_category[0]
        else:
            return "unknown"
    
    def extract_financial_metrics(self, text: str) -> Dict[str, Any]:
        """Extract key financial metrics from text with multilingual support.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dictionary of extracted financial metrics
        """
        metrics = {}
        
        # Extract currency values with support for multiple currencies
        currency_pattern = r'(?:USD|€|\$|£|₪)?\s?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s?(?:million|billion|thousand|m|b|k|₪|שקל|ש"ח)?'
        currency_matches = re.findall(currency_pattern, text)
        
        if currency_matches:
            # Process all matches but limit to avoid excessive output
            metrics['currency_values'] = [self._normalize_number(match) for match in currency_matches[:10]]
        
        # Extract percentages
        percentage_pattern = r'(\d+\.?\d*)%'
        percentage_matches = re.findall(percentage_pattern, text)
        
        if percentage_matches:
            metrics['percentages'] = [float(match) for match in percentage_matches[:10]]
            
        # Extract dates (common financial report date formats - including Hebrew)
        date_patterns = [
            r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}',
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{4}-\d{2}-\d{2}',
            # Hebrew date formats
            r'\d{1,2}\s+(?:ינואר|פברואר|מרץ|אפריל|מאי|יוני|יולי|אוגוסט|ספטמבר|אוקטובר|נובמבר|דצמבר)\s+\d{4}'
        ]
        
        dates = []
        for pattern in date_patterns:
            date_matches = re.findall(pattern, text)
            dates.extend(date_matches)
            
        if dates:
            metrics['dates'] = dates[:5]  # Limit to 5 dates
            
        # Extract fiscal periods
        period_pattern = r'(?:FY|Q[1-4]|רבעון\s+\d)\s?\'?\d{2,4}'
        period_matches = re.findall(period_pattern, text)
        
        if period_matches:
            metrics['fiscal_periods'] = period_matches
        
        # Extract ISIN codes
        isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
        isin_matches = re.findall(isin_pattern, text)
        
        if isin_matches:
            # Process ISIN matches
            metrics['isins'] = []
            for isin in isin_matches:
                isin_info = {
                    'code': isin,
                    'details': self._get_isin_details(isin)
                }
                metrics['isins'].append(isin_info)
            
        return metrics
        
    def _get_isin_details(self, isin: str) -> Dict[str, Any]:
        """Get details for an ISIN code from database.
        
        Args:
            isin: ISIN code
            
        Returns:
            Dictionary with security details if available
        """
        # Check if ISIN is in our database
        if isin in self.isin_database:
            return self.isin_database[isin]
            
        # If not in database, return basic validation info
        basic_info = {
            'country_code': isin[:2],
            'is_valid': self._validate_isin(isin)
        }
        
        return basic_info
    
    def _validate_isin(self, isin: str) -> bool:
        """Validate ISIN code format and check digit.
        
        Args:
            isin: ISIN code to validate
            
        Returns:
            Boolean indicating if ISIN is valid
        """
        if not re.match(r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$', isin):
            return False
            
        # Convert letters to numbers (A=10, B=11, ..., Z=35)
        chars = list(isin[:-1])  # All characters except the check digit
        check_digit = int(isin[-1])
        
        # Convert alpha to numeric
        for i, char in enumerate(chars):
            if 'A' <= char <= 'Z':
                # Convert letter to number (A=10, B=11, etc.)
                chars[i] = str(ord(char) - ord('A') + 10)
        
        # Concatenate all digits
        digits = ''.join(chars)
        
        # Compute the check digit
        total = 0
        for i, digit in enumerate(reversed(digits)):
            num = int(digit)
            if i % 2 == 0:
                num *= 2
                if num > 9:
                    num -= 9
            total += num
            
        computed_check = (10 - (total % 10)) % 10
        
        return computed_check == check_digit
        
    def analyze_financial_table(self, df: pd.DataFrame, table_type: str = None) -> Dict[str, Any]:
        """Perform analysis on a financial table with multilingual support.
        
        Args:
            df: DataFrame containing table data
            table_type: Type of financial table if known
            
        Returns:
            Dictionary containing analysis results
        """
        if df.empty:
            return {"error": "Empty table provided"}
            
        # If table_type not provided, classify the table
        if not table_type:
            table_type = self.classify_table(df)
            
        # Perform specific analysis based on table type
        analysis = {
            "table_type": table_type,
            "columns": len(df.columns),
            "rows": len(df),
        }
        
        # Try to identify time periods (columns are often time periods in financial tables)
        time_periods = self._extract_time_periods(df)
        if time_periods:
            analysis["time_periods"] = time_periods
            
        # Check for ISIN codes in the table
        isins = self._extract_isins_from_table(df)
        if isins:
            analysis["isins"] = isins
            
        # Basic numerical analysis
        try:
            # Convert to numeric where possible
            numeric_df = df.map(self._try_numeric_conversion) # Use map instead of deprecated applymap
            
            # Calculate basic statistics for numeric columns
            numeric_cols = numeric_df.select_dtypes(include=['number']).columns
            if not numeric_cols.empty:
                stats = numeric_df[numeric_cols].describe()
                analysis["statistics"] = {
                    col: {
                        "mean": stats[col]["mean"],
                        "min": stats[col]["min"],
                        "max": stats[col]["max"]
                    } for col in numeric_cols
                }
                
                # Calculate growth rates if time series data
                if table_type in ["income_statement", "cash_flow"] and len(numeric_cols) > 1:
                    growth_rates = self._calculate_growth_rates(numeric_df[numeric_cols])
                    if growth_rates:
                        analysis["growth_rates"] = growth_rates
        except Exception as e:
            self.logger.warning(f"Error in numeric analysis: {str(e)}")
            
        # Specific analysis by table type
        if table_type == "income_statement":
            income_analysis = self._analyze_income_statement(df)
            if income_analysis:
                analysis["income_analysis"] = income_analysis
        elif table_type == "balance_sheet":
            balance_analysis = self._analyze_balance_sheet(df)
            if balance_analysis:
                analysis["balance_analysis"] = balance_analysis
        elif table_type == "cash_flow":
            cash_flow_analysis = self._analyze_cash_flow(df)
            if cash_flow_analysis:
                analysis["cash_flow_analysis"] = cash_flow_analysis
        elif table_type == "ratios":
            ratio_analysis = self._analyze_ratios(df)
            if ratio_analysis:
                analysis["ratio_analysis"] = ratio_analysis
        elif table_type == "investment_portfolio":
            portfolio_analysis = self._analyze_investment_portfolio(df)
            if portfolio_analysis:
                analysis["portfolio_analysis"] = portfolio_analysis
                
        return analysis
    
    def _extract_isins_from_table(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Extract ISIN codes from a table.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of ISIN information
        """
        isins = []
        isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
        
        # Look in all columns (convert to string first)
        for col in df.columns:
            col_vals = df[col].astype(str)
            for i, val in enumerate(col_vals):
                matches = re.findall(isin_pattern, val)
                for isin in matches:
                    # Try to find the security name (often in same row, different column)
                    row_data = df.iloc[i].astype(str).tolist()
                    
                    # Look for text fields that might be names
                    potential_names = [
                        val for val in row_data 
                        if isinstance(val, str) and len(val) > 3 and not re.match(isin_pattern, val)
                    ]
                    
                    name = potential_names[0] if potential_names else "Unknown"
                    
                    isin_info = {
                        "code": isin,
                        "name": name,
                        "row": i,
                        "column": col,
                        "details": self._get_isin_details(isin)
                    }
                    
                    isins.append(isin_info)
        
        return isins
        
    def _normalize_number(self, value_str: str) -> float:
        """Convert string number with commas to float."""
        try:
            # Remove commas and other non-numeric characters
            clean_str = re.sub(r'[^\d.]', '', value_str)
            return float(clean_str)
        except ValueError:
            return 0.0
            
    def _try_numeric_conversion(self, value) -> Union[float, Any]:
        """Try to convert a value to numeric with multilingual support.
        
        Args:
            value: Value to convert
            
        Returns:
            Numeric value if conversion possible, otherwise original value
        """
        if pd.isna(value):
            return np.nan
            
        if isinstance(value, (int, float)):
            return value
            
        if not isinstance(value, str):
            return value
        
        # Remove Unicode characters that might interfere with parsing
        clean_str = value.strip()
        
        # Remove currency symbols and commas
        clean_str = re.sub(r'[,$€£₪%]', '', clean_str)
        
        # Handle parentheses for negative numbers (common in financial statements)
        if clean_str.startswith('(') and clean_str.endswith(')'):
            clean_str = '-' + clean_str[1:-1]
            
        # Handle Hebrew notation for shekels
        if 'ש"ח' in clean_str or 'שקל' in clean_str:
            clean_str = re.sub(r'ש"ח|שקל', '', clean_str)
            
        # Handle suffixes like K, M, B
        multiplier = 1
        if clean_str.endswith(('K', 'k', 'ק')):
            multiplier = 1000
            clean_str = clean_str[:-1]
        elif clean_str.endswith(('M', 'm', 'מ')):
            multiplier = 1000000
            clean_str = clean_str[:-1]
        elif clean_str.endswith(('B', 'b', 'ב')):
            multiplier = 1000000000
            clean_str = clean_str[:-1]
            
        # Replace Hebrew decimal point (sometimes used)
        clean_str = clean_str.replace('־', '.')
            
        try:
            return float(clean_str) * multiplier
        except ValueError:
            return value
            
    def _extract_time_periods(self, df: pd.DataFrame) -> List[str]:
        """Extract time periods from column headers with multilingual support."""
        periods = []
        
        # Common date patterns in financial tables (English and Hebrew)
        date_patterns = [
            r'\d{4}',  # Year (e.g., 2023)
            r'FY\d{2,4}',  # Fiscal year (e.g., FY2023)
            r'Q[1-4]\s?\d{4}',  # Quarter (e.g., Q1 2023)
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s?\d{2,4}',  # Month Year
            # Hebrew date patterns
            r'שנת\s+\d{4}',  # Year in Hebrew
            r'רבעון\s+\d{1}\s+\d{4}'  # Quarter in Hebrew
        ]
        
        # Check column headers
        for col in df.columns:
            col_str = str(col).strip()
            for pattern in date_patterns:
                if re.search(pattern, col_str, re.IGNORECASE):
                    periods.append(col_str)
                    break
                    
        return periods
        
    def _calculate_growth_rates(self, df: pd.DataFrame) -> Dict[str, List[float]]:
        """Calculate period-over-period growth rates."""
        growth_rates = {}
        
        # Need at least 2 columns for growth calculation
        if len(df.columns) < 2:
            return {}
            
        # Calculate for each row
        for idx, row in df.iterrows():
            values = row.values
            rates = []
            
            for i in range(1, len(values)):
                if values[i-1] != 0 and not pd.isna(values[i-1]) and not pd.isna(values[i]):
                    rate = ((values[i] - values[i-1]) / abs(values[i-1])) * 100
                    rates.append(round(rate, 2))
                else:
                    rates.append(None)
                    
            if any(rate is not None for rate in rates):
                growth_rates[str(idx)] = rates
                
        return growth_rates
        
    def _analyze_income_statement(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze income statement data with multilingual support."""
        analysis = {}
        
        # Try to identify key rows with both English and Hebrew terms
        key_items = {
            'revenue': ['revenue', 'sales', 'total revenue', 'הכנסות', 'מכירות', 'סך הכנסות'],
            'gross_profit': ['gross profit', 'gross margin', 'רווח גולמי', 'מרווח גולמי'],
            'operating_income': ['operating income', 'operating profit', 'ebit', 'רווח תפעולי', 'רווח מפעולות'],
            'net_income': ['net income', 'net profit', 'profit after tax', 'net earnings', 'רווח נקי', 'רווח אחרי מס']
        }
        
        # Find indices of key rows
        found_indices = {}
        for item_name, search_terms in key_items.items():
            for idx, row_label in enumerate(df.index):
                if isinstance(row_label, str) and any(term in row_label.lower() for term in search_terms):
                    found_indices[item_name] = idx
                    break
        
        # If no match in index, try searching in the first column
        if df.shape[1] > 0:
            first_col = df.iloc[:, 0]
            for item_name, search_terms in key_items.items():
                if item_name not in found_indices:
                    for idx, value in enumerate(first_col):
                        if isinstance(value, str) and any(term in value.lower() for term in search_terms):
                            found_indices[item_name] = idx
                            break
        
        # Extract values for key metrics
        for item_name, idx in found_indices.items():
            analysis[item_name] = df.iloc[idx, 1:].tolist()  # Skip the label column
        
        # Calculate margins if we have revenue and other metrics
        if 'revenue' in found_indices and len(analysis.get('revenue', [])) > 0:
            for metric in ['gross_profit', 'operating_income', 'net_income']:
                if metric in found_indices and len(analysis.get(metric, [])) == len(analysis['revenue']):
                    margin_name = f"{metric}_margin"
                    margins = []
                    
                    for i, rev in enumerate(analysis['revenue']):
                        if rev != 0 and not pd.isna(rev) and not pd.isna(analysis[metric][i]):
                            margin = (analysis[metric][i] / rev) * 100
                            margins.append(round(margin, 2))
                        else:
                            margins.append(None)
                            
                    analysis[margin_name] = margins
        
        return analysis
    
    def _analyze_balance_sheet(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze balance sheet data with multilingual support."""
        analysis = {}
        
        # Key balance sheet items to look for (English and Hebrew)
        key_items = {
            'total_assets': ['total assets', 'assets', 'סך נכסים', 'נכסים', 'סך הנכסים'],
            'total_liabilities': ['total liabilities', 'liabilities', 'סך התחייבויות', 'התחייבויות'],
            'equity': ['total equity', 'shareholders equity', 'stockholders equity', 'הון עצמי', 'הון', 'סך ההון'],
            'cash': ['cash', 'cash and cash equivalents', 'cash & equivalents', 'מזומנים', 'מזומנים ושווי מזומנים'],
            'debt': ['total debt', 'long term debt', 'short term debt', 'חוב', 'חוב לזמן ארוך', 'חוב לזמן קצר']
        }
        
        # Find indices of key rows (same approach as income statement)
        found_indices = {}
        for item_name, search_terms in key_items.items():
            for idx, row_label in enumerate(df.index):
                if isinstance(row_label, str) and any(term in row_label.lower() for term in search_terms):
                    found_indices[item_name] = idx
                    break
        
        # If no match in index, try searching in the first column
        if df.shape[1] > 0:
            first_col = df.iloc[:, 0]
            for item_name, search_terms in key_items.items():
                if item_name not in found_indices:
                    for idx, value in enumerate(first_col):
                        if isinstance(value, str) and any(term in value.lower() for term in search_terms):
                            found_indices[item_name] = idx
                            break
        
        # Extract values for key metrics
        for item_name, idx in found_indices.items():
            analysis[item_name] = df.iloc[idx, 1:].tolist()  # Skip the label column
        
        # Calculate financial ratios if we have the necessary data
        if 'total_assets' in found_indices and 'total_liabilities' in found_indices:
            if len(analysis.get('total_assets', [])) > 0 and len(analysis.get('total_liabilities', [])) == len(analysis['total_assets']):
                debt_to_assets = []
                
                for i, assets in enumerate(analysis['total_assets']):
                    if assets != 0 and not pd.isna(assets) and not pd.isna(analysis['total_liabilities'][i]):
                        ratio = (analysis['total_liabilities'][i] / assets)
                        debt_to_assets.append(round(ratio, 2))
                    else:
                        debt_to_assets.append(None)
                        
                analysis['debt_to_assets_ratio'] = debt_to_assets
        
        if 'cash' in found_indices and 'total_assets' in found_indices:
            if len(analysis.get('cash', [])) > 0 and len(analysis.get('total_assets', [])) == len(analysis['cash']):
                cash_ratio = []
                
                for i, assets in enumerate(analysis['total_assets']):
                    if assets != 0 and not pd.isna(assets) and not pd.isna(analysis['cash'][i]):
                        ratio = (analysis['cash'][i] / assets) * 100
                        cash_ratio.append(round(ratio, 2))
                    else:
                        cash_ratio.append(None)
                        
                analysis['cash_to_assets_percent'] = cash_ratio
        
        return analysis
    
    def _analyze_cash_flow(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze cash flow statement data with multilingual support."""
        analysis = {}
        
        # Key cash flow items to look for (English and Hebrew)
        key_items = {
            'operating_cash_flow': ['operating cash flow', 'cash from operations', 'net cash from operating activities', 
                                   'תזרים מזומנים מפעילות שוטפת', 'מזומנים מפעילות תפעולית'],
            'investing_cash_flow': ['investing cash flow', 'cash from investing', 'net cash from investing activities',
                                   'תזרים מזומנים מפעילות השקעה', 'מזומנים מפעילות השקעה'],
            'financing_cash_flow': ['financing cash flow', 'cash from financing', 'net cash from financing activities',
                                   'תזרים מזומנים מפעילות מימון', 'מזומנים מפעילות מימון'],
            'capex': ['capital expenditures', 'capex', 'purchases of property and equipment',
                     'השקעות הוניות', 'רכישת רכוש קבוע'],
            'free_cash_flow': ['free cash flow', 'fcf', 'תזרים מזומנים חופשי']
        }
        
        # Find indices of key rows
        found_indices = {}
        for item_name, search_terms in key_items.items():
            for idx, row_label in enumerate(df.index):
                if isinstance(row_label, str) and any(term in row_label.lower() for term in search_terms):
                    found_indices[item_name] = idx
                    break
        
        # If no match in index, try searching in the first column
        if df.shape[1] > 0:
            first_col = df.iloc[:, 0]
            for item_name, search_terms in key_items.items():
                if item_name not in found_indices:
                    for idx, value in enumerate(first_col):
                        if isinstance(value, str) and any(term in value.lower() for term in search_terms):
                            found_indices[item_name] = idx
                            break
        
        # Extract values for key metrics
        for item_name, idx in found_indices.items():
            analysis[item_name] = df.iloc[idx, 1:].tolist()  # Skip the label column
        
        # Calculate free cash flow if not already present and we have the necessary components
        if 'free_cash_flow' not in found_indices and 'operating_cash_flow' in found_indices and 'capex' in found_indices:
            if len(analysis.get('operating_cash_flow', [])) > 0 and len(analysis.get('capex', [])) == len(analysis['operating_cash_flow']):
                fcf = []
                
                for i, ocf in enumerate(analysis['operating_cash_flow']):
                    if not pd.isna(ocf) and not pd.isna(analysis['capex'][i]):
                        # Capex is typically negative, so we add it to operating cash flow
                        flow = ocf + analysis['capex'][i]
                        fcf.append(flow)
                    else:
                        fcf.append(None)
                        
                analysis['calculated_free_cash_flow'] = fcf
        
        return analysis
    
    def _analyze_ratios(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze financial ratios table with multilingual support."""
        analysis = {}
        
        # Key financial ratios to look for (English and Hebrew)
        key_ratios = {
            'roe': ['return on equity', 'roe', 'תשואה על ההון', 'תשואה להון'],
            'roa': ['return on assets', 'roa', 'תשואה על הנכסים', 'תשואה לנכסים'],
            'current_ratio': ['current ratio', 'יחס שוטף'],
            'quick_ratio': ['quick ratio', 'acid test ratio', 'יחס מהיר'],
            'debt_to_equity': ['debt to equity', 'debt/equity', 'יחס חוב להון'],
            'pe_ratio': ['price to earnings', 'p/e ratio', 'pe ratio', 'מכפיל רווח'],
            'dividend_yield': ['dividend yield', 'תשואת דיבידנד'],
            'profit_margin': ['profit margin', 'net margin', 'שולי רווח', 'מרווח נקי'],
            'operating_margin': ['operating margin', 'מרווח תפעולי']
        }
        
        # Find indices of key rows
        found_indices = {}
        for ratio_name, search_terms in key_ratios.items():
            for idx, row_label in enumerate(df.index):
                if isinstance(row_label, str) and any(term in row_label.lower() for term in search_terms):
                    found_indices[ratio_name] = idx
                    break
        
        # If no match in index, try searching in the first column
        if df.shape[1] > 0:
            first_col = df.iloc[:, 0]
            for ratio_name, search_terms in key_ratios.items():
                if ratio_name not in found_indices:
                    for idx, value in enumerate(first_col):
                        if isinstance(value, str) and any(term in value.lower() for term in search_terms):
                            found_indices[ratio_name] = idx
                            break
        
        # Extract values for key ratios
        for ratio_name, idx in found_indices.items():
            analysis[ratio_name] = df.iloc[idx, 1:].tolist()  # Skip the label column
        
        return analysis
    
    def _analyze_investment_portfolio(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze investment portfolio data with ISIN detection.
        
        Args:
            df: DataFrame containing portfolio data
            
        Returns:
            Dictionary with portfolio analysis
        """
        analysis = {}
        
        # Extract ISINs and security info
        securities = self._extract_isins_from_table(df)
        if securities:
            analysis["securities"] = securities
            
        # Try to identify key portfolio metrics
        metric_patterns = {
            'asset_type': ['asset type', 'asset class', 'type', 'סוג נכס', 'סוג'],
            'weight': ['weight', 'allocation', '%', 'percent', 'משקל', 'הקצאה', 'אחוז'],
            'value': ['value', 'amount', 'balance', 'ערך', 'סכום', 'יתרה'],
            'price': ['price', 'מחיר'],
            'quantity': ['quantity', 'shares', 'units', 'כמות', 'יחידות', 'מניות'],
            'yield': ['yield', 'תשואה'],
            'maturity': ['maturity', 'date', 'expiry', 'מועד פדיון', 'תאריך']
        }
        
        # Look for columns matching these metrics
        found_columns = {}
        for metric_name, search_terms in metric_patterns.items():
            for col in df.columns:
                col_str = str(col).lower()
                if any(term in col_str for term in search_terms):
                    found_columns[metric_name] = col
                    break
        
        # If no match in columns, try searching in the first row
        if df.shape[0] > 0:
            first_row = df.iloc[0]
            for metric_name, search_terms in metric_patterns.items():
                if metric_name not in found_columns:
                    for col, value in first_row.items():
                        if isinstance(value, str) and any(term in value.lower() for term in search_terms):
                            found_columns[metric_name] = col
                            break
        
        # Extract column values for identified metrics
        metrics_data = {}
        for metric_name, col in found_columns.items():
            try:
                values = df[col].tolist()[1:]  # Skip header if present
                metrics_data[metric_name] = values
            except Exception as e:
                self.logger.warning(f"Error extracting {metric_name}: {str(e)}")
        
        if metrics_data:
            analysis["metrics"] = metrics_data
            
        # Try to calculate portfolio composition by asset type
        if 'asset_type' in found_columns and 'weight' in found_columns:
            try:
                asset_types = df[found_columns['asset_type']].tolist()[1:]
                weights = df[found_columns['weight']].tolist()[1:]
                
                # Convert weights to numeric values
                numeric_weights = []
                for w in weights:
                    if isinstance(w, str):
                        # Remove % sign and convert to float
                        w = w.replace('%', '').strip()
                    try:
                        numeric_weights.append(float(w))
                    except (ValueError, TypeError):
                        numeric_weights.append(np.nan)
                
                # Create composition dictionary
                composition = {}
                for asset_type, weight in zip(asset_types, numeric_weights):
                    if not pd.isna(weight) and asset_type:
                        asset_type_str = str(asset_type).strip()
                        if asset_type_str in composition:
                            composition[asset_type_str] += weight
                        else:
                            composition[asset_type_str] = weight
                
                if composition:
                    analysis["composition"] = composition
            except Exception as e:
                self.logger.warning(f"Error calculating portfolio composition: {str(e)}")
        
        return analysis
    
    def analyze_document_text(self, text: str) -> Dict[str, Any]:
        """Analyze financial document text content for key metrics and entities.
        
        Args:
            text: Document text content
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {}
        
        # Extract basic financial metrics
        metrics = self.extract_financial_metrics(text)
        if metrics:
            analysis["metrics"] = metrics
            
        # Try to classify document type based on content
        doc_type = self._classify_document_type(text)
        if doc_type:
            analysis["document_type"] = doc_type
            
        # Extract potential securities information
        securities = self._extract_securities_info(text)
        if securities:
            analysis["securities"] = securities
            
        return analysis
    
    def _classify_document_type(self, text: str) -> str:
        """Classify financial document type based on content.
        
        Args:
            text: Document text
            
        Returns:
            Document type classification
        """
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Count matches for different document types
        type_scores = {}
        
        # Annual report indicators
        annual_report_terms = ['annual report', 'yearly report', 'fiscal year', 'דוח שנתי', 'דו"ח שנתי', 'שנת כספים']
        type_scores['annual_report'] = sum(text_lower.count(term) for term in annual_report_terms)
        
        # Quarterly report indicators
        quarterly_report_terms = ['quarterly report', 'quarter ended', 'q1', 'q2', 'q3', 'q4', 'דוח רבעוני', 'דו"ח רבעוני', 'רבעון']
        type_scores['quarterly_report'] = sum(text_lower.count(term) for term in quarterly_report_terms)
        
        # Portfolio statement indicators
        portfolio_terms = ['portfolio', 'holdings', 'securities', 'תיק השקעות', 'אחזקות', 'ניירות ערך']
        type_scores['portfolio_statement'] = sum(text_lower.count(term) for term in portfolio_terms)
        
        # Financial statement indicators
        financial_statement_terms = ['balance sheet', 'income statement', 'cash flow', 'מאזן', 'דוח רווח והפסד', 'תזרים מזומנים']
        type_scores['financial_statement'] = sum(text_lower.count(term) for term in financial_statement_terms)
        
        # Get the type with the highest score
        max_type = max(type_scores.items(), key=lambda x: x[1])
        
        # Only return a type if it has a minimum score
        if max_type[1] > 0:
            return max_type[0]
        else:
            return "unknown"
    
    def _extract_securities_info(self, text: str) -> List[Dict[str, Any]]:
        """Extract information about securities mentioned in text.
        
        Args:
            text: Document text
            
        Returns:
            List of dictionaries with security information
        """
        securities = []
        
        # Extract ISIN codes
        isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
        isin_matches = re.finditer(isin_pattern, text)
        
        for match in isin_matches:
            isin = match.group(0)
            
            # Look for security name near the ISIN (within 100 characters)
            context_start = max(0, match.start() - 100)
            context_end = min(len(text), match.end() + 100)
            context = text[context_start:context_end]
            
            # Try to extract security name from context
            name = self._extract_security_name(context, isin)
            
            security_info = {
                "isin": isin,
                "name": name,
                "details": self._get_isin_details(isin),
                "position": match.start()
            }
            
            # Try to extract additional information like price, quantity, etc.
            additional_info = self._extract_security_additional_info(context)
            if additional_info:
                security_info.update(additional_info)
                
            securities.append(security_info)
            
        return securities
    
    def _extract_security_name(self, context: str, isin: str) -> str:
        """Extract security name from surrounding context.
        
        Args:
            context: Text surrounding the ISIN
            isin: ISIN code to exclude from possible names
            
        Returns:
            Extracted security name or placeholder
        """
        # Remove the ISIN from the context to avoid confusion
        context_without_isin = context.replace(isin, " ")
        
        # Look for patterns that might indicate security names
        # 1. Text followed by "ISIN:" pattern
        name_pattern1 = r'([A-Za-zא-ת0-9\s\.\,\-\(\)]{3,40})\s+(?:ISIN|איסין)'
        match1 = re.search(name_pattern1, context_without_isin)
        if match1:
            return match1.group(1).strip()
            
        # 2. Text in quotation marks
        name_pattern2 = r'[""]([^""]+)[""]'
        match2 = re.search(name_pattern2, context_without_isin)
        if match2:
            return match2.group(1).strip()
            
        # 3. Text with specific formatting (e.g., bold, all caps)
        name_pattern3 = r'([A-Z\s\.]{3,40})'  # All caps text
        match3 = re.search(name_pattern3, context_without_isin)
        if match3:
            return match3.group(1).strip()
            
        # If no patterns match, look for the longest word sequence
        words = re.findall(r'[A-Za-zא-ת][A-Za-zא-ת\s\.\,\-]{2,40}', context_without_isin)
        if words:
            # Return the longest word sequence as a best guess
            return max(words, key=len).strip()
            
        return "Unknown Security"
    
    def _extract_security_additional_info(self, context: str) -> Dict[str, Any]:
        """Extract additional information about a security from surrounding context.
        
        Args:
            context: Text surrounding the security reference
            
        Returns:
            Dictionary with additional information
        """
        info = {}
        
        # Extract price if present
        price_pattern = r'(?:price|מחיר)[:\s]+([0-9,\.]+)'
        price_match = re.search(price_pattern, context, re.IGNORECASE)
        if price_match:
            try:
                price_str = price_match.group(1).replace(',', '')
                info['price'] = float(price_str)
            except (ValueError, IndexError):
                pass
                
        # Extract quantity if present
        quantity_pattern = r'(?:quantity|amount|units|shares|כמות|יחידות)[:\s]+([0-9,\.]+)'
        quantity_match = re.search(quantity_pattern, context, re.IGNORECASE)
        if quantity_match:
            try:
                quantity_str = quantity_match.group(1).replace(',', '')
                info['quantity'] = float(quantity_str)
            except (ValueError, IndexError):
                pass
                
        # Extract value if present
        value_pattern = r'(?:value|שווי|ערך)[:\s]+([0-9,\.]+)'
        value_match = re.search(value_pattern, context, re.IGNORECASE)
        if value_match:
            try:
                value_str = value_match.group(1).replace(',', '')
                info['value'] = float(value_str)
            except (ValueError, IndexError):
                pass
                
        # Extract percentage if present
        percentage_pattern = r'(?:percentage|percent|weight|אחוז|משקל)[:\s]+([0-9\.]+)%?'
        percentage_match = re.search(percentage_pattern, context, re.IGNORECASE)
        if percentage_match:
            try:
                percentage_str = percentage_match.group(1)
                info['percentage'] = float(percentage_str)
            except (ValueError, IndexError):
                pass
                
        return info