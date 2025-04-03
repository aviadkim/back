import re
import unicodedata
import logging

logger = logging.getLogger(__name__)

class HebrewHandler:
    """Handler for Hebrew language text processing."""

    def __init__(self):
        """Initialize the Hebrew handler."""
        # Hebrew characters range
        self.hebrew_chars = set('אבגדהוזחטיכלמנסעפצקרשת')
        # Hebrew diacritics (nikud)
        self.hebrew_diacritics = set([
            '\u05B0', '\u05B1', '\u05B2', '\u05B3', '\u05B4', '\u05B5',
            '\u05B6', '\u05B7', '\u05B8', '\u05B9', '\u05BB', '\u05BC',
            '\u05BD', '\u05BF', '\u05C1', '\u05C2'
        ])
        # Common Hebrew financial terms
        self.financial_terms = {
            'balance_sheet': [
                'מאזן', 'נכסים', 'התחייבויות', 'הון עצמי', 'רכוש קבוע',
                'רכוש שוטף', 'מזומנים', 'השקעות', 'חייבים', 'מלאי'
            ],
            'income_statement': [
                'רווח והפסד', 'הכנסות', 'הוצאות', 'רווח תפעולי', 'רווח נקי',
                'עלות המכר', 'הוצאות מכירה', 'הוצאות הנהלה', 'מס הכנסה'
            ],
            'cash_flow': [
                'תזרים מזומנים', 'פעילות שוטפת', 'פעילות השקעה', 'פעילות מימון',
                'דיבידנד', 'ריבית'
            ],
            'securities': [
                'ניירות ערך', 'מניות', 'אגרות חוב', 'קרנות', 'תעודות סל',
                'נאסד"ק', 'תל אביב', 'דאו ג\'ונס', 'יורו', 'דולר'
            ]
        }

    def is_hebrew_text(self, text):
        """Check if text is primarily in Hebrew.

        Args:
            text: Text to check

        Returns:
            Boolean indicating if text is primarily Hebrew
        """
        if not text:
            return False

        # Count Hebrew and non-Hebrew characters
        hebrew_count = 0
        other_count = 0

        for char in text:
            if char in self.hebrew_chars:
                hebrew_count += 1
            elif not char.isspace() and char not in self.hebrew_diacritics:
                other_count += 1

        # Text is considered Hebrew if at least 30% of characters are Hebrew
        return hebrew_count > 0 and hebrew_count / (hebrew_count + other_count) >= 0.3

    def normalize_hebrew(self, text):
        """Normalize Hebrew text.

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        if not text:
            return text

        # Remove diacritics (nikud)
        normalized = ''.join(c for c in text if c not in self.hebrew_diacritics)

        # Replace final forms with regular forms
        final_forms_map = {
            'ך': 'כ',
            'ם': 'מ',
            'ן': 'נ',
            'ף': 'פ',
            'ץ': 'צ'
        }

        for final, regular in final_forms_map.items():
            normalized = normalized.replace(final, regular)

        return normalized

    def fix_mixed_direction(self, text):
        """Fix mixed direction text (Hebrew + English/numbers).

        Args:
            text: Text to fix

        Returns:
            Text with proper direction markers
        """
        if not text:
            return text

        # Add right-to-left mark to the beginning of Hebrew text blocks
        rtl_mark = '\u200F'  # Right-to-Left Mark
        ltr_mark = '\u200E'  # Left-to-Right Mark

        # Handle lines separately
        lines = text.split('\n')
        fixed_lines = []

        for line in lines:
            if self.is_hebrew_text(line):
                # Add RTL mark to the beginning of Hebrew lines
                line = rtl_mark + line

                # Find English/numeric segments and add LTR marks
                # Find segments of English letters or digits
                segments = re.finditer(r'[a-zA-Z0-9]+', line)

                # Add LTR marks to these segments
                offset = 0
                modified_line = line
                for segment in segments:
                    start, end = segment.span()
                    start += offset
                    end += offset
                    modified_line = modified_line[:start] + ltr_mark + modified_line[start:end] + rtl_mark + modified_line[end:]
                    offset += 2  # Account for added marks

                fixed_lines.append(modified_line)
            else:
                # Non-Hebrew line, leave as is
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def identify_financial_terms(self, text):
        """Identify Hebrew financial terms in text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary of identified terms by category
        """
        if not text:
            return {}

        # Normalize the text
        normalized = self.normalize_hebrew(text)

        # Initialize results
        results = {category: [] for category in self.financial_terms.keys()}

        # Check each category
        for category, terms in self.financial_terms.items():
            for term in terms:
                normalized_term = self.normalize_hebrew(term)
                if normalized_term in normalized:
                    results[category].append(term)

        # Filter out empty categories
        return {k: v for k, v in results.items() if v}

    def extract_israeli_isin(self, text):
        """Extract Israeli ISIN numbers (IL prefixed).

        Args:
            text: Text to analyze

        Returns:
            List of ISIN numbers
        """
        # Israeli ISINs start with 'IL' followed by 10 characters
        isin_pattern = r'IL[0-9A-Z]{10}'
        matches = re.findall(isin_pattern, text)

        # Validate ISINs
        valid_isins = []
        for isin in matches:
            if self._validate_isin(isin):
                valid_isins.append(isin)

        return valid_isins

    def _validate_isin(self, isin):
        """Validate an ISIN number.

        Args:
            isin: ISIN number to validate

        Returns:
            Boolean indicating if ISIN is valid
        """
        if not isin or len(isin) != 12:
            return False

        # Check if the ISIN starts with IL
        if not isin.startswith('IL'):
            return False

        # Convert letters to numbers (A=10, B=11, ..., Z=35)
        digits = []
        for char in isin:
            if char.isdigit():
                digits.append(int(char))
            elif char.isalpha():
                digits.append(ord(char.upper()) - ord('A') + 10)

        # Apply the Luhn algorithm
        doubled = []
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:  # Every second digit from the right
                doubled.append(digit * 2)
            else:
                doubled.append(digit)

        # Sum the individual digits
        total = 0
        for num in doubled:
            if num >= 10:
                total += 1 + (num % 10)  # Sum the digits (e.g., 12 -> 1+2 = 3)
            else:
                total += num

        # Number is valid if the sum is divisible by 10
        return total % 10 == 0