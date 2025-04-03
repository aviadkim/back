import cv2
import numpy as np
from PIL import Image
import pandas as pd
import logging
import io

logger = logging.getLogger(__name__)

class EnhancedTableDetector:
    """Enhanced table detection using computer vision techniques."""

    def __init__(self, config=None):
        """Initialize the table detector.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.min_table_area = self.config.get('min_table_area', 100)  # Minimum area to consider as table
        self.line_min_width = self.config.get('line_min_width', 15)   # Minimum line width to detect
        self.line_max_width = self.config.get('line_max_width', 1000) # Maximum line width to detect
        self.min_columns = self.config.get('min_columns', 2)          # Minimum columns to consider as table

    def detect_tables(self, image):
        """Detect tables in an image.

        Args:
            image: PIL Image or path to image

        Returns:
            List of detected table regions as (x, y, w, h) tuples
        """
        # Convert PIL Image to OpenCV format if needed
        if isinstance(image, str):
            image = cv2.imread(image)
        elif isinstance(image, Image.Image):
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Threshold the image
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        # Find horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.line_max_width, 1))
        detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        cnts_horizontal = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts_horizontal = cnts_horizontal[0] if len(cnts_horizontal) == 2 else cnts_horizontal[1]

        # Find vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, self.line_max_width))
        detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        cnts_vertical = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts_vertical = cnts_vertical[0] if len(cnts_vertical) == 2 else cnts_vertical[1]

        # Create mask for table regions
        mask = np.zeros(image.shape[:2], dtype=np.uint8)

        # Draw horizontal lines
        for c in cnts_horizontal:
            cv2.drawContours(mask, [c], -1, 255, 2)

        # Draw vertical lines
        for c in cnts_vertical:
            cv2.drawContours(mask, [c], -1, 255, 2)

        # Dilate mask to connect nearby lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
        mask = cv2.dilate(mask, kernel, iterations=4)

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
            if area > self.min_table_area and 0.2 < aspect_ratio < 5:
                # Check if region has enough columns
                roi = gray[y:y+h, x:x+w]
                if self._count_columns(roi) >= self.min_columns:
                    table_regions.append((x, y, w, h))

        return table_regions

    def extract_table_content(self, image, region):
        """Extract table content from a region.

        Args:
            image: PIL Image or OpenCV image
            region: Table region as (x, y, w, h) tuple

        Returns:
            Pandas DataFrame containing table data
        """
        # Convert PIL Image to OpenCV format if needed
        if isinstance(image, Image.Image):
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        elif isinstance(image, str):
            cv_image = cv2.imread(image)
        else:
            cv_image = image

        # Extract region
        x, y, w, h = region
        table_roi = cv_image[y:y+h, x:x+w]

        # Convert to grayscale
        gray = cv2.cvtColor(table_roi, cv2.COLOR_BGR2GRAY)

        # Threshold
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        # Find cells in the table
        cells = self._find_cells(thresh)

        # Extract text from each cell
        table_data = self._extract_cells_text(gray, cells)

        return table_data

    def _count_columns(self, roi):
        """Count number of columns in a table region."""
        # Threshold
        _, thresh = cv2.threshold(roi, 150, 255, cv2.THRESH_BINARY_INV)

        # Find vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, self.line_max_width))
        detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

        # Count vertical lines
        column_count = 0
        prev_x = -self.line_min_width * 2  # Initialize with a value that ensures first line is counted

        # Find contours of vertical lines
        cnts = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        # Sort contours from left to right
        sorted_cnts = sorted(cnts, key=lambda c: cv2.boundingRect(c)[0])

        for c in sorted_cnts:
            x, y, w, h = cv2.boundingRect(c)
            # Only count if line is tall enough and far enough from previous line
            if h > roi.shape[0] * 0.5 and x - prev_x > self.line_min_width:
                column_count += 1
                prev_x = x

        # Add 1 to account for columns (not just dividers)
        return column_count + 1

    def _find_cells(self, thresh):
        """Find cells in a table."""
        # Simplified implementation - in a real system you would need more sophisticated cell detection
        # This example just finds horizontal and vertical lines to determine cell boundaries

        # Find horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.line_max_width, 1))
        horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

        # Find vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, self.line_max_width))
        vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

        # Combine lines
        table_grid = cv2.add(horizontal_lines, vertical_lines)

        # Dilate grid lines
        kernel = np.ones((3, 3), np.uint8)
        table_grid = cv2.dilate(table_grid, kernel, iterations=1)

        # Invert grid to get cells
        cells = cv2.bitwise_not(table_grid)

        # Find contours of cells
        cnts = cv2.findContours(cells, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        # Get cell bounding boxes
        cell_boxes = []
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            # Filter out small regions
            if w > 20 and h > 10:
                cell_boxes.append((x, y, w, h))

        return cell_boxes

    def _extract_cells_text(self, image, cells):
        """Extract text from table cells.

        In a real implementation, this would use OCR on each cell.
        This simplified version just creates a DataFrame with cell positions.
        """
        # Sort cells by position (top to bottom, left to right)
        sorted_cells = sorted(cells, key=lambda box: (box[1], box[0]))

        # Determine rows and columns
        unique_y_coords = set()
        for x, y, w, h in sorted_cells:
            # Use the center of the cell to determine row
            center_y = y + h // 2
            unique_y_coords.add(center_y // 20 * 20)  # Group rows with similar y coordinates

        unique_y_coords = sorted(list(unique_y_coords))
        num_rows = len(unique_y_coords)

        # Group cells by row
        rows = [[] for _ in range(num_rows)]
        for x, y, w, h in sorted_cells:
            center_y = y + h // 2
            row_idx = unique_y_coords.index(center_y // 20 * 20)
            rows[row_idx].append((x, y, w, h))

        # Sort cells in each row by x coordinate
        for i in range(num_rows):
            rows[i] = sorted(rows[i], key=lambda box: box[0])

        # Create DataFrame
        if not rows:
            return pd.DataFrame()

        # Get the maximum number of columns
        max_cols = max(len(row) for row in rows)

        # Initialize data with empty strings
        data = [["" for _ in range(max_cols)] for _ in range(num_rows)]

        # In a real implementation, you would use OCR to extract text from each cell
        # For this example, we'll just put placeholders
        for row_idx, row in enumerate(rows):
            for col_idx, (x, y, w, h) in enumerate(row):
                if col_idx < max_cols:
                    data[row_idx][col_idx] = f"Cell {row_idx},{col_idx}"

        return pd.DataFrame(data)