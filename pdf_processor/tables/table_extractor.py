import fitz  # PyMuPDF
import numpy as np
import cv2
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
import logging
import tempfile
import os

class TableExtractor:
    """Extract and structure tabular data from PDF documents.
    
    This class handles the detection and extraction of tables from
    PDFs using both heuristic and visual approaches.
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
            doc = fitz.open(pdf_path)
            pages_to_process = page_numbers if page_numbers is not None else range(len(doc))
            
            for page_num in pages_to_process:
                if page_num >= len(doc):
                    continue
                    
                page = doc[page_num]
                tables = self._extract_page_tables(page)
                if tables:
                    result[page_num] = tables
                    
            return result
        except Exception as e:
            self.logger.error(f"Failed to extract tables from {pdf_path}: {str(e)}")
            raise
    
    def _extract_page_tables(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """Extract tables from a single page.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            List of dictionaries containing table data and metadata
        """
        # Extract tables using multiple approaches and combine results
        tables = []
        
        # First try the built-in table extraction (for structured PDFs)
        structured_tables = self._extract_structured_tables(page)
        if structured_tables:
            tables.extend(structured_tables)
            
        # If no tables found with built-in extraction, try visual approach
        if not tables:
            visual_tables = self._extract_visual_tables(page)
            if visual_tables:
                tables.extend(visual_tables)
                
        return tables
    
    def _extract_structured_tables(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """Extract tables using built-in table extraction.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            List of dictionaries containing structured table data
        """
        tables = []
        
        # Extract tables using PyMuPDF's built-in extraction
        tab = page.find_tables()
        if tab and tab.tables:
            for idx, table in enumerate(tab.tables):
                rows = []
                header = []
                
                # Extract header if available
                if len(table.rows) > 0:
                    header = [cell.text.strip() for cell in table.rows[0].cells]
                
                # Extract data rows
                for row_idx, row in enumerate(table.rows):
                    if row_idx == 0 and header:  # Skip header row
                        continue
                        
                    row_data = [cell.text.strip() for cell in row.cells]
                    rows.append(row_data)
                
                # Create structured table data
                table_data = {
                    "id": idx,
                    "bbox": [table.rect.x0, table.rect.y0, table.rect.x1, table.rect.y1],
                    "header": header,
                    "rows": rows,
                    "row_count": len(rows) + (1 if header else 0),
                    "col_count": len(header) if header else (len(rows[0]) if rows else 0),
                    "extraction_method": "structured"
                }
                
                tables.append(table_data)
                
        return tables
    
    def _extract_visual_tables(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """Extract tables using image processing techniques.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            List of dictionaries containing table data extracted visually
        """
        tables = []
        
        try:
            # Render page to image for visual processing
            zoom = 2  # Higher zoom for better resolution
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_filename = tmp.name
                pix.save(tmp_filename)
            
            # Load with OpenCV
            img = cv2.imread(tmp_filename)
            
            # Clean up temp file
            os.unlink(tmp_filename)
            
            if img is None:
                return []
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
            
            # Detect horizontal lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Detect vertical lines
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)
            
            # Combine lines
            combined = cv2.add(horizontal_lines, vertical_lines)
            
            # Find contours
            contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area to find table boundaries
            min_area = 20000  # Minimum area to consider as a table
            for idx, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area > min_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Convert coordinates back to PDF space
                    x0, y0 = x / zoom, y / zoom
                    x1, y1 = (x + w) / zoom, (y + h) / zoom
                    
                    # Extract text within these bounds
                    table_rect = fitz.Rect(x0, y0, x1, y1)
                    text_blocks = [b for b in page.get_text("blocks") 
                                  if fitz.Rect(b[:4]).intersects(table_rect)]
                    
                    # Try to organize into rows and columns using y-coordinates
                    rows = self._organize_blocks_into_rows(text_blocks)
                    
                    if rows:
                        table_data = {
                            "id": idx,
                            "bbox": [x0, y0, x1, y1],
                            "header": rows[0] if rows else [],
                            "rows": rows[1:] if len(rows) > 1 else [],
                            "row_count": len(rows),
                            "col_count": len(rows[0]) if rows and rows[0] else 0,
                            "extraction_method": "visual"
                        }
                        
                        tables.append(table_data)
            
        except Exception as e:
            self.logger.error(f"Error in visual table extraction: {str(e)}")
            
        return tables
    
    def _organize_blocks_into_rows(self, blocks: List[List]) -> List[List[str]]:
        """Organize text blocks into rows based on y-coordinates.
        
        Args:
            blocks: List of text blocks with coordinates
            
        Returns:
            List of rows, each containing cell text
        """
        if not blocks:
            return []
            
        # Sort blocks by y-coordinate (top to bottom)
        blocks_sorted = sorted(blocks, key=lambda b: b[1])  # Sort by y0
        
        # Group blocks by similar y-coordinates to form rows
        rows = []
        current_row = []
        current_y = blocks_sorted[0][1]
        y_threshold = 10  # Threshold for considering blocks in the same row
        
        for block in blocks_sorted:
            if abs(block[1] - current_y) <= y_threshold:
                current_row.append(block)
            else:
                # Start a new row
                if current_row:
                    # Sort blocks in the row by x-coordinate (left to right)
                    current_row.sort(key=lambda b: b[0])
                    rows.append([b[4] for b in current_row])  # Extract text
                current_row = [block]
                current_y = block[1]
        
        # Add the last row
        if current_row:
            current_row.sort(key=lambda b: b[0])
            rows.append([b[4] for b in current_row])
            
        return rows
    
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
