import cv2
import numpy as np
import pandas as pd
import pytesseract
import logging
import re
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import os
from pdf2image import convert_from_path
import itertools

logger = logging.getLogger(__name__)

class EnhancedTableExtractor:
    """
    Advanced table extraction from images and PDFs with specialized support
    for financial tables in Hebrew and English.
    """

    def __init__(self, language: str = "eng+heb", use_hough_transform: bool = True):
        """
        Initialize the enhanced table extractor.

        Args:
            language: OCR language(s) to use
            use_hough_transform: Whether to use Hough transform for line detection
        """
        self.language = language
        self.use_hough_transform = use_hough_transform
        self.logger = logging.getLogger(__name__)

        # Specialized patterns for financial data
        self.number_pattern = r'[-+]?[\d,]+\.?\d*%?'
        self.currency_pattern = r'[$₪€£¥]'
        self.date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'

        # Headers commonly found in financial tables
        self.financial_headers = [
            # English
            r'amount', r'balance', r'cost', r'currency', r'date', r'isin', r'market value',
            r'maturity', r'name', r'price', r'quantity', r'rate', r'security', r'symbol',
            r'value', r'yield', r'total',
            # Hebrew
            r'סכום', r'יתרה', r'עלות', r'מטבע', r'תאריך', r'שווי שוק', r'מח"מ',
            r'שם', r'מחיר', r'כמות', r'שיעור', r'ני"ע', r'סימול', r'ערך', r'תשואה', r'סה"כ'
        ]

    def _binary_search_page_count(self, pdf_path: str, low: int, high: int) -> int:
        """Helper function to find the total page count using binary search."""
        mid = 0
        while low <= high:
            mid = (low + high) // 2
            try:
                # Try converting the middle page
                convert_from_path(pdf_path, first_page=mid, last_page=mid)
                # If successful, the page exists, try higher pages
                low = mid + 1
            except Exception:
                # If error, the page doesn't exist, try lower pages
                high = mid - 1
        # High will hold the last successfully converted page number
        return high

    def extract_tables_from_pdf(self, pdf_path: str, page_numbers: Optional[List[int]] = None) -> Dict[int, List[Dict[str, Any]]]:
        """
        Extract tables from specified pages in a PDF.

        Args:
            pdf_path: Path to the PDF file
            page_numbers: List of page numbers to process (1-based, None for all)

        Returns:
            Dictionary with page numbers (0-based) as keys and lists of tables as values
        """
        result = {}
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            self.logger.error(f"PDF file not found: {pdf_path}")
            return result

        try:
            # Determine which pages to process
            if page_numbers is None:
                # Get total pages efficiently
                try:
                    # pdfinfo might be faster if available
                    import subprocess
                    output = subprocess.check_output(['pdfinfo', pdf_path]).decode('utf-8')
                    match = re.search(r'Pages:\s*(\d+)', output)
                    if match:
                        total_pages = int(match.group(1))
                    else:
                        raise ValueError("Could not parse pdfinfo output")
                    self.logger.info(f"Found {total_pages} pages using pdfinfo.")
                except (FileNotFoundError, ValueError, subprocess.CalledProcessError):
                    self.logger.warning("pdfinfo not found or failed. Using slower method to count pages.")
                    # Fallback: Convert first page to check if PDF is valid
                    try:
                        first_page = convert_from_path(pdf_path, first_page=1, last_page=1)
                        if not first_page:
                            self.logger.error(f"Failed to convert page 1 of PDF {pdf_path}")
                            return result
                    except Exception as e:
                         self.logger.error(f"Error converting page 1 of PDF {pdf_path}: {e}")
                         return result

                    # Use binary search to find total pages
                    total_pages = self._binary_search_page_count(pdf_path, 1, 200) # Limit search range
                    if total_pages == 0: # If binary search failed, assume 1 page if first page worked
                         total_pages = 1
                    self.logger.info(f"Found {total_pages} pages using binary search conversion.")


                page_numbers = list(range(1, total_pages + 1))

            # Process each specified page
            for page_num in page_numbers:
                try:
                    self.logger.info(f"Processing page {page_num} of {pdf_path}")
                    # Convert PDF page to image
                    images = convert_from_path(
                        pdf_path,
                        first_page=page_num,
                        last_page=page_num,
                        dpi=300  # Higher DPI for better table detection
                    )

                    if not images:
                        self.logger.warning(f"No image converted for page {page_num}")
                        continue

                    # Process the page image
                    page_image = np.array(images[0])
                    tables = self.extract_tables_from_image(page_image)

                    if tables:
                        result[page_num - 1] = tables  # Store with 0-based index
                        self.logger.info(f"Found {len(tables)} tables on page {page_num}")
                    else:
                         self.logger.info(f"No tables found on page {page_num}")


                except Exception as e:
                    self.logger.error(f"Error processing page {page_num} of {pdf_path}: {str(e)}", exc_info=True)

            return result

        except Exception as e:
            self.logger.error(f"Failed to extract tables from {pdf_path}: {str(e)}", exc_info=True)
            return result

    def extract_tables_from_image(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Extract tables from an image.

        Args:
            image: NumPy array containing the image

        Returns:
            List of dictionaries containing table data and metadata
        """
        tables = []

        try:
            # Preprocess the image
            preprocessed, gray = self._preprocess_image(image)

            # Detect tables in the image
            table_regions = self._detect_table_regions(preprocessed)
            self.logger.debug(f"Detected {len(table_regions)} potential table regions.")

            # Process each detected table region
            for i, region in enumerate(table_regions):
                x, y, w, h = region
                self.logger.debug(f"Processing region {i}: bbox=({x}, {y}, {w}, {h})")

                # Extract the table region from the original grayscale image for OCR
                table_img_gray = gray[y:y+h, x:x+w]
                # Extract from preprocessed for cell detection if needed
                table_img_preprocessed = preprocessed[y:y+h, x:x+w]

                # Detect cells in the table (using preprocessed image)
                cells = self._detect_table_cells(table_img_preprocessed)
                self.logger.debug(f"Detected {len(cells)} potential cells in region {i}.")

                if not cells:
                    self.logger.warning(f"No cells detected in region {i}. Skipping.")
                    continue

                # Extract text from cells using the grayscale image
                table_data = self._extract_text_from_cells(table_img_gray, cells)
                self.logger.debug(f"Extracted text data from {len(table_data)} cells.")

                # Process into structured table with header and rows
                processed_table = self._process_table_data(table_data)
                self.logger.debug(f"Processed table data: {len(processed_table.get('rows', []))} rows, {len(processed_table.get('header', []))} header cols.")


                # Add table metadata
                table_dict = {
                    "id": f"cv-{i}", # Prefix to distinguish from text-based
                    "bbox": [x, y, x+w, y+h],
                    "header": processed_table.get("header", []),
                    "rows": processed_table.get("rows", []),
                    "row_count": len(processed_table.get("rows", [])),
                    "col_count": len(processed_table.get("header", [])) if processed_table.get("header") else
                               (len(processed_table.get("rows", [[]])[0]) if processed_table.get("rows") else 0),
                    "extraction_method": "cv2"
                }
                # Add header row to row_count if header exists
                if table_dict["header"]:
                    table_dict["row_count"] += 1


                # Only add if table has reasonable dimensions
                if table_dict["row_count"] >= 2 and table_dict["col_count"] >= 2:
                    tables.append(table_dict)
                    self.logger.debug(f"Added CV-based table {i} with {table_dict['row_count']} rows and {table_dict['col_count']} cols.")
                else:
                    self.logger.debug(f"Skipping CV-based table {i} due to small dimensions ({table_dict['row_count']}x{table_dict['col_count']}).")


            # If no tables found with vision approach, try text-based approach
            if not tables:
                self.logger.info("No tables found using CV method, attempting text-based extraction.")
                # Extract all text from the image (use original grayscale for better OCR)
                try:
                    text = pytesseract.image_to_string(gray, lang=self.language)
                    self.logger.debug(f"Extracted text for text-based approach (length: {len(text)}).")

                    # Try to identify tables from text structure
                    text_tables = self._identify_tables_in_text(text)
                    self.logger.debug(f"Identified {len(text_tables)} potential tables in text.")


                    for i, text_table in enumerate(text_tables):
                        table_dict = {
                            "id": f"text-{i}", # Prefix to distinguish
                            "bbox": [0, 0, image.shape[1], image.shape[0]],  # Bbox is the whole image
                            "header": text_table.get("header", []),
                            "rows": text_table.get("rows", []),
                            "row_count": len(text_table.get("rows", [])),
                            "col_count": len(text_table.get("header", [])) if text_table.get("header") else
                                       (len(text_table.get("rows", [[]])[0]) if text_table.get("rows") else 0),
                            "extraction_method": "text"
                        }
                        # Add header row to row_count if header exists
                        if table_dict["header"]:
                            table_dict["row_count"] += 1

                        # Only add if table has reasonable dimensions
                        if table_dict["row_count"] >= 2 and table_dict["col_count"] >= 2:
                            tables.append(table_dict)
                            self.logger.debug(f"Added text-based table {i} with {table_dict['row_count']} rows and {table_dict['col_count']} cols.")
                        else:
                             self.logger.debug(f"Skipping text-based table {i} due to small dimensions ({table_dict['row_count']}x{table_dict['col_count']}).")

                except pytesseract.TesseractNotFoundError:
                     self.logger.error("Tesseract is not installed or not in PATH. Text-based extraction failed.")
                except Exception as e:
                     self.logger.error(f"Error during text-based table extraction: {str(e)}", exc_info=True)


            return tables

        except Exception as e:
            self.logger.error(f"Error extracting tables from image: {str(e)}", exc_info=True)
            return []

    def _preprocess_image(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess an image for table detection.

        Args:
            image: NumPy array containing the image

        Returns:
            Tuple containing:
                - Preprocessed binary image (for line/contour detection)
                - Grayscale image (for OCR)
        """
        # Convert to grayscale
        if len(image.shape) == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif len(image.shape) == 3 and image.shape[2] == 4: # Handle RGBA
            gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        else:
            gray = image.copy() # Assume already grayscale

        # Apply adaptive thresholding for potentially better results on varying illumination
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)

        # Remove noise using morphological opening
        kernel_size = 3
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        # Increase iterations slightly for potentially cleaner lines
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

        return opening, gray


    def _detect_table_regions(self, preprocessed_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect table regions in a preprocessed image using contours.
        More robust than line detection for tables without clear borders.

        Args:
            preprocessed_image: Preprocessed binary image

        Returns:
            List of table regions as (x, y, width, height) tuples
        """
        regions = []

        # Dilate to connect text into larger blocks
        # Adjust kernel size based on image size? Maybe fixed is okay.
        dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3)) # Wider kernel to connect words/columns
        dilated = cv2.dilate(preprocessed_image, dilate_kernel, iterations=3) # More iterations

        # Find contours on the dilated image
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by size to find potential tables
        image_area = preprocessed_image.shape[0] * preprocessed_image.shape[1]
        min_area_ratio = 0.01  # Lowered threshold slightly
        max_area_ratio = 0.95 # Avoid taking the whole page
        min_width = 50
        min_height = 50

        potential_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            # Filter based on size and aspect ratio
            if (area > image_area * min_area_ratio and
                area < image_area * max_area_ratio and
                w > min_width and h > min_height and
                0.1 < w / (h + 1e-6) < 10): # Avoid division by zero
                potential_regions.append((x, y, w, h))

        # Optional: Merge overlapping or very close regions if needed
        # (Skipping for simplicity now)

        # Optional: Fallback to line detection if contour method fails
        if not potential_regions and self.use_hough_transform:
             self.logger.debug("No regions found via contours, trying line detection.")
             regions = self._detect_tables_by_lines(preprocessed_image)
        else:
             regions = potential_regions


        # Sort regions by y-coordinate, then x-coordinate
        regions.sort(key=lambda r: (r[1], r[0]))

        return regions


    def _detect_tables_by_lines(self, preprocessed_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect tables by finding intersecting horizontal and vertical lines.
        (Used as a fallback if contour method fails)

        Args:
            preprocessed_image: Preprocessed binary image

        Returns:
            List of table regions as (x, y, width, height) tuples
        """
        regions = []

        # Detect horizontal lines
        horizontal = preprocessed_image.copy()
        # Make kernel size relative but ensure minimum
        horizontal_size = max(50, horizontal.shape[1] // 30)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
        horizontal = cv2.morphologyEx(horizontal, cv2.MORPH_OPEN, horizontal_kernel, iterations=2) # More iterations

        # Detect vertical lines
        vertical = preprocessed_image.copy()
        vertical_size = max(50, vertical.shape[0] // 30)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))
        vertical = cv2.morphologyEx(vertical, cv2.MORPH_OPEN, vertical_kernel, iterations=2) # More iterations

        # Combine horizontal and vertical lines (bitwise AND to find intersections)
        # Using ADD might be better to just get the grid structure
        # combined = cv2.bitwise_and(horizontal, vertical)
        combined = cv2.add(horizontal, vertical)


        # Find contours in the combined image (representing the table grid)
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by size and shape
        for contour in contours:
             # Approximate contour to a polygon
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

            # We expect tables to be roughly rectangular (4 vertices)
            # but allow for slight imperfections
            if len(approx) >= 4:
                x, y, w, h = cv2.boundingRect(contour)

                # Check if potential table (reasonable size and aspect ratio)
                if (w > 100 and h > 50 and  # Minimum size adjusted
                    0.1 < w / (h + 1e-6) < 10): # Wider aspect ratio range
                    regions.append((x, y, w, h))

        # Sort regions by y-coordinate, then x-coordinate
        regions.sort(key=lambda r: (r[1], r[0]))

        return regions


    def _detect_table_cells(self, table_image_preprocessed: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect cells within a table image using contours on inverted thresholded image.
        This works better for tables where content defines cells, not just lines.

        Args:
            table_image_preprocessed: Preprocessed binary image of the table region

        Returns:
            List of cell regions as (x, y, width, height) tuples, sorted top-to-bottom, left-to-right.
        """
        cells = []
        # Invert the image - we want contours around the content (black text on white bg becomes white on black)
        # If already inverted by preprocessing, maybe don't invert again? Check _preprocess_image output.
        # Our preprocess outputs THRESH_BINARY_INV, so content is white. No need to invert.
        # inverted_thresh = cv2.bitwise_not(table_image_thresh)

        # Dilate slightly to connect parts of characters/numbers within a cell
        # Use smaller kernel than region detection
        cell_dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated_cells = cv2.dilate(table_image_preprocessed, cell_dilate_kernel, iterations=1)


        # Find contours of the content within cells
        contours, _ = cv2.findContours(dilated_cells, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours that likely represent cell content
        min_cell_w = 5
        min_cell_h = 5
        max_cell_w = table_image_preprocessed.shape[1] * 0.8 # Avoid taking huge chunks
        max_cell_h = table_image_preprocessed.shape[0] * 0.5
        min_cell_area = 25

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if (w > min_cell_w and h > min_cell_h and
                w < max_cell_w and h < max_cell_h and
                area > min_cell_area):
                 # Add a small padding to the bounding box for OCR
                 padding = 2
                 x1 = max(0, x - padding)
                 y1 = max(0, y - padding)
                 x2 = min(table_image_preprocessed.shape[1], x + w + padding)
                 y2 = min(table_image_preprocessed.shape[0], y + h + padding)
                 cells.append((x1, y1, x2 - x1, y2 - y1)) # Store as x, y, w, h

        if not cells:
            self.logger.warning("Cell detection using content contours failed. Trying line-based cell detection.")
            cells = self._detect_cells_by_lines(table_image_preprocessed)


        # Sort cells top-to-bottom, then left-to-right
        # Sort primarily by y, but allow for some tolerance (e.g., half cell height)
        # Then sort by x
        if cells:
            avg_h = sum(c[3] for c in cells) / len(cells) if cells else 10
            cells.sort(key=lambda c: (round(c[1] / (avg_h * 0.5)), c[0]))

        return cells

    def _detect_cells_by_lines(self, table_image_preprocessed: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """ Fallback cell detection using horizontal/vertical lines """
        cells = []
        # Detect horizontal lines
        horizontal = table_image_preprocessed.copy()
        h_kernel_size = max(15, horizontal.shape[1] // 50) # Adjust kernel size
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_kernel_size, 1))
        horizontal = cv2.morphologyEx(horizontal, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

        # Detect vertical lines
        vertical = table_image_preprocessed.copy()
        v_kernel_size = max(15, vertical.shape[0] // 50) # Adjust kernel size
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_kernel_size))
        vertical = cv2.morphologyEx(vertical, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

        # Combine lines
        grid = cv2.add(horizontal, vertical)

        # Find contours of the grid lines themselves
        contours, _ = cv2.findContours(grid, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) # Use LIST

        # Find bounding boxes of the spaces *between* the lines (the cells)
        # This is complex. A simpler approach: find contours on the *inverted* grid.
        inverted_grid = cv2.bitwise_not(grid)
        cell_contours, _ = cv2.findContours(inverted_grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        min_cell_w = 5
        min_cell_h = 5
        for contour in cell_contours:
             x, y, w, h = cv2.boundingRect(contour)
             # Filter small noise contours
             if w > min_cell_w and h > min_cell_h:
                 # Add padding
                 padding = 1
                 x1 = max(0, x - padding)
                 y1 = max(0, y - padding)
                 x2 = min(table_image_preprocessed.shape[1], x + w + padding)
                 y2 = min(table_image_preprocessed.shape[0], y + h + padding)
                 cells.append((x1, y1, x2 - x1, y2 - y1))

        return cells


    def _extract_text_from_cells(self, table_image_gray: np.ndarray, cells: List[Tuple[int, int, int, int]]) -> List[Dict[str, Any]]:
        """
        Extract text from detected cell regions using OCR.

        Args:
            table_image_gray: Grayscale image of the table region
            cells: List of cell regions as (x, y, width, height) tuples

        Returns:
            List of dictionaries, each containing 'bbox' and 'text' for a cell.
        """
        cell_data = []
        try:
            for i, (x, y, w, h) in enumerate(cells):
                if w <= 0 or h <= 0:
                    self.logger.warning(f"Skipping invalid cell bbox: {(x, y, w, h)}")
                    continue

                # Extract the cell image from the grayscale table image
                cell_img = table_image_gray[y:y+h, x:x+w]

                # Basic preprocessing for OCR on the cell image
                # Rescale for potentially better OCR? Maybe not needed if DPI is high.
                # cell_img = cv2.resize(cell_img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
                # Thresholding might help sometimes, but adaptive was done before.
                # _, cell_thresh = cv2.threshold(cell_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                # Use pytesseract to extract text
                # Configure Tesseract: page segmentation mode 6 assumes a single uniform block of text.
                # Other modes (e.g., 7: treat as single text line) might be useful too.
                config = f'--psm 6 --oem 3 -l {self.language}' # OEM 3 is default LSTM engine
                text = pytesseract.image_to_string(cell_img, config=config).strip()

                # Clean up common OCR errors if needed (e.g., replacing '|' with 'l' or '1')
                text = text.replace('\n', ' ').replace('\r', '') # Replace newlines within cell text

                cell_data.append({
                    "bbox": (x, y, w, h),
                    "text": text
                })
        except pytesseract.TesseractNotFoundError:
            self.logger.error("Tesseract is not installed or not in PATH. OCR failed.")
            # Return empty data or raise exception? Returning empty for now.
            return []
        except Exception as e:
            self.logger.error(f"Error during OCR for a cell: {e}", exc_info=True)
            # Continue with other cells if one fails? Yes.

        return cell_data


    def _process_table_data(self, cell_data: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
        """
        Organize extracted cell text into rows and identify a potential header.

        Args:
            cell_data: List of dictionaries with 'bbox' and 'text' for each cell.

        Returns:
            Dictionary with 'header' (list of strings) and 'rows' (list of lists of strings).
        """
        if not cell_data:
            return {"header": [], "rows": []}

        # Estimate number of rows and columns based on cell positions
        # Group cells by approximate Y coordinate to form rows
        rows_dict = {}
        avg_h = sum(c['bbox'][3] for c in cell_data) / len(cell_data) if cell_data else 10
        y_tolerance = avg_h * 0.5 # Allow half cell height tolerance for row grouping

        for cell in cell_data:
            x, y, w, h = cell['bbox']
            text = cell['text']

            # Find the row key (center y-coordinate rounded to nearest tolerance step)
            row_key = round( (y + h/2) / y_tolerance)

            if row_key not in rows_dict:
                rows_dict[row_key] = []
            rows_dict[row_key].append({'x': x, 'text': text})

        # Sort rows by their key (approximated Y position)
        sorted_row_keys = sorted(rows_dict.keys())

        # Sort cells within each row by X coordinate
        structured_rows = []
        for key in sorted_row_keys:
            row_cells = sorted(rows_dict[key], key=lambda c: c['x'])
            structured_rows.append([cell['text'] for cell in row_cells])

        # Basic header detection: Assume the first row is the header
        # More advanced: Check for financial keywords, different formatting, etc.
        header = []
        rows = []
        if structured_rows:
            potential_header = structured_rows[0]
            # Simple check: does it contain any financial keywords?
            has_financial_keyword = any(
                re.search(fh_pattern, cell_text, re.IGNORECASE)
                for cell_text in potential_header
                for fh_pattern in self.financial_headers
            )
            # Simple check: is it significantly different from the next row (e.g., fewer numbers)?
            is_different = True
            if len(structured_rows) > 1:
                 num_numeric_header = sum(1 for cell in potential_header if re.match(self.number_pattern, cell.replace(',','')))
                 num_numeric_row1 = sum(1 for cell in structured_rows[1] if re.match(self.number_pattern, cell.replace(',','')))
                 if abs(num_numeric_header - num_numeric_row1) < len(potential_header) * 0.5: # Heuristic
                      is_different = False


            # Assume header if it has keywords or looks different enough
            if has_financial_keyword or is_different:
                 header = potential_header
                 rows = structured_rows[1:]
                 self.logger.debug("Detected header based on keywords or difference from first row.")
            else:
                 # No clear header detected, treat all as rows
                 header = [] # Or create generic header like ['Col1', 'Col2', ...]
                 rows = structured_rows
                 self.logger.debug("No clear header detected, treating all rows as data.")

        # Ensure all rows have the same number of columns (pad if necessary)
        max_cols = len(header) if header else 0
        if rows:
            max_cols = max(max_cols, max(len(row) for row in rows))

        if header and len(header) < max_cols:
             header.extend([''] * (max_cols - len(header)))
        for i in range(len(rows)):
             if len(rows[i]) < max_cols:
                 rows[i].extend([''] * (max_cols - len(rows[i])))


        return {"header": header, "rows": rows}


    def _identify_tables_in_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Attempt to identify table structures within raw OCR text.
        This is a heuristic approach.

        Args:
            text: Full text extracted from an image/page.

        Returns:
            List of dictionaries, each representing a potential table
            with 'header' and 'rows'.
        """
        tables = []
        lines = text.splitlines()

        potential_table_lines = []
        in_table = False
        min_cols = 2 # Minimum columns to be considered a table
        min_rows = 3 # Minimum rows (including potential header)

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                # Blank line often signifies end of a table
                if in_table and len(potential_table_lines) >= min_rows:
                    processed = self._process_text_lines_as_table(potential_table_lines, min_cols)
                    if processed:
                        tables.append(processed)
                potential_table_lines = []
                in_table = False
                continue

            # Heuristic: Look for lines with multiple distinct columns separated by spaces
            # Use a regex to find multiple sequences of non-space characters separated by 2+ spaces
            # Or simply count space-separated tokens
            columns = re.split(r'\s{2,}', line) # Split on 2 or more spaces
            if len(columns) >= min_cols:
                # Check if previous line also looked like a table row
                if i > 0 and len(re.split(r'\s{2,}', lines[i-1].strip())) >= min_cols:
                    in_table = True
                elif not in_table and len(potential_table_lines) == 0: # Start of potential table
                     # Check if it looks like a header (more text, fewer numbers?)
                     # This is tricky, maybe just start collecting
                     in_table = True

                if in_table:
                    potential_table_lines.append(line)
            else:
                # Line doesn't look like a table row
                if in_table and len(potential_table_lines) >= min_rows:
                    processed = self._process_text_lines_as_table(potential_table_lines, min_cols)
                    if processed:
                        tables.append(processed)
                potential_table_lines = []
                in_table = False

        # Process any remaining lines if we were in a table at the end
        if in_table and len(potential_table_lines) >= min_rows:
            processed = self._process_text_lines_as_table(potential_table_lines, min_cols)
            if processed:
                tables.append(processed)

        return tables

    def _process_text_lines_as_table(self, lines: List[str], min_cols: int) -> Optional[Dict[str, Any]]:
        """ Helper to structure lines identified as a potential table """
        table_rows = []
        num_cols = 0
        for line in lines:
            # Split conservatively first
            cols = re.split(r'\s{2,}', line.strip())
            if len(cols) >= min_cols:
                table_rows.append(cols)
                num_cols = max(num_cols, len(cols))
            # else: ignore lines that don't fit the column structure?

        if not table_rows:
            return None

        # Pad rows to have consistent column count
        for i in range(len(table_rows)):
            if len(table_rows[i]) < num_cols:
                table_rows[i].extend([''] * (num_cols - len(table_rows[i])))

        # Basic header detection (same logic as _process_table_data)
        header = []
        rows = []
        if table_rows:
            potential_header = table_rows[0]
            has_financial_keyword = any(
                re.search(fh_pattern, cell_text, re.IGNORECASE)
                for cell_text in potential_header
                for fh_pattern in self.financial_headers
            )
            is_different = True
            if len(table_rows) > 1:
                 num_numeric_header = sum(1 for cell in potential_header if re.match(self.number_pattern, cell.replace(',','')))
                 num_numeric_row1 = sum(1 for cell in table_rows[1] if re.match(self.number_pattern, cell.replace(',','')))
                 if abs(num_numeric_header - num_numeric_row1) < len(potential_header) * 0.5:
                      is_different = False

            if has_financial_keyword or is_different:
                 header = potential_header
                 rows = table_rows[1:]
            else:
                 header = []
                 rows = table_rows

        return {"header": header, "rows": rows}

# Example Usage (optional, for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Starting EnhancedTableExtractor example")

    # Create dummy dependencies if they don't exist
    os.makedirs("test_outputs", exist_ok=True)
    dummy_pdf_path = "test_dummy.pdf"

    # Create a simple dummy PDF if it doesn't exist (requires reportlab)
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch

        if not os.path.exists(dummy_pdf_path):
             logger.info(f"Creating dummy PDF: {dummy_pdf_path}")
             c = canvas.Canvas(dummy_pdf_path, pagesize=letter)
             textobject = c.beginText(inch, 10*inch)
             textobject.textLine("Page 1: Some text before the table.")
             textobject.textLine("")
             textobject.textLine("Header A | Header B | Header C")
             textobject.textLine("-------------------------------")
             textobject.textLine("Row 1 A  | 123.45   | Item 1")
             textobject.textLine("Row 1 B  | 67.8     | Item 2")
             textobject.textLine("Row 1 C  | 90       | Item 3")
             textobject.textLine("")
             textobject.textLine("Some text after the table.")
             c.drawText(textobject)
             c.showPage()
             textobject = c.beginText(inch, 10*inch)
             textobject.textLine("Page 2: Another table")
             textobject.textLine("")
             textobject.textLine("שם נייר | כמות | מחיר")
             textobject.textLine("---------|------|------")
             textobject.textLine("תעודה א  | 100  | 50.5")
             textobject.textLine("תעודה ב  | 200  | 25.0")
             c.drawText(textobject)
             c.save()
             logger.info(f"Dummy PDF created.")

    except ImportError:
        logger.warning("reportlab not installed. Cannot create dummy PDF. Please create 'test_dummy.pdf' manually for testing.")
        # Exit if no PDF exists? Or just skip extraction test.
        if not os.path.exists(dummy_pdf_path):
             logger.error("No dummy PDF found and reportlab not available. Exiting example.")
             exit()


    # Initialize extractor
    extractor = EnhancedTableExtractor(language="eng+heb") # Add heb for Hebrew example

    # Extract tables from the dummy PDF
    logger.info(f"Extracting tables from: {dummy_pdf_path}")
    extracted_data = extractor.extract_tables_from_pdf(dummy_pdf_path)

    # Print results
    if extracted_data:
        logger.info("Extraction Results:")
        for page_idx, tables in extracted_data.items():
            logger.info(f"--- Page {page_idx + 1} ---")
            for i, table in enumerate(tables):
                logger.info(f"  Table {i+1} (Method: {table['extraction_method']}, BBox: {table.get('bbox', 'N/A')})")
                df = pd.DataFrame(table['rows'], columns=table['header'] if table['header'] else None)
                logger.info(f"\n{df.to_string(index=False)}\n")
                # Save to CSV for inspection
                output_csv = f"test_outputs/page_{page_idx+1}_table_{i+1}.csv"
                df.to_csv(output_csv, index=False, encoding='utf-8-sig')
                logger.info(f"Table saved to {output_csv}")
    else:
        logger.warning("No tables extracted.")

    logger.info("EnhancedTableExtractor example finished.")