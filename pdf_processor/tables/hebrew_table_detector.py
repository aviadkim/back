import numpy as np
import cv2
import pandas as pd
import logging
from typing import List, Dict, Any, Tuple, Optional
import pytesseract
from pytesseract import Output
import re
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)

class HebrewTableDetector:
    """
    Specialized detector for financial tables in Hebrew documents.
    Focuses on identifying tables based on structure and Hebrew financial keywords.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Hebrew table detector.

        Args:
            config: Configuration options
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Language configuration - primarily Hebrew, but include English for mixed content
        self.language = self.config.get('language', 'heb+eng')

        # Detection parameters (can be tuned via config)
        self.min_table_area_ratio = self.config.get('min_table_area_ratio', 0.02) # Slightly smaller threshold
        self.line_min_width = self.config.get('line_min_width', 20)
        self.line_max_width = self.config.get('line_max_width', 1000)
        self.line_min_height = self.config.get('line_min_height', 20)
        self.line_max_height = self.config.get('line_max_height', 1000)
        self.text_alignment_row_threshold = self.config.get('text_alignment_row_threshold', 3) # Min rows for text alignment detection
        self.text_alignment_col_threshold = self.config.get('text_alignment_col_threshold', 2) # Min cols for text alignment detection


        # OCR configuration
        self.psm = self.config.get('psm', 6)  # Assume a single uniform block of text by default

        # Hebrew financial table patterns (more comprehensive)
        self.financial_headers_heb = [
            r'מס"ד', r'סה"כ', r'סך הכל', r'יתרה', r'סכום', r'עלות', r'שער', r'מטבע',
            r'תאריך', r'תשואה', r'אחוז', r'כמות', r'שווי', r'מחיר', r'נייר', r'תיאור',
            r'חשבון', r'סוג נייר', r'אסמכתא', r'ת\.ערך', r'ני"ע', r'תנועה', r'ריבית',
            r'קרן', r'הצמדה', r'עמלה', r'מספר', r'פירוט', r'מזהה', r'קוד', r'שם',
            r'ערך נקוב', r'מח"מ', r'דירוג'
        ]
        # Add common English terms often found in Hebrew financial docs
        self.financial_headers_eng = [
            r'no\.', r'total', r'balance', r'amount', r'cost', r'rate', r'currency',
            r'date', r'yield', r'percent', r'quantity', r'value', r'price', r'security',
            r'description', r'account', r'type', r'reference', r'isin', r'name', r'id',
            r'code', r'interest', r'commission', r'principal', r'linkage', r'rating'
        ]
        self.all_financial_headers = self.financial_headers_heb + self.financial_headers_eng
        # Compile regex for efficiency
        self.financial_header_pattern = re.compile(
            '|'.join(self.all_financial_headers),
            re.IGNORECASE
        )

        # Pattern for typical numeric values in financial tables (allows commas, periods, %)
        self.numeric_pattern = re.compile(r'^-?[\d,]+(?:\.\d+)?%?$')
        # Pattern for ISIN
        self.isin_pattern = re.compile(r'\b[A-Z]{2}[A-Z0-9]{9}[0-9]\b')


    def detect_tables(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect financial tables in an image.

        Args:
            image: NumPy array containing the image

        Returns:
            List of detected tables with metadata
        """
        try:
            # Preprocess the image
            processed_image, gray_image = self._preprocess_image(image)

            # Detect table regions using multiple strategies
            table_regions_lines = self._detect_table_regions_by_lines(processed_image, image.shape)
            table_regions_text = self._detect_tables_by_text_alignment(processed_image)

            # Combine and deduplicate regions (simple overlap check for now)
            all_regions = self._combine_regions(table_regions_lines, table_regions_text)
            self.logger.info(f"Detected {len(all_regions)} potential table regions.")


            tables = []
            for i, region in enumerate(all_regions):
                x, y, w, h = region
                self.logger.debug(f"Processing region {i}: bbox=({x}, {y}, {w}, {h})")

                # Extract the table region from the original grayscale image for OCR
                table_img_gray = gray_image[y:y+h, x:x+w]

                # Process table region to extract structure and content using OCR
                table_data = self._process_table_region_ocr(table_img_gray)

                # Basic validation: check if OCR returned reasonable data
                if not table_data or (not table_data.get("header") and not table_data.get("rows")):
                    self.logger.debug(f"Skipping region {i} due to lack of extracted data.")
                    continue

                # Verify if it's likely a financial table based on content
                is_financial, financial_score = self._is_financial_table(table_data)

                # Estimate confidence based on detection method and financial score
                # (This is a simple heuristic, could be improved)
                confidence = financial_score
                if region in table_regions_lines: confidence += 0.1 # Slightly higher confidence if lines detected
                confidence = min(1.0, confidence) # Cap at 1.0


                table_info = {
                    "id": f"heb-{i}", # Unique ID prefix
                    "bbox": [x, y, x+w, y+h],
                    "is_financial": is_financial,
                    "direction": self._detect_table_direction(table_data), # Detect RTL/LTR
                    "header": table_data.get("header", []),
                    "rows": table_data.get("rows", []),
                    "row_count": len(table_data.get("rows", [])),
                    "col_count": len(table_data.get("header", [])) if table_data.get("header") else
                                (len(table_data.get("rows", [[]])[0]) if table_data.get("rows") else 0),
                    "confidence": round(confidence, 2)
                }
                # Add header row to row_count if header exists
                if table_info["header"]:
                    table_info["row_count"] += 1

                # Only add if table has minimum dimensions and some confidence
                if table_info["row_count"] >= 2 and table_info["col_count"] >= 2 and table_info["confidence"] > 0.2:
                    tables.append(table_info)
                    self.logger.debug(f"Added Hebrew table {i} (Financial: {is_financial}, Confidence: {confidence:.2f})")
                else:
                     self.logger.debug(f"Skipping Hebrew table {i} due to small dimensions or low confidence.")


            return tables

        except Exception as e:
            self.logger.error(f"Error detecting Hebrew tables: {str(e)}", exc_info=True)
            return []

    def _preprocess_image(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess image for table detection.

        Args:
            image: Input image

        Returns:
            Tuple: (Preprocessed binary image, Grayscale image)
        """
        # Convert to grayscale
        if len(image.shape) == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif len(image.shape) == 3 and image.shape[2] == 4: # Handle RGBA
            gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        else:
            gray = image.copy() # Assume already grayscale

        # Apply adaptive thresholding (Gaussian works well generally)
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, # Invert: Text becomes white, background black
            11, # Block size (needs to be odd)
            2   # Constant subtracted from the mean
        )

        # Noise removal using morphological opening
        kernel_size = 2 # Small kernel for fine noise
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        binary_opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

        return binary_opened, gray

    def _detect_table_regions_by_lines(self, binary_image: np.ndarray, original_shape: Tuple[int, int, ...]) -> List[Tuple[int, int, int, int]]:
        """ Detect potential table regions using horizontal and vertical lines. """
        regions = []
        image_area = original_shape[0] * original_shape[1]
        min_table_area = image_area * self.min_table_area_ratio

        # Detect horizontal lines
        horizontal = binary_image.copy()
        h_kernel_size = max(self.line_min_width, min(self.line_max_width, original_shape[1] // 40)) # Relative size
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_kernel_size, 1))
        horizontal = cv2.morphologyEx(horizontal, cv2.MORPH_OPEN, h_kernel, iterations=1) # Use OPEN

        # Detect vertical lines
        vertical = binary_image.copy()
        v_kernel_size = max(self.line_min_height, min(self.line_max_height, original_shape[0] // 40)) # Relative size
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_kernel_size))
        vertical = cv2.morphologyEx(vertical, cv2.MORPH_OPEN, v_kernel, iterations=1) # Use OPEN

        # Combine lines (ADD is usually better than AND for finding the grid structure)
        combined = cv2.add(horizontal, vertical)

        # Find contours of the combined grid structure
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter based on area and aspect ratio
            if (w * h >= min_table_area and
                0.1 < w / (h + 1e-6) < 10): # Wider aspect ratio tolerance
                regions.append((x, y, w, h))

        self.logger.debug(f"Detected {len(regions)} regions using line detection.")
        return regions

    def _detect_tables_by_text_alignment(self, binary_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """ Detect tables by finding aligned text blocks (contours). """
        # Text is white in the preprocessed image (THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours: return []

        # Extract bounding boxes and filter small noise
        min_char_w = 5 # Heuristic minimum character width
        min_char_h = 8 # Heuristic minimum character height
        text_boxes = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > min_char_w * min_char_h * 0.5]
        text_boxes = [b for b in text_boxes if b[2] > min_char_w and b[3] > min_char_h]

        if not text_boxes: return []

        # Group boxes by rows using y-coordinate proximity
        text_boxes.sort(key=lambda box: box[1]) # Sort by Y first
        rows = []
        current_row = []
        if text_boxes:
            current_row.append(text_boxes[0])
            last_y = text_boxes[0][1] + text_boxes[0][3] / 2 # Use center y

            for box in text_boxes[1:]:
                box_center_y = box[1] + box[3] / 2
                # If vertical distance is small enough, consider it the same row
                if abs(box_center_y - last_y) < (box[3] * 0.7): # Tolerance based on box height
                    current_row.append(box)
                else:
                    if current_row: rows.append(sorted(current_row, key=lambda b: b[0])) # Sort row by X
                    current_row = [box]
                    last_y = box_center_y
            if current_row: rows.append(sorted(current_row, key=lambda b: b[0])) # Add last row


        # Identify potential table blocks (consecutive rows with enough columns)
        table_regions = []
        start_row_idx = 0
        for i in range(len(rows)):
            # Check if current row looks like part of a table
            is_table_row = len(rows[i]) >= self.text_alignment_col_threshold

            if is_table_row and i == start_row_idx: continue # Still in the potential table start

            if is_table_row and i > start_row_idx: # Continue potential table
                 pass
            else: # End of potential table block (or current row is not a table row)
                if i > start_row_idx and (i - start_row_idx) >= self.text_alignment_row_threshold:
                    # Found a block of potential table rows
                    table_rows_in_block = rows[start_row_idx:i]
                    all_boxes_in_block = [box for row in table_rows_in_block for box in row]
                    if all_boxes_in_block:
                        min_x = min(b[0] for b in all_boxes_in_block)
                        min_y = min(b[1] for b in all_boxes_in_block)
                        max_x = max(b[0] + b[2] for b in all_boxes_in_block)
                        max_y = max(b[1] + b[3] for b in all_boxes_in_block)
                        padding = 5 # Small padding
                        table_regions.append((
                            max(0, min_x - padding), max(0, min_y - padding),
                            min(binary_image.shape[1], max_x + padding) - max(0, min_x - padding),
                            min(binary_image.shape[0], max_y + padding) - max(0, min_y - padding)
                        ))
                # Reset start index for next potential block
                start_row_idx = i + 1


        # Check the last block
        if (len(rows) - start_row_idx) >= self.text_alignment_row_threshold:
             table_rows_in_block = rows[start_row_idx:]
             all_boxes_in_block = [box for row in table_rows_in_block for box in row]
             if all_boxes_in_block:
                 min_x = min(b[0] for b in all_boxes_in_block)
                 min_y = min(b[1] for b in all_boxes_in_block)
                 max_x = max(b[0] + b[2] for b in all_boxes_in_block)
                 max_y = max(b[1] + b[3] for b in all_boxes_in_block)
                 padding = 5
                 table_regions.append((
                     max(0, min_x - padding), max(0, min_y - padding),
                     min(binary_image.shape[1], max_x + padding) - max(0, min_x - padding),
                     min(binary_image.shape[0], max_y + padding) - max(0, min_y - padding)
                 ))

        self.logger.debug(f"Detected {len(table_regions)} regions using text alignment.")
        return table_regions

    def _combine_regions(self, regions1: List, regions2: List, overlap_threshold=0.5) -> List:
        """ Combine regions from different methods, removing significant overlaps. """
        all_regions = regions1 + regions2
        if not all_regions: return []

        # Sort by area (descending) to prioritize larger regions
        all_regions.sort(key=lambda r: r[2] * r[3], reverse=True)

        keep_regions = []
        for region in all_regions:
            is_overlapping = False
            x1, y1, w1, h1 = region
            for kept_region in keep_regions:
                x2, y2, w2, h2 = kept_region

                # Calculate intersection area
                xA = max(x1, x2)
                yA = max(y1, y2)
                xB = min(x1 + w1, x2 + w2)
                yB = min(y1 + h1, y2 + h2)
                intersection_area = max(0, xB - xA) * max(0, yB - yA)

                # Calculate overlap ratio relative to the smaller region
                area1 = w1 * h1
                area2 = w2 * h2
                min_area = min(area1, area2)

                if min_area > 0 and (intersection_area / min_area) > overlap_threshold:
                    is_overlapping = True
                    break # Overlaps significantly with an already kept region

            if not is_overlapping:
                keep_regions.append(region)

        self.logger.debug(f"Combined regions: {len(all_regions)} -> {len(keep_regions)} after deduplication.")
        # Sort final regions top-to-bottom, left-to-right
        keep_regions.sort(key=lambda r: (r[1], r[0]))
        return keep_regions


    def _process_table_region_ocr(self, table_image_gray: np.ndarray) -> Dict[str, Any]:
        """
        Extract table structure and text from a region using OCR (pytesseract).

        Args:
            table_image_gray: Grayscale image of the table region.

        Returns:
            Dictionary with 'header', 'rows'.
        """
        try:
            # Use pytesseract to get detailed OCR data including bounding boxes
            # PSM 6: Assume a single uniform block of text. Good for tables.
            # PSM 4: Assume a single column of text of variable sizes. Might be better?
            # PSM 11: Sparse text. Find as much text as possible in no particular order.
            # PSM 12: Sparse text with OSD.
            # Let's try PSM 6 first, maybe fallback to 11 or 4 if needed.
            ocr_config = f'--psm {self.psm} --oem 3 -l {self.language}'
            ocr_data = pytesseract.image_to_data(table_image_gray, config=ocr_config, output_type=Output.DICT)

            # Process OCR data into cells/rows
            n_boxes = len(ocr_data['level'])
            cells = []
            min_conf = 40 # Minimum confidence score to consider a word

            for i in range(n_boxes):
                if int(ocr_data['conf'][i]) > min_conf and ocr_data['text'][i].strip():
                    (x, y, w, h) = (ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i])
                    text = ocr_data['text'][i].strip()
                    cells.append({'bbox': (x, y, w, h), 'text': text})

            if not cells: return {}

            # Group cells into rows based on vertical position (similar to text alignment)
            cells.sort(key=lambda c: c['bbox'][1]) # Sort by Y
            rows_dict = {}
            avg_h = sum(c['bbox'][3] for c in cells) / len(cells) if cells else 10
            y_tolerance = avg_h * 0.6 # Tolerance for row grouping

            for cell in cells:
                x, y, w, h = cell['bbox']
                row_key = round((y + h/2) / y_tolerance) # Group by center y +/- tolerance

                if row_key not in rows_dict: rows_dict[row_key] = []
                rows_dict[row_key].append(cell)

            # Sort rows by key (Y position) and cells within rows by X position
            sorted_row_keys = sorted(rows_dict.keys())
            structured_rows_data = []
            for key in sorted_row_keys:
                row_cells = sorted(rows_dict[key], key=lambda c: c['bbox'][0])
                # Combine text of cells that might belong to the same column entry
                # This needs a more sophisticated column detection logic.
                # Simple approach for now: just take the text.
                structured_rows_data.append([cell['text'] for cell in row_cells])


            # Basic Header Detection (first row) - can be improved
            header = []
            rows = []
            if structured_rows_data:
                # Simple heuristic: Assume first row is header if it contains financial keywords
                # or fewer numbers than the next row.
                potential_header = structured_rows_data[0]
                is_likely_header = False
                if any(self.financial_header_pattern.search(cell) for cell in potential_header):
                    is_likely_header = True
                elif len(structured_rows_data) > 1:
                    num_numeric_header = sum(1 for cell in potential_header if self.numeric_pattern.match(cell.replace(',','')))
                    num_numeric_row1 = sum(1 for cell in structured_rows_data[1] if self.numeric_pattern.match(cell.replace(',','')))
                    # Header likely has fewer numbers than data rows
                    if num_numeric_header < len(potential_header) * 0.5 and num_numeric_header < num_numeric_row1:
                         is_likely_header = True


                if is_likely_header:
                    header = potential_header
                    rows = structured_rows_data[1:]
                else:
                    header = [] # No header detected
                    rows = structured_rows_data

            # Pad rows to ensure consistent column count based on max row length or header length
            max_cols = len(header)
            if rows: max_cols = max(max_cols, max(len(r) for r in rows))

            if header and len(header) < max_cols: header.extend([''] * (max_cols - len(header)))
            for i in range(len(rows)):
                if len(rows[i]) < max_cols: rows[i].extend([''] * (max_cols - len(rows[i])))


            return {"header": header, "rows": rows}

        except pytesseract.TesseractNotFoundError:
            self.logger.error("Tesseract is not installed or not in PATH.")
            return {}
        except Exception as e:
            self.logger.error(f"Error during OCR processing of table region: {e}", exc_info=True)
            return {}


    def _is_financial_table(self, table_data: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Check if the extracted table data likely represents a financial table.
        Returns a boolean and a confidence score (0.0 - 1.0).
        """
        header = table_data.get("header", [])
        rows = table_data.get("rows", [])
        if not header and not rows: return False, 0.0

        financial_header_matches = 0
        total_header_cells = len(header)
        if total_header_cells > 0:
            for cell in header:
                if self.financial_header_pattern.search(cell):
                    financial_header_matches += 1
            header_score = financial_header_matches / total_header_cells
        else:
            header_score = 0.0 # No header, lower confidence


        numeric_cells = 0
        isin_cells = 0
        total_data_cells = sum(len(row) for row in rows)

        if total_data_cells > 0:
            for row in rows:
                for cell in row:
                    cell_str = str(cell).strip()
                    if self.numeric_pattern.match(cell_str.replace(',','')): # Check for numbers (ignore commas)
                        numeric_cells += 1
                    elif self.isin_pattern.match(cell_str): # Check for ISINs
                         isin_cells += 1

            numeric_ratio = numeric_cells / total_data_cells
            isin_ratio = isin_cells / total_data_cells
        else:
            numeric_ratio = 0.0
            isin_ratio = 0.0

        # Combine scores (weights can be adjusted)
        # Higher weight for headers, significant weight for numeric data or ISINs
        score = (header_score * 0.5) + (numeric_ratio * 0.4) + (isin_ratio * 0.6)
        # Boost score slightly if both header and numeric/ISIN data are present
        if header_score > 0.2 and (numeric_ratio > 0.1 or isin_ratio > 0):
             score += 0.1


        score = min(1.0, score) # Cap score at 1.0
        is_financial = score > 0.3 # Threshold for classifying as financial

        self.logger.debug(f"Financial table check: HeaderScore={header_score:.2f}, NumericRatio={numeric_ratio:.2f}, IsinRatio={isin_ratio:.2f} -> FinalScore={score:.2f}")

        return is_financial, score


    def _detect_table_direction(self, table_data: Dict[str, Any]) -> str:
        """
        Detect if the table content is primarily Right-to-Left (Hebrew) or Left-to-Right.
        """
        header = table_data.get("header", [])
        rows = table_data.get("rows", [])
        all_text = " ".join(header) + " " + " ".join(" ".join(map(str, row)) for row in rows)

        if not all_text.strip(): return "ltr" # Default to LTR if no text

        # Count Hebrew characters vs Latin characters
        hebrew_chars = len(re.findall(r'[\u0590-\u05FF]', all_text))
        latin_chars = len(re.findall(r'[a-zA-Z]', all_text))

        # Simple heuristic: if Hebrew characters dominate, assume RTL
        if hebrew_chars > latin_chars * 1.5: # Require significantly more Hebrew
            return "rtl"
        else:
            return "ltr"


# Example Usage (Optional)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Starting HebrewTableDetector example")

    # --- Create a dummy PDF with Hebrew text and a table ---
    dummy_pdf_path = "test_hebrew_dummy.pdf"
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_RIGHT # Import for text alignment

        # Register a Hebrew font (ensure you have a Hebrew TTF file, e.g., Arial)
        # Adjust font path as needed
        try:
             # Try common locations or a specific path
             hebrew_font_path = "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf" # Example Linux path
             if not os.path.exists(hebrew_font_path):
                  hebrew_font_path = "C:/Windows/Fonts/arial.ttf" # Example Windows path
             if not os.path.exists(hebrew_font_path):
                  # Fallback or raise error
                  raise FileNotFoundError("Arial.ttf not found in common locations.")

             pdfmetrics.registerFont(TTFont('HebrewArial', hebrew_font_path))
             styles = getSampleStyleSheet()
             # Create a right-aligned style using the Hebrew font
             style_right = styles['Normal']
             style_right.fontName = 'HebrewArial'
             style_right.alignment = TA_RIGHT
             style_body = styles['BodyText']
             style_body.fontName = 'HebrewArial'
             style_body.alignment = TA_RIGHT

             logger.info(f"Registered Hebrew font from: {hebrew_font_path}")
             heb_font_registered = True
        except Exception as font_err:
             logger.warning(f"Could not register Hebrew font: {font_err}. Hebrew text in PDF might not render correctly.")
             heb_font_registered = False
             # Use default styles if font registration failed
             styles = getSampleStyleSheet()
             style_right = styles['Normal']
             style_body = styles['BodyText']


        logger.info(f"Creating dummy Hebrew PDF: {dummy_pdf_path}")
        doc = SimpleDocTemplate(dummy_pdf_path, pagesize=letter)
        story = []

        # Add some Hebrew text (reversed for ReportLab)
        heb_text1 = ".םלועב םולש" # Shalom Ba'olam
        heb_text2 = ".תירבעב הקידב תגצומ הז" # Zeh matzgat bdika be'ivrit
        if heb_font_registered:
             story.append(Paragraph(heb_text1[::-1], style_right))
             story.append(Spacer(1, 0.2*inch))
             story.append(Paragraph(heb_text2[::-1], style_body))
             story.append(Spacer(1, 0.5*inch))
        else:
             story.append(Paragraph("Shalom Ba'olam (Hebrew Font Missing)", styles['Normal']))
             story.append(Spacer(1, 0.2*inch))
             story.append(Paragraph("Zeh matzgat bdika be'ivrit (Hebrew Font Missing)", styles['BodyText']))
             story.append(Spacer(1, 0.5*inch))


        # Create table data with Hebrew headers (reversed for ReportLab)
        table_data = [
            ['"כיס'[::-1], '"רואית'[::-1], '"שמ'[::-1]], # Header: שם, תיאור, סכום
            ['543,210', 'ב תנועה'[::-1], 'א קלח'[::-1]], # Row 1: חלק א, תנועה ב, 10,234.5
            ['12,000', 'א תנועה'[::-1], 'ב קלח'[::-1]], # Row 2: חלק ב, תנועה א, 12,000
            ['1,245,210', '"הכ סה'[::-1], ''] # Row 3: '', סה"כ, 1,245,210
        ]

        # Apply styles to table data if font is available
        if heb_font_registered:
             styled_table_data = []
             for row in table_data:
                  styled_row = [Paragraph(str(cell)[::-1] if isinstance(cell, str) and re.search(r'[\u0590-\u05FF]', cell) else str(cell), style_right) for cell in row]
                  styled_table_data.append(styled_row)
             table_data_to_use = styled_table_data
        else:
             # Use plain text if font failed
             table_data_to_use = [
                 ['Sum', 'Description', 'Name'],
                 ['10,234.50', 'Movement B', 'Part A'],
                 ['12,000.00', 'Movement A', 'Part B'],
                 ['1,245,210', 'Total', '']
             ]


        # Create table object
        table = Table(table_data_to_use, colWidths=[1.5*inch, 3*inch, 1.5*inch])

        # Add style to the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT' if heb_font_registered else 'CENTER'), # Right align for Hebrew
            ('FONTNAME', (0, 0), (-1, 0), 'HebrewArial' if heb_font_registered else 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'HebrewArial' if heb_font_registered else 'Helvetica'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(table)
        doc.build(story)
        logger.info(f"Dummy Hebrew PDF created.")

    except ImportError:
        logger.error("reportlab not installed. Cannot create dummy Hebrew PDF.")
        exit()
    except FileNotFoundError as fnf_err:
         logger.error(f"Font file error: {fnf_err}. Cannot create PDF with Hebrew.")
         exit()
    except Exception as pdf_err:
        logger.error(f"Failed to create dummy Hebrew PDF: {pdf_err}", exc_info=True)
        exit()


    # --- Detect tables in the dummy PDF ---
    try:
        # Convert PDF page to image
        images = convert_from_path(dummy_pdf_path, dpi=300)
        if not images:
            logger.error("Failed to convert PDF to image.")
            exit()

        image = np.array(images[0])

        # Initialize detector
        detector = HebrewTableDetector()

        # Detect tables
        logger.info("Detecting tables in the dummy image...")
        detected_tables = detector.detect_tables(image)

        # Print results
        if detected_tables:
            logger.info(f"Detected {len(detected_tables)} tables:")
            for i, table in enumerate(detected_tables):
                logger.info(f"--- Table {i+1} ---")
                logger.info(f"  BBox: {table['bbox']}")
                logger.info(f"  Financial: {table['is_financial']}")
                logger.info(f"  Confidence: {table['confidence']}")
                logger.info(f"  Direction: {table['direction']}")
                logger.info(f"  Header: {table['header']}")
                # logger.info(f"  Rows: {table['rows']}") # Can be verbose
                logger.info(f"  Dimensions: {table['row_count']} rows x {table['col_count']} cols")
                # Optionally save table region image
                # x, y, w, h = table['bbox']
                # cv2.imwrite(f"test_hebrew_table_{i+1}.png", image[y:y+h, x:x+w])
        else:
            logger.warning("No tables detected.")

    except Exception as detect_err:
        logger.error(f"Error during table detection: {detect_err}", exc_info=True)


    logger.info("HebrewTableDetector example finished.")