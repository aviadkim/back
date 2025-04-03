import cv2
import numpy as np
from PIL import Image
import pandas as pd
import logging
import io
import pytesseract # Added import for cell text extraction

logger = logging.getLogger(__name__)

class EnhancedTableDetector:
    """Enhanced table detection using computer vision techniques."""
    
    def __init__(self, config=None):
        """Initialize the table detector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.min_table_area = self.config.get('min_table_area', 10000)  # Increased minimum area
        self.line_min_width = self.config.get('line_min_width', 15)   # Minimum line width to detect
        self.line_max_width = self.config.get('line_max_width', 1000) # Maximum line width to detect
        self.min_columns = self.config.get('min_columns', 2)          # Minimum columns to consider as table
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialized EnhancedTableDetector")
        
    def detect_tables(self, image):
        """Detect tables in an image.
        
        Args:
            image: PIL Image or path to image
            
        Returns:
            List of detected table regions as (x, y, w, h) tuples
        """
        # Convert PIL Image to OpenCV format if needed
        if isinstance(image, str):
            cv_image = cv2.imread(image)
            if cv_image is None:
                self.logger.error(f"Failed to read image from path: {image}")
                return []
        elif isinstance(image, Image.Image):
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
             # Assuming image is already an OpenCV image (numpy array)
            cv_image = image

        if cv_image is None or cv_image.size == 0:
            self.logger.error("Invalid image provided for table detection.")
            return []

        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Dilate to connect nearby text - Use smaller kernel for less merging
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)) # Smaller kernel
        dilated = cv2.dilate(thresh, kernel, iterations=2) # Fewer iterations
        
        # Find horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.line_min_width, 1)) # Use min_width
        detect_horizontal = cv2.morphologyEx(dilated, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        cnts_horizontal = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts_horizontal = cnts_horizontal[0] if len(cnts_horizontal) == 2 else cnts_horizontal[1]
        
        # Find vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, self.line_min_width)) # Use min_width
        detect_vertical = cv2.morphologyEx(dilated, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        cnts_vertical = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts_vertical = cnts_vertical[0] if len(cnts_vertical) == 2 else cnts_vertical[1]
        
        # Create mask for table regions by combining horizontal and vertical lines
        mask = np.zeros_like(gray)
        
        # Draw horizontal lines on mask
        for c in cnts_horizontal:
             cv2.drawContours(mask, [c], -1, 255, 2) # Thickness 2
        
        # Draw vertical lines on mask
        for c in cnts_vertical:
             cv2.drawContours(mask, [c], -1, 255, 2) # Thickness 2
        
        # Combine horizontal and vertical masks
        combined_mask = cv2.add(detect_horizontal, detect_vertical)

        # Dilate mask to connect nearby lines and form table boundaries
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)) # Moderate kernel
        mask = cv2.dilate(combined_mask, kernel, iterations=3) # Moderate iterations
        
        # Find contours in mask - these are potential tables
        cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        
        # Filter contours to find tables
        table_regions = []
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            area = w * h
            aspect_ratio = w / float(h) if h > 0 else 0
            
            # Check if region is likely a table (area and aspect ratio checks)
            # Adjust aspect ratio constraints if needed
            if area > self.min_table_area and 0.1 < aspect_ratio < 10:
                # Check if region has enough columns (using a refined check)
                roi = gray[y:y+h, x:x+w]
                if self._count_columns(roi) >= self.min_columns:
                    table_regions.append((x, y, w, h))
        
        self.logger.info(f"Detected {len(table_regions)} potential tables")
        # Optional: Add merging overlapping regions logic here if needed
        return table_regions
    
    def extract_table_content(self, image, region):
        """Extract table content from a region using OCR.
        
        Args:
            image: PIL Image or OpenCV image
            region: Table region as (x, y, w, h) tuple
            
        Returns:
            Pandas DataFrame containing table data, or None if extraction fails
        """
        # Convert PIL Image to OpenCV format if needed
        if isinstance(image, Image.Image):
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        elif isinstance(image, str):
            cv_image = cv2.imread(image)
            if cv_image is None:
                self.logger.error(f"Failed to read image for table content extraction: {image}")
                return None
        else:
            cv_image = image # Assume OpenCV format

        if cv_image is None or cv_image.size == 0:
            self.logger.error("Invalid image provided for table content extraction.")
            return None

        # Extract region
        x, y, w, h = region
        # Add padding to region to capture borders if necessary
        padding = 5
        y_start = max(0, y - padding)
        y_end = min(cv_image.shape[0], y + h + padding)
        x_start = max(0, x - padding)
        x_end = min(cv_image.shape[1], x + w + padding)
        
        table_roi = cv_image[y_start:y_end, x_start:x_end]

        if table_roi.size == 0:
             self.logger.warning(f"Table ROI is empty for region {region}")
             return pd.DataFrame() # Return empty DataFrame

        # Convert to grayscale
        gray = cv2.cvtColor(table_roi, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding - experiment with different types
        # _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # Find cells in the table (Refined cell finding)
        cells = self._find_cells(thresh)
        
        if not cells:
            self.logger.warning(f"No cells found in table region {region}. Trying direct OCR on region.")
            # Fallback: Try OCR on the whole region if no cells are found
            try:
                text = pytesseract.image_to_string(gray, config='--psm 6').strip()
                # Attempt to parse the text into a basic structure if possible
                lines = [line.split('\t') for line in text.split('\n') if line.strip()]
                if lines:
                    return pd.DataFrame(lines)
                else:
                    return pd.DataFrame()
            except Exception as e:
                self.logger.error(f"Fallback OCR failed for region {region}: {e}")
                return pd.DataFrame()


        # Extract text from each cell
        table_data = self._extract_cells_text(gray, cells)
        
        return table_data
    
    def _count_columns(self, roi):
        """Count number of columns in a table region based on vertical lines."""
        if roi is None or roi.size == 0:
            return 0
        # Threshold
        # _, thresh = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        thresh = cv2.adaptiveThreshold(roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # Find vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, roi.shape[0] // 4)) # Adjust kernel height
        detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        
        # Count vertical lines (contours)
        cnts = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        
        # Filter contours that are likely column separators
        column_lines = 0
        min_line_height = roi.shape[0] * 0.3 # Line must be at least 30% of ROI height
        for c in cnts:
            _, _, _, h = cv2.boundingRect(c)
            if h > min_line_height:
                column_lines += 1

        # Number of columns is typically number of separators + 1
        # However, this can be unreliable. Consider alternative methods if needed.
        # For now, return line count + 1 as a proxy for columns.
        return column_lines + 1
    
    def _find_cells(self, thresh):
        """Find cells in a table based on intersecting lines."""
        # Find horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (thresh.shape[1] // 10, 1)) # Adjust kernel width
        horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        
        # Find vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, thresh.shape[0] // 10)) # Adjust kernel height
        vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        
        # Combine lines to form grid
        table_grid = cv2.add(horizontal_lines, vertical_lines)
        
        # Dilate grid lines slightly
        kernel = np.ones((3, 3), np.uint8)
        table_grid = cv2.dilate(table_grid, kernel, iterations=1)
        
        # Find contours of the grid intersections (potential cell corners)
        # This approach is complex. Alternative: Find contours in the inverted grid.
        
        # Invert grid to get potential cell areas
        inverted_grid = cv2.bitwise_not(table_grid)
        # Erode slightly to separate cells that might be connected
        inverted_grid = cv2.erode(inverted_grid, kernel, iterations=1)

        # Find contours of potential cells
        cnts = cv2.findContours(inverted_grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        
        # Get cell bounding boxes
        cell_boxes = []
        min_cell_width = 10
        min_cell_height = 5
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            # Filter out very small regions
            if w > min_cell_width and h > min_cell_height:
                cell_boxes.append((x, y, w, h))
        
        # Add logic here to merge overlapping boxes or refine cell boundaries if needed
        
        return cell_boxes
    
    def _extract_cells_text(self, image, cells):
        """Extract text from table cells using OCR.
        
        Args:
            image: Grayscale image containing the table ROI
            cells: List of cell bounding boxes (x, y, w, h) relative to the ROI
            
        Returns:
            Pandas DataFrame with extracted text
        """
        if not cells:
            return pd.DataFrame()

        # Sort cells primarily by y-coordinate (top-to-bottom), then x-coordinate (left-to-right)
        # Add a tolerance for y-coordinate to group cells in the same row
        y_tolerance = 10
        sorted_cells = sorted(cells, key=lambda box: (round(box[1] / y_tolerance), box[0]))
        
        # Determine rows and columns structure
        rows_data = []
        current_row = []
        if sorted_cells:
            current_y = round(sorted_cells[0][1] / y_tolerance)
            for cell in sorted_cells:
                cell_y = round(cell[1] / y_tolerance)
                if cell_y == current_y:
                    current_row.append(cell)
                else:
                    # Sort cells within the completed row by x-coordinate
                    rows_data.append(sorted(current_row, key=lambda box: box[0]))
                    current_row = [cell]
                    current_y = cell_y
            # Add the last row
            rows_data.append(sorted(current_row, key=lambda box: box[0]))

        if not rows_data:
            return pd.DataFrame()
            
        # Get the maximum number of columns found in any row
        max_cols = max(len(row) for row in rows_data) if rows_data else 0
        
        # Initialize data structure for DataFrame
        data = []
        
        # Use OCR to extract text from each cell
        for row_idx, row in enumerate(rows_data):
            row_text = [""] * max_cols # Initialize row with empty strings
            for col_idx, (x, y, w, h) in enumerate(row):
                if col_idx < max_cols:
                    # Extract cell ROI from the grayscale image
                    # Add a small padding to avoid cutting off characters at borders
                    pad = 2
                    cell_roi = image[max(0, y-pad):min(image.shape[0], y+h+pad), 
                                     max(0, x-pad):min(image.shape[1], x+w+pad)]
                    
                    if cell_roi.size == 0:
                        text = ""
                    else:
                        # Use pytesseract to extract text - specify language if known
                        # Use --psm 6 for assuming a single uniform block of text, or 7 for single line
                        try:
                            # Preprocess cell ROI slightly if needed (e.g., thresholding)
                            _, cell_thresh = cv2.threshold(cell_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                            text = pytesseract.image_to_string(cell_thresh, config='--psm 7').strip()
                            # Basic text cleaning
                            text = text.replace('\n', ' ').replace('\r', '') 
                        except Exception as e:
                            self.logger.warning(f"Error extracting text from cell ({row_idx},{col_idx}): {str(e)}")
                            text = ""
                    row_text[col_idx] = text
            data.append(row_text)
        
        # Create DataFrame, attempt to use first row as header if appropriate
        try:
            df = pd.DataFrame(data)
            # Optional: Heuristic to detect header row and set it
            # if len(df) > 1 and all(isinstance(c, str) and c for c in df.iloc[0]):
            #     df.columns = df.iloc[0]
            #     df = df[1:].reset_index(drop=True)
        except Exception as e:
            self.logger.error(f"Error creating DataFrame from extracted cells: {e}")
            return pd.DataFrame() # Return empty DataFrame on error

        return df