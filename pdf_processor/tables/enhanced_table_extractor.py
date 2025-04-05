import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import os
from pdf2image import convert_from_path
from PIL import Image
import torch # Added import
import cv2 # Added import for color conversion
# Assuming standard installation paths for table-transformer and transformers
# Adjust imports if necessary based on actual library structure
from transformers import DetrFeatureExtractor, TableTransformerForObjectDetection
# We might need a separate structure recognition model or the detection model might handle both
# For now, let's assume we need both detection and structure recognition models.
# Using example model names, replace if different ones were installed/intended.
# Note: table_transformer library itself might have wrapper classes. Using transformers directly for now.
# from table_transformer.models import TableTransformer # Example if library provides direct class
import re # Added missing import for pdfinfo parsing

logger = logging.getLogger(__name__)

class EnhancedTableExtractor:
    """
    Advanced table extraction from images and PDFs with specialized support
    for financial tables in Hebrew and English. Now uses Table-Transformer.
    """

    # TODO: Consider adding model caching or making model loading configurable
    DETECTION_MODEL_NAME = "microsoft/table-transformer-detection"
    STRUCTURE_MODEL_NAME = "microsoft/table-transformer-structure-recognition-v1.1-all" # Using v1.1 as example

    def __init__(self, language: str = "eng+heb"): # Removed unused use_hough_transform
        """
        Initialize the enhanced table extractor using Table-Transformer models.

        Args:
            language: OCR language(s) hint (may be used by structure model if it performs OCR)
        """
        self.language = language # Keep language if structure model uses it
        self.logger = logging.getLogger(__name__)

        try:
            self.logger.info(f"Loading Table-Transformer models: Detection='{self.DETECTION_MODEL_NAME}', Structure='{self.STRUCTURE_MODEL_NAME}'")
            # Load models and feature extractor
            self.feature_extractor = DetrFeatureExtractor() # Default feature extractor
            self.detection_model = TableTransformerForObjectDetection.from_pretrained(self.DETECTION_MODEL_NAME)
            # Assuming structure recognition is also handled by a TableTransformerForObjectDetection model type
            # Or it might be a different class from table_transformer library itself.
            # Adjust the class if necessary.
            self.structure_model = TableTransformerForObjectDetection.from_pretrained(self.STRUCTURE_MODEL_NAME)
            # TODO: Add device placement (e.g., .to('cuda') if GPU is available)
            self.logger.info("Table-Transformer models loaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load Table-Transformer models: {e}", exc_info=True)
            # Raise or handle appropriately - perhaps disable table extraction
            raise RuntimeError("Failed to initialize Table-Transformer models") from e

        # Specialized patterns for financial data (Kept in case needed for post-processing)
        self.number_pattern = r'[-+]?[\d,]+\.?\d*%?'
        self.currency_pattern = r'[$₪€£¥]'
        self.date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'

        # Headers commonly found in financial tables (Kept in case needed for post-processing)
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
        Uses Table-Transformer via extract_tables_from_image.
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

                    # Process the page image using the new method
                    page_image = np.array(images[0])
                    tables = self.extract_tables_from_image(page_image)

                    if tables:
                        result[page_num - 1] = tables  # Store with 0-based index
                        self.logger.info(f"Found {len(tables)} tables on page {page_num} using Table-Transformer.")
                    else:
                         self.logger.info(f"No tables found on page {page_num} using Table-Transformer.")


                except Exception as e:
                    self.logger.error(f"Error processing page {page_num} of {pdf_path}: {str(e)}", exc_info=True)

            return result

        except Exception as e:
            self.logger.error(f"Failed to extract tables from {pdf_path}: {str(e)}", exc_info=True)
            return result

    def extract_tables_from_image(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Extract tables from an image using Table-Transformer models.

        Args:
            image: NumPy array containing the image (expected BGR format from pdf2image/cv2)

        Returns:
            List of dictionaries containing table data and metadata
        """
        tables = []
        try:
            # Convert NumPy array (BGR) to PIL RGB Image
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).convert("RGB")
            width, height = pil_image.size
            self.logger.debug(f"Processing image with shape: ({width}, {height}) using Table-Transformer.")

            # 1. Detect table locations using the detection model
            # Prepare image for detection model
            encoding = self.feature_extractor(pil_image, return_tensors="pt")
            # TODO: Add device placement if needed: encoding.to(self.detection_model.device)

            with torch.no_grad():
                 outputs = self.detection_model(**encoding)

            # Post-process detection results to get table bounding boxes
            # Target sizes need to match the original image size for bbox conversion
            target_sizes = torch.tensor([pil_image.size[::-1]]) # size is (width, height), tensor needs (height, width)
            detection_results = self.feature_extractor.post_process_object_detection(
                outputs, threshold=0.7, target_sizes=target_sizes # Adjust threshold as needed
            )[0] # Get results for the first (only) image

            # Filter detections for tables based on label ID
            table_label_id = self.detection_model.config.label2id["table"]
            table_indices = [i for i, label in enumerate(detection_results['labels']) if label == table_label_id]
            detected_table_boxes = detection_results['boxes'][table_indices]
            detected_table_scores = detection_results['scores'][table_indices]

            self.logger.info(f"Detected {len(detected_table_boxes)} potential tables (detection score > {0.7}).") # Use actual threshold

            # 2. For each detected table, extract structure using the structure model
            for i, (box, score) in enumerate(zip(detected_table_boxes, detected_table_scores)):
                try:
                    # Crop the table from the original PIL image
                    table_crop = pil_image.crop(box.tolist())
                    self.logger.debug(f"Processing detected table {i} (score: {score:.2f}) with bbox: {box.tolist()}")

                    # Prepare cropped table image for structure recognition model
                    structure_encoding = self.feature_extractor(table_crop, return_tensors="pt")
                    # TODO: Add device placement if needed

                    with torch.no_grad():
                        structure_outputs = self.structure_model(**structure_encoding)

                    # Post-process structure recognition results
                    structure_target_sizes = torch.tensor([table_crop.size[::-1]])
                    structure_results = self.feature_extractor.post_process_object_detection(
                        structure_outputs, threshold=0.6, target_sizes=structure_target_sizes # Adjust threshold
                    )[0]

                    # TODO: Implement logic to reconstruct the table from structure_results
                    # This involves mapping detected elements (rows, columns, headers, cells)
                    # and potentially running OCR on cell bounding boxes if the model doesn't provide text.
                    # This part is complex and depends heavily on the specific model's output format.
                    # For now, we'll create a placeholder structure.
                    # Example placeholder:
                    header = ["Header 1", "Header 2"] # Placeholder
                    rows = [["Row1Cell1", "Row1Cell2"], ["Row2Cell1", "Row2Cell2"]] # Placeholder
                    row_count = len(rows)
                    col_count = len(header) if header else (len(rows[0]) if rows else 0)

                    # --- Placeholder Logic Start ---
                    # Actual implementation requires parsing structure_results['boxes'], structure_results['labels'],
                    # structure_results['scores'] according to self.structure_model.config.label2id mapping
                    # (e.g., "table row", "table column", "table cell", "table column header")
                    # and potentially using an OCR engine (like easyocr or tesseract) on cell boxes.
                    self.logger.warning(f"Table {i} structure reconstruction logic is a placeholder.")
                    # --- Placeholder Logic End ---


                    if row_count >= 1 and col_count >= 1: # Simplified check for placeholder
                         table_dict = {
                            "id": f"tt-{i}", # Table-Transformer ID
                            "bbox": box.tolist(), # Use the detection bbox
                            "header": header,
                            "rows": rows,
                            "row_count": row_count + (1 if header else 0), # Include header in count
                            "col_count": col_count,
                            "detection_score": score.item(), # Add detection score
                            "extraction_method": "table-transformer"
                         }
                         tables.append(table_dict)
                         self.logger.debug(f"Added table {i} from Table-Transformer.")
                    else:
                         self.logger.debug(f"Skipping table {i} from Table-Transformer due to insufficient structure (placeholder).")

                except Exception as e:
                    self.logger.error(f"Error processing detected table {i}: {str(e)}", exc_info=True)


            # No fallback to text-based method for now, focusing on Table-Transformer
            if not tables:
                 self.logger.info("No tables extracted using Table-Transformer.")

            return tables

        except Exception as e:
            self.logger.error(f"Error extracting tables from image using Table-Transformer: {str(e)}", exc_info=True)
            return []

    # --- Old Methods Removed ---
    # _preprocess_image, _detect_table_regions, _detect_tables_by_lines,
    # _detect_table_cells, _detect_cells_by_lines, _extract_text_from_cells,
    # _process_table_data, _identify_tables_in_text, _process_text_lines_as_table

    # Placeholder for potential helper methods needed for Table-Transformer output processing
    # def _parse_structure_output(self, structure_results, table_crop_image):
    #     # Complex logic to convert model output boxes/labels into header/rows
    #     # May involve geometric analysis and OCR calls if text isn't included
    #     pass