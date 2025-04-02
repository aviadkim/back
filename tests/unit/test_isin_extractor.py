import pytest
import sys
import os
import re

# Import the correct function name
from financial_data_extractor import extract_isin_numbers

class TestISINExtractor:
    def test_extract_valid_isins(self):
        """Test that valid ISINs are correctly extracted"""
        text = """
        The portfolio contains following securities: CH1908490000, XS2530201644, 
        XS2692298537, and US0378331005 (Apple Inc.).
        """
        result = extract_isin_numbers(text)
        assert len(result) >= 3
        assert "CH1908490000" in result
        assert "XS2530201644" in result
        assert "US0378331005" in result
    
    def test_extract_isins_from_empty_text(self):
        """Test extraction from empty text"""
        assert extract_isin_numbers("") == []
    
    def test_extract_isins_with_noise(self):
        """Test ISIN extraction with surrounding noise"""
        text = """
        The ISIN number CH1908490000 appears within text.
        Sometimes they appear with a prefix: ISIN: XS2530201644
        Or with a suffix: US0378331005 (Apple Inc.)
        """
        result = extract_isin_numbers(text)
        assert len(result) >= 3
        assert "CH1908490000" in result
        assert "XS2530201644" in result
        assert "US0378331005" in result
