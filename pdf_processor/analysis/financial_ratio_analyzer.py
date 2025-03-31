import re
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class FinancialRatioAnalyzer:
    """Analyze financial ratios from extracted data."""
    
    def __init__(self):
        """Initialize the financial ratio analyzer."""
        # Define common financial ratios and their components
        self.ratio_definitions = {
            'current_ratio': {
                'formula': 'current_assets / current_liabilities',
                'description': 'Measures the ability to pay short-term obligations',
                'ideal_range': '1.5 to 3.0'
            },
            'quick_ratio': {
                'formula': '(current_assets - inventory) / current_liabilities',
                'description': 'Measures the ability to pay short-term obligations without selling inventory',
                'ideal_range': '1.0 or higher'
            },
            'debt_to_equity': {
                'formula': 'total_debt / total_equity',
                'description': 'Measures financial leverage',
                'ideal_range': 'Below 2.0'
            },
            'return_on_equity': {
                'formula': 'net_income / shareholders_equity',
                'description': 'Measures profitability relative to shareholders\' investment',
                'ideal_range': '15-20%'
            },
            'return_on_assets': {
                'formula': 'net_income / total_assets',
                'description': 'Measures how efficiently assets are used to generate earnings',
                'ideal_range': '5% or higher'
            },
            'profit_margin': {
                'formula': 'net_income / revenue',
                'description': 'Percentage of revenue that represents profit',
                'ideal_range': 'Varies by industry'
            },
            'asset_turnover': {
                'formula': 'revenue / total_assets',
                'description': 'Measures efficiency of asset utilization',
                'ideal_range': 'Varies by industry'
            }
        }
        
        # Define alternative names for financial metrics (lowercase)
        self.metric_synonyms = {
            'current_assets': ['current assets', 'total current assets', 'נכסים שוטפים'],
            'current_liabilities': ['current liabilities', 'total current liabilities', 'התחייבויות שוטפות'],
            'inventory': ['inventory', 'inventories', 'מלאי'],
            'total_debt': ['total debt', 'long term debt', 'short term debt', 'סך חוב', 'חוב לזמן ארוך', 'חוב לזמן קצר', 'total liabilities', 'liabilities', 'התחייבויות'], # Added liabilities as synonym for debt
            'total_equity': ['total equity', 'shareholders equity', 'stockholders equity', 'equity', 'הון עצמי', 'סך הון'],
            'net_income': ['net income', 'net profit', 'profit after tax', 'רווח נקי', 'רווח לאחר מס'],
            'revenue': ['revenue', 'sales', 'total revenue', 'הכנסות', 'מכירות'],
            'total_assets': ['total assets', 'assets', 'סך נכסים', 'נכסים'],
            'shareholders_equity': ['shareholders equity', 'stockholders equity', 'equity', 'הון עצמי'] # Same as total_equity
        }
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialized FinancialRatioAnalyzer")
    
    def calculate_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Calculate financial ratios from extracted data.
        
        Args:
            financial_data: Dictionary containing extracted 'entities' and potentially 'tables'.
                            Expected entities format: List of dicts with 'itemType', 'numericValue'.
            
        Returns:
            Dictionary of calculated ratios with their values and metadata
        """
        # Extract numeric values from the financial data (primarily entities for now)
        metrics = self._extract_metrics(financial_data)
        self.logger.debug(f"Extracted metrics for ratio calculation: {metrics}")
        
        # Calculate ratios
        ratios = {}
        
        for ratio_name, ratio_info in self.ratio_definitions.items():
            try:
                # Try to calculate the ratio using extracted metrics
                ratio_value = self._calculate_ratio(ratio_name, metrics)
                
                if ratio_value is not None:
                    # Create ratio entry with value and metadata
                    ratios[ratio_name] = {
                        'value': round(ratio_value, 4), # Round for consistency
                        'formula': ratio_info['formula'],
                        'description': ratio_info['description'],
                        'ideal_range': ratio_info['ideal_range']
                    }
                    
                    # Add interpretation if applicable
                    interpretation = self._interpret_ratio(ratio_name, ratio_value)
                    if interpretation:
                        ratios[ratio_name]['interpretation'] = interpretation
                else:
                     self.logger.debug(f"Could not calculate ratio '{ratio_name}' due to missing metrics.")

            except Exception as e:
                self.logger.warning(f"Error calculating {ratio_name}: {str(e)}")
        
        self.logger.info(f"Calculated {len(ratios)} financial ratios")
        return ratios
    
    def _extract_metrics(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract numeric metrics primarily from financial entities.
           Placeholder for future extraction from tables.
        
        Args:
            financial_data: Dictionary containing financial information, expects 'entities' key.
            
        Returns:
            Dictionary of metric names and their numeric values
        """
        metrics = {}
        
        # Extract from financial entities first (as provided by Entity Recognizer)
        if 'entities' in financial_data and isinstance(financial_data['entities'], list):
             self._extract_from_entities(financial_data['entities'], metrics)
        else:
             self.logger.warning("No 'entities' list found in financial_data for metric extraction.")


        # Placeholder: Add logic here later to extract/refine metrics from 'tables' if needed
        # For example, identify balance sheet/income statement tables and extract totals.
        # if 'tables' in financial_data:
        #     # ... logic to parse tables and extract/confirm metrics ...
        #     pass

        # Ensure required metrics have numeric values
        for key in metrics:
             if not isinstance(metrics[key], (int, float)):
                  try:
                       metrics[key] = float(metrics[key])
                  except (ValueError, TypeError):
                       self.logger.warning(f"Could not convert metric '{key}' value '{metrics[key]}' to float.")
                       # Decide whether to remove the metric or keep it as is
                       # For ratio calculation, non-numeric values will cause issues.
                       # Let's remove them for now.
                       del metrics[key]


        return metrics
    
    # Removed _extract_from_income_statement, _extract_from_balance_sheet, _extract_from_cash_flow
    # as the current logic primarily uses entities. These can be added back if table analysis is implemented.

    def _extract_from_entities(self, entities: List[Dict[str, Any]], metrics: Dict[str, float]):
        """Extract metrics from financial entities list.
        
        Args:
            entities: List of financial entities (dicts with 'itemType', 'numericValue', 'itemValue').
            metrics: Dictionary to populate with metrics.
        """
        self.logger.debug(f"Extracting metrics from {len(entities)} entities.")
        # Prioritize entities with numericValue
        for entity in entities:
            item_type = entity.get('itemType', '').lower()
            numeric_value = entity.get('numericValue')
            item_value_str = entity.get('itemValue', '') # Original string value

            if numeric_value is None:
                 # Attempt to parse numeric value from itemValue_str if numericValue is missing
                 if item_value_str:
                      parsed_value = self._parse_numeric_value(item_value_str)
                      if parsed_value is not None:
                           numeric_value = parsed_value
                      else:
                           continue # Skip if no numeric value can be obtained
                 else:
                      continue # Skip if no numeric value and no string value

            # Try to match entity type with known metrics based on synonyms
            for metric_name, synonyms in self.metric_synonyms.items():
                # Check if any synonym is present in the itemType
                # Use word boundaries for more precise matching if needed
                if any(synonym in item_type for synonym in synonyms):
                    # Assign the value. Overwrite if already present (last one wins, or add logic for confidence/priority)
                    try:
                         metrics[metric_name] = float(numeric_value)
                         self.logger.debug(f"Mapped entity '{item_type}' to metric '{metric_name}' with value {numeric_value}")
                         break # Stop checking synonyms for this entity once matched
                    except (ValueError, TypeError):
                         self.logger.warning(f"Could not convert numericValue '{numeric_value}' for entity '{item_type}' to float.")
                         break # Stop checking synonyms if value is invalid

    def _parse_numeric_value(self, value_str: str) -> Optional[float]:
        """Attempt to parse a numeric value from a string, handling K, M, B."""
        if not isinstance(value_str, str):
            return None
        
        value_str = value_str.strip()
        # Remove currency symbols and commas
        cleaned_str = re.sub(r'[$,€£₪,]', '', value_str)
        
        multiplier = 1.0
        if cleaned_str.endswith('K'):
            multiplier = 1_000.0
            cleaned_str = cleaned_str[:-1]
        elif cleaned_str.endswith('M'):
            multiplier = 1_000_000.0
            cleaned_str = cleaned_str[:-1]
        elif cleaned_str.endswith('B'):
            multiplier = 1_000_000_000.0
            cleaned_str = cleaned_str[:-1]
            
        try:
            return float(cleaned_str) * multiplier
        except ValueError:
            return None

    def _calculate_ratio(self, ratio_name: str, metrics: Dict[str, float]) -> Optional[float]:
        """Calculate a specific financial ratio. Handles missing keys and division by zero."""
        try:
            if ratio_name == 'current_ratio':
                num = metrics.get('current_assets')
                den = metrics.get('current_liabilities')
                if num is not None and den is not None and den != 0:
                    return num / den
            
            elif ratio_name == 'quick_ratio':
                ca = metrics.get('current_assets')
                inv = metrics.get('inventory', 0.0) # Default inventory to 0 if not found
                cl = metrics.get('current_liabilities')
                if ca is not None and cl is not None and cl != 0:
                    return (ca - inv) / cl
            
            elif ratio_name == 'debt_to_equity':
                debt = metrics.get('total_debt')
                equity = metrics.get('total_equity')
                # Try shareholders_equity if total_equity is missing
                if equity is None:
                     equity = metrics.get('shareholders_equity')
                if debt is not None and equity is not None and equity != 0:
                    return debt / equity
            
            elif ratio_name == 'return_on_equity':
                ni = metrics.get('net_income')
                equity = metrics.get('shareholders_equity')
                 # Try total_equity if shareholders_equity is missing
                if equity is None:
                     equity = metrics.get('total_equity')
                if ni is not None and equity is not None and equity != 0:
                    return ni / equity
            
            elif ratio_name == 'return_on_assets':
                ni = metrics.get('net_income')
                assets = metrics.get('total_assets')
                if ni is not None and assets is not None and assets != 0:
                    return ni / assets
            
            elif ratio_name == 'profit_margin':
                ni = metrics.get('net_income')
                rev = metrics.get('revenue')
                if ni is not None and rev is not None and rev != 0:
                    return ni / rev
            
            elif ratio_name == 'asset_turnover':
                rev = metrics.get('revenue')
                assets = metrics.get('total_assets')
                if rev is not None and assets is not None and assets != 0:
                    return rev / assets
            
            return None # Ratio definition not found or calculation failed
        except ZeroDivisionError:
             self.logger.warning(f"Division by zero encountered while calculating {ratio_name}.")
             return None
        except Exception as e:
            self.logger.error(f"Unexpected error calculating {ratio_name}: {str(e)}")
            return None
    
    def _interpret_ratio(self, ratio_name: str, ratio_value: float) -> Optional[str]:
        """Provide interpretation for a calculated ratio."""
        # Ensure ratio_value is a float for comparison
        if not isinstance(ratio_value, (int, float)):
             return "Invalid ratio value for interpretation."

        if ratio_name == 'current_ratio':
            if ratio_value < 1:
                return "Low liquidity: Potential difficulty meeting short-term obligations."
            elif 1 <= ratio_value < 1.5:
                return "Acceptable liquidity, but could be stronger."
            elif 1.5 <= ratio_value <= 3:
                return "Good liquidity: Strong ability to cover short-term liabilities."
            else: # ratio_value > 3
                return "High liquidity: May indicate inefficient use of assets."
        
        elif ratio_name == 'quick_ratio':
            if ratio_value < 1:
                return "Low immediate liquidity: Relies on inventory sales to meet short-term debts."
            else: # ratio_value >= 1
                return "Good immediate liquidity: Can meet short-term obligations without selling inventory."
        
        elif ratio_name == 'debt_to_equity':
            if ratio_value < 0.5:
                return "Low leverage: Primarily financed by equity, lower financial risk."
            elif 0.5 <= ratio_value < 1.5: # Adjusted range slightly
                return "Moderate leverage: Balanced use of debt and equity."
            elif 1.5 <= ratio_value < 2.5: # Adjusted range slightly
                 return "High leverage: Relies significantly on debt, higher financial risk."
            else: # ratio_value >= 2.5
                 return "Very high leverage: Aggressively financed by debt, potentially very high risk."

        elif ratio_name == 'return_on_equity':
            # ROE interpretation is highly context-dependent (industry, growth stage)
            # Providing general guidelines
            if ratio_value < 0.05:
                 return "Low profitability relative to shareholder equity."
            elif 0.05 <= ratio_value < 0.15:
                 return "Moderate profitability relative to shareholder equity."
            elif 0.15 <= ratio_value < 0.25:
                 return "Good profitability relative to shareholder equity."
            else: # ratio_value >= 0.25
                 return "High profitability relative to shareholder equity."

        elif ratio_name == 'return_on_assets':
             if ratio_value < 0.02:
                  return "Low efficiency in using assets to generate profit."
             elif 0.02 <= ratio_value < 0.05:
                  return "Moderate efficiency in using assets to generate profit."
             else: # ratio_value >= 0.05
                  return "Good efficiency in using assets to generate profit."

        elif ratio_name == 'profit_margin':
            # Profit margin interpretation is highly industry-specific
            if ratio_value < 0.05:
                return "Low profit margin: A small percentage of revenue translates to profit."
            elif 0.05 <= ratio_value < 0.15:
                return "Average profit margin."
            else: # ratio_value >= 0.15
                return "High profit margin: A significant percentage of revenue is retained as profit."
        
        # Add interpretations for other ratios like asset_turnover if needed
        
        return None # No specific interpretation defined for this ratio