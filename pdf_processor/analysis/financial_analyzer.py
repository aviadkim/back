import pandas as pd
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
from datetime import datetime

class FinancialAnalyzer:
    """Analyze financial data extracted from documents.
    
    This class provides methods to recognize, categorize and analyze
    financial information from document text and tables.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.financial_terms = {
            'income_statement': [
                'revenue', 'sales', 'income', 'expense', 'cost of goods', 'gross profit',
                'operating income', 'ebitda', 'net income', 'earnings per share', 'eps',
                'profit', 'loss', 'margin', 'tax', 'depreciation', 'amortization'
            ],
            'balance_sheet': [
                'assets', 'liabilities', 'equity', 'cash', 'accounts receivable',
                'inventory', 'property', 'equipment', 'debt', 'loans', 'capital',
                'retained earnings', 'shares outstanding', 'book value'
            ],
            'cash_flow': [
                'cash flow', 'operating activities', 'investing activities',
                'financing activities', 'capital expenditure', 'capex', 'dividend',
                'repurchase', 'issuance', 'free cash flow', 'fcf'
            ],
            'ratios': [
                'ratio', 'return on', 'roe', 'roa', 'roi', 'eps', 'p/e', 'price to earnings',
                'debt to equity', 'current ratio', 'quick ratio', 'profit margin',
                'operating margin', 'net margin'
            ]
        }
        
    def classify_table(self, df: pd.DataFrame) -> str:
        """Classify a table based on its content.
        
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
            count = sum(1 for term in terms if term in table_text)
            scores[category] = count
            
        # Return the category with the highest score, if any terms matched
        max_category = max(scores.items(), key=lambda x: x[1])
        if max_category[1] > 0:
            return max_category[0]
        else:
            return "unknown"
            
    def extract_financial_metrics(self, text: str) -> Dict[str, Any]:
        """Extract key financial metrics from text.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dictionary of extracted financial metrics
        """
        metrics = {}
        
        # Extract currency values
        currency_pattern = r'(?:USD|€|\$|£)?\s?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s?(?:million|billion|thousand|m|b|k)?'
        currency_matches = re.findall(currency_pattern, text)
        
        if currency_matches:
            # Process all matches but limit to avoid excessive output
            metrics['currency_values'] = [self._normalize_number(match) for match in currency_matches[:10]]
        
        # Extract percentages
        percentage_pattern = r'(\d+\.?\d*)%'
        percentage_matches = re.findall(percentage_pattern, text)
        
        if percentage_matches:
            metrics['percentages'] = [float(match) for match in percentage_matches[:10]]
            
        # Extract dates (common financial report date formats)
        date_patterns = [
            r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}',
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{4}-\d{2}-\d{2}'
        ]
        
        dates = []
        for pattern in date_patterns:
            date_matches = re.findall(pattern, text)
            dates.extend(date_matches)
            
        if dates:
            metrics['dates'] = dates[:5]  # Limit to 5 dates
            
        # Extract fiscal periods
        period_pattern = r'(?:FY|Q[1-4])\s?\'?\d{2,4}'
        period_matches = re.findall(period_pattern, text)
        
        if period_matches:
            metrics['fiscal_periods'] = period_matches
            
        return metrics
        
    def analyze_financial_table(self, df: pd.DataFrame, table_type: str = None) -> Dict[str, Any]:
        """Perform analysis on a financial table.
        
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
            
        # Basic numerical analysis
        try:
            # Convert to numeric where possible
            numeric_df = df.applymap(self._try_numeric_conversion)
            
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
                
        return analysis
        
    def _normalize_number(self, value_str: str) -> float:
        """Convert string number with commas to float."""
        try:
            # Remove commas
            clean_str = value_str.replace(',', '')
            return float(clean_str)
        except ValueError:
            return 0.0
            
    def _try_numeric_conversion(self, value) -> Union[float, Any]:
        """Try to convert a value to numeric, return original if not possible."""
        if pd.isna(value):
            return np.nan
            
        if isinstance(value, (int, float)):
            return value
            
        if not isinstance(value, str):
            return value
            
        # Remove currency symbols and commas
        clean_str = re.sub(r'[,$€£%]', '', value.strip())
        
        # Handle parentheses for negative numbers (common in financial statements)
        if clean_str.startswith('(') and clean_str.endswith(')'):
            clean_str = '-' + clean_str[1:-1]
            
        # Handle suffixes like K, M, B
        multiplier = 1
        if clean_str.endswith(('K', 'k')):
            multiplier = 1000
            clean_str = clean_str[:-1]
        elif clean_str.endswith(('M', 'm')):
            multiplier = 1000000
            clean_str = clean_str[:-1]
        elif clean_str.endswith(('B', 'b')):
            multiplier = 1000000000
            clean_str = clean_str[:-1]
            
        try:
            return float(clean_str) * multiplier
        except ValueError:
            return value
            
    def _extract_time_periods(self, df: pd.DataFrame) -> List[str]:
        """Extract time periods from column headers."""
        periods = []
        
        # Common date patterns in financial tables
        date_patterns = [
            r'\d{4}',  # Year (e.g., 2023)
            r'FY\d{2,4}',  # Fiscal year (e.g., FY2023)
            r'Q[1-4]\s?\d{4}',  # Quarter (e.g., Q1 2023)
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s?\d{2,4}'  # Month Year
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
        """Analyze income statement data."""
        analysis = {}
        
        # Try to identify key rows
        key_items = {
            'revenue': ['revenue', 'sales', 'total revenue'],
            'gross_profit': ['gross profit', 'gross margin'],
            'operating_income': ['operating income', 'operating profit', 'ebit'],
            'net_income': ['net income', 'net profit', 'profit after tax', 'net earnings']
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
        """Analyze balance sheet data."""
        analysis = {}
        
        # Key balance sheet items to look for
        key_items = {
            'total_assets': ['total assets', 'assets'],
            'total_liabilities': ['total liabilities', 'liabilities'],
            'equity': ['total equity', 'shareholders equity', 'stockholders equity'],
            'cash': ['cash', 'cash and cash equivalents', 'cash & equivalents'],
            'debt': ['total debt', 'long term debt', 'short term debt']
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
        """Analyze cash flow statement data."""
        analysis = {}
        
        # Key cash flow items to look for
        key_items = {
            'operating_cash_flow': ['operating cash flow', 'cash from operations', 'net cash from operating activities'],
            'investing_cash_flow': ['investing cash flow', 'cash from investing', 'net cash from investing activities'],
            'financing_cash_flow': ['financing cash flow', 'cash from financing', 'net cash from financing activities'],
            'capex': ['capital expenditures', 'capex', 'purchases of property and equipment'],
            'free_cash_flow': ['free cash flow', 'fcf']
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
        """Analyze financial ratios table."""
        analysis = {}
        
        # Key financial ratios to look for
        key_ratios = {
            'roe': ['return on equity', 'roe'],
            'roa': ['return on assets', 'roa'],
            'current_ratio': ['current ratio'],
            'quick_ratio': ['quick ratio', 'acid test ratio'],
            'debt_to_equity': ['debt to equity', 'debt/equity'],
            'pe_ratio': ['price to earnings', 'p/e ratio', 'pe ratio'],
            'dividend_yield': ['dividend yield'],
            'profit_margin': ['profit margin', 'net margin'],
            'operating_margin': ['operating margin']
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
