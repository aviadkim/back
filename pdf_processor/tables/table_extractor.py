# import PyPDF2 # Replaced by pypdf
from pypdf import PdfReader # Import from pypdf
import pdf2image
import pytesseract
import pandas as pd
import numpy as np
import cv2
from typing import List, Dict, Any, Tuple, Optional
import logging
import tempfile
import os
import re

class TableExtractor:
    """Extract and structure tabular data from PDF documents.
    
    This class handles the detection and extraction of tables from
    PDFs using both text-based and computer vision approaches.
    With enhanced support for financial documents and multilingual content.
    """
    
    def __init__(self, language="eng+heb"):
        """Initialize the table extractor.
        
        Args:
            language: OCR language to use if needed. Default supports both English and Hebrew.
        """
        self.logger = logging.getLogger(__name__)
        self.language = language
        
    def extract_tables(self, pdf_path: str, page_numbers: Optional[List[int]] = None) -> Dict[int, List[Dict[str, Any]]]:
        """Extract tables from specified pages in a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            page_numbers: List of page numbers to process (None for all)
            
        Returns:
            Dictionary with page numbers as keys and lists of tables as values
        """
        result = {}
        
        try:
            # Open the PDF file
            with open(pdf_path, 'rb') as file:
                # Use pypdf instead of PyPDF2
                from pypdf import PdfReader
                reader = PdfReader(file)
                total_pages = len(reader.pages)
                
                # Determine which pages to process
                pages_to_process = page_numbers if page_numbers is not None else range(total_pages)
                
                for page_num in pages_to_process:
                    try: # Add try block for individual page processing
                        if page_num >= total_pages:
                            self.logger.warning(f"Requested page number {page_num} exceeds total pages {total_pages}. Skipping.")
                            continue

                        self.logger.debug(f"Extracting tables from page {page_num+1}")

                        # Extract tables from the page
                        page = reader.pages[page_num] # This might raise IndexError

                        # Try different extraction methods
                        tables_text = self._extract_tables_from_text(page)
                        tables_cv = self._extract_tables_with_cv(pdf_path, page_num)

                        # Merge and deduplicate tables
                        tables = self._merge_table_results(tables_text, tables_cv)

                        if tables:
                            result[page_num] = tables
                    except IndexError:
                        self.logger.error(f"Failed to access page {page_num} in {pdf_path}. Skipping page.")
                        # Optionally add an empty list or error marker for this page in results
                        result[page_num] = [{"error": "Failed to access page"}]
                    except Exception as page_e:
                        self.logger.error(f"Failed to process page {page_num} in {pdf_path}: {str(page_e)}")
                        # Optionally add an empty list or error marker for this page in results
                        result[page_num] = [{"error": f"Failed to process page: {str(page_e)}"}]
                    
            return result
        except FileNotFoundError:
             self.logger.error(f"File not found: {pdf_path}")
             raise # Re-raise FileNotFoundError
        except Exception as e:
            self.logger.error(f"Failed to extract tables from {pdf_path}: {str(e)}")
            # Return empty dict or raise custom exception
            return {"error": f"Failed to process PDF for tables: {str(e)}"}
    
    # Update type hint if pypdf's PageObject is different or just use generic 'Any'
    # from pypdf.page import PageObject # Check actual import if needed
    from typing import Any # Use Any for now
    def _extract_tables_from_text(self, page: Any) -> List[Dict[str, Any]]:
        """Extract tables using text-based approaches.
        
        Args:
            page: PyPDF2 PageObject
            
        Returns:
            List of dictionaries containing table data and metadata
        """
        tables = []
        
        # Extract text from the page
        text = page.extract_text()
        
        if not text or len(text.strip()) < 50:
            return []
        
        # Now analyze text for table-like structures
        tables_data = self._identify_tables_in_text(text)
        
        # Format tables
        for idx, table_data in enumerate(tables_data):
            table = {
                "id": idx,
                "bbox": table_data.get("bbox", [0, 0, 0, 0]),  # Coordinates if available
                "header": table_data.get("header", []),
                "rows": table_data.get("rows", []),
                "row_count": len(table_data.get("rows", [])) + (1 if table_data.get("header") else 0),
                "col_count": len(table_data.get("header", [])) if table_data.get("header") else 
                            (len(table_data.get("rows", [[]])[0]) if table_data.get("rows") else 0),
                "extraction_method": "text"
            }
            
            tables.append(table)
                
        return tables
    
    def _extract_tables_with_cv(self, pdf_path: str, page_num: int) -> List[Dict[str, Any]]:
        """Extract tables using computer vision techniques.
        
        Args:
            pdf_path: Path to the PDF file
            page_num: Page number
            
        Returns:
            List of dictionaries containing table data and metadata
        """
        tables = []
        
        try:
            # Convert PDF page to image
            images = pdf2image.convert_from_path(
                pdf_path,
                first_page=page_num+1,
                last_page=page_num+1,
                dpi=300  # Higher DPI for better quality
            )
            
            if not images:
                return []
                
            # Process the image to find tables
            image = images[0]
            
            # Convert PIL image to OpenCV format
            open_cv_image = np.array(image)
            open_cv_image = open_cv_image[:, :, ::-1].copy()  # RGB to BGR
            
            # Convert to grayscale
            gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to make table lines more visible
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
            
            # Detect horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=3)
            vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=3)
            
            # Combine horizontal and vertical lines
            table_mask = cv2.add(horizontal_lines, vertical_lines)
            
            # Find contours
            contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Process each contour as a potential table
            for idx, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter small rectangles
                if w < 100 or h < 100:
                    continue
                    
                # Extract table region from the original image
                table_region = gray[y:y+h, x:x+w]
                
                # Apply OCR on the table region
                table_text = pytesseract.image_to_string(
                    table_region, 
                    lang=self.language,
                    config='--psm 6'  # Assume a uniform block of text
                )
                
                # Process the table text into structured data
                header, rows = self._process_table_ocr_text(table_text)
                
                if rows:  # Only add if we found rows
                    table = {
                        "id": idx,
                        "bbox": [x, y, x+w, y+h],
                        "header": header,
                        "rows": rows,
                        "row_count": len(rows) + (1 if header else 0),
                        "col_count": len(header) if header else (len(rows[0]) if rows else 0),
                        "extraction_method": "cv"
                    }
                    
                    tables.append(table)
        except Exception as e:
            self.logger.warning(f"CV-based table extraction failed: {str(e)}")
            
        return tables
    
    def _process_table_ocr_text(self, text: str) -> Tuple[List[str], List[List[str]]]:
        """Process OCR text from a table region into structured header and rows.
        
        Args:
            text: OCR text from table region
            
        Returns:
            Tuple of (header, rows)
        """
        if not text or not text.strip():
            return [], []
            
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        if not lines:
            return [], []
        
        # Initialize header and rows
        header = []
        rows = []
        
        # First line is often the header
        if lines:
            first_line = lines[0]
            # Check if first line looks like a header
            if self._is_likely_header(first_line):
                header = self._split_line_into_columns(first_line)
                lines = lines[1:]  # Remove header from lines
                
        # Process remaining lines as rows
        for line in lines:
            if line.strip():
                columns = self._split_line_into_columns(line)
                if columns:
                    rows.append(columns)
        
        return header, rows
    
    def _is_likely_header(self, line: str) -> bool:
        """Check if a line is likely to be a table header.
        
        Args:
            line: Line of text
            
        Returns:
            Boolean indicating if line is likely a header
        """
        # Common header terms in financial tables (English and Hebrew)
        header_terms = [
            # English
            'name', 'date', 'value', 'price', 'amount', 'total', 'balance', 'interest', 
            'rate', 'yield', 'maturity', 'isin', 'quantity', 'security', 'description',
            # Hebrew
            'שם', 'תאריך', 'ערך', 'מחיר', 'סכום', 'סה״כ', 'סה"כ', 'יתרה', 'ריבית',
            'תשואה', 'פדיון', 'כמות', 'ני"ע', 'ני״ע', 'תיאור'
        ]
        
        # Check if line contains any header term
        line_lower = line.lower()
        for term in header_terms:
            if term.lower() in line_lower:
                return True
                
        # Check if line has different formatting than other lines
        if line.isupper() or all(c.isupper() for c in line if c.isalpha()):
            return True
            
        return False
    
    def _identify_tables_in_text(self, text: str) -> List[Dict[str, Any]]:
        """Identify potential tables in text content.
        
        Args:
            text: Text content to analyze
            
        Returns:
            List of potential tables with headers and rows
        """
        if not text:
            return []
            
        tables = []
        lines = text.split('\n')
        
        # Simple heuristic: Look for consistent separator patterns or columnar alignment
        current_table = None
        table_start_line = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                # End of table?
                if current_table and current_table["rows"]:
                    tables.append(current_table)
                    current_table = None
                continue
            
            # Check if this line could be part of a table
            is_table_row = self._is_potential_table_row(line)
            
            if is_table_row:
                if current_table is None:
                    # Start a new table
                    current_table = {
                        "header": [],
                        "rows": [],
                        "bbox": [0, table_start_line * 20, 600, (i + 1) * 20]  # Rough estimate of position
                    }
                    table_start_line = i
                    
                    # Check if this could be a header row
                    if self._is_likely_header(line):
                        current_table["header"] = self._split_line_into_columns(line)
                    else:
                        # Not a header, just a regular row
                        current_table["rows"].append(self._split_line_into_columns(line))
                else:
                    # Add as a row to current table
                    columns = self._split_line_into_columns(line)
                    
                    # Update bbox to include this row
                    if "bbox" in current_table:
                        bbox = current_table["bbox"]
                        bbox[3] = (i + 1) * 20  # Update bottom coordinate
                        
                    if columns:
                        current_table["rows"].append(columns)
            elif current_table:
                # Not a table row but we're in a table context
                # Check if it might be a continuation of the last row or a header/footer
                if self._could_be_table_related(line, current_table):
                    # Continue with current table
                    continue
                else:
                    # End of table
                    if current_table and current_table["rows"]:
                        tables.append(current_table)
                    current_table = None
        
        # Add the last table if it exists
        if current_table and current_table["rows"]:
            tables.append(current_table)
            
        # Filter out tables with inconsistent columns
        return [t for t in tables if self._is_valid_table(t)]
    
    def _is_potential_table_row(self, line: str) -> bool:
        """Check if a line might be a row in a table.
        
        Args:
            line: Line of text
            
        Returns:
            Boolean indicating if the line might be a table row
        """
        # Check for common table indicators
        
        # Multiple spaces or tabs between "columns"
        if re.search(r'\S+\s{3,}\S+', line):
            return True
            
        # Multiple instances of numeric data
        number_pattern = r'[\$€£¥₪]?\s?\d+[\.,]?\d*\s?[KkMmBb]?'
        numbers = re.findall(number_pattern, line)
        if len(numbers) >= 3:  # If line has multiple numbers, likely a financial table row
            return True
            
        # Content separated by | or similar characters
        if '|' in line or ';' in line:
            return True
            
        # Check for ISIN pattern (common in financial documents)
        isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
        if re.search(isin_pattern, line):
            return True
            
        # Multiple currency symbols
        currency_symbols = ['$', '€', '£', '₪', '¥']
        currency_count = sum(line.count(symbol) for symbol in currency_symbols)
        if currency_count >= 2:
            return True
            
        # Check for percentage values
        percentage_pattern = r'\d+\.?\d*\s?%'
        percentages = re.findall(percentage_pattern, line)
        if len(percentages) >= 2:
            return True
            
        return False
    
    def _could_be_table_related(self, line: str, table: Dict[str, Any]) -> bool:
        """Check if a line could be related to a table as a title, note, etc.
        
        Args:
            line: Line of text
            table: Current table data
            
        Returns:
            Boolean indicating if the line might be related to the table
        """
        # Check if line is short (could be a title or footnote)
        if len(line) < 50:
            return True
            
        # Check if line contains terms like "note", "total", etc.
        note_terms = ["note", "total", "sum", "average", "הערה", "סיכום", "סה״כ", "סה\"כ", "ממוצע"]
        for term in note_terms:
            if term in line.lower():
                return True
                
        return False
    
    def _is_valid_table(self, table: Dict[str, Any]) -> bool:
        """Check if a table has a consistent structure.
        
        Args:
            table: Table data
            
        Returns:
            Boolean indicating if the table has a valid structure
        """
        rows = table.get("rows", [])
        if not rows:
            return False
            
        # Check for consistent column count
        col_counts = [len(row) for row in rows]
        if len(set(col_counts)) > 2:  # Allow at most 2 different column counts
            return False
            
        # Check if most columns contain data (not just whitespace)
        empty_cells = 0
        total_cells = 0
        
        for row in rows:
            for cell in row:
                total_cells += 1
                if not cell.strip():
                    empty_cells += 1
                    
        if total_cells > 0 and empty_cells / total_cells > 0.5:  # More than 50% empty
            return False
            
        return True
    
    def _split_line_into_columns(self, line: str) -> List[str]:
        """Split a line of text into columns.
        
        Args:
            line: Line of text
            
        Returns:
            List of column values
        """
        # First try splitting by pipe characters if they exist
        if '|' in line:
            return [col.strip() for col in line.split('|')]
            
        # Try splitting by multiple spaces
        if '  ' in line:
            # Replace 2+ spaces with a special marker
            marked_line = re.sub(r'  +', ' ||| ', line)
            return [col.strip() for col in marked_line.split(' ||| ')]
            
        # Try splitting by tab characters
        if '\t' in line:
            return [col.strip() for col in line.split('\t')]
        
        # Try detection of numbers and creating splits based on that
        amount_pattern = r'(?:[\$€£₪]\s*[\d,\.]+|\d+(?:[,\.]\d+)*\s*(?:%|₪|€|£|\$)?)'
        if re.search(amount_pattern, line):
            # Find all financial amounts
            amounts = re.finditer(amount_pattern, line)
            
            # Collect start positions of amounts
            positions = [(m.start(), m.end()) for m in amounts]
            
            if len(positions) >= 2:
                # Use amount positions to split the line
                columns = []
                start_pos = 0
                
                for pos_start, pos_end in positions:
                    # If there's text before the amount, add it as a column
                    if pos_start > start_pos:
                        pre_text = line[start_pos:pos_start].strip()
                        if pre_text:
                            columns.append(pre_text)
                    
                    # Add the amount as a column
                    columns.append(line[pos_start:pos_end].strip())
                    start_pos = pos_end
                
                # Add any remaining text after the last amount
                if start_pos < len(line):
                    remaining = line[start_pos:].strip()
                    if remaining:
                        columns.append(remaining)
                
                return columns
        
        # Fallback: Just return the whole line as a single column
        return [line.strip()] if line.strip() else []
    
    def _merge_table_results(self, tables_text: List[Dict[str, Any]], tables_cv: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge and deduplicate table results from different extraction methods.
        
        Args:
            tables_text: Tables extracted by text-based method
            tables_cv: Tables extracted by computer vision method
            
        Returns:
            Merged list of tables with duplicates removed
        """
        if not tables_text:
            return tables_cv
            
        if not tables_cv:
            return tables_text
            
        # Start with all tables from text-based extraction
        merged_tables = list(tables_text)
        
        # Add CV-based tables that don't overlap with text-based tables
        for cv_table in tables_cv:
            is_duplicate = False
            
            # Check if this CV table overlaps with any text-based table
            for text_table in tables_text:
                if self._tables_are_similar(cv_table, text_table):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                merged_tables.append(cv_table)
                
        # Reindex the tables
        for i, table in enumerate(merged_tables):
            table["id"] = i
            
        return merged_tables
    
    def _tables_are_similar(self, table1: Dict[str, Any], table2: Dict[str, Any]) -> bool:
        """Check if two tables are likely the same content.
        
        Args:
            table1: First table
            table2: Second table
            
        Returns:
            Boolean indicating if tables are similar
        """
        # Check row and column counts
        row_count1 = table1.get("row_count", 0)
        row_count2 = table2.get("row_count", 0)
        
        col_count1 = table1.get("col_count", 0)
        col_count2 = table2.get("col_count", 0)
        
        # If dimensions are very different, tables are different
        if abs(row_count1 - row_count2) > max(2, row_count1 * 0.3) or \
           abs(col_count1 - col_count2) > max(2, col_count1 * 0.3):
            return False
            
        # Compare headers
        header1 = table1.get("header", [])
        header2 = table2.get("header", [])
        
        if header1 and header2 and len(header1) == len(header2):
            matching_cells = sum(1 for h1, h2 in zip(header1, header2) 
                               if h1.lower().strip() == h2.lower().strip()
                               or self._strings_are_similar(h1, h2))
            
            if matching_cells / len(header1) > 0.5:  # More than 50% match
                return True
                
        # Compare first few rows
        rows1 = table1.get("rows", [])[:3]  # Check only first 3 rows
        rows2 = table2.get("rows", [])[:3]
        
        if rows1 and rows2 and len(rows1) > 0 and len(rows2) > 0:
            for r1 in rows1:
                for r2 in rows2:
                    if len(r1) == len(r2):
                        matching_cells = sum(1 for c1, c2 in zip(r1, r2) 
                                         if c1.lower().strip() == c2.lower().strip()
                                         or self._strings_are_similar(c1, c2))
                        
                        if matching_cells / len(r1) > 0.5:  # More than 50% match
                            return True
        
        return False
    
    def _strings_are_similar(self, str1: str, str2: str) -> bool:
        """Check if two strings are similar (handling OCR variations).
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Boolean indicating if strings are similar
        """
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        # Exact match
        if str1 == str2:
            return True
            
        # If either string is empty, they're not similar
        if not str1 or not str2:
            return False
            
        # Check if one string is contained in the other
        if str1 in str2 or str2 in str1:
            return True
            
        # Check numeric values
        num_pattern = r'\d+\.?\d*'
        num1 = re.findall(num_pattern, str1)
        num2 = re.findall(num_pattern, str2)
        
        if num1 and num2 and num1[0] == num2[0]:
            return True
            
        # Check for common prefixes
        min_len = min(len(str1), len(str2))
        if min_len > 3 and str1[:min_len//2] == str2[:min_len//2]:
            return True
            
        return False
    
    def convert_to_dataframe(self, table: Dict[str, Any]) -> pd.DataFrame:
        """Convert a table dictionary to a pandas DataFrame.
        
        Args:
            table: Table dictionary with header and rows
            
        Returns:
            Pandas DataFrame representation of the table
        """
        header = table.get("header", [])
        rows = table.get("rows", [])
        
        if not rows:
            return pd.DataFrame()
            
        # If header exists, use it for column names
        if header and len(header) == len(rows[0]):
            df = pd.DataFrame(rows, columns=header)
        else:
            # No header or length mismatch, use default column names
            df = pd.DataFrame(rows)
            
        # Clean column names
        if not header:
            # Generate simple column names
            df.columns = [f"Column_{i+1}" for i in range(len(df.columns))]
        
        return df
    
    def extract_tables_from_image(self, image_path: str) -> List[Dict[str, Any]]:
        """Extract tables directly from an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dictionaries containing table data and metadata
        """
        tables = []
        
        try:
            # Read the image
            img = cv2.imread(image_path)
            if img is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return []
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to make table lines more visible
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
            
            # Detect horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=3)
            vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=3)
            
            # Combine horizontal and vertical lines
            table_mask = cv2.add(horizontal_lines, vertical_lines)
            
            # Find contours
            contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Process each contour as a potential table
            for idx, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter small rectangles
                if w < 100 or h < 100:
                    continue
                    
                # Extract table region from the original image
                table_region = gray[y:y+h, x:x+w]
                
                # Apply OCR on the table region
                table_text = pytesseract.image_to_string(
                    table_region, 
                    lang=self.language,
                    config='--psm 6'  # Assume a uniform block of text
                )
                
                # Process the table text into structured data
                header, rows = self._process_table_ocr_text(table_text)
                
                if rows:  # Only add if we found rows
                    table = {
                        "id": idx,
                        "bbox": [x, y, x+w, y+h],
                        "header": header,
                        "rows": rows,
                        "row_count": len(rows) + (1 if header else 0),
                        "col_count": len(header) if header else (len(rows[0]) if rows else 0),
                        "extraction_method": "image"
                    }
                    
                    tables.append(table)
                    
            # If no tables found with line detection, try text-based detection
            if not tables:
                text = pytesseract.image_to_string(gray, lang=self.language)
                tables_data = self._identify_tables_in_text(text)
                
                for idx, table_data in enumerate(tables_data):
                    table = {
                        "id": idx,
                        "bbox": table_data.get("bbox", [0, 0, 0, 0]),
                        "header": table_data.get("header", []),
                        "rows": table_data.get("rows", []),
                        "row_count": len(table_data.get("rows", [])) + (1 if table_data.get("header") else 0),
                        "col_count": len(table_data.get("header", [])) if table_data.get("header") else 
                                    (len(table_data.get("rows", [[]])[0]) if table_data.get("rows") else 0),
                        "extraction_method": "text"
                    }
                    
                    tables.append(table)
                
        except Exception as e:
            self.logger.error(f"Failed to extract tables from image {image_path}: {str(e)}")
            
        return tables