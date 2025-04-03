import re
import logging
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import requests
from pathlib import Path
import json
import os

logger = logging.getLogger(__name__)

class ISINDetector:
    """
    Class for detecting and validating International Securities Identification Numbers (ISIN)
    in financial documents.
    """

    def __init__(self, isin_db_path: Optional[str] = None):
        """
        Initialize the ISIN detector.

        Args:
            isin_db_path: Path to a JSON file containing known ISIN mappings
        """
        self.logger = logging.getLogger(__name__)
        self.isin_db = {}

        # Load ISIN database if provided
        if isin_db_path and os.path.exists(isin_db_path):
            try:
                with open(isin_db_path, 'r', encoding='utf-8') as f:
                    self.isin_db = json.load(f)
                self.logger.info(f"Loaded {len(self.isin_db)} ISIN records from database")
            except Exception as e:
                self.logger.error(f"Failed to load ISIN database: {str(e)}")

        # Regular expression for ISIN detection
        # Format: 2 letters (country code) + 9 alphanumeric + 1 check digit
        self.isin_pattern = r'\b([A-Z]{2})([A-Z0-9]{9})([0-9])\b'

        # Common prefixes that might appear before ISIN codes
        self.isin_prefixes = [
            'ISIN', 'isin', 'מספר ISIN', 'מס\' ISIN', 'מס ISIN',
            'International Securities Identification Number',
            'קוד בינלאומי', 'סימול בינלאומי'
        ]

    def detect_isin_numbers(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect ISIN numbers in the given text.

        Args:
            text: Text content to analyze

        Returns:
            List of dictionaries with ISIN codes and metadata
        """
        isin_codes = []

        # First look for ISIN with prefixes (higher confidence)
        for prefix in self.isin_prefixes:
            # Look for pattern: prefix followed by ISIN within reasonable distance
            prefix_pattern = fr'{re.escape(prefix)}[:\s]*([A-Z]{{2}}[A-Z0-9]{{9}}[0-9])'
            matches = re.finditer(prefix_pattern, text, re.IGNORECASE)

            for match in matches:
                isin_code = match.group(1)
                if self._validate_isin(isin_code):
                    description = self._get_isin_description(isin_code, text)
                    isin_codes.append({
                        'code': isin_code,
                        'description': description,
                        'confidence': 'high',
                        'context': text[max(0, match.start() - 50):min(len(text), match.end() + 50)]
                    })

        # Then look for standalone ISIN patterns (lower confidence)
        all_matches = re.finditer(self.isin_pattern, text)

        for match in all_matches:
            isin_code = match.group(0)

            # Skip if already found with prefix
            if any(isin['code'] == isin_code for isin in isin_codes):
                continue

            if self._validate_isin(isin_code):
                description = self._get_isin_description(isin_code, text)
                isin_codes.append({
                    'code': isin_code,
                    'description': description,
                    'confidence': 'medium',
                    'context': text[max(0, match.start() - 50):min(len(text), match.end() + 50)]
                })

        return isin_codes

    def detect_isin_in_table(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect ISIN numbers in a pandas DataFrame (e.g., from extracted table).

        Args:
            df: DataFrame to analyze

        Returns:
            List of dictionaries with ISIN codes and metadata
        """
        isin_codes = []

        # Convert DataFrame to string for analysis
        table_str = df.to_string()

        # Find all potential ISIN matches
        matches = re.finditer(self.isin_pattern, table_str)

        for match in matches:
            isin_code = match.group(0)
            if self._validate_isin(isin_code):
                # Try to find the corresponding row
                row_data = self._find_row_with_isin(df, isin_code)

                description = ''
                if row_data:
                    # Try to get description from the same row
                    description = self._extract_description_from_row(row_data)

                isin_codes.append({
                    'code': isin_code,
                    'description': description,
                    'confidence': 'high' if row_data else 'medium',
                    'table_data': row_data if row_data else {}
                })

        return isin_codes

    def _validate_isin(self, isin_code: str) -> bool:
        """
        Validate an ISIN code using the Luhn algorithm.

        Args:
            isin_code: ISIN code to validate

        Returns:
            Boolean indicating if the ISIN is valid
        """
        if not re.match(r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$', isin_code):
            return False

        # Convert letters to numbers according to ISIN rules
        # A=10, B=11, ..., Z=35
        chars = []
        for char in isin_code[:-1]:  # Exclude check digit
            if 'A' <= char <= 'Z':
                chars.append(str(ord(char) - ord('A') + 10))
            else:
                chars.append(char)

        # Join the characters
        digits = ''.join(chars)

        # Apply Luhn algorithm
        total = 0
        for i, digit in enumerate(reversed(digits)):
            value = int(digit)
            if i % 2 == 0:  # Even positions (from right)
                value *= 2
                if value > 9:
                    value -= 9
            total += value

        check_digit = (10 - (total % 10)) % 10

        return check_digit == int(isin_code[-1])

    def _get_isin_description(self, isin_code: str, context: str) -> str:
        """
        Try to get a description for an ISIN code.

        Args:
            isin_code: ISIN code
            context: Surrounding text context

        Returns:
            Description string if found, empty string otherwise
        """
        # First check our local database
        if isin_code in self.isin_db:
            return self.isin_db[isin_code].get('description', '')

        # Try to extract from context
        description = self._extract_description_from_context(isin_code, context)
        if description:
            return description

        return ''

    def _extract_description_from_context(self, isin_code: str, context: str) -> str:
        """
        Extract a description for an ISIN code from surrounding text.

        Args:
            isin_code: ISIN code
            context: Surrounding text context

        Returns:
            Description string if found, empty string otherwise
        """
        # Look for description patterns in Hebrew and English
        patterns = [
            # Format: ISIN code followed by description
            fr'{re.escape(isin_code)}\s*[-–]\s*([^,.;()\n]+)',
            fr'{re.escape(isin_code)}\s*[-–:]\s*([^,.;()\n]+)',
            # Format: Description followed by ISIN code
            fr'([^,.;()\n]{5,50})\s*[-–:]\s*{re.escape(isin_code)}',
            fr'([^,.;()\n]{5,50})\s*\({re.escape(isin_code)}\)',
        ]

        for pattern in patterns:
            match = re.search(pattern, context)
            if match:
                description = match.group(1).strip()
                if 5 <= len(description) <= 100:  # Reasonable length for a security name
                    return description

        return ''

    def _find_row_with_isin(self, df: pd.DataFrame, isin_code: str) -> Dict[str, Any]:
        """
        Find the row in a DataFrame that contains the given ISIN code.

        Args:
            df: DataFrame to search
            isin_code: ISIN code to look for

        Returns:
            Dictionary with row data, or empty dict if not found
        """
        # Convert DataFrame to string representation for each cell
        str_df = df.astype(str)

        for i, row in str_df.iterrows():
            for col, val in row.items():
                if isin_code in val:
                    # Return full row as dictionary
                    return df.iloc[i].to_dict()

        return {}

    def _extract_description_from_row(self, row_data: Dict[str, Any]) -> str:
        """
        Extract a security description from a table row.

        Args:
            row_data: Dictionary containing row data

        Returns:
            Description string if found, empty string otherwise
        """
        # Common column names that might contain security descriptions
        description_columns = [
            'name', 'description', 'security', 'security name', 'instrument',
            'שם', 'תיאור', 'שם נייר', 'נייר ערך', 'מכשיר', 'תיאור נייר'
        ]

        # Check each potential description column
        for col in description_columns:
            for key in row_data.keys():
                if col.lower() in str(key).lower():
                    value = str(row_data[key]).strip()
                    if value and len(value) >= 3:
                        return value

        # If no specific column found, look for the longest string value
        # that isn't an ISIN code
        candidate = ''
        for value in row_data.values():
            value_str = str(value).strip()
            if (len(value_str) > len(candidate) and
                len(value_str) >= 3 and
                len(value_str) <= 100 and
                not re.match(r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$', value_str)):
                candidate = value_str

        return candidate

    def update_isin_database(self, isin_code: str, metadata: Dict[str, Any],
                           save_to_file: bool = True) -> None:
        """
        Update the local ISIN database with new information.

        Args:
            isin_code: ISIN code to update
            metadata: Dictionary with metadata about the ISIN
            save_to_file: Whether to save the updated database to file
        """
        if isin_code not in self.isin_db:
            self.isin_db[isin_code] = {}

        # Update with new metadata
        self.isin_db[isin_code].update(metadata)

        # Save to file if requested
        if save_to_file and hasattr(self, 'isin_db_path') and self.isin_db_path:
            try:
                with open(self.isin_db_path, 'w', encoding='utf-8') as f:
                    json.dump(self.isin_db, f, ensure_ascii=False, indent=2)
                self.logger.info(f"Updated ISIN database saved to {self.isin_db_path}")
            except Exception as e:
                self.logger.error(f"Failed to save ISIN database: {str(e)}")