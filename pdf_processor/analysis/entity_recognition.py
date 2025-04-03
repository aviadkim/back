import re
import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class FinancialEntityRecognizer:
    """Recognize and extract financial entities from text."""
    
    def __init__(self):
        """Initialize the financial entity recognizer."""
        # Regex patterns for various financial entities
        # Improved currency regex to handle symbols before/after and spaces
        self.patterns = {
            'isin': r'[A-Z]{2}[A-Z0-9]{9}[0-9]',  # International Securities Identification Number
            'currency_amount': r'(?:[\$€£₪]\s?|\s?[\$€£₪])(\d{1,3}(?:[,.]\d{3})*(?:[.,]\d+)?)\s?(K|M|B|T)?', # Currency amounts with symbols and optional scale (K, M, B, T)
            'percentage': r'(\d+\.?\d*)\s?%',  # Percentage values
            'date': r'\b(0?[1-9]|[12][0-9]|3[01])[./-](0?[1-9]|1[012])[./-]((?:19|20)\d\d)\b',  # Dates in DD/MM/YYYY format with word boundaries
        }
        
        # Common financial terms (lowercase for case-insensitive matching)
        self.financial_terms = {
            'income_statement': [
                'revenue', 'sales', 'income', 'expense', 'cost of goods', 'gross profit',
                'operating income', 'ebitda', 'net income', 'earnings per share', 'eps'
            ],
            'balance_sheet': [
                'assets', 'liabilities', 'equity', 'cash', 'accounts receivable',
                'inventory', 'property', 'equipment', 'debt', 'loans', 'capital'
            ],
            'cash_flow': [
                'cash flow', 'operating activities', 'investing activities',
                'financing activities', 'capital expenditure', 'capex', 'dividend'
            ]
        }
        
        # Hebrew financial terms
        self.hebrew_financial_terms = {
            'income_statement': [
                'הכנסות', 'מכירות', 'רווח', 'הוצאות', 'עלות המכר', 'רווח גולמי',
                'רווח תפעולי', 'רווח נקי', 'רווח למניה'
            ],
            'balance_sheet': [
                'נכסים', 'התחייבויות', 'הון עצמי', 'מזומנים', 'לקוחות',
                'מלאי', 'רכוש קבוע', 'ציוד', 'חוב', 'הלוואות', 'הון'
            ],
            'cash_flow': [
                'תזרים מזומנים', 'פעילות שוטפת', 'פעילות השקעה',
                'פעילות מימון', 'השקעות הוניות', 'דיבידנד'
            ]
        }
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialized FinancialEntityRecognizer")
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract financial entities from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary of entity types and their instances
        """
        entities = {
            'isin_numbers': [],
            'currency_amounts': [],
            'percentages': [],
            'dates': [],
            'financial_terms': []
        }
        
        if not text:
            self.logger.warning("Received empty text for entity extraction.")
            return entities
        
        # Extract ISIN numbers and validate them
        isin_matches = re.findall(self.patterns['isin'], text)
        entities['isin_numbers'] = [isin for isin in isin_matches if self.validate_isin(isin)]
        
        # Extract currency amounts
        # The regex now captures the number and optional scale (K/M/B/T)
        currency_matches = re.findall(self.patterns['currency_amount'], text)
        # Reconstruct the full amount string including symbol (which is not captured)
        # This requires finding the match position and checking nearby characters, 
        # or adjusting regex to capture symbol. For simplicity, just return number part.
        entities['currency_amounts'] = [f"{m[0]}{m[1]}" for m in currency_matches] # Combine number and scale
        
        # Extract percentages
        percentage_matches = re.findall(self.patterns['percentage'], text)
        entities['percentages'] = [f"{m}%" for m in percentage_matches]
        
        # Extract dates
        date_matches = re.findall(self.patterns['date'], text)
        # Format date consistently (e.g., DD/MM/YYYY)
        entities['dates'] = [f"{m[0].zfill(2)}/{m[1].zfill(2)}/{m[2]}" for m in date_matches]
        
        # Extract financial terms (case-insensitive for English)
        entities['financial_terms'] = self._extract_financial_terms(text)
        
        # Remove duplicates from lists
        for key in entities:
            entities[key] = list(set(entities[key]))

        self.logger.info(f"Extracted {sum(len(v) for v in entities.values())} unique entities from text")
        return entities
    
    def _extract_financial_terms(self, text: str) -> List[str]:
        """Extract financial terms from text (case-insensitive for English).
        
        Args:
            text: Input text
            
        Returns:
            List of unique financial terms found
        """
        found_terms = set() # Use a set to store unique terms
        
        # Check for English terms (case-insensitive)
        lower_text = text.lower()
        for category, terms in self.financial_terms.items():
            for term in terms:
                # Use word boundaries to avoid partial matches (e.g., 'asset' in 'assets')
                if re.search(r'\b' + re.escape(term) + r'\b', lower_text):
                    found_terms.add(term)
        
        # Check for Hebrew terms (case-sensitive, as Hebrew doesn't have case)
        for category, terms in self.hebrew_financial_terms.items():
            for term in terms:
                 # Use word boundaries if applicable for Hebrew (might need adjustment)
                 # For simplicity, using basic substring check for now
                if term in text:
                    found_terms.add(term)
        
        return list(found_terms)
    
    def validate_isin(self, isin: str) -> bool:
        """Validate an ISIN number using the Luhn algorithm adaptation.
        
        Args:
            isin: ISIN number to validate
            
        Returns:
            Boolean indicating if ISIN is valid
        """
        if not isin or not re.match(self.patterns['isin'], isin):
            return False
            
        # Convert letters to numbers (A=10, B=11, ..., Z=35) and concatenate
        num_str = ""
        for char in isin:
            if char.isdigit():
                num_str += char
            elif char.isalpha():
                num_str += str(ord(char.upper()) - ord('A') + 10)
            else:
                 return False # Invalid character

        # Luhn algorithm application
        n_digits = len(num_str)
        n_sum = 0
        is_second = False
        for i in range(n_digits - 1, -1, -1):
            d = int(num_str[i])
            if is_second:
                d = d * 2
            # We add the digits of d // 10 and d % 10
            n_sum += d // 10
            n_sum += d % 10
            is_second = not is_second
            
        # Number is valid if the sum modulo 10 is 0
        return n_sum % 10 == 0

# Example Usage (optional, for testing)
if __name__ == '__main__':
    recognizer = FinancialEntityRecognizer()
    sample_text = """
    Apple Inc. (ISIN: US0378331005) reported revenue of $100B. 
    Tesla (ISIN: US88160R1014) had a net income of 5.5M Euros (€5,500,000).
    Date: 31/12/2023. Growth was 15.5%. 
    החברה דיווחה על רווח נקי של ₪200K. נכסים כוללים מזומנים.
    Invalid ISIN: US0378331006.
    """
    
    entities = recognizer.extract_entities(sample_text)
    print("Extracted Entities:")
    for entity_type, instances in entities.items():
        print(f"  {entity_type}: {instances}")

    print("\nISIN Validation:")
    print(f"US0378331005 valid? {recognizer.validate_isin('US0378331005')}")
    print(f"US88160R1014 valid? {recognizer.validate_isin('US88160R1014')}")
    print(f"US0378331006 valid? {recognizer.validate_isin('US0378331006')}") # Should be False