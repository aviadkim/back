import unittest
from pdf_processor.analysis.financial_ratio_analyzer import FinancialRatioAnalyzer
from pdf_processor.analysis.entity_recognition import FinancialEntityRecognizer

class TestFinancialAnalysis(unittest.TestCase):
    
    def setUp(self):
        self.ratio_analyzer = FinancialRatioAnalyzer()
        self.entity_recognizer = FinancialEntityRecognizer()
        
        # Sample financial data structured as expected by the ratio analyzer
        # The 'entities' list should contain dicts with 'itemType' and 'numericValue'
        self.sample_data_for_ratios = {
            'entities': [
                {
                    'itemType': 'current assets', # Matched via synonyms
                    'numericValue': 1000000.0,
                    'itemValue': '$1,000,000' # Original value (optional)
                },
                {
                    'itemType': 'current liabilities',
                    'numericValue': 500000.0,
                    'itemValue': '500,000'
                },
                {
                    'itemType': 'inventory',
                    'numericValue': 300000.0,
                    'itemValue': '300K'
                },
                {
                    'itemType': 'total assets',
                    'numericValue': 2000000.0,
                    'itemValue': '2,000,000'
                },
                {
                    'itemType': 'total equity', # Use a synonym
                    'numericValue': 1500000.0,
                    'itemValue': '1.5M'
                },
                 {
                    'itemType': 'shareholders equity', # Explicitly add for ROE test
                    'numericValue': 1500000.0,
                    'itemValue': '1.5M'
                },
                {
                    'itemType': 'net income',
                    'numericValue': 250000.0,
                    'itemValue': '250,000'
                },
                {
                    'itemType': 'revenue',
                    'numericValue': 1500000.0,
                    'itemValue': '1,500,000'
                },
                 { # Add a debt value for debt_to_equity test
                    'itemType': 'total debt',
                    'numericValue': 750000.0,
                    'itemValue': '750K'
                }
            ]
            # 'tables' data could be added here if table extraction logic is used by ratio analyzer
        }
    
    def test_ratio_calculation(self):
        """Test that financial ratios are calculated correctly."""
        # Calculate ratios using the sample data
        ratios = self.ratio_analyzer.calculate_ratios(self.sample_data_for_ratios)
        
        # Check that we have the expected ratios calculated
        self.assertIn('current_ratio', ratios, "Current Ratio missing")
        self.assertIn('quick_ratio', ratios, "Quick Ratio missing")
        self.assertIn('debt_to_equity', ratios, "Debt to Equity missing")
        self.assertIn('return_on_equity', ratios, "Return on Equity missing")
        self.assertIn('return_on_assets', ratios, "Return on Assets missing")
        self.assertIn('profit_margin', ratios, "Profit Margin missing")
        self.assertIn('asset_turnover', ratios, "Asset Turnover missing")
        
        # Check specific ratio values (using assertAlmostEqual for float comparisons)
        self.assertAlmostEqual(ratios['current_ratio']['value'], 2.0, places=4)  # 1000000 / 500000
        self.assertAlmostEqual(ratios['quick_ratio']['value'], 1.4, places=4)    # (1000000 - 300000) / 500000
        self.assertAlmostEqual(ratios['debt_to_equity']['value'], 0.5, places=4) # 750000 / 1500000
        self.assertAlmostEqual(ratios['return_on_equity']['value'], 0.1667, places=4) # 250000 / 1500000
        self.assertAlmostEqual(ratios['return_on_assets']['value'], 0.125, places=4)  # 250000 / 2000000
        self.assertAlmostEqual(ratios['profit_margin']['value'], 0.1667, places=4)  # 250000 / 1500000
        self.assertAlmostEqual(ratios['asset_turnover']['value'], 0.75, places=4) # 1500000 / 2000000

        # Test interpretation generation (optional)
        self.assertIn('interpretation', ratios['current_ratio'])
        self.assertIn('interpretation', ratios['quick_ratio'])
        self.assertIn('interpretation', ratios['debt_to_equity'])

    def test_entity_recognition(self):
        """Test financial entity recognition."""
        # Sample text with financial entities
        text = """
        The company reported revenue of $1,500,000 for the fiscal year ending 31/12/2023.
        Net profit margin increased to 16.7% from 15.2% in the previous year.
        The balance sheet shows total assets of $2,000,000 and current assets of $1,000,000.
        The inventory value is $300,000 and current liabilities stand at $500,000.
        The ISIN number for the company's stock is US0378331005.
        רווח נקי היה ₪250K.
        """
        
        # Extract entities
        entities = self.entity_recognizer.extract_entities(text)
        
        # Check that we extracted the expected entities (using sets for easier comparison)
        self.assertIn('US0378331005', set(entities.get('isin_numbers', [])))
        # Note: Currency regex might capture slightly differently, adjust assertion as needed
        self.assertTrue(any('1500000' in amount for amount in entities.get('currency_amounts', [])))
        self.assertTrue(any('250K' in amount for amount in entities.get('currency_amounts', []))) # Check Hebrew currency
        self.assertIn('16.7%', set(entities.get('percentages', [])))
        self.assertIn('15.2%', set(entities.get('percentages', [])))
        self.assertIn('31/12/2023', set(entities.get('dates', [])))
        self.assertIn('revenue', set(entities.get('financial_terms', [])))
        self.assertIn('net profit', set(entities.get('financial_terms', []))) # Check if 'net profit' is extracted
        self.assertIn('total assets', set(entities.get('financial_terms', [])))
        self.assertIn('current assets', set(entities.get('financial_terms', [])))
        self.assertIn('inventory', set(entities.get('financial_terms', [])))
        self.assertIn('current liabilities', set(entities.get('financial_terms', [])))
        self.assertIn('רווח נקי', set(entities.get('financial_terms', []))) # Check Hebrew term

    def test_isin_validation(self):
        """Test ISIN validation logic."""
        valid_isin = "US0378331005"  # Apple Inc.
        invalid_isin_checksum = "US0378331006" # Incorrect checksum
        invalid_isin_format = "US1234567890" # Incorrect format
        
        self.assertTrue(self.entity_recognizer.validate_isin(valid_isin), "Valid ISIN failed validation")
        self.assertFalse(self.entity_recognizer.validate_isin(invalid_isin_checksum), "Invalid ISIN (checksum) passed validation")
        self.assertFalse(self.entity_recognizer.validate_isin(invalid_isin_format), "Invalid ISIN (format) passed validation")
        self.assertFalse(self.entity_recognizer.validate_isin(""), "Empty string passed ISIN validation")
        self.assertFalse(self.entity_recognizer.validate_isin(None), "None passed ISIN validation")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False) # Add args for running in some environments
