import PyPDF2
import pdf2image
import pytesseract
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
import logging
import tempfile
import os
import re

class TableExtractor:
    """Extract and structure tabular data from PDF documents.
    
    This class handles the detection and extraction of tables from
    PDFs using text-based approaches.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
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
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
                
                # Determine which pages to process
                pages_to_process = page_numbers if page_numbers is not None else range(total_pages)
                
                for page_num in pages_to_process:
                    if page_num >= total_pages:
                        continue
                        
                    # Extract tables from the page
                    page = reader.pages[page_num]
                    tables = self._extract_page_tables(page, pdf_path, page_num)
                    
                    if tables:
                        result[page_num] = tables
                    
            return result
        except Exception as e:
            self.logger.error(f"Failed to extract tables from {pdf_path}: {str(e)}")
            raise
    
    def _extract_page_tables(self, page: PyPDF2.PageObject, pdf_path: str, page_num: int) -> List[Dict[str, Any]]:
        """Extract tables from a single page.
        
        Args:
            page: PyPDF2 PageObject
            pdf_path: Path to the PDF file
            page_num: Page number
            
        Returns:
            List of dictionaries containing table data and metadata
        """
        tables = []
        
        # Extract text from the page
        text = page.extract_text()
        
        # If direct text extraction yields little text, use OCR
        if not text or len(text.strip()) < 100:
            # Convert PDF page to image
            images = pdf2image.convert_from_path(
                pdf_path,
                first_page=page_num+1,
                last_page=page_num+1
            )
            
            if images:
                # Use OCR with table configuration
                text = pytesseract.image_to_string(
                    images[0],
                    config='--psm 6'  # Assume a single uniform block of text
                )
        
        # Now analyze text for table-like structures
        tables_data = self._identify_tables_in_text(text)
        
        # Format tables
        for idx, table_data in enumerate(tables_data):
            table = {
                "id": idx,
                "bbox": [0, 0, 0, 0],  # Placeholder coordinates
                "header": table_data.get("header", []),
                "rows": table_data.get("rows", []),
                "row_count": len(table_data.get("rows", [])) + (1 if table_data.get("header") else 0),
                "col_count": len(table_data.get("header", [])) if table_data.get("header") else 
                            (len(table_data.get("rows", [[]])[0]) if table_data.get("rows") else 0),
                "extraction_method": "text"
            }
            
            tables.append(table)
                
        return tables
    
    def _identify_tables_in_text(self, text: str) -> List[Dict[str, Any]]:
        """Identify potential tables in text.
        
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
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                # End of table?
                if current_table and current_table["rows"]:
                    tables.append(current_table)
                    current_table = None
                continue
            
            # Check if this line could be a header (contains multiple words separated by 2+ spaces)
            words = line.split()
            if len(words) >= 3 and '  ' in line:
                # This might be a header or a new table row
                if current_table is None:
                    # Start a new table
                    current_table = {
                        "header": self._split_line_into_columns(line),
                        "rows": []
                    }
                else:
                    # Add as a row to current table
                    current_table["rows"].append(self._split_line_into_columns(line))
            elif current_table:
                # This line might be part of a table row
                current_table["rows"].append(self._split_line_into_columns(line))
        
        # Add the last table if it exists
        if current_table and current_table["rows"]:
            tables.append(current_table)
            
        return tables
    
    def _split_line_into_columns(self, line: str) -> List[str]:
        """Split a line of text into columns.
        
        Args:
            line: Line of text
            
        Returns:
            List of column values
        """
        # First try splitting by multiple spaces
        if '  ' in line:
            # Replace 2+ spaces with a special marker
            marked_line = re.sub(r'  +', ' ||| ', line)
            return [col.strip() for col in marked_line.split(' ||| ')]
        
        # Fallback: just split by whitespace
        return line.split()
    
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
            return pd.DataFrame(rows, columns=header)
        else:
            # No header or length mismatch, use default column names
            return pd.DataFrame(rows)
