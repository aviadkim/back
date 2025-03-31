import logging
import os
from pathlib import Path
from pdf2image import convert_from_path, pdfinfo_from_path
from .extraction.enhanced_ocr import EnhancedOCR
from .tables.enhanced_table_detector import EnhancedTableDetector
from .analysis.entity_recognition import FinancialEntityRecognizer
from .analysis.financial_ratio_analyzer import FinancialRatioAnalyzer # Import the ratio analyzer
from utils.error_handler import ErrorHandler # Import centralized error handler

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Orchestrates the processing of a document using OCR, table detection, and entity recognition."""

    def __init__(self, config=None):
        """Initialize the DocumentProcessor with necessary components."""
        self.config = config or {}
        self.ocr_processor = EnhancedOCR(config=self.config.get('ocr', {}))
        self.table_detector = EnhancedTableDetector(config=self.config.get('tables', {}))
        self.entity_recognizer = FinancialEntityRecognizer() # Configurable later if needed
        self.ratio_analyzer = FinancialRatioAnalyzer() # Initialize the ratio analyzer
        logger.info("DocumentProcessor initialized.")

    def process_document(self, file_path):
        """
        Process a document file (currently supports PDF).

        Args:
            file_path (str or Path): Path to the document file.

        Returns:
            dict: A dictionary containing the processing results (metadata, text, tables, entities, ratios)
                  or an error message.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {"error": "File not found"}
        if not file_path.suffix.lower() == '.pdf':
            logger.error(f"Unsupported file type: {file_path.suffix}")
            return {"error": "Unsupported file type, only PDF is supported"}

        logger.info(f"Starting processing for document: {file_path.name}")

        full_text = ""
        all_tables = {}
        all_entities_structured = {} # Keep the structured entities from recognizer
        formatted_entities_for_ratios = [] # List for ratio analyzer input
        page_count = 0
        language_detected = self.config.get('default_language', 'eng') # Default language

        try:
            # Get PDF metadata (like page count)
            pdf_info = pdfinfo_from_path(file_path, userpw=None, poppler_path=None)
            page_count = pdf_info.get('Pages', 0)
            logger.info(f"Document has {page_count} pages.")

            # Process each page
            for i in range(page_count):
                page_num = i + 1
                logger.debug(f"Processing page {page_num}/{page_count}")

                # 1. Convert page to image
                try:
                    images = convert_from_path(file_path, first_page=page_num, last_page=page_num, dpi=300) # Use higher DPI
                    if not images:
                        logger.warning(f"Could not convert page {page_num} to image.")
                        continue
                    page_image = images[0]
                except Exception as img_err:
                    logger.error(f"Error converting page {page_num} to image: {img_err}")
                    continue # Skip page on conversion error

                # 2. Perform OCR on the page image
                # Use 'auto' language detection based on config
                page_text = self.ocr_processor.process_image(page_image, language='auto')
                full_text += f"\n--- Page {page_num} ---\n{page_text}"

                # Basic language detection heuristic (if Hebrew found, assume Hebrew)
                if self.ocr_processor._contains_hebrew(page_text):
                     language_detected = 'heb' # Or a mix like 'heb+eng'

                # 3. Detect tables on the page image
                table_regions = self.table_detector.detect_tables(page_image)
                page_tables = []
                if table_regions:
                    logger.info(f"Detected {len(table_regions)} tables on page {page_num}")
                    for region_idx, region in enumerate(table_regions):
                        # 4. Extract content from each detected table
                        table_df = self.table_detector.extract_table_content(page_image, region)
                        if table_df is not None and not table_df.empty:
                             # Convert DataFrame to list of lists for JSON serialization
                             table_data = {
                                 "id": f"page_{page_num}_table_{region_idx+1}",
                                 "page": page_num,
                                 "region": region, # (x, y, w, h)
                                 "data": table_df.values.tolist(),
                                 "header": table_df.columns.tolist()
                             }
                             page_tables.append(table_data)
                        else:
                             logger.warning(f"Could not extract content for table {region_idx+1} on page {page_num}")

                if page_tables:
                    all_tables[str(page_num)] = page_tables

            # 5. Perform entity recognition on the full text
            logger.info("Performing entity recognition on full text...")
            all_entities_structured = self.entity_recognizer.extract_entities(full_text)

            # Format entities for ratio analyzer input
            # This structure matches the example in the feedback's test case
            for entity_type, instances in all_entities_structured.items():
                 # Ensure instances is a list before iterating
                 if not isinstance(instances, list):
                      logger.warning(f"Expected list for entity type '{entity_type}', got {type(instances)}. Skipping.")
                      continue
                 for instance in instances:
                      # Map the recognized entity type (e.g., 'currency_amounts') to a more general term if needed
                      # For now, use a simplified mapping or pass the raw type
                      item_type_for_ratio = entity_type.replace('_', ' ') # Basic conversion
                      entity_record = {'itemType': item_type_for_ratio, 'itemValue': instance}

                      # Attempt to parse numeric value if applicable (e.g., currency, percentage)
                      numeric_value = None
                      if entity_type == 'currency_amounts':
                           # Use the analyzer's parsing logic
                           numeric_value = self.ratio_analyzer._parse_numeric_value(instance)
                      elif entity_type == 'percentages':
                           try:
                                numeric_str = str(instance).replace('%', '').strip() # Ensure string conversion
                                numeric_value = float(numeric_str) / 100.0
                           except (ValueError, TypeError):
                                pass # Keep numeric_value as None
                      # Add other types if needed (e.g., if recognizer returns numeric types directly)

                      if numeric_value is not None:
                           entity_record['numericValue'] = numeric_value
                      formatted_entities_for_ratios.append(entity_record)

            # 6. Calculate financial ratios
            logger.info("Calculating financial ratios...")
            # Pass the formatted entities list to the ratio analyzer
            calculated_ratios = self.ratio_analyzer.calculate_ratios({"entities": formatted_entities_for_ratios})

            # 7. Assemble the final results
            result = {
                "metadata": {
                    "filename": file_path.name,
                    "page_count": page_count,
                    "language": language_detected, # Add detected language
                    "processing_status": "completed",
                    "size_bytes": file_path.stat().st_size,
                    # Add more metadata as needed (e.g., processing time)
                },
                "full_text": full_text,
                "tables": all_tables, # Dictionary with page number as key
                "entities": all_entities_structured, # Keep the original structured entities
                "ratios": calculated_ratios # Add the calculated ratios
            }
            logger.info(f"Successfully processed document: {file_path.name}")
            return result

        except Exception as e:
            logger.exception(f"Error processing document {file_path.name}: {e}")
            # Use centralized error handler format if possible
            error_info = ErrorHandler.handle_pdf_extraction_error(e, str(file_path))
            return {
                 "error": error_info["message"],
                 "details": error_info["error"],
                 "metadata": {
                     "filename": file_path.name,
                     "processing_status": "failed"
                 }
            }
